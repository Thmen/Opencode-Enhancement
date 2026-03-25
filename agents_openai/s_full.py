#!/usr/bin/env python3
# Harness: all mechanisms combined -- the complete cockpit for the model.
"""
s_full.py - Full Reference Agent

Capstone implementation combining every mechanism from s01-s11.
Session s12 (task-aware worktree isolation) is taught separately.
NOT a teaching session -- this is the "put it all together" reference.

    +------------------------------------------------------------------+
    |                        FULL AGENT                                 |
    |                                                                   |
    |  System prompt (s05 skills, task-first + optional todo nag)      |
    |                                                                   |
    |  Before each LLM call:                                            |
    |  +--------------------+  +------------------+  +--------------+  |
    |  | Microcompact (s06) |  | Drain bg (s08)   |  | Check inbox  |  |
    |  | Auto-compact (s06) |  | notifications    |  | (s09)        |  |
    |  +--------------------+  +------------------+  +--------------+  |
    |                                                                   |
    |  Tool dispatch (s02 pattern):                                     |
    |  +--------+----------+----------+---------+-----------+          |
    |  | bash   | read     | write    | edit    | TodoWrite |          |
    |  | task   | load_sk  | compress | bg_run  | bg_check  |          |
    |  | t_crt  | t_get    | t_upd    | t_list  | spawn_tm  |          |
    |  | list_tm| send_msg | rd_inbox | bcast   | shutdown  |          |
    |  | plan   | idle     | claim    |         |           |          |
    |  +--------+----------+----------+---------+-----------+          |
    |                                                                   |
    |  Subagent (s04):  spawn -> work -> return summary                 |
    |  Teammate (s09):  spawn -> work -> idle -> auto-claim (s11)      |
    |  Shutdown (s10):  request_id handshake                            |
    |  Plan gate (s10): submit -> approve/reject                        |
    +------------------------------------------------------------------+

    REPL commands: /compact /tasks /team /inbox
"""

import json
import re
import subprocess
import time
from pathlib import Path

from agents_openai import s11_autonomous_agents as team_mod
from agents_openai._openai_responses import (
    append_response_output,
    build_function_call_output,
    convert_tools_to_openai,
    extract_function_calls,
    extract_output_text,
    get_client,
    get_model,
    run_tool_loop,
)
from agents_openai.s08_background_tasks import BackgroundManager

WORKDIR = Path.cwd()
TASKS_DIR = WORKDIR / ".tasks"
SKILLS_DIR = WORKDIR / "skills"
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
TOKEN_THRESHOLD = 100000


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
        result = subprocess.run(command, shell=True, cwd=WORKDIR, capture_output=True, text=True, timeout=120)
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
        return f"Wrote {len(content)} bytes to {path}"
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


class TodoManager:
    def __init__(self):
        self.items = []

    def update(self, items: list) -> str:
        validated = []
        ip = 0
        for index, item in enumerate(items):
            content = str(item.get("content", "")).strip()
            status = str(item.get("status", "pending")).lower()
            active_form = str(item.get("activeForm", "")).strip()
            if not content:
                raise ValueError(f"Item {index}: content required")
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"Item {index}: invalid status '{status}'")
            if not active_form:
                raise ValueError(f"Item {index}: activeForm required")
            if status == "in_progress":
                ip += 1
            validated.append({"content": content, "status": status, "activeForm": active_form})
        if len(validated) > 20:
            raise ValueError("Max 20 todos")
        if ip > 1:
            raise ValueError("Only one in_progress allowed")
        self.items = validated
        return self.render()

    def render(self) -> str:
        if not self.items:
            return "No todos."
        lines = []
        for item in self.items:
            marker = {"completed": "[x]", "in_progress": "[>]", "pending": "[ ]"}.get(item["status"], "[?]")
            suffix = f" <- {item['activeForm']}" if item["status"] == "in_progress" else ""
            lines.append(f"{marker} {item['content']}{suffix}")
        done = sum(1 for item in self.items if item["status"] == "completed")
        lines.append(f"\n({done}/{len(self.items)} completed)")
        return "\n".join(lines)


class TaskManager:
    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(exist_ok=True)
        self._next_id = self._max_id() + 1

    def _max_id(self) -> int:
        ids = [int(file_path.stem.split("_")[1]) for file_path in self.dir.glob("task_*.json")]
        return max(ids) if ids else 0

    def _load(self, task_id: int) -> dict:
        path = self.dir / f"task_{task_id}.json"
        if not path.exists():
            raise ValueError(f"Task {task_id} not found")
        return json.loads(path.read_text())

    def _save(self, task: dict):
        path = self.dir / f"task_{task['id']}.json"
        path.write_text(json.dumps(task, indent=2))

    def create(self, subject: str, description: str = "") -> str:
        task = {
            "id": self._next_id,
            "subject": subject,
            "description": description,
            "status": "pending",
            "blockedBy": [],
            "blocks": [],
            "owner": "",
        }
        self._save(task)
        self._next_id += 1
        return json.dumps(task, indent=2)

    def get(self, task_id: int) -> str:
        return json.dumps(self._load(task_id), indent=2)

    def update(self, task_id: int, status: str = None, add_blocked_by: list = None, add_blocks: list = None) -> str:
        task = self._load(task_id)
        if status:
            task["status"] = status
        if add_blocked_by:
            task["blockedBy"] = list(set(task["blockedBy"] + add_blocked_by))
        if add_blocks:
            task["blocks"] = list(set(task["blocks"] + add_blocks))
        self._save(task)
        return json.dumps(task, indent=2)

    def list_all(self) -> str:
        tasks = [json.loads(file_path.read_text()) for file_path in sorted(self.dir.glob("task_*.json"))]
        if not tasks:
            return "No tasks."
        return "\n".join(f"{task['id']}: {task['subject']} [{task['status']}]" for task in tasks)


class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills = {}
        if skills_dir.exists():
            for file_path in sorted(skills_dir.rglob("SKILL.md")):
                text = file_path.read_text()
                match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
                meta, body = {}, text
                if match:
                    for line in match.group(1).strip().splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            meta[key.strip()] = value.strip()
                    body = match.group(2).strip()
                name = meta.get("name", file_path.parent.name)
                self.skills[name] = {"meta": meta, "body": body}

    def descriptions(self) -> str:
        if not self.skills:
            return "(no skills)"
        return "\n".join(f"  - {name}: {skill['meta'].get('description', '-')}" for name, skill in self.skills.items())

    def load(self, name: str) -> str:
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self.skills.keys())}"
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"


TODO = TodoManager()
TASKS = TaskManager(TASKS_DIR)
SKILLS = SkillLoader(SKILLS_DIR)
BG = BackgroundManager()


def estimate_tokens(messages: list) -> int:
    return len(json.dumps(messages, default=str)) // 4


def microcompact(messages: list):
    outputs = [item for item in messages if isinstance(item, dict) and item.get("type") == "function_call_output"]
    if len(outputs) <= 3:
        return
    for item in outputs[:-3]:
        if isinstance(item.get("output"), str) and len(item["output"]) > 100:
            item["output"] = "[cleared]"


def auto_compact(messages: list, client_obj=None) -> list:
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(path, "w", encoding="utf-8") as handle:
        for item in messages:
            handle.write(json.dumps(item, default=str) + "\n")
    conv_text = json.dumps(messages, default=str)[:80000]
    response = (client_obj or get_client()).responses.create(
        model=get_model(),
        input=[{"role": "user", "content": f"Summarize for continuity:\n{conv_text}"}],
        max_output_tokens=2000,
    )
    summary = extract_output_text(response)
    return [
        {"role": "user", "content": f"[Compressed. Transcript: {path}]\n{summary}"},
        {"role": "assistant", "content": "Understood. Continuing with summary context."},
    ]


def run_subagent(prompt: str, agent_type: str = "Explore") -> str:
    sub_tools = [
        {"name": "bash", "description": "Run command.",
         "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
        {"name": "read_file", "description": "Read file.",
         "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    ]
    if agent_type != "Explore":
        sub_tools += [
            {"name": "write_file", "description": "Write file.",
             "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
            {"name": "edit_file", "description": "Edit file.",
             "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
        ]
    sub_handlers = {
        "bash": lambda command: run_bash(command),
        "read_file": lambda path: run_read(path),
        "write_file": lambda path, content: run_write(path, content),
        "edit_file": lambda path, old_text, new_text: run_edit(path, old_text, new_text),
    }
    sub_messages = [{"role": "user", "content": prompt}]
    text, _ = run_tool_loop(
        client=get_client(),
        model=get_model(),
        instructions=None,
        input_items=sub_messages,
        tools=sub_tools,
        handlers=sub_handlers,
        max_output_tokens=8000,
        max_turns=30,
    )
    return text or "(subagent failed)"


SYSTEM = f"""You are a coding agent at {WORKDIR}.
Use tools over prose. Keep todos current. Load skills on demand. Use task and team tools for larger work.

Skills available:
{SKILLS.descriptions()}"""

TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
    {"name": "TodoWrite", "description": "Update task list.",
     "input_schema": {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"content": {"type": "string"}, "status": {"type": "string"}, "activeForm": {"type": "string"}}, "required": ["content", "status", "activeForm"]}}}, "required": ["items"]}},
    {"name": "task", "description": "Spawn a subagent with fresh context.",
     "input_schema": {"type": "object", "properties": {"prompt": {"type": "string"}, "agent_type": {"type": "string"}}, "required": ["prompt"]}},
    {"name": "load_skill", "description": "Load a skill by name.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "compact", "description": "Trigger manual context compression.",
     "input_schema": {"type": "object", "properties": {"focus": {"type": "string"}}}},
    {"name": "background_run", "description": "Run command in background.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "check_background", "description": "Check background task status.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}}}},
    {"name": "task_create", "description": "Create a new task.",
     "input_schema": {"type": "object", "properties": {"subject": {"type": "string"}, "description": {"type": "string"}}, "required": ["subject"]}},
    {"name": "task_update", "description": "Update a task.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}, "status": {"type": "string"}, "addBlockedBy": {"type": "array", "items": {"type": "integer"}}, "addBlocks": {"type": "array", "items": {"type": "integer"}}}, "required": ["task_id"]}},
    {"name": "task_list", "description": "List tasks.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "task_get", "description": "Get a task by id.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"]}},
    {"name": "spawn_teammate", "description": "Spawn an autonomous teammate.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "role": {"type": "string"}, "prompt": {"type": "string"}}, "required": ["name", "role", "prompt"]}},
    {"name": "list_teammates", "description": "List teammates.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "send_message", "description": "Send a message to a teammate.",
     "input_schema": {"type": "object", "properties": {"to": {"type": "string"}, "content": {"type": "string"}, "msg_type": {"type": "string", "enum": list(team_mod.VALID_MSG_TYPES)}}, "required": ["to", "content"]}},
    {"name": "read_inbox", "description": "Read and drain the lead inbox.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "broadcast", "description": "Broadcast to teammates.",
     "input_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}},
]


def tool_handlers():
    handlers = {
        "bash": lambda command: run_bash(command),
        "read_file": lambda path, limit=None: run_read(path, limit),
        "write_file": lambda path, content: run_write(path, content),
        "edit_file": lambda path, old_text, new_text: run_edit(path, old_text, new_text),
        "TodoWrite": lambda items: TODO.update(items),
        "task": lambda prompt, agent_type=None: run_subagent(prompt, agent_type or "Explore"),
        "load_skill": lambda name: SKILLS.load(name),
        "compact": lambda focus=None: "Compressing...",
        "background_run": lambda command: BG.run(command),
        "check_background": lambda task_id=None: BG.check(task_id),
        "task_create": lambda subject, description=None: TASKS.create(subject, description or ""),
        "task_update": lambda task_id, status=None, addBlockedBy=None, addBlocks=None: TASKS.update(task_id, status, addBlockedBy, addBlocks),
        "task_list": lambda: TASKS.list_all(),
        "task_get": lambda task_id: TASKS.get(task_id),
        "spawn_teammate": lambda name, role, prompt: team_mod.TEAM.spawn(name, role, prompt),
        "list_teammates": lambda: team_mod.TEAM.list_all(),
        "send_message": lambda to, content, msg_type=None: team_mod.BUS.send("lead", to, content, msg_type or "message"),
        "read_inbox": lambda: json.dumps(team_mod.BUS.read_inbox("lead"), indent=2),
        "broadcast": lambda content: team_mod.BUS.broadcast("lead", content, team_mod.TEAM.member_names()),
    }
    return handlers


def agent_loop(messages: list, client_obj=None) -> str:
    client = client_obj or get_client()
    handlers = tool_handlers()
    openai_tools = convert_tools_to_openai(TOOLS)

    while True:
        microcompact(messages)
        if estimate_tokens(messages) > TOKEN_THRESHOLD:
            messages[:] = auto_compact(messages, client_obj=client)

        notifs = BG.drain_notifications()
        if notifs:
            notif_text = "\n".join(f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs)
            messages.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})
            messages.append({"role": "assistant", "content": "Noted background results."})

        inbox = team_mod.BUS.read_inbox("lead")
        if inbox:
            messages.append({"role": "user", "content": f"<inbox>{json.dumps(inbox, indent=2)}</inbox>"})
            messages.append({"role": "assistant", "content": "Noted inbox messages."})

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
                payload = json.loads(call.arguments or "{}")
                if not isinstance(payload, dict):
                    raise ValueError("Function arguments must decode to an object")
                output = handlers.get(call.name, lambda **_: f"Unknown tool: {call.name}")(**payload)
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
            query = input("\033[36ms_full_openai >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        if query.strip() == "/compact":
            history[:] = auto_compact(history)
            print("[manual compact complete]")
            continue
        if query.strip() == "/tasks":
            print(TASKS.list_all())
            continue
        if query.strip() == "/team":
            print(team_mod.TEAM.list_all())
            continue
        if query.strip() == "/inbox":
            print(json.dumps(team_mod.BUS.read_inbox("lead"), indent=2))
            continue
        history.append({"role": "user", "content": query})
        final_text = agent_loop(history)
        if final_text:
            print(final_text)
        print()
