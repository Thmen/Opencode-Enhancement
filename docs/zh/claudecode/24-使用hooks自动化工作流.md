[首页](README.md) / 使用 hooks 自动化工作流

# 使用 hooks 自动化工作流

> 当 Claude Code 编辑文件、完成任务或需要输入时自动运行 shell 命令。格式化代码、发送通知、验证命令并强制执行项目规则。

Hooks 是用户定义的 shell 命令，在 Claude Code 生命周期中的特定点执行。它们对 Claude Code 的行为提供确定性控制，确保某些操作始终发生，而不是依赖 LLM 选择运行它们。使用 hooks 来强制执行项目规则、自动化重复任务，并将 Claude Code 与现有工具集成。

对于需要判断而不是确定性规则的决策，你也可以使用 [基于提示的 hooks](快速开始/01-ClaudeCode概述.md#prompt-based-hooks) 或 [基于代理的 hooks](快速开始/01-ClaudeCode概述.md#agent-based-hooks)，它们使用 Claude 模型来评估条件。

有关扩展 Claude Code 的其他方式，请参阅 [skills](45-使用skills扩展Claude.md)，用于为 Claude 提供额外的指令和可执行命令，[subagents](47-创建自定义subagents.md) 用于在隔离的上下文中运行任务，以及 [plugins](37-创建插件.md) 用于打包要在项目间共享的扩展。

<Tip>
  本指南涵盖常见用例和入门方法。有关完整的事件架构、JSON 输入/输出格式和异步 hooks 和 MCP 工具 hooks 等高级功能，请参阅 [Hooks 参考](23-Hooks参考.md)。
</Tip>

## 设置你的第一个 hook

要创建 hook，请将 `hooks` 块添加到 [设置文件](快速开始/01-ClaudeCode概述.md#configure-hook-location)。本演练创建一个桌面通知 hook，这样每当 Claude 等待你的输入而不是监视终端时，你都会收到警报。

<Steps>
  <Step title="将 hook 添加到你的设置">
    打开 `~/.claude/settings.json` 并添加一个 `Notification` hook。下面的示例使用 `osascript` 用于 macOS；有关 Linux 和 Windows 命令，请参阅 [在 Claude 需要输入时获得通知](快速开始/01-ClaudeCode概述.md#get-notified-when-claude-needs-input)。

    ```json  theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
              }
            ]
          }
        ]
      }
    }
    ```

    如果你的设置文件已经有一个 `hooks` 键，请将 `Notification` 条目合并到其中，而不是替换整个对象。你也可以通过在 CLI 中描述你想要的内容来要求 Claude 为你编写 hook。
  </Step>

  <Step title="验证配置">
    输入 `/hooks` 打开 hooks 浏览器。你将看到所有可用 hook 事件的列表，每个配置了 hooks 的事件旁边都有一个计数。选择 `Notification` 以确认你的新 hook 出现在列表中。选择 hook 会显示其详细信息：事件、匹配器、类型、源文件和命令。
  </Step>

  <Step title="测试 hook">
    按 `Esc` 返回 CLI。要求 Claude 做需要权限的事情，然后切换离开终端。你应该会收到桌面通知。
  </Step>
</Steps>

<Tip>
  `/hooks` 菜单是只读的。要添加、修改或删除 hooks，请直接编辑你的设置 JSON 或要求 Claude 进行更改。
</Tip>

## 你可以自动化什么

Hooks 让你在 Claude Code 生命周期中的关键点运行代码：编辑后格式化文件、在执行前阻止命令、在 Claude 需要输入时发送通知、在会话开始时注入上下文等。有关完整的 hook 事件列表，请参阅 [Hooks 参考](23-Hooks参考.md#hook-lifecycle)。

每个示例都包含一个现成的配置块，你可以将其添加到 [设置文件](快速开始/01-ClaudeCode概述.md#configure-hook-location)。最常见的模式：

* [在 Claude 需要输入时获得通知](快速开始/01-ClaudeCode概述.md#get-notified-when-claude-needs-input)
* [编辑后自动格式化代码](快速开始/01-ClaudeCode概述.md#auto-format-code-after-edits)
* [阻止对受保护文件的编辑](快速开始/01-ClaudeCode概述.md#block-edits-to-protected-files)
* [压缩后重新注入上下文](快速开始/01-ClaudeCode概述.md#re-inject-context-after-compaction)
* [审计配置更改](快速开始/01-ClaudeCode概述.md#audit-configuration-changes)
* [自动批准特定权限提示](快速开始/01-ClaudeCode概述.md#auto-approve-specific-permission-prompts)

### 在 Claude 需要输入时获得通知

每当 Claude 完成工作并需要你的输入时获得桌面通知，这样你可以切换到其他任务而无需检查终端。

此 hook 使用 `Notification` 事件，当 Claude 等待输入或权限时触发。下面的每个选项卡使用平台的原生通知命令。将其添加到 `~/.claude/settings.json`：

<Tabs>
  <Tab title="macOS">
    ```json  theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>

  <Tab title="Linux">
    ```json  theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>

  <Tab title="Windows (PowerShell)">
    ```json  theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "powershell.exe -Command \"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('Claude Code needs your attention', 'Claude Code')\""
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>
</Tabs>

### 编辑后自动格式化代码

在 Claude 编辑的每个文件上自动运行 [Prettier](https://prettier.io/)，以便格式保持一致而无需手动干预。

此 hook 使用带有 `Edit|Write` 匹配器的 `PostToolUse` 事件，因此它仅在文件编辑工具之后运行。该命令使用 [`jq`](https://jqlang.github.io/jq/) 提取编辑的文件路径并将其传递给 Prettier。将其添加到项目根目录中的 `.claude/settings.json`：

```json  theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

<Note>
  本页上的 Bash 示例使用 `jq` 进行 JSON 解析。使用 `brew install jq`（macOS）、`apt-get install jq`（Debian/Ubuntu）安装它，或参阅 [`jq` 下载](https://jqlang.github.io/jq/download/)。
</Note>

### 阻止对受保护文件的编辑

防止 Claude 修改敏感文件，如 `.env`、`package-lock.json` 或 `.git/` 中的任何内容。Claude 会收到解释编辑被阻止原因的反馈，因此它可以调整其方法。

此示例使用 hook 调用的单独脚本文件。该脚本根据受保护模式列表检查目标文件路径，并以代码 2 退出以阻止编辑。

<Steps>
  <Step title="创建 hook 脚本">
    将其保存到 `.claude/hooks/protect-files.sh`：

    ```bash  theme={null}
    #!/bin/bash
    # protect-files.sh

    INPUT=$(cat)
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

    PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

    for pattern in "${PROTECTED_PATTERNS[@]}"; do
      if [[ "$FILE_PATH" == *"$pattern"* ]]; then
        echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
        exit 2
      fi
    done

    exit 0
    ```
  </Step>

  <Step title="使脚本可执行（macOS/Linux）">
    Hook 脚本必须可执行才能让 Claude Code 运行它们：

    ```bash  theme={null}
    chmod +x .claude/hooks/protect-files.sh
    ```
  </Step>

  <Step title="注册 hook">
    将 `PreToolUse` hook 添加到 `.claude/settings.json`，在任何 `Edit` 或 `Write` 工具调用之前运行脚本：

    ```json  theme={null}
    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "Edit|Write",
            "hooks": [
              {
                "type": "command",
                "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
              }
            ]
          }
        ]
      }
    }
    ```
  </Step>
</Steps>

### 压缩后重新注入上下文

当 Claude 的上下文窗口填满时，压缩会总结对话以释放空间。这可能会丢失重要细节。使用带有 `compact` 匹配器的 `SessionStart` hook 在每次压缩后重新注入关键上下文。

你的命令写入 stdout 的任何文本都会添加到 Claude 的上下文中。此示例提醒 Claude 项目约定和最近的工作。将其添加到项目根目录中的 `.claude/settings.json`：

```json  theme={null}
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}
```

你可以用任何产生动态输出的命令替换 `echo`，如 `git log --oneline -5` 来显示最近的提交。有关在每个会话开始时注入上下文，请考虑改用 [CLAUDE.md](使用 Claude Code/03-Claude如何记住你的项目.md)。有关环境变量，请参阅参考中的 [`CLAUDE_ENV_FILE`](23-Hooks参考.md#persist-environment-variables)。

### 审计配置更改

跟踪会话期间设置或 skills 文件何时更改。`ConfigChange` 事件在外部进程或编辑器修改配置文件时触发，因此你可以记录更改以进行合规性检查或阻止未授权的修改。

此示例将每个更改附加到审计日志。将其添加到 `~/.claude/settings.json`：

```json  theme={null}
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log"
          }
        ]
      }
    ]
  }
}
```

匹配器按配置类型过滤：`user_settings`、`project_settings`、`local_settings`、`policy_settings` 或 `skills`。要阻止更改生效，以代码 2 退出或返回 `{"decision": "block"}`。有关完整的输入架构，请参阅 [ConfigChange 参考](23-Hooks参考.md#configchange)。

### 自动批准特定权限提示

跳过你总是允许的工具调用的批准对话。此示例自动批准 `ExitPlanMode`，这是 Claude 在完成呈现计划并要求继续时调用的工具，因此你不会在每次计划准备好时被提示。

与上面的退出代码示例不同，自动批准需要你的 hook 将 JSON 决策写入 stdout。`PermissionRequest` hook 在 Claude Code 即将显示权限对话时触发，返回 `"behavior": "allow"` 代表你回答它。

匹配器将 hook 的范围限制为仅 `ExitPlanMode`，因此没有其他提示受到影响。将其添加到 `~/.claude/settings.json`：

```json  theme={null}
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

当 hook 批准时，Claude Code 退出计划模式并恢复进入计划模式之前处于活动状态的任何权限模式。成绩单显示"Allowed by PermissionRequest hook"，其中对话会出现。hook 路径始终保持当前对话：它无法清除上下文并以对话可以的方式启动新的实现会话。

要改为设置特定的权限模式，你的 hook 的输出可以包含一个 `updatedPermissions` 数组，其中包含 `setMode` 条目。`mode` 值是任何权限模式，如 `default`、`acceptEdits` 或 `bypassPermissions`，`destination: "session"` 仅将其应用于当前会话。

要将会话切换到 `acceptEdits`，你的 hook 将此 JSON 写入 stdout：

```json  theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedPermissions": [
        { "type": "setMode", "mode": "acceptEdits", "destination": "session" }
      ]
    }
  }
}
```

保持匹配器尽可能狭窄。匹配 `.*` 或留下匹配器为空会自动批准每个权限提示，包括文件写入和 shell 命令。有关完整的决策字段集，请参阅 [PermissionRequest 参考](23-Hooks参考.md#permissionrequest-decision-control)。

## Hooks 如何工作

Hook 事件在 Claude Code 中的特定生命周期点触发。当事件触发时，所有匹配的 hooks 并行运行，相同的 hook 命令会自动去重。下表显示每个事件及其触发时间：

| Event                | When it fires                                                                                                                                  |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| `SessionStart`       | When a session begins or resumes                                                                                                               |
| `UserPromptSubmit`   | When you submit a prompt, before Claude processes it                                                                                           |
| `PreToolUse`         | Before a tool call executes. Can block it                                                                                                      |
| `PermissionRequest`  | When a permission dialog appears                                                                                                               |
| `PostToolUse`        | After a tool call succeeds                                                                                                                     |
| `PostToolUseFailure` | After a tool call fails                                                                                                                        |
| `Notification`       | When Claude Code sends a notification                                                                                                          |
| `SubagentStart`      | When a subagent is spawned                                                                                                                     |
| `SubagentStop`       | When a subagent finishes                                                                                                                       |
| `Stop`               | When Claude finishes responding                                                                                                                |
| `StopFailure`        | When the turn ends due to an API error. Output and exit code are ignored                                                                       |
| `TeammateIdle`       | When an [agent team](01-协调ClaudeCode会话团队.md) teammate is about to go idle                                                                             |
| `TaskCompleted`      | When a task is being marked as completed                                                                                                       |
| `InstructionsLoaded` | When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session |
| `ConfigChange`       | When a configuration file changes during a session                                                                                             |
| `WorktreeCreate`     | When a worktree is being created via `--worktree` or `isolation: "worktree"`. Replaces default git behavior                                    |
| `WorktreeRemove`     | When a worktree is being removed, either at session exit or when a subagent finishes                                                           |
| `PreCompact`         | Before context compaction                                                                                                                      |
| `PostCompact`        | After context compaction completes                                                                                                             |
| `Elicitation`        | When an MCP server requests user input during a tool call                                                                                      |
| `ElicitationResult`  | After a user responds to an MCP elicitation, before the response is sent back to the server                                                    |
| `SessionEnd`         | When a session terminates                                                                                                                      |

每个 hook 都有一个 `type` 来确定它如何运行。大多数 hooks 使用 `"type": "command"`，它运行 shell 命令。还有三种其他类型可用：

* `"type": "http"`：将事件数据 POST 到 URL。请参阅 [HTTP hooks](快速开始/01-ClaudeCode概述.md#http-hooks)。
* `"type": "prompt"`：单轮 LLM 评估。请参阅 [基于提示的 hooks](快速开始/01-ClaudeCode概述.md#prompt-based-hooks)。
* `"type": "agent"`：具有工具访问权限的多轮验证。请参阅 [基于代理的 hooks](快速开始/01-ClaudeCode概述.md#agent-based-hooks)。

### 读取输入并返回输出

Hooks 通过 stdin、stdout、stderr 和退出代码与 Claude Code 通信。当事件触发时，Claude Code 将事件特定的数据作为 JSON 传递到脚本的 stdin。你的脚本读取该数据，完成其工作，并通过退出代码告诉 Claude Code 接下来要做什么。

#### Hook 输入

每个事件都包含常见字段，如 `session_id` 和 `cwd`，但每个事件类型添加不同的数据。例如，当 Claude 运行 Bash 命令时，`PreToolUse` hook 在 stdin 上接收类似以下内容：

```json  theme={null}
{
  "session_id": "abc123",          // 此会话的唯一 ID
  "cwd": "/Users/sarah/myproject", // 事件触发时的工作目录
  "hook_event_name": "PreToolUse", // 哪个事件触发了此 hook
  "tool_name": "Bash",             // Claude 即将使用的工具
  "tool_input": {                  // Claude 传递给工具的参数
    "command": "npm test"          // 对于 Bash，这是 shell 命令
  }
}
```

你的脚本可以解析该 JSON 并对任何这些字段进行操作。`UserPromptSubmit` hooks 获取 `prompt` 文本，`SessionStart` hooks 获取 `source`（启动、恢复、清除、压缩），等等。有关共享字段，请参阅参考中的 [常见输入字段](23-Hooks参考.md#common-input-fields)，以及每个事件的部分了解事件特定的架构。

#### Hook 输出

你的脚本通过写入 stdout 或 stderr 并以特定代码退出来告诉 Claude Code 接下来要做什么。例如，一个想要阻止命令的 `PreToolUse` hook：

```bash  theme={null}
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q "drop table"; then
  echo "Blocked: dropping tables is not allowed" >&2  # stderr 变成 Claude 的反馈
  exit 2 # exit 2 = 阻止操作
fi

exit 0  # exit 0 = 让它继续
```

退出代码确定接下来会发生什么：

* **退出 0**：操作继续。对于 `UserPromptSubmit` 和 `SessionStart` hooks，你写入 stdout 的任何内容都会添加到 Claude 的上下文中。
* **退出 2**：操作被阻止。写入原因到 stderr，Claude 会收到它作为反馈，以便它可以调整。
* **任何其他退出代码**：操作继续。Stderr 被记录但不显示给 Claude。使用 `Ctrl+O` 切换详细模式以在成绩单中查看这些消息。

#### 结构化 JSON 输出

退出代码给你两个选项：允许或阻止。为了获得更多控制，退出 0 并改为将 JSON 对象打印到 stdout。

<Note>
  使用退出 2 以 stderr 消息阻止，或使用 JSON 退出 0 以获得结构化控制。不要混合它们：Claude Code 在你退出 2 时忽略 JSON。
</Note>

例如，`PreToolUse` hook 可以拒绝工具调用并告诉 Claude 为什么，或将其升级给用户以获得批准：

```json  theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep for better performance"
  }
}
```

Claude Code 读取 `permissionDecision` 并取消工具调用，然后将 `permissionDecisionReason` 反馈给 Claude。这三个选项特定于 `PreToolUse`：

* `"allow"`：继续而不显示权限提示
* `"deny"`：取消工具调用并将原因发送给 Claude
* `"ask"`：照常向用户显示权限提示

其他事件使用不同的决策模式。例如，`PostToolUse` 和 `Stop` hooks 使用顶级 `decision: "block"` 字段，而 `PermissionRequest` 使用 `hookSpecificOutput.decision.behavior`。有关按事件的完整分解，请参阅参考中的 [摘要表](23-Hooks参考.md#decision-control)。

对于 `UserPromptSubmit` hooks，改用 `additionalContext` 将文本注入到 Claude 的上下文中。基于提示的 hooks（`type: "prompt"`）处理输出的方式不同：请参阅 [基于提示的 hooks](快速开始/01-ClaudeCode概述.md#prompt-based-hooks)。

### 使用匹配器过滤 hooks

没有匹配器，hook 会在其事件的每次出现时触发。匹配器让你缩小范围。例如，如果你只想在文件编辑后运行格式化程序（而不是在每个工具调用后），将匹配器添加到你的 `PostToolUse` hook：

```json  theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "prettier --write ..." }
        ]
      }
    ]
  }
}
```

`"Edit|Write"` 匹配器是一个与工具名称匹配的正则表达式模式。hook 仅在 Claude 使用 `Edit` 或 `Write` 工具时触发，而不是在它使用 `Bash`、`Read` 或任何其他工具时触发。

每个事件类型在特定字段上匹配。匹配器支持精确字符串和正则表达式模式：

| 事件                                                                                         | 匹配器过滤的内容 | 示例匹配器值                                                                         |
| :----------------------------------------------------------------------------------------- | :------- | :----------------------------------------------------------------------------- |
| `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`                        | 工具名称     | `Bash`、`Edit\|Write`、`mcp__.*`                                                 |
| `SessionStart`                                                                             | 会话如何启动   | `startup`、`resume`、`clear`、`compact`                                           |
| `SessionEnd`                                                                               | 会话为什么结束  | `clear`、`logout`、`prompt_input_exit`、`bypass_permissions_disabled`、`other`     |
| `Notification`                                                                             | 通知类型     | `permission_prompt`、`idle_prompt`、`auth_success`、`elicitation_dialog`          |
| `SubagentStart`                                                                            | 代理类型     | `Bash`、`Explore`、`Plan` 或自定义代理名称                                               |
| `PreCompact`                                                                               | 什么触发了压缩  | `manual`、`auto`                                                                |
| `SubagentStop`                                                                             | 代理类型     | 与 `SubagentStart` 相同的值                                                         |
| `ConfigChange`                                                                             | 配置源      | `user_settings`、`project_settings`、`local_settings`、`policy_settings`、`skills` |
| `UserPromptSubmit`、`Stop`、`TeammateIdle`、`TaskCompleted`、`WorktreeCreate`、`WorktreeRemove` | 不支持匹配器   | 始终在每次出现时触发                                                                     |

显示不同事件类型上匹配器的更多示例：

<Tabs>
  <Tab title="记录每个 Bash 命令">
    仅匹配 `Bash` 工具调用并将每个命令记录到文件。`PostToolUse` 事件在命令完成后触发，因此 `tool_input.command` 包含运行的内容。hook 在 stdin 上接收事件数据作为 JSON，`jq -r '.tool_input.command'` 仅提取命令字符串，`>>` 将其附加到日志文件：

    ```json  theme={null}
    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Bash",
            "hooks": [
              {
                "type": "command",
                "command": "jq -r '.tool_input.command' >> ~/.claude/command-log.txt"
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>

  <Tab title="匹配 MCP 工具">
    MCP 工具使用与内置工具不同的命名约定：`mcp__<server>__<tool>`，其中 `<server>` 是 MCP 服务器名称，`<tool>` 是它提供的工具。例如，`mcp__github__search_repositories` 或 `mcp__filesystem__read_file`。使用正则表达式匹配器来针对来自特定服务器的所有工具，或使用 `mcp__.*__write.*` 之类的模式跨服务器匹配。有关完整的示例列表，请参阅参考中的 [匹配 MCP 工具](23-Hooks参考.md#match-mcp-tools)。

    下面的命令使用 `jq` 从 hook 的 JSON 输入中提取工具名称，并将其写入 stderr，其中它显示在详细模式（`Ctrl+O`）中：

    ```json  theme={null}
    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "mcp__github__.*",
            "hooks": [
              {
                "type": "command",
                "command": "echo \"GitHub tool called: $(jq -r '.tool_name')\" >&2"
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>

  <Tab title="在会话结束时清理">
    `SessionEnd` 事件支持会话结束原因的匹配器。此 hook 仅在 `clear` 时触发（当你运行 `/clear` 时），而不是在正常退出时：

    ```json  theme={null}
    {
      "hooks": {
        "SessionEnd": [
          {
            "matcher": "clear",
            "hooks": [
              {
                "type": "command",
                "command": "rm -f /tmp/claude-scratch-*.txt"
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>
</Tabs>

有关完整的匹配器语法，请参阅 [Hooks 参考](23-Hooks参考.md#configuration)。

### 配置 hook 位置

你添加 hook 的位置决定了其范围：

| 位置                                                              | 范围                      | 可共享          |
| :-------------------------------------------------------------- | :---------------------- | :----------- |
| `~/.claude/settings.json`                                       | 所有你的项目                  | 否，本地到你的机器    |
| `.claude/settings.json`                                         | 单个项目                    | 是，可以提交到仓库    |
| `.claude/settings.local.json`                                   | 单个项目                    | 否，gitignored |
| 托管策略设置                                                          | 组织范围                    | 是，管理员控制      |
| [Plugin](37-创建插件.md) `hooks/hooks.json`                     | 启用插件时                   | 是，与插件捆绑      |
| [Skill](45-使用skills扩展Claude.md) 或 [agent](47-创建自定义subagents.md) frontmatter | 当 skill 或 agent 处于活动状态时 | 是，在组件文件中定义   |

在 Claude Code 中运行 [`/hooks`](23-Hooks参考.md#the-hooks-menu) 以浏览所有按事件分组的配置 hooks。要一次禁用所有 hooks，在设置文件中设置 `"disableAllHooks": true`。

如果你在 Claude Code 运行时直接编辑设置文件，文件监视器通常会自动拾取 hook 更改。

## 基于提示的 hooks

对于需要判断而不是确定性规则的决策，使用 `type: "prompt"` hooks。Claude Code 不运行 shell 命令，而是将你的提示和 hook 的输入数据发送到 Claude 模型（默认为 Haiku）来做出决策。如果你需要更多功能，可以使用 `model` 字段指定不同的模型。

模型的唯一工作是返回一个是/否决策作为 JSON：

* `"ok": true`：操作继续
* `"ok": false`：操作被阻止。模型的 `"reason"` 被反馈给 Claude，以便它可以调整。

此示例使用 `Stop` hook 询问模型是否所有请求的任务都已完成。如果模型返回 `"ok": false`，Claude 继续工作并使用 `reason` 作为其下一条指令：

```json  theme={null}
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}."
          }
        ]
      }
    ]
  }
}
```

有关完整的配置选项，请参阅参考中的 [基于提示的 hooks](23-Hooks参考.md#prompt-based-hooks)。

## 基于代理的 hooks

当验证需要检查文件或运行命令时，使用 `type: "agent"` hooks。与只进行单个 LLM 调用的提示 hooks 不同，代理 hooks 生成一个 subagent，它可以读取文件、搜索代码和使用其他工具来验证条件，然后返回决策。

代理 hooks 使用与提示 hooks 相同的 `"ok"` / `"reason"` 响应格式，但默认超时更长（60 秒）和最多 50 个工具使用轮次。

此示例验证在允许 Claude 停止之前测试通过：

```json  theme={null}
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

当 hook 输入数据本身足以做出决策时使用提示 hooks。当你需要根据代码库的实际状态验证某些内容时使用代理 hooks。

有关完整的配置选项，请参阅参考中的 [基于代理的 hooks](23-Hooks参考.md#agent-based-hooks)。

## HTTP hooks

使用 `type: "http"` hooks 将事件数据 POST 到 HTTP 端点，而不是运行 shell 命令。端点接收命令 hook 在 stdin 上接收的相同 JSON，并使用相同的 JSON 格式通过 HTTP 响应体返回结果。

HTTP hooks 在你想要 web 服务器、云函数或外部服务处理 hook 逻辑时很有用：例如，一个跨团队记录工具使用事件的共享审计服务。

此示例将每个工具使用 POST 到本地日志服务：

```json  theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

端点应使用与命令 hooks 相同的 [输出格式](23-Hooks参考.md#json-output) 返回 JSON 响应体。要阻止工具调用，返回 2xx 响应，包含适当的 `hookSpecificOutput` 字段。HTTP 状态代码本身无法阻止操作。

标头值支持使用 `$VAR_NAME` 或 `${VAR_NAME}` 语法的环境变量插值。仅解析 `allowedEnvVars` 数组中列出的变量；所有其他 `$VAR` 引用保持为空。

有关完整的配置选项和响应处理，请参阅参考中的 [HTTP hooks](23-Hooks参考.md#http-hook-fields)。

## 限制和故障排除

### 限制

* 命令 hooks 仅通过 stdout、stderr 和退出代码通信。它们无法直接触发命令或工具调用。HTTP hooks 改为通过响应体通信。
* Hook 超时默认为 10 分钟，可通过 `timeout` 字段（以秒为单位）按 hook 配置。
* `PostToolUse` hooks 无法撤销操作，因为工具已经执行。
* `PermissionRequest` hooks 不在 [非交互模式](22-以编程方式运行ClaudeCode.md)（`-p`）中触发。对于自动化权限决策，使用 `PreToolUse` hooks。
* `Stop` hooks 在 Claude 完成响应时触发，而不仅仅在任务完成时。它们不在用户中断时触发。

### Hook 未触发

Hook 已配置但从不执行。

* 运行 `/hooks` 并确认 hook 出现在正确的事件下
* 检查匹配器模式是否与工具名称完全匹配（匹配器区分大小写）
* 验证你是否触发了正确的事件类型（例如，`PreToolUse` 在工具执行前触发，`PostToolUse` 在之后触发）
* 如果在非交互模式（`-p`）中使用 `PermissionRequest` hooks，改用 `PreToolUse`

### Hook 输出中的错误

你在成绩单中看到类似"PreToolUse hook error: ..."的消息。

* 你的脚本意外以非零代码退出。通过管道传递示例 JSON 来手动测试它：
  ```bash  theme={null}
  echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
  echo $?  # 检查退出代码
  ```
* 如果你看到"command not found"，使用绝对路径或 `$CLAUDE_PROJECT_DIR` 来引用脚本
* 如果你看到"jq: command not found"，安装 `jq` 或使用 Python/Node.js 进行 JSON 解析
* 如果脚本根本没有运行，使其可执行：`chmod +x ./my-hook.sh`

### `/hooks` 显示未配置 hooks

你编辑了设置文件但 hooks 不出现在菜单中。

* 文件编辑通常会自动拾取。如果几秒钟后它们还没有出现，文件监视器可能错过了更改：重新启动你的会话以强制重新加载。
* 验证你的 JSON 有效（不允许尾随逗号和注释）
* 确认设置文件在正确的位置：`.claude/settings.json` 用于项目 hooks，`~/.claude/settings.json` 用于全局 hooks

### Stop hook 永远运行

Claude 继续工作在无限循环中而不是停止。

你的 Stop hook 脚本需要检查它是否已经触发了继续。从 JSON 输入中解析 `stop_hook_active` 字段，如果为 `true` 则提前退出：

```bash  theme={null}
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # 允许 Claude 停止
fi
# ... 你的 hook 逻辑的其余部分
```

### JSON 验证失败

Claude Code 显示 JSON 解析错误，即使你的 hook 脚本输出有效的 JSON。

当 Claude Code 运行 hook 时，它生成一个 shell，该 shell 源你的配置文件（`~/.zshrc` 或 `~/.bashrc`）。如果你的配置文件包含无条件的 `echo` 语句，该输出会被添加到你的 hook 的 JSON 前面：

```text  theme={null}
Shell ready on arm64
{"decision": "block", "reason": "Not allowed"}
```

Claude Code 尝试将其解析为 JSON 并失败。要修复此问题，在你的 shell 配置文件中包装 echo 语句，使其仅在交互式 shell 中运行：

```bash  theme={null}
# 在 ~/.zshrc 或 ~/.bashrc 中
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

`$-` 变量包含 shell 标志，`i` 表示交互式。Hooks 在非交互式 shell 中运行，因此 echo 被跳过。

### 调试技术

使用 `Ctrl+O` 切换详细模式以在成绩单中查看 hook 输出，或运行 `claude --debug` 以获取完整的执行详情，包括哪些 hooks 匹配及其退出代码。

## 了解更多

* [Hooks 参考](23-Hooks参考.md)：完整的事件架构、JSON 输出格式、异步 hooks 和 MCP 工具 hooks
* [安全考虑](23-Hooks参考.md#security-considerations)：在共享或生产环境中部署 hooks 之前查看
* [Bash 命令验证器示例](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py)：完整的参考实现
