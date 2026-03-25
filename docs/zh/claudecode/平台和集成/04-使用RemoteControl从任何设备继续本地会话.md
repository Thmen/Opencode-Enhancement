[首页](../README.md) / [平台和集成](README.md) / 使用 Remote Control 从任何设备继续本地会话

# 使用 Remote Control 从任何设备继续本地会话

> 使用 Remote Control 从您的手机、平板电脑或任何浏览器继续本地 Claude Code 会话。适用于 claude.ai/code 和 Claude 移动应用。

<Note>
  Remote Control 在所有计划中都可用。在 Team 和 Enterprise 上，在管理员在 [Claude Code 管理员设置](https://claude.ai/admin-settings/claude-code)中启用 Remote Control 切换之前，它默认处于关闭状态。
</Note>

Remote Control 将 [claude.ai/code](https://claude.ai/code) 或 Claude 应用（[iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 和 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)）连接到在您的机器上运行的 Claude Code 会话。在您的办公桌上启动一个任务，然后从沙发上的手机或另一台计算机上的浏览器继续。

当您在机器上启动 Remote Control 会话时，Claude 始终在本地运行，因此没有任何内容移动到云端。使用 Remote Control，您可以：

* **远程使用您的完整本地环境**：您的文件系统、[MCP servers](../29-通过MCP将ClaudeCode连接到工具.md)、工具和项目配置都保持可用
* **同时从两个界面工作**：对话在所有连接的设备上保持同步，因此您可以从终端、浏览器和手机交替发送消息
* **在中断后恢复**：如果您的笔记本电脑进入睡眠状态或网络断开，当您的机器重新上线时，会话会自动重新连接

与[网络上的 Claude Code](../07-ClaudeCodeontheweb.md)（在云基础设施上运行）不同，Remote Control 会话直接在您的机器上运行并与您的本地文件系统交互。网络和移动界面只是该本地会话的一个窗口。

<Note>
  Remote Control 需要 Claude Code v2.1.51 或更高版本。使用 `claude --version` 检查您的版本。
</Note>

本页涵盖设置、如何启动和连接到会话，以及 Remote Control 与网络上的 Claude Code 的比较。

## 要求

在使用 Remote Control 之前，请确认您的环境满足以下条件：

* **订阅**：在 Pro、Max、Team 和 Enterprise 计划中可用。不支持 API 密钥。在 Team 和 Enterprise 上，管理员必须首先在 [Claude Code 管理员设置](https://claude.ai/admin-settings/claude-code)中启用 Remote Control 切换。
* **身份验证**：运行 `claude` 并使用 `/login` 通过 claude.ai 登录（如果您还没有登录）。
* **工作区信任**：在您的项目目录中至少运行一次 `claude` 以接受工作区信任对话框。

## 启动 Remote Control 会话

您可以启动专用的 Remote Control 服务器、启动启用了 Remote Control 的交互式会话，或连接已经运行的会话。

<Tabs>
  <Tab title="服务器模式">
    导航到您的项目目录并运行：

    ```bash  theme={null}
    claude remote-control
    ```

    该进程在您的终端中以服务器模式保持运行，等待远程连接。它显示一个会话 URL，您可以使用该 URL 从[另一个设备连接](../快速开始/01-ClaudeCode概述.md#connect-from-another-device)，您可以按空格键显示 QR 码以从手机快速访问。当远程会话处于活动状态时，终端显示连接状态和工具活动。

    可用标志：

    | 标志                           | 描述                                                                                                                                                                                                                  |
    | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `--name "My Project"`        | 设置自定义会话标题，在 claude.ai/code 的会话列表中可见。                                                                                                                                                                                |
    | `--spawn <mode>`             | 如何创建并发会话。在运行时按 `w` 切换。<br />• `same-dir`（默认）：所有会话共享当前工作目录，因此如果编辑相同的文件可能会冲突。<br />• `worktree`：每个按需会话都获得自己的 [git worktree](../使用 Claude Code/02-常见工作流程.md#run-parallel-claude-code-sessions-with-git-worktrees)。需要 git 存储库。 |
    | `--capacity <N>`             | 最大并发会话数。默认为 32。                                                                                                                                                                                                     |
    | `--verbose`                  | 显示详细的连接和会话日志。                                                                                                                                                                                                       |
    | `--sandbox` / `--no-sandbox` | 启用或禁用[沙箱](../39-Sandboxing.md)以进行文件系统和网络隔离。默认关闭。                                                                                                                                                                      |
  </Tab>

  <Tab title="交互式会话">
    要启动启用了 Remote Control 的普通交互式 Claude Code 会话，请使用 `--remote-control` 标志（或 `--rc`）：

    ```bash  theme={null}
    claude --remote-control
    ```

    可选地为会话传递一个名称：

    ```bash  theme={null}
    claude --remote-control "My Project"
    ```

    这为您提供了一个完整的交互式会话在您的终端中，您也可以从 claude.ai 或 Claude 应用控制。与 `claude remote-control`（服务器模式）不同，您可以在会话也可远程使用时在本地输入消息。
  </Tab>

  <Tab title="从现有会话">
    如果您已经在 Claude Code 会话中并想远程继续它，请使用 `/remote-control`（或 `/rc`）命令：

    ```text  theme={null}
    /remote-control
    ```

    传递一个名称作为参数以设置自定义会话标题：

    ```text  theme={null}
    /remote-control My Project
    ```

    这启动一个 Remote Control 会话，该会话继承您当前的对话历史记录，并显示一个会话 URL 和 QR 码，您可以使用它从[另一个设备连接](../快速开始/01-ClaudeCode概述.md#connect-from-another-device)。`--verbose`、`--sandbox` 和 `--no-sandbox` 标志不适用于此命令。
  </Tab>
</Tabs>

### 从另一个设备连接

一旦 Remote Control 会话处于活动状态，您有几种方式从另一个设备连接：

* **打开会话 URL** 在任何浏览器中直接转到 [claude.ai/code](https://claude.ai/code) 上的会话。`claude remote-control` 和 `/remote-control` 都在终端中显示此 URL。
* **扫描 QR 码** 显示在会话 URL 旁边，直接在 Claude 应用中打开它。使用 `claude remote-control` 时，按空格键切换 QR 码显示。
* **打开 [claude.ai/code](https://claude.ai/code) 或 Claude 应用** 并在会话列表中按名称查找会话。Remote Control 会话在在线时显示带有绿色状态点的计算机图标。

远程会话标题按以下顺序选择：

1. 您传递给 `--name`、`--remote-control` 或 `/remote-control` 的名称
2. 您使用 `/rename` 设置的标题
3. 现有对话历史记录中的最后一条有意义的消息
4. 您发送的第一条提示

如果环境已经有活动会话，您将被询问是否继续它或启动新会话。

如果您还没有 Claude 应用，请在 Claude Code 中使用 `/mobile` 命令显示 [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 或 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 的下载 QR 码。

### 为所有会话启用 Remote Control

默认情况下，Remote Control 仅在您显式运行 `claude remote-control`、`claude --remote-control` 或 `/remote-control` 时激活。要为每个交互式会话自动启用它，请在 Claude Code 中运行 `/config` 并将**为所有会话启用 Remote Control** 设置为 `true`。将其设置回 `false` 以禁用。

启用此设置后，每个交互式 Claude Code 进程注册一个远程会话。如果您运行多个实例，每个实例都获得自己的环境和会话。要从单个进程运行多个并发会话，请改用带有 `--spawn` 的服务器模式。

## 连接和安全

您的本地 Claude Code 会话仅发出出站 HTTPS 请求，从不在您的机器上打开入站端口。当您启动 Remote Control 时，它向 Anthropic API 注册并轮询工作。当您从另一个设备连接时，服务器通过流连接在网络或移动客户端和您的本地会话之间路由消息。

所有流量都通过 Anthropic API 通过 TLS 传输，与任何 Claude Code 会话的传输安全相同。连接使用多个短期凭证，每个凭证的范围限定为单一目的并独立过期。

## Remote Control 与网络上的 Claude Code 的比较

Remote Control 和[网络上的 Claude Code](../07-ClaudeCodeontheweb.md)都使用 claude.ai/code 界面。关键区别在于会话运行的位置：Remote Control 在您的机器上执行，因此您的本地 MCP servers、工具和项目配置保持可用。网络上的 Claude Code 在 Anthropic 管理的云基础设施中执行。

当您处于本地工作中间并想从另一个设备继续时，使用 Remote Control。当您想在没有任何本地设置的情况下启动任务、处理您没有克隆的存储库或并行运行多个任务时，使用网络上的 Claude Code。

## 限制

* **每个交互式进程一个远程会话**：在服务器模式之外，每个 Claude Code 实例一次支持一个远程会话。使用带有 `--spawn` 的服务器模式从单个进程运行多个并发会话。
* **终端必须保持打开**：Remote Control 作为本地进程运行。如果您关闭终端或停止 `claude` 进程，会话结束。再次运行 `claude remote-control` 以启动新会话。
* **扩展网络中断**：如果您的机器处于唤醒状态但无法在大约 10 分钟以上的时间内到达网络，会话超时并且进程退出。再次运行 `claude remote-control` 以启动新会话。

## 故障排除

### "Remote Control 尚未为您的账户启用"

在存在某些环境变量的情况下，资格检查可能会失败：

* `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 或 `DISABLE_TELEMETRY`：取消设置它们并重试。
* `CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_VERTEX` 或 `CLAUDE_CODE_USE_FOUNDRY`：Remote Control 需要 claude.ai 身份验证，不适用于第三方提供商。

如果这些都没有设置，请运行 `/logout` 然后 `/login` 以刷新。

### "Remote Control 被您的组织的策略禁用"

此错误有三个不同的原因。首先运行 `/status` 以查看您使用的登录方法和订阅。

* **您使用 API 密钥或 Console 账户进行身份验证**：Remote Control 需要 claude.ai OAuth。运行 `/login` 并选择 claude.ai 选项。如果在您的环境中设置了 `ANTHROPIC_API_KEY`，请取消设置它。
* **您的 Team 或 Enterprise 管理员尚未启用它**：Remote Control 在这些计划上默认处于关闭状态。管理员可以在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 通过打开 **Remote Control** 切换来启用它。这是一个服务器端组织设置，不是[仅管理设置](../35-配置权限.md#managed-only-settings)密钥。
* **管理员切换呈灰色**：您的组织有数据保留或合规配置与 Remote Control 不兼容。这无法从管理面板更改。请联系 Anthropic 支持以讨论选项。

### "Remote credentials fetch failed"

Claude Code 无法从 Anthropic API 获取短期凭证以建立连接。使用 `--verbose` 重新运行以查看完整错误：

```bash  theme={null}
claude remote-control --verbose
```

常见原因：

* 未登录：运行 `claude` 并使用 `/login` 使用您的 claude.ai 账户进行身份验证。Remote Control 不支持 API 密钥身份验证。
* 网络或代理问题：防火墙或代理可能阻止出站 HTTPS 请求。Remote Control 需要访问端口 443 上的 Anthropic API。
* 会话创建失败：如果您还看到 `Session creation failed — see debug log`，失败发生在设置的早期。检查您的订阅是否处于活动状态。

## 选择正确的方法

Claude Code offers several ways to work when you're not at your terminal. They differ in what triggers the work, where Claude runs, and how much you need to set up.

|                                                | Trigger                                                                                        | Claude runs on                                                                                                   | Setup                                                                                                                                | Best for                                                      |
| :--------------------------------------------- | :--------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| [Dispatch](../13-使用ClaudeCodeDesktop.md#sessions-from-dispatch) | Message a task from the Claude mobile app                                                      | Your machine (Desktop)                                                                                           | [Pair the mobile app with Desktop](https://support.claude.com/en/articles/13947068)                                                  | Delegating work while you're away, minimal setup              |
| [Remote Control](04-使用RemoteControl从任何设备继续本地会话.md)           | Drive a running session from [claude.ai/code](https://claude.ai/code) or the Claude mobile app | Your machine (CLI or VS Code)                                                                                    | Run `claude remote-control`                                                                                                          | Steering in-progress work from another device                 |
| [Channels](../05-使用channels将事件推送到运行中的会话.md)                       | Push events from a chat app like Telegram or Discord, or your own server                       | Your machine (CLI)                                                                                               | [Install a channel plugin](../05-使用channels将事件推送到运行中的会话.md#quickstart) or [build your own](/en/channels-reference)                                      | Reacting to external events like CI failures or chat messages |
| [Slack](05-Slack中的ClaudeCode.md)                             | Mention `@Claude` in a team channel                                                            | Anthropic cloud                                                                                                  | [Install the Slack app](05-Slack中的ClaudeCode.md#setting-up-claude-code-in-slack) with [Claude Code on the web](../07-ClaudeCodeontheweb.md) enabled | PRs and reviews from team chat                                |
| [Scheduled tasks](../40-按计划运行提示词.md)         | Set a schedule                                                                                 | [CLI](../40-按计划运行提示词.md), [Desktop](../13-使用ClaudeCodeDesktop.md#schedule-recurring-tasks), or [cloud](../52-在网络上安排任务.md) | Pick a frequency                                                                                                                     | Recurring automation like daily reviews                       |

## 相关资源

* [网络上的 Claude Code](../07-ClaudeCodeontheweb.md)：在 Anthropic 管理的云环境中运行会话，而不是在您的机器上
* [Channels](../05-使用channels将事件推送到运行中的会话.md)：将 Telegram 或 Discord 转发到会话中，以便 Claude 在您离开时对消息做出反应
* [Dispatch](../13-使用ClaudeCodeDesktop.md#sessions-from-dispatch)：从您的手机发送任务消息，它可以生成 Desktop 会话来处理它
* [身份验证](../04-身份验证.md)：设置 `/login` 并管理 claude.ai 的凭证
* [CLI 参考](../08-CLI参考.md)：包括 `claude remote-control` 的标志和命令的完整列表
* [安全](../41-安全性.md)：Remote Control 会话如何适应 Claude Code 安全模型
* [数据使用](../12-数据使用.md)：在本地和远程会话期间通过 Anthropic API 流动的数据
