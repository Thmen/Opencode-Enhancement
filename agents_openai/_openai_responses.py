from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Iterable, Mapping

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def _load_openai_env() -> None:
    load_dotenv(override=True)


def get_client():
    _load_openai_env()
    return create_client(os.getenv("OPENAI_BASE_URL"))


def get_model() -> str:
    _load_openai_env()
    return os.environ["MODEL_ID"]


def create_client(base_url: str | None = None):
    from openai import OpenAI

    kwargs = {}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _with_nullable_type(schema: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(schema)
    schema_type = updated.get("type")
    if isinstance(schema_type, str):
        if schema_type != "null":
            updated["type"] = [schema_type, "null"]
    elif isinstance(schema_type, list):
        if "null" not in schema_type:
            updated["type"] = [*schema_type, "null"]
    return updated


def normalize_schema_for_strict(schema: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(schema)
    schema_type = normalized.get("type")

    if schema_type == "object" or "properties" in normalized:
        properties = normalized.get("properties", {})
        required = set(normalized.get("required", []))
        normalized_props: dict[str, Any] = {}

        for name, prop_schema in properties.items():
            child = normalize_schema_for_strict(prop_schema)
            if name not in required:
                child = _with_nullable_type(child)
            normalized_props[name] = child

        normalized["type"] = "object"
        normalized["properties"] = normalized_props
        normalized["required"] = list(normalized_props.keys())
        normalized.setdefault("additionalProperties", False)

    if schema_type == "array" and "items" in normalized:
        normalized["items"] = normalize_schema_for_strict(normalized["items"])

    return normalized


def convert_tool_to_openai(tool: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "name": tool["name"],
        "description": tool.get("description", ""),
        "parameters": normalize_schema_for_strict(tool.get("input_schema", {"type": "object", "properties": {}})),
        "strict": True,
    }


def convert_tools_to_openai(tools: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [convert_tool_to_openai(tool) for tool in tools]


def serialize_output_item(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return deepcopy(item)
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_none=True)
    if hasattr(item, "dict") and callable(item.dict):
        return item.dict()
    if hasattr(item, "__dict__"):
        return {
            key: deepcopy(value)
            for key, value in vars(item).items()
            if not key.startswith("_")
        }
    raise TypeError(f"Cannot serialize output item of type {type(item)!r}")


def append_response_output(input_items: list[Any], response: Any) -> None:
    for item in _get_attr(response, "output", []) or []:
        input_items.append(serialize_output_item(item))


@dataclass
class FunctionCall:
    name: str
    call_id: str
    arguments: str
    raw_item: Any


def extract_function_calls(response: Any) -> list[FunctionCall]:
    calls: list[FunctionCall] = []
    for item in _get_attr(response, "output", []) or []:
        if _get_attr(item, "type") != "function_call":
            continue
        calls.append(
            FunctionCall(
                name=_get_attr(item, "name", ""),
                call_id=_get_attr(item, "call_id", ""),
                arguments=_get_attr(item, "arguments", "") or "",
                raw_item=item,
            )
        )
    return calls


def extract_output_text(response: Any) -> str:
    output_text = _get_attr(response, "output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    fragments: list[str] = []
    for item in _get_attr(response, "output", []) or []:
        if _get_attr(item, "type") != "message":
            continue
        for content in _get_attr(item, "content", []) or []:
            text_value = _get_attr(content, "text")
            if isinstance(text_value, str):
                fragments.append(text_value)
    return "".join(fragments)


def stringify_tool_output(output: Any) -> str:
    if isinstance(output, str):
        return output
    if output is None:
        return ""
    if isinstance(output, (dict, list, tuple, bool, int, float)):
        return json.dumps(output, ensure_ascii=True, default=str)
    return str(output)


def build_function_call_output(call_id: str, output: Any) -> dict[str, Any]:
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": stringify_tool_output(output),
    }


def request_once(
    *,
    client: Any,
    model: str,
    instructions: str | None,
    input_items: list[Any],
    tools: Iterable[Mapping[str, Any]],
    max_output_tokens: int = 8000,
    tool_choice: str = "auto",
    parallel_tool_calls: bool = True,
) -> tuple[Any, list[FunctionCall], str]:
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=input_items,
        tools=convert_tools_to_openai(tools),
        max_output_tokens=max_output_tokens,
        tool_choice=tool_choice,
        parallel_tool_calls=parallel_tool_calls,
    )
    append_response_output(input_items, response)
    function_calls = extract_function_calls(response)
    return response, function_calls, extract_output_text(response)


def execute_function_calls(
    function_calls: Iterable[FunctionCall],
    handlers: Mapping[str, Callable[..., Any]],
    input_items: list[Any] | None = None,
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for call in function_calls:
        handler = handlers.get(call.name)
        try:
            arguments = json.loads(call.arguments or "{}")
            if not isinstance(arguments, dict):
                raise ValueError("Function arguments must decode to an object")
            output = handler(**arguments) if handler else f"Unknown tool: {call.name}"
        except Exception as exc:
            output = f"Error: {exc}"
        item = build_function_call_output(call.call_id, output)
        outputs.append(item)
        if input_items is not None:
            input_items.append(item)
    return outputs


def run_tool_loop(
    *,
    client: Any,
    model: str,
    instructions: str | None,
    input_items: list[Any],
    tools: Iterable[Mapping[str, Any]],
    handlers: Mapping[str, Callable[..., Any]],
    max_output_tokens: int = 8000,
    tool_choice: str = "auto",
    parallel_tool_calls: bool = True,
    max_turns: int | None = None,
) -> tuple[str, Any]:
    openai_tools = convert_tools_to_openai(tools)
    turn_count = 0

    while True:
        turn_count += 1
        if max_turns is not None and turn_count > max_turns:
            raise RuntimeError(f"Tool loop exceeded max_turns={max_turns}")
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=input_items,
            tools=openai_tools,
            max_output_tokens=max_output_tokens,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
        )
        append_response_output(input_items, response)
        function_calls = extract_function_calls(response)
        if not function_calls:
            return extract_output_text(response), response

        execute_function_calls(function_calls, handlers, input_items)
