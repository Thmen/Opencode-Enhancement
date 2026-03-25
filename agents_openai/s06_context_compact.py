#!/usr/bin/env python3
# Harness: compression -- clean memory for infinite sessions.
"""
s06_context_compact.py - Compact

Three-layer compression pipeline so the agent can work forever:

    Every turn:
    +------------------+
    | Tool call result |
    +------------------+
            |
            v
    [Layer 1: micro_compact]        (silent, every turn)
      Replace tool_result content older than last 3
      with "[Previous: used {tool_name}]"
            |
            v
    [Check: tokens > 50000?]
       |               |
       no              yes
       |               |
       v               v
    continue    [Layer 2: auto_compact]
                  Save full transcript to .transcripts/
                  Ask LLM to summarize conversation.
                  Replace all messages with [summary].
                        |
                        v
                [Layer 3: compact tool]
                  Model calls compact -> immediate summarization.
                  Same as auto, triggered manually.

Key insight: "The agent can forget strategically and keep working forever."
"""

import json
import subprocess
import time
from pathlib import Path

from agents_openai._openai_responses import (
    append_response_output,
    build_function_call_output,
    convert_tools_to_openai,
    extract_function_calls,
    extract_output_text,
    get_client,
    get_model,
)

WORKDIR = Path.cwd()
SYSTEM = f"You are a coding agent at {WORKDIR}. Use tools to solve tasks."
THRESHOLD = 50000
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
KEEP_RECENT = 3


def estimate_tokens(messages: list) -> int:
    return len(str(messages)) // 4


def micro_compact(messages: list) -> list:
    tool_outputs = []
    for index, item in enumerate(messages):
        if isinstance(item, dict) and item.get("type") == "function_call_output":
            tool_outputs.append((index, item))

    if len(tool_outputs) <= KEEP_RECENT:
        return messages

    tool_name_map = {}
    for item in messages:
        if isinstance(item, dict) and item.get("type") == "function_call":
            tool_name_map[item.get("call_id", "")] = item.get("name", "unknown")

    for _, item in tool_outputs[:-KEEP_RECENT]:
        output = item.get("output")
        if isinstance(output, str) and len(output) > 100:
            tool_name = tool_name_map.get(item.get("call_id", ""), "unknown")
            item["output"] = f"[Previous: used {tool_name}]"
    return messages


def auto_compact(messages: list, client_obj=None) -> list:
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w", encoding="utf-8") as handle:
        for item in messages:
            handle.write(json.dumps(item, default=str) + "\n")

    conversation_text = json.dumps(messages, default=str)[:80000]
    response = (client_obj or get_client()).responses.create(
        model=get_model(),
        input=[
            {
                "role": "user",
                "content": (
                    "Summarize this conversation for continuity. Include: "
                    "1) What was accomplished, 2) Current state, 3) Key decisions made. "
                    "Be concise but preserve critical details.\n\n"
                    + conversation_text
                ),
            }
        ],
        max_output_tokens=2000,
    )
    summary = extract_output_text(response)
    return [
        {"role": "user", "content": f"[Conversation compressed. Transcript: {transcript_path}]\n\n{summary}"},
        {"role": "assistant", "content": "Understood. I have the context from the summary. Continuing."},
    ]


def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = (result.stdout + result.stderr).strip()
        return output[:50000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int = None) -> str:
    try:
        lines = safe_path(path).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more)"]
        return "\n".join(lines)[:50000]
    except Exception as exc:
        return f"Error: {exc}"


def run_write(path: str, content: str) -> str:
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"Wrote {len(content)} bytes"
    except Exception as exc:
        return f"Error: {exc}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        file_path = safe_path(path)
        content = file_path.read_text()
        if old_text not in content:
            return f"Error: Text not found in {path}"
        file_path.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as exc:
        return f"Error: {exc}"


TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read file contents.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to file.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "name": "compact",
        "description": "Trigger manual conversation compression.",
        "input_schema": {
            "type": "object",
            "properties": {"focus": {"type": "string", "description": "What to preserve in the summary"}},
        },
    },
]


def tool_handlers():
    return {
        "bash": lambda command: run_bash(command),
        "read_file": lambda path, limit=None: run_read(path, limit),
        "write_file": lambda path, content: run_write(path, content),
        "edit_file": lambda path, old_text, new_text: run_edit(path, old_text, new_text),
        "compact": lambda focus=None: "Compressing...",
    }


def agent_loop(messages: list, client_obj=None) -> str:
    client = client_obj or get_client()
    handlers = tool_handlers()
    openai_tools = convert_tools_to_openai(TOOLS)

    while True:
        micro_compact(messages)
        if estimate_tokens(messages) > THRESHOLD:
            messages[:] = auto_compact(messages, client_obj=client)

        response = client.responses.create(
            model=get_model(),
            instructions=SYSTEM,
            input=messages,
            tools=openai_tools,
            max_output_tokens=8000,
            tool_choice="auto",
            parallel_tool_calls=True,
        )
        append_response_output(messages, response)
        function_calls = extract_function_calls(response)
        if not function_calls:
            return extract_output_text(response)

        manual_compact = False
        for call in function_calls:
            try:
                arguments = json.loads(call.arguments or "{}")
                if not isinstance(arguments, dict):
                    raise ValueError("Function arguments must decode to an object")
                handler = handlers.get(call.name)
                output = handler(**arguments) if handler else f"Unknown tool: {call.name}"
            except Exception as exc:
                output = f"Error: {exc}"
            if call.name == "compact":
                manual_compact = True
            messages.append(build_function_call_output(call.call_id, output))

        if manual_compact:
            messages[:] = auto_compact(messages, client_obj=client)


if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms06-openai >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        final_text = agent_loop(history)
        if final_text:
            print(final_text)
        print()
