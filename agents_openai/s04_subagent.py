#!/usr/bin/env python3
# Harness: context isolation -- protecting the model's clarity of thought.
"""
s04_subagent.py - Subagents

Spawn a child agent with fresh messages=[]. The child works in its own
context, sharing the filesystem, then returns only a summary to the parent.

    Parent agent                     Subagent
    +------------------+             +------------------+
    | messages=[...]   |             | messages=[]      |  <-- fresh
    |                  |  dispatch   |                  |
    | tool: task       | ---------->| while tool_use:  |
    |   prompt="..."   |            |   call tools     |
    |   description="" |            |   append results |
    |                  |  summary   |                  |
    |   result = "..." | <--------- | return last text |
    +------------------+             +------------------+
              |
    Parent context stays clean.
    Subagent context is discarded.

Key insight: "Process isolation gives context isolation for free."
"""

import subprocess
from pathlib import Path

from agents_openai._openai_responses import get_client, get_model, run_tool_loop

WORKDIR = Path.cwd()
SYSTEM = f"You are a coding agent at {WORKDIR}. Use the task tool to delegate exploration or subtasks."
SUBAGENT_SYSTEM = f"You are a coding subagent at {WORKDIR}. Complete the given task, then summarize your findings."


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


CHILD_TOOLS = [
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
]

PARENT_TOOLS = CHILD_TOOLS + [
    {
        "name": "task",
        "description": "Spawn a subagent with fresh context. It shares the filesystem but not conversation history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "description": {"type": "string", "description": "Short description of the task"},
            },
            "required": ["prompt"],
        },
    }
]


def child_handlers(bash_runner=None):
    return {
        "bash": lambda command: (bash_runner or run_bash)(command),
        "read_file": lambda path, limit=None: run_read(path, limit),
        "write_file": lambda path, content: run_write(path, content),
        "edit_file": lambda path, old_text, new_text: run_edit(path, old_text, new_text),
    }


def run_subagent(prompt: str, client_obj=None, bash_runner=None) -> str:
    sub_messages = [{"role": "user", "content": prompt}]
    text, _ = run_tool_loop(
        client=client_obj or get_client(),
        model=get_model(),
        instructions=SUBAGENT_SYSTEM,
        input_items=sub_messages,
        tools=CHILD_TOOLS,
        handlers=child_handlers(bash_runner),
        max_output_tokens=8000,
        max_turns=30,
    )
    return text or "(no summary)"


def parent_handlers(client_obj=None, bash_runner=None, task_runner=None):
    handlers = child_handlers(bash_runner)
    handlers["task"] = lambda prompt, description=None: (
        task_runner(prompt)
        if task_runner
        else run_subagent(prompt, client_obj=client_obj, bash_runner=bash_runner)
    )
    return handlers


def agent_loop(messages: list, client_obj=None, bash_runner=None, task_runner=None) -> str:
    text, _ = run_tool_loop(
        client=client_obj or get_client(),
        model=get_model(),
        instructions=SYSTEM,
        input_items=messages,
        tools=PARENT_TOOLS,
        handlers=parent_handlers(client_obj=client_obj, bash_runner=bash_runner, task_runner=task_runner),
        max_output_tokens=8000,
    )
    return text


if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms04-openai >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        final_text = agent_loop(history)
        if final_text:
            print(final_text)
        print()
