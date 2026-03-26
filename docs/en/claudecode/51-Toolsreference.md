[Home](README.md) / Tools reference

# Tools reference

> Complete reference for the tools Claude Code can use, including permission requirements.

Claude Code has access to a set of tools that help it understand and modify your codebase. The tool names below are the exact strings you use in [permission rules](36-Configurepermissions.md#tool-specific-permission-rules), [subagent tool lists](48-Createcustomsubagents.md), and [hook matchers](24-Hooksreference.md).

| Tool                   | Description                                                                                                                                                                                                                                                                                                                                                                 | Permission Required |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------ |
| `Agent`                | Spawns a [subagent](48-Createcustomsubagents.md) with its own context window to handle a task                                                                                                                                                                                                                                                                                            | No                  |
| `AskUserQuestion`      | Asks multiple-choice questions to gather requirements or clarify ambiguity                                                                                                                                                                                                                                                                                                  | No                  |
| `Bash`                 | Executes shell commands in your environment. See [Bash tool behavior](Getting started/02-ClaudeCodeoverview.md#bash-tool-behavior)                                                                                                                                                                                                                                                                                  | Yes                 |
| `CronCreate`           | Schedules a recurring or one-shot prompt within the current session (gone when Claude exits). See [scheduled tasks](41-Runpromptsonaschedule.md)                                                                                                                                                                                                                                    | No                  |
| `CronDelete`           | Cancels a scheduled task by ID                                                                                                                                                                                                                                                                                                                                              | No                  |
| `CronList`             | Lists all scheduled tasks in the session                                                                                                                                                                                                                                                                                                                                    | No                  |
| `Edit`                 | Makes targeted edits to specific files                                                                                                                                                                                                                                                                                                                                      | Yes                 |
| `EnterPlanMode`        | Switches to plan mode to design an approach before coding                                                                                                                                                                                                                                                                                                                   | No                  |
| `EnterWorktree`        | Creates an isolated [git worktree](Use Claude Code/02-Commonworkflows.md#run-parallel-claude-code-sessions-with-git-worktrees) and switches into it                                                                                                                                                                                                                                          | No                  |
| `ExitPlanMode`         | Presents a plan for approval and exits plan mode                                                                                                                                                                                                                                                                                                                            | Yes                 |
| `ExitWorktree`         | Exits a worktree session and returns to the original directory                                                                                                                                                                                                                                                                                                              | No                  |
| `Glob`                 | Finds files based on pattern matching                                                                                                                                                                                                                                                                                                                                       | No                  |
| `Grep`                 | Searches for patterns in file contents                                                                                                                                                                                                                                                                                                                                      | No                  |
| `ListMcpResourcesTool` | Lists resources exposed by connected [MCP servers](30-ConnectClaudeCodetotoolsviaMCP.md)                                                                                                                                                                                                                                                                                                                 | No                  |
| `LSP`                  | Code intelligence via language servers. Reports type errors and warnings automatically after file edits. Also supports navigation operations: jump to definitions, find references, get type info, list symbols, find implementations, trace call hierarchies. Requires a [code intelligence plugin](17-Discoverandinstallprebuiltpluginsthroughmarketplaces.md#code-intelligence) and its language server binary | No                  |
| `NotebookEdit`         | Modifies Jupyter notebook cells                                                                                                                                                                                                                                                                                                                                             | Yes                 |
| `PowerShell`           | Executes PowerShell commands on Windows. Opt-in preview. See [PowerShell tool](Getting started/02-ClaudeCodeoverview.md#powershell-tool)                                                                                                                                                                                                                                                                            | Yes                 |
| `Read`                 | Reads the contents of files                                                                                                                                                                                                                                                                                                                                                 | No                  |
| `ReadMcpResourceTool`  | Reads a specific MCP resource by URI                                                                                                                                                                                                                                                                                                                                        | No                  |
| `Skill`                | Executes a [skill](46-ExtendClaudewithskills.md#control-who-invokes-a-skill) within the main conversation                                                                                                                                                                                                                                                                                     | Yes                 |
| `TaskCreate`           | Creates a new task in the task list                                                                                                                                                                                                                                                                                                                                         | No                  |
| `TaskGet`              | Retrieves full details for a specific task                                                                                                                                                                                                                                                                                                                                  | No                  |
| `TaskList`             | Lists all tasks with their current status                                                                                                                                                                                                                                                                                                                                   | No                  |
| `TaskOutput`           | (Deprecated) Retrieves output from a background task. Prefer `Read` on the task's output file path                                                                                                                                                                                                                                                                          | No                  |
| `TaskStop`             | Kills a running background task by ID                                                                                                                                                                                                                                                                                                                                       | No                  |
| `TaskUpdate`           | Updates task status, dependencies, details, or deletes tasks                                                                                                                                                                                                                                                                                                                | No                  |
| `TodoWrite`            | Manages the session task checklist. Available in non-interactive mode and the [Agent SDK](23-RunClaudeCodeprogrammatically.md); interactive sessions use TaskCreate, TaskGet, TaskList, and TaskUpdate instead                                                                                                                                                                                     | No                  |
| `ToolSearch`           | Searches for and loads deferred tools when [tool search](30-ConnectClaudeCodetotoolsviaMCP.md#scale-with-mcp-tool-search) is enabled                                                                                                                                                                                                                                                                     | No                  |
| `WebFetch`             | Fetches content from a specified URL                                                                                                                                                                                                                                                                                                                                        | Yes                 |
| `WebSearch`            | Performs web searches                                                                                                                                                                                                                                                                                                                                                       | Yes                 |
| `Write`                | Creates or overwrites files                                                                                                                                                                                                                                                                                                                                                 | Yes                 |

Permission rules can be configured using `/permissions` or in [permission settings](44-ClaudeCodesettings.md#available-settings). Also see [Tool-specific permission rules](36-Configurepermissions.md#tool-specific-permission-rules).

## Bash tool behavior

The Bash tool runs each command in a separate process with the following persistence behavior:

* Working directory persists across commands. Set `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` to reset to the project directory after each command.
* Environment variables do not persist. An `export` in one command will not be available in the next.

Activate your virtualenv or conda environment before launching Claude Code. To make environment variables persist across Bash commands, set [`CLAUDE_ENV_FILE`](18-Environmentvariables.md) to a shell script before launching Claude Code, or use a [SessionStart hook](24-Hooksreference.md#persist-environment-variables) to populate it dynamically.

## PowerShell tool

On Windows, Claude Code can run PowerShell commands natively instead of routing through Git Bash. This is an opt-in preview.

### Enable the PowerShell tool

Set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` in your environment or in `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}
```

Claude Code auto-detects `pwsh.exe` (PowerShell 7+) with a fallback to `powershell.exe` (PowerShell 5.1). The Bash tool remains registered alongside the PowerShell tool, so you may need to ask Claude to use PowerShell.

### Shell selection in settings, hooks, and skills

Three additional settings control where PowerShell is used:

* `"defaultShell": "powershell"` in [`settings.json`](44-ClaudeCodesettings.md#available-settings): routes interactive `!` commands through PowerShell. Requires the PowerShell tool to be enabled.
* `"shell": "powershell"` on individual [command hooks](24-Hooksreference.md#command-hook-fields): runs that hook in PowerShell. Hooks spawn PowerShell directly, so this works regardless of `CLAUDE_CODE_USE_POWERSHELL_TOOL`.
* `shell: powershell` in [skill frontmatter](46-ExtendClaudewithskills.md#frontmatter-reference): runs `` !`command` `` blocks in PowerShell. Requires the PowerShell tool to be enabled.

### Preview limitations

The PowerShell tool has the following known limitations during the preview:

* Auto mode does not work with the PowerShell tool yet
* PowerShell profiles are not loaded
* Sandboxing is not supported
* Only supported on native Windows, not WSL
* Git Bash is still required to start Claude Code

## See also

* [Permissions](36-Configurepermissions.md): permission system, rule syntax, and tool-specific patterns
* [Subagents](48-Createcustomsubagents.md): configure tool access for subagents
* [Hooks](25-Automateworkflowswithhooks.md): run custom commands before or after tool execution
