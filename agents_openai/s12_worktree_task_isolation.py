#!/usr/bin/env python3
# Harness: directory isolation -- parallel execution lanes that never collide.
"""
s12_worktree_task_isolation.py - Worktree + Task Isolation

Directory-level isolation for parallel task execution.
Tasks are the control plane and worktrees are the execution plane.

    .tasks/task_12.json
      {
        "id": 12,
        "subject": "Implement auth refactor",
        "status": "in_progress",
        "worktree": "auth-refactor"
      }

    .worktrees/index.json
      {
        "worktrees": [
          {
            "name": "auth-refactor",
            "path": ".../.worktrees/auth-refactor",
            "branch": "wt/auth-refactor",
            "task_id": 12,
            "status": "active"
          }
        ]
      }

Key insight: "Isolate by directory, coordinate by task ID."
"""

import json
import re
import subprocess
import time
from pathlib import Path

from agents_openai._openai_responses import get_client, get_model, run_tool_loop

WORKDIR = Path.cwd()


def detect_repo_root(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return None
        root = Path(result.stdout.strip())
        return root if root.exists() else None
    except Exception:
        return None


REPO_ROOT = detect_repo_root(WORKDIR) or WORKDIR
SYSTEM = (
    f"You are a coding agent at {WORKDIR}. "
    "Use task + worktree tools for multi-task work. "
    "For parallel or risky changes: create tasks, allocate worktree lanes, "
    "run commands in those lanes, then choose keep/remove for closeout. "
    "Use worktree_events when you need lifecycle visibility."
)


class EventBus:
    def __init__(self, event_log_path: Path):
        self.path = event_log_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def emit(self, event: str, task: dict | None = None, worktree: dict | None = None, error: str | None = None):
        payload = {"event": event, "ts": time.time(), "task": task or {}, "worktree": worktree or {}}
        if error:
            payload["error"] = error
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")

    def list_recent(self, limit: int = 20) -> str:
        n = max(1, min(int(limit or 20), 200))
        lines = self.path.read_text(encoding="utf-8").splitlines()
        items = []
        for line in lines[-n:]:
            try:
                items.append(json.loads(line))
            except Exception:
                items.append({"event": "parse_error", "raw": line})
        return json.dumps(items, indent=2)


class TaskManager:
    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self._next_id = self._max_id() + 1

    def _max_id(self) -> int:
        ids = []
        for file_path in self.dir.glob("task_*.json"):
            try:
                ids.append(int(file_path.stem.split("_")[1]))
            except Exception:
                pass
        return max(ids) if ids else 0

    def _path(self, task_id: int) -> Path:
        return self.dir / f"task_{task_id}.json"

    def _load(self, task_id: int) -> dict:
        path = self._path(task_id)
        if not path.exists():
            raise ValueError(f"Task {task_id} not found")
        return json.loads(path.read_text())

    def _save(self, task: dict):
        self._path(task["id"]).write_text(json.dumps(task, indent=2))

    def create(self, subject: str, description: str = "") -> str:
        task = {
            "id": self._next_id,
            "subject": subject,
            "description": description,
            "status": "pending",
            "owner": "",
            "worktree": "",
            "blockedBy": [],
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self._save(task)
        self._next_id += 1
        return json.dumps(task, indent=2)

    def get(self, task_id: int) -> str:
        return json.dumps(self._load(task_id), indent=2)

    def exists(self, task_id: int) -> bool:
        return self._path(task_id).exists()

    def update(self, task_id: int, status: str = None, owner: str = None) -> str:
        task = self._load(task_id)
        if status:
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"Invalid status: {status}")
            task["status"] = status
        if owner is not None:
            task["owner"] = owner
        task["updated_at"] = time.time()
        self._save(task)
        return json.dumps(task, indent=2)

    def bind_worktree(self, task_id: int, worktree: str, owner: str = "") -> str:
        task = self._load(task_id)
        task["worktree"] = worktree
        if owner:
            task["owner"] = owner
        if task["status"] == "pending":
            task["status"] = "in_progress"
        task["updated_at"] = time.time()
        self._save(task)
        return json.dumps(task, indent=2)

    def unbind_worktree(self, task_id: int) -> str:
        task = self._load(task_id)
        task["worktree"] = ""
        task["updated_at"] = time.time()
        self._save(task)
        return json.dumps(task, indent=2)

    def list_all(self) -> str:
        tasks = [json.loads(file_path.read_text()) for file_path in sorted(self.dir.glob("task_*.json"))]
        if not tasks:
            return "No tasks."
        lines = []
        for task in tasks:
            marker = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}.get(task["status"], "[?]")
            owner = f" owner={task['owner']}" if task.get("owner") else ""
            worktree = f" wt={task['worktree']}" if task.get("worktree") else ""
            lines.append(f"{marker} #{task['id']}: {task['subject']}{owner}{worktree}")
        return "\n".join(lines)


TASKS = TaskManager(REPO_ROOT / ".tasks")
EVENTS = EventBus(REPO_ROOT / ".worktrees" / "events.jsonl")


class WorktreeManager:
    def __init__(self, repo_root: Path, tasks: TaskManager, events: EventBus):
        self.repo_root = repo_root
        self.tasks = tasks
        self.events = events
        self.dir = repo_root / ".worktrees"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.dir / "index.json"
        if not self.index_path.exists():
            self.index_path.write_text(json.dumps({"worktrees": []}, indent=2))
        self.git_available = self._is_git_repo()

    def _is_git_repo(self) -> bool:
        try:
            result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.repo_root, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def _run_git(self, args: list[str]) -> str:
        if not self.git_available:
            raise RuntimeError("Not in a git repository. worktree tools require git.")
        result = subprocess.run(["git", *args], cwd=self.repo_root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            message = (result.stdout + result.stderr).strip()
            raise RuntimeError(message or f"git {' '.join(args)} failed")
        return (result.stdout + result.stderr).strip() or "(no output)"

    def _load_index(self) -> dict:
        return json.loads(self.index_path.read_text())

    def _save_index(self, data: dict):
        self.index_path.write_text(json.dumps(data, indent=2))

    def _find(self, name: str) -> dict | None:
        for wt in self._load_index().get("worktrees", []):
            if wt.get("name") == name:
                return wt
        return None

    def _validate_name(self, name: str):
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,40}", name or ""):
            raise ValueError("Invalid worktree name. Use 1-40 chars: letters, numbers, ., _, -")

    def create(self, name: str, task_id: int = None, base_ref: str = "HEAD") -> str:
        self._validate_name(name)
        if self._find(name):
            raise ValueError(f"Worktree '{name}' already exists in index")
        if task_id is not None and not self.tasks.exists(task_id):
            raise ValueError(f"Task {task_id} not found")

        path = self.dir / name
        branch = f"wt/{name}"
        self.events.emit("worktree.create.before", task={"id": task_id} if task_id is not None else {}, worktree={"name": name, "base_ref": base_ref})
        self._run_git(["worktree", "add", "-b", branch, str(path), base_ref])
        entry = {"name": name, "path": str(path), "branch": branch, "task_id": task_id, "status": "active", "created_at": time.time()}
        index = self._load_index()
        index["worktrees"].append(entry)
        self._save_index(index)
        if task_id is not None:
            self.tasks.bind_worktree(task_id, name)
        self.events.emit("worktree.create.after", task={"id": task_id} if task_id is not None else {}, worktree=entry)
        return json.dumps(entry, indent=2)

    def list_all(self) -> str:
        entries = self._load_index().get("worktrees", [])
        if not entries:
            return "No worktrees."
        lines = []
        for wt in entries:
            task_info = f" task={wt['task_id']}" if wt.get("task_id") is not None else ""
            lines.append(f"{wt['name']}: {wt['status']}{task_info} -> {wt['path']}")
        return "\n".join(lines)

    def status(self, name: str) -> str:
        wt = self._find(name)
        if not wt:
            return f"Error: Worktree '{name}' not found"
        result = subprocess.run(["git", "status", "--short", "--branch"], cwd=wt["path"], capture_output=True, text=True, timeout=30)
        return (result.stdout + result.stderr).strip() or "(clean)"

    def run(self, name: str, command: str) -> str:
        wt = self._find(name)
        if not wt:
            return f"Error: Worktree '{name}' not found"
        result = subprocess.run(command, shell=True, cwd=wt["path"], capture_output=True, text=True, timeout=120)
        return ((result.stdout + result.stderr).strip() or "(no output)")[:50000]

    def keep(self, name: str) -> str:
        index = self._load_index()
        for wt in index.get("worktrees", []):
            if wt.get("name") == name:
                wt["status"] = "kept"
                self._save_index(index)
                self.events.emit("worktree.keep", task={"id": wt.get("task_id")}, worktree=wt)
                return f"Marked worktree '{name}' as kept"
        return f"Error: Worktree '{name}' not found"

    def remove(self, name: str, force: bool = False, complete_task: bool = False) -> str:
        index = self._load_index()
        target = None
        remaining = []
        for wt in index.get("worktrees", []):
            if wt.get("name") == name:
                target = wt
            else:
                remaining.append(wt)
        if not target:
            return f"Error: Worktree '{name}' not found"
        args = ["worktree", "remove"]
        if force:
            args.append("--force")
        args.append(target["path"])
        self._run_git(args)
        if target.get("task_id") is not None:
            if complete_task:
                self.tasks.update(target["task_id"], status="completed")
            self.tasks.unbind_worktree(target["task_id"])
        index["worktrees"] = remaining
        self._save_index(index)
        self.events.emit("worktree.remove", task={"id": target.get("task_id")}, worktree=target)
        return f"Removed worktree '{name}'"


WORKTREES = WorktreeManager(REPO_ROOT, TASKS, EVENTS)


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
    {"name": "bash", "description": "Run a shell command in the current workspace (blocking).",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
    {"name": "task_create", "description": "Create a new task on the shared task board.",
     "input_schema": {"type": "object", "properties": {"subject": {"type": "string"}, "description": {"type": "string"}}, "required": ["subject"]}},
    {"name": "task_list", "description": "List all tasks with status, owner, and worktree binding.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "task_get", "description": "Get task details by ID.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"]}},
    {"name": "task_update", "description": "Update task status or owner.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}, "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}, "owner": {"type": "string"}}, "required": ["task_id"]}},
    {"name": "task_bind_worktree", "description": "Bind a task to a worktree name.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}, "worktree": {"type": "string"}, "owner": {"type": "string"}}, "required": ["task_id", "worktree"]}},
    {"name": "worktree_create", "description": "Create a git worktree and optionally bind it to a task.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "task_id": {"type": "integer"}, "base_ref": {"type": "string"}}, "required": ["name"]}},
    {"name": "worktree_list", "description": "List worktrees tracked in .worktrees/index.json.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "worktree_status", "description": "Show git status for one worktree.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "worktree_run", "description": "Run a shell command in a named worktree directory.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "command": {"type": "string"}}, "required": ["name", "command"]}},
    {"name": "worktree_remove", "description": "Remove a worktree and optionally mark its bound task completed.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "force": {"type": "boolean"}, "complete_task": {"type": "boolean"}}, "required": ["name"]}},
    {"name": "worktree_keep", "description": "Mark a worktree as kept in lifecycle state without removing it.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "worktree_events", "description": "List recent worktree/task lifecycle events from .worktrees/events.jsonl.",
     "input_schema": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
]


def tool_handlers():
    return {
        "bash": lambda command: run_bash(command),
        "read_file": lambda path, limit=None: run_read(path, limit),
        "write_file": lambda path, content: run_write(path, content),
        "edit_file": lambda path, old_text, new_text: run_edit(path, old_text, new_text),
        "task_create": lambda subject, description=None: TASKS.create(subject, description or ""),
        "task_list": lambda: TASKS.list_all(),
        "task_get": lambda task_id: TASKS.get(task_id),
        "task_update": lambda task_id, status=None, owner=None: TASKS.update(task_id, status, owner),
        "task_bind_worktree": lambda task_id, worktree, owner=None: TASKS.bind_worktree(task_id, worktree, owner or ""),
        "worktree_create": lambda name, task_id=None, base_ref=None: WORKTREES.create(name, task_id, base_ref or "HEAD"),
        "worktree_list": lambda: WORKTREES.list_all(),
        "worktree_status": lambda name: WORKTREES.status(name),
        "worktree_run": lambda name, command: WORKTREES.run(name, command),
        "worktree_keep": lambda name: WORKTREES.keep(name),
        "worktree_remove": lambda name, force=False, complete_task=False: WORKTREES.remove(name, force, complete_task),
        "worktree_events": lambda limit=None: EVENTS.list_recent(limit or 20),
    }


def agent_loop(messages: list, client_obj=None) -> str:
    text, _ = run_tool_loop(
        client=client_obj or get_client(),
        model=get_model(),
        instructions=SYSTEM,
        input_items=messages,
        tools=TOOLS,
        handlers=tool_handlers(),
        max_output_tokens=8000,
    )
    return text


if __name__ == "__main__":
    print(f"Repo root for s12-openai: {REPO_ROOT}")
    if not WORKTREES.git_available:
        print("Note: Not in a git repo. worktree_* tools will return errors.")
    history = []
    while True:
        try:
            query = input("\033[36ms12-openai >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        final_text = agent_loop(history)
        if final_text:
            print(final_text)
        print()
