[首页](../README.md) / [平台和集成](README.md) / 在 VS Code 中使用 Claude Code

# 在 VS Code 中使用 Claude Code

> 安装和配置 VS Code 的 Claude Code 扩展。获得 AI 编码协助，包括内联差异、@-提及、计划审查和快捷键。

<img src="https://mintcdn.com/claude-code/-YhHHmtSxwr7W8gy/images/vs-code-extension-interface.jpg?fit=max&auto=format&n=-YhHHmtSxwr7W8gy&q=85&s=300652d5678c63905e6b0ea9e50835f8" alt="VS Code 编辑器，右侧打开 Claude Code 扩展面板，显示与 Claude 的对话" width="2500" height="1155" data-path="images/vs-code-extension-interface.jpg" />

VS Code 扩展为 Claude Code 提供了原生图形界面，直接集成到您的 IDE 中。这是在 VS Code 中使用 Claude Code 的推荐方式。

使用该扩展，您可以在接受 Claude 的计划之前审查和编辑它们、在进行编辑时自动接受、@-提及具有特定行范围的文件、访问对话历史记录，以及在单独的选项卡或窗口中打开多个对话。

## 前置条件

安装前，请确保您拥有：

* VS Code 1.98.0 或更高版本
* Anthropic 账户（首次打开扩展时您将登录）。如果您使用第三方提供商（如 Amazon Bedrock 或 Google Vertex AI），请参阅[使用第三方提供商](../快速开始/01-ClaudeCode概述.md#use-third-party-providers)。

<Tip>
  该扩展包括 CLI（命令行界面），您可以从 VS Code 的集成终端访问它以获得高级功能。有关详细信息，请参阅 [VS Code 扩展与 Claude Code CLI](../快速开始/01-ClaudeCode概述.md#vs-code-extension-vs-claude-code-cli)。
</Tip>

## 安装扩展

点击您的 IDE 的链接以直接安装：

* [为 VS Code 安装](vscode:extension/anthropic.claude-code)
* [为 Cursor 安装](cursor:extension/anthropic.claude-code)

或在 VS Code 中，按 `Cmd+Shift+X`（Mac）或 `Ctrl+Shift+X`（Windows/Linux）打开扩展视图，搜索"Claude Code"，然后点击**安装**。

<Note>如果安装后扩展没有出现，请重启 VS Code 或从命令面板运行"Developer: Reload Window"。</Note>

## 开始使用

安装后，您可以通过 VS Code 界面开始使用 Claude Code：

<Steps>
  <Step title="打开 Claude Code 面板">
    在整个 VS Code 中，Spark 图标表示 Claude Code：<img src="https://mintcdn.com/claude-code/c5r9_6tjPMzFdDDT/images/vs-code-spark-icon.svg?fit=max&auto=format&n=c5r9_6tjPMzFdDDT&q=85&s=3ca45e00deadec8c8f4b4f807da94505" alt="Spark icon" style={{display: "inline", height: "0.85em", verticalAlign: "middle"}} width="16" height="16" data-path="images/vs-code-spark-icon.svg" />

    打开 Claude 的最快方式是点击**编辑器工具栏**（编辑器右上角）中的 Spark 图标。该图标仅在您打开文件时出现。

        <img src="https://mintcdn.com/claude-code/mfM-EyoZGnQv8JTc/images/vs-code-editor-icon.png?fit=max&auto=format&n=mfM-EyoZGnQv8JTc&q=85&s=eb4540325d94664c51776dbbfec4cf02" alt="VS Code 编辑器显示编辑器工具栏中的 Spark 图标" width="2796" height="734" data-path="images/vs-code-editor-icon.png" />

    打开 Claude Code 的其他方式：

    * **活动栏**：点击左侧边栏中的 Spark 图标打开会话列表。点击任何会话以将其作为完整编辑器选项卡打开，或开始新的会话。此图标在活动栏中始终可见。
    * **命令面板**：`Cmd+Shift+P`（Mac）或 `Ctrl+Shift+P`（Windows/Linux），输入"Claude Code"，然后选择一个选项，如"在新选项卡中打开"
    * **状态栏**：点击窗口右下角的\*\*✱ Claude Code\*\*。即使没有打开文件也可以使用。

    首次打开面板时，会出现**学习 Claude Code** 检查清单。通过点击**显示给我**来完成每一项，或用 X 关闭它。要稍后重新打开它，请在 VS Code 设置中的扩展 → Claude Code 下取消选中**隐藏入门**。

    您可以拖动 Claude 面板在 VS Code 中重新定位它。有关详细信息，请参阅[自定义您的工作流](../快速开始/01-ClaudeCode概述.md#customize-your-workflow)。
  </Step>

  <Step title="发送提示">
    要求 Claude 帮助您处理代码或文件，无论是解释某些内容的工作原理、调试问题还是进行更改。

    <Tip>Claude 会自动看到您选择的文本。按 `Option+K`（Mac）/ `Alt+K`（Windows/Linux）也可以在您的提示中插入 @-提及引用（如 `@file.ts#5-10`）。</Tip>

    以下是询问文件中特定行的示例：

        <img src="https://mintcdn.com/claude-code/FVYz38sRY-VuoGHA/images/vs-code-send-prompt.png?fit=max&auto=format&n=FVYz38sRY-VuoGHA&q=85&s=ede3ed8d8d5f940e01c5de636d009cfd" alt="VS Code 编辑器，Python 文件中的第 2-3 行被选中，Claude Code 面板显示关于这些行的问题，带有 @-提及引用" width="3288" height="1876" data-path="images/vs-code-send-prompt.png" />
  </Step>

  <Step title="审查更改">
    当 Claude 想要编辑文件时，它会显示原始内容和建议更改的并排比较，然后请求许可。您可以接受、拒绝或告诉 Claude 改为做什么。

        <img src="https://mintcdn.com/claude-code/FVYz38sRY-VuoGHA/images/vs-code-edits.png?fit=max&auto=format&n=FVYz38sRY-VuoGHA&q=85&s=e005f9b41c541c5c7c59c082f7c4841c" alt="VS Code 显示 Claude 建议更改的差异，带有权限提示，询问是否进行编辑" width="3292" height="1876" data-path="images/vs-code-edits.png" />
  </Step>
</Steps>

有关您可以使用 Claude Code 做什么的更多想法，请参阅[常见工作流](../使用 Claude Code/02-常见工作流程.md)。

<Tip>
  从命令面板运行"Claude Code: Open Walkthrough"以获得基础知识的引导式教程。
</Tip>

## 使用提示框

提示框支持多个功能：

* **权限模式**：点击提示框底部的模式指示器以切换模式。在正常模式下，Claude 在每个操作前请求许可。在 Plan mode 中，Claude 描述它将做什么，并在进行更改前等待批准。VS Code 会自动将计划作为完整的 markdown 文档打开，您可以添加内联注释以在 Claude 开始前提供反馈。在自动接受模式下，Claude 进行编辑而不询问。在 VS Code 设置中的 `claudeCode.initialPermissionMode` 下设置默认值。
* **命令菜单**：点击 `/` 或输入 `/` 以打开命令菜单。选项包括附加文件、切换模型、切换扩展思考、查看计划使用情况（`/usage`）以及启动 [Remote Control](04-使用RemoteControl从任何设备继续本地会话.md) 会话（`/remote-control`）。自定义部分提供对 MCP servers、hooks、memory、permissions 和 plugins 的访问。带有终端图标的项目在集成终端中打开。
* **上下文指示器**：提示框显示您使用了多少 Claude 的 context window。Claude 在需要时自动压缩，或者您可以手动运行 `/compact`。
* **扩展思考**：让 Claude 花更多时间推理复杂问题。通过命令菜单（`/`）切换它。有关详细信息，请参阅[扩展思考](../使用 Claude Code/02-常见工作流程.md#use-extended-thinking-thinking-mode)。
* **多行输入**：按 `Shift+Enter` 添加新行而不发送。这也适用于问题对话框的"其他"自由文本输入。

### 引用文件和文件夹

使用 @-提及为 Claude 提供有关特定文件或文件夹的上下文。当您输入 `@` 后跟文件或文件夹名称时，Claude 会读取该内容，可以回答有关它的问题或对其进行更改。Claude Code 支持模糊匹配，因此您可以输入部分名称来找到您需要的内容：

```text  theme={null}
> Explain the logic in @auth (fuzzy matches auth.js, AuthService.ts, etc.)
> What's in @src/components/ (include a trailing slash for folders)
```

对于大型 PDF，您可以要求 Claude 读取特定页面而不是整个文件：单个页面、范围（如第 1-10 页）或开放式范围（如第 3 页及以后）。

当您在编辑器中选择文本时，Claude 可以自动看到您突出显示的代码。提示框页脚显示选择了多少行。按 `Option+K`（Mac）/ `Alt+K`（Windows/Linux）插入带有文件路径和行号的 @-提及（例如 `@app.ts#5-10`）。点击选择指示器以切换 Claude 是否可以看到您突出显示的文本 - 眼睛斜线图标表示选择对 Claude 隐藏。

您也可以在将文件拖到提示框时按住 `Shift` 以将它们添加为附件。点击任何附件上的 X 以将其从上下文中删除。

### 恢复过去的对话

点击 Claude Code 面板顶部的下拉菜单以访问您的对话历史记录。您可以按关键字搜索或按时间浏览（今天、昨天、过去 7 天等）。点击任何对话以使用完整的消息历史记录恢复它。新会话根据您的第一条消息接收 AI 生成的标题。将鼠标悬停在会话上以显示重命名和删除操作：重命名以给它一个描述性标题，或删除以将其从列表中删除。有关恢复会话的更多信息，请参阅[常见工作流](../使用 Claude Code/02-常见工作流程.md#resume-previous-conversations)。

### 从 Claude.ai 恢复远程会话

如果您使用[网络上的 Claude Code](../07-ClaudeCodeontheweb.md)，您可以直接在 VS Code 中恢复这些远程会话。这需要使用 **Claude.ai Subscription** 登录，而不是 Anthropic Console。

<Steps>
  <Step title="打开过去的对话">
    点击 Claude Code 面板顶部的**过去的对话**下拉菜单。
  </Step>

  <Step title="选择远程选项卡">
    对话框显示两个选项卡：本地和远程。点击**远程**以查看来自 claude.ai 的会话。
  </Step>

  <Step title="选择要恢复的会话">
    浏览或搜索您的远程会话。点击任何会话以下载它并在本地继续对话。
  </Step>
</Steps>

<Note>
  只有使用 GitHub 存储库启动的网络会话才会出现在远程选项卡中。恢复会在本地加载对话历史记录；更改不会同步回 claude.ai。
</Note>

## 自定义您的工作流

一旦您启动并运行，您可以重新定位 Claude 面板、运行多个会话或切换到终端模式。

### 选择 Claude 的位置

您可以拖动 Claude 面板在 VS Code 中重新定位它。抓住面板的选项卡或标题栏并将其拖到：

* **次级边栏**：窗口的右侧。在您编码时保持 Claude 可见。
* **主边栏**：左侧边栏，带有资源管理器、搜索等图标。
* **编辑器区域**：将 Claude 作为选项卡打开，与您的文件并排。适用于辅助任务。

<Tip>
  为您的主 Claude 会话使用边栏，并为辅助任务打开其他选项卡。Claude 会记住您首选的位置。活动栏会话列表图标与 Claude 面板分开：会话列表在活动栏中始终可见，而 Claude 面板图标仅在面板停靠到左侧边栏时出现在那里。
</Tip>

### 运行多个对话

从命令面板使用**在新选项卡中打开**或**在新窗口中打开**来启动其他对话。每个对话维护自己的历史记录和上下文，允许您并行处理不同的任务。

使用选项卡时，spark 图标上的小彩色点表示状态：蓝色表示权限请求待处理，橙色表示 Claude 在选项卡隐藏时完成。

### 切换到终端模式

默认情况下，扩展打开图形聊天面板。如果您更喜欢 CLI 风格的界面，打开[使用终端设置](vscode://settings/claudeCode.useTerminal)并勾选该框。

您也可以打开 VS Code 设置（Mac 上为 `Cmd+,` 或 Windows/Linux 上为 `Ctrl+,`），转到扩展 → Claude Code，然后勾选**使用终端**。

## 管理 plugins

VS Code 扩展包括用于安装和管理 [plugins](../37-创建插件.md) 的图形界面。在提示框中输入 `/plugins` 以打开**管理 plugins** 界面。

### 安装 plugins

plugin 对话框显示两个选项卡：**Plugins** 和 **Marketplaces**。

在 Plugins 选项卡中：

* **已安装的 plugins** 显示在顶部，带有切换开关以启用或禁用它们
* **可用的 plugins** 来自您配置的 marketplaces，显示在下方
* 搜索以按名称或描述过滤 plugins
* 点击任何可用 plugin 上的**安装**

当您安装 plugin 时，选择安装范围：

* **为您安装**：在您的所有项目中可用（用户范围）
* **为此项目安装**：与项目协作者共享（项目范围）
* **本地安装**：仅适用于您，仅在此存储库中（本地范围）

### 管理 marketplaces

切换到 **Marketplaces** 选项卡以添加或删除 plugin 源：

* 输入 GitHub 存储库、URL 或本地路径以添加新的 marketplace
* 点击刷新图标以更新 marketplace 的 plugin 列表
* 点击垃圾桶图标以删除 marketplace

进行更改后，横幅会提示您重启 Claude Code 以应用更新。

<Note>
  VS Code 中的 plugin 管理在幕后使用相同的 CLI 命令。您在扩展中配置的 plugins 和 marketplaces 也可在 CLI 中使用，反之亦然。
</Note>

有关 plugin 系统的更多信息，请参阅 [Plugins](../37-创建插件.md) 和 [Plugin marketplaces](../36-创建和分发pluginmarketplace.md)。

## 使用 Chrome 自动化浏览器任务

将 Claude 连接到您的 Chrome 浏览器以测试网络应用、使用控制台日志进行调试，以及在不离开 VS Code 的情况下自动化浏览器工作流。这需要 [Claude in Chrome extension](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) 版本 1.0.36 或更高版本。

在提示框中输入 `@browser` 后跟您想要 Claude 做的事情：

```text  theme={null}
@browser go to localhost:3000 and check the console for errors
```

您也可以打开附件菜单以选择特定的浏览器工具，如打开新选项卡或读取页面内容。

Claude 为浏览器任务打开新选项卡并共享您的浏览器登录状态，因此它可以访问您已登录的任何网站。

有关设置说明、完整的功能列表和故障排除，请参阅[使用 Claude Code 与 Chrome](01-在Chrome中使用ClaudeCode（测试版）.md)。

## VS Code 命令和快捷键

打开命令面板（Mac 上为 `Cmd+Shift+P` 或 Windows/Linux 上为 `Ctrl+Shift+P`）并输入"Claude Code"以查看 Claude Code 扩展的所有可用 VS Code 命令。

某些快捷键取决于哪个面板"获得焦点"（接收键盘输入）。当您的光标在代码文件中时，编辑器获得焦点。当您的光标在 Claude 的提示框中时，Claude 获得焦点。使用 `Cmd+Esc` / `Ctrl+Esc` 在它们之间切换。

<Note>
  这些是用于控制扩展的 VS Code 命令。并非所有内置 Claude Code 命令都在扩展中可用。有关详细信息，请参阅 [VS Code 扩展与 Claude Code CLI](../快速开始/01-ClaudeCode概述.md#vs-code-extension-vs-claude-code-cli)。
</Note>

| 命令        | 快捷键                                                   | 描述                       |
| --------- | ----------------------------------------------------- | ------------------------ |
| 焦点输入      | `Cmd+Esc`（Mac）/ `Ctrl+Esc`（Windows/Linux）             | 在编辑器和 Claude 之间切换焦点      |
| 在边栏中打开    | -                                                     | 在左侧边栏中打开 Claude          |
| 在终端中打开    | -                                                     | 在终端模式下打开 Claude          |
| 在新选项卡中打开  | `Cmd+Shift+Esc`（Mac）/ `Ctrl+Shift+Esc`（Windows/Linux） | 将新对话作为编辑器选项卡打开           |
| 在新窗口中打开   | -                                                     | 在单独的窗口中打开新对话             |
| 新对话       | `Cmd+N`（Mac）/ `Ctrl+N`（Windows/Linux）                 | 开始新对话（需要 Claude 获得焦点）    |
| 插入 @-提及引用 | `Option+K`（Mac）/ `Alt+K`（Windows/Linux）               | 插入对当前文件和选择的引用（需要编辑器获得焦点） |
| 显示日志      | -                                                     | 查看扩展调试日志                 |
| 登出        | -                                                     | 登出您的 Anthropic 账户        |

## 配置设置

扩展有两种类型的设置：

* **扩展设置**在 VS Code 中：控制扩展在 VS Code 中的行为。使用 `Cmd+,`（Mac）或 `Ctrl+,`（Windows/Linux）打开，然后转到扩展 → Claude Code。您也可以输入 `/` 并选择**常规配置**以打开设置。
* **Claude Code 设置**在 `~/.claude/settings.json` 中：在扩展和 CLI 之间共享。用于允许的命令、环境变量、hooks 和 MCP servers。有关详细信息，请参阅[设置](../43-ClaudeCode设置.md)。

<Tip>
  将 `"$schema": "https://json.schemastore.org/claude-code-settings.json"` 添加到您的 `settings.json` 以在 VS Code 中直接获得所有可用设置的自动完成和内联验证。
</Tip>

### 扩展设置

| 设置                                | 默认值       | 描述                                                                                                                                                                                                      |
| --------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `selectedModel`                   | `default` | 新对话的模型。使用 `/model` 按会话更改。                                                                                                                                                                               |
| `useTerminal`                     | `false`   | 以终端模式而不是图形面板启动 Claude                                                                                                                                                                                   |
| `initialPermissionMode`           | `default` | 控制新对话的批准提示：`default`、`plan`、`acceptEdits`、`auto` 或 `bypassPermissions`。请参阅[权限模式](../使用 Claude Code/04-选择权限模式.md)。                                                                                              |
| `preferredLocation`               | `panel`   | Claude 打开的位置：`sidebar`（右侧）或 `panel`（新选项卡）                                                                                                                                                               |
| `autosave`                        | `true`    | 在 Claude 读取或写入文件前自动保存文件                                                                                                                                                                                 |
| `useCtrlEnterToSend`              | `false`   | 使用 Ctrl/Cmd+Enter 而不是 Enter 发送提示                                                                                                                                                                        |
| `enableNewConversationShortcut`   | `true`    | 启用 Cmd/Ctrl+N 以开始新对话                                                                                                                                                                                    |
| `hideOnboarding`                  | `false`   | 隐藏入门检查清单（毕业帽图标）                                                                                                                                                                                         |
| `respectGitIgnore`                | `true`    | 从文件搜索中排除 .gitignore 模式                                                                                                                                                                                  |
| `environmentVariables`            | `[]`      | 为 Claude 进程设置环境变量。对于共享配置，请改用 Claude Code 设置。                                                                                                                                                            |
| `disableLoginPrompt`              | `false`   | 跳过身份验证提示（用于第三方提供商设置）                                                                                                                                                                                    |
| `allowDangerouslySkipPermissions` | `false`   | 添加 [Auto](../使用 Claude Code/04-选择权限模式.md#eliminate-prompts-with-auto-mode) 和 Bypass permissions 到模式选择器。Auto 需要 Team 计划和 Claude Sonnet 4.6 或 Opus 4.6，因此即使此切换打开，该选项也可能保持不可用。仅在没有互联网访问的沙箱中使用 Bypass permissions。 |
| `claudeProcessWrapper`            | -         | 用于启动 Claude 进程的可执行文件路径                                                                                                                                                                                  |

## VS Code 扩展与 Claude Code CLI

Claude Code 既可作为 VS Code 扩展（图形面板）也可作为 CLI（终端中的命令行界面）使用。某些功能仅在 CLI 中可用。如果您需要仅限 CLI 的功能，请在 VS Code 的集成终端中运行 `claude`。

| 功能            | CLI                   | VS Code 扩展                               |
| ------------- | --------------------- | ---------------------------------------- |
| 命令和 skills    | [全部](../10-内置命令.md) | 子集（输入 `/` 以查看可用的）                        |
| MCP server 配置 | 是                     | 部分（通过 CLI 添加服务器；使用聊天面板中的 `/mcp` 管理现有服务器） |
| Checkpoints   | 是                     | 是                                        |
| `!` bash 快捷键  | 是                     | 否                                        |
| Tab 完成        | 是                     | 否                                        |

### 使用 checkpoints 进行倒带

VS Code 扩展支持 checkpoints，它们跟踪 Claude 的文件编辑并让您倒带到之前的状态。将鼠标悬停在任何消息上以显示倒带按钮，然后从三个选项中选择：

* **从此处分叉对话**：从此消息开始新的对话分支，同时保持所有代码更改完整
* **将代码倒带到此处**：将文件更改恢复到对话中的此点，同时保持完整的对话历史记录
* **分叉对话并倒带代码**：开始新的对话分支并将文件更改恢复到此点

有关 checkpoints 如何工作及其限制的完整详细信息，请参阅 [Checkpointing](../06-checkpointing.md)。

### 在 VS Code 中运行 CLI

要在 VS Code 中使用 CLI，请打开集成终端（Windows/Linux 上为 `` Ctrl+` `` 或 Mac 上为 `` Cmd+` ``）并运行 `claude`。CLI 会自动与您的 IDE 集成，以获得差异查看和诊断共享等功能。

如果使用外部终端，请在 Claude Code 中运行 `/ide` 以将其连接到 VS Code。

### 在扩展和 CLI 之间切换

扩展和 CLI 共享相同的对话历史记录。要在 CLI 中继续扩展对话，请在终端中运行 `claude --resume`。这会打开一个交互式选择器，您可以在其中搜索和选择您的对话。

### 在提示中包含终端输出

使用 `@terminal:name` 在您的提示中引用终端输出，其中 `name` 是终端的标题。这让 Claude 可以看到命令输出、错误消息或日志，而无需复制粘贴。

### 监控后台进程

当 Claude 运行长时间运行的命令时，扩展在状态栏中显示进度。但是，与 CLI 相比，后台任务的可见性有限。为了获得更好的可见性，让 Claude 输出命令，以便您可以在 VS Code 的集成终端中运行它。

### 使用 MCP 连接到外部工具

MCP（Model Context Protocol）servers 为 Claude 提供对外部工具、数据库和 API 的访问。

要添加 MCP server，请打开集成终端（`` Ctrl+` `` 或 `` Cmd+` ``）并运行：

```bash  theme={null}
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

配置后，要求 Claude 使用这些工具（例如，"审查 PR #456"）。

要在不离开 VS Code 的情况下管理 MCP servers，请在聊天面板中输入 `/mcp`。MCP 管理对话框让您启用或禁用服务器、重新连接到服务器以及管理 OAuth 身份验证。有关可用服务器，请参阅 [MCP 文档](../29-通过MCP将ClaudeCode连接到工具.md)。

## 使用 git

Claude Code 与 git 集成以帮助直接在 VS Code 中进行版本控制工作流。要求 Claude 提交更改、创建拉取请求或跨分支工作。

### 创建提交和拉取请求

Claude 可以暂存更改、编写提交消息并根据您的工作创建拉取请求：

```text  theme={null}
> commit my changes with a descriptive message
> create a pr for this feature
> summarize the changes I've made to the auth module
```

创建拉取请求时，Claude 会根据实际代码更改生成描述，并可以添加有关测试或实现决策的上下文。

### 使用 git worktrees 进行并行任务

使用 `--worktree`（`-w`）标志在隔离的 worktree 中启动 Claude，该 worktree 具有自己的文件和分支：

```bash  theme={null}
claude --worktree feature-auth
```

每个 worktree 维护独立的文件状态，同时共享 git 历史记录。这可以防止 Claude 实例在处理不同任务时相互干扰。有关更多详细信息，请参阅[使用 Git worktrees 运行并行 Claude Code 会话](../使用 Claude Code/02-常见工作流程.md#run-parallel-claude-code-sessions-with-git-worktrees)。

## 使用第三方提供商

默认情况下，Claude Code 直接连接到 Anthropic 的 API。如果您的组织使用 Amazon Bedrock、Google Vertex AI 或 Microsoft Foundry 来访问 Claude，请配置扩展以改用您的提供商：

<Steps>
  <Step title="禁用登录提示">
    打开[禁用登录提示设置](vscode://settings/claudeCode.disableLoginPrompt)并勾选该框。

    您也可以打开 VS Code 设置（Mac 上为 `Cmd+,` 或 Windows/Linux 上为 `Ctrl+,`），搜索"Claude Code login"，然后勾选**禁用登录提示**。
  </Step>

  <Step title="配置您的提供商">
    按照您的提供商的设置指南：

    * [Amazon Bedrock 上的 Claude Code](../02-AmazonBedrock上的ClaudeCode.md)
    * [Google Vertex AI 上的 Claude Code](../21-GoogleVertexAI上的ClaudeCode.md)
    * [Microsoft Foundry 上的 Claude Code](../30-ClaudeCodeonMicrosoftFoundry.md)

    这些指南涵盖在 `~/.claude/settings.json` 中配置您的提供商，这确保您的设置在 VS Code 扩展和 CLI 之间共享。
  </Step>
</Steps>

## 安全和隐私

您的代码保持私密。Claude Code 处理您的代码以提供协助，但不使用它来训练模型。有关数据处理的详细信息以及如何选择退出日志记录，请参阅[数据和隐私](../12-数据使用.md)。

启用自动编辑权限后，Claude Code 可以修改 VS Code 配置文件（如 `settings.json` 或 `tasks.json`），VS Code 可能会自动执行。要在处理不受信任的代码时降低风险：

* 为不受信任的工作区启用 [VS Code 受限模式](https://code.visualstudio.com/docs/editor/workspace-trust#_restricted-mode)
* 使用手动批准模式而不是自动接受编辑
* 在接受更改前仔细审查它们

### 内置 IDE MCP server

当扩展处于活动状态时，它运行一个本地 MCP server，CLI 会自动连接到该服务器。这是 CLI 如何在 VS Code 的原生差异查看器中打开差异、读取您当前的 @-提及选择，以及 — 当您在 Jupyter notebook 中工作时 — 要求 VS Code 执行单元格的方式。

该服务器名为 `ide`，从 `/mcp` 中隐藏，因为没有什么可配置的。但是，如果您的组织使用 `PreToolUse` hook 来允许列表 MCP 工具，您需要知道它存在。

**传输和身份验证。** 该服务器绑定到 `127.0.0.1` 上的随机高端口，无法从其他机器访问。每次扩展激活都会生成一个新的随机身份验证令牌，CLI 必须提供该令牌才能连接。该令牌被写入 `~/.claude/ide/` 下的锁定文件，权限为 `0600`，在 `0700` 目录中，因此只有运行 VS Code 的用户可以读取它。

**暴露给模型的工具。** 该服务器托管十几个工具，但只有两个对模型可见。其余的是 CLI 用于自己的 UI 的内部 RPC — 打开差异、读取选择、保存文件 — 并在工具列表到达 Claude 之前被过滤掉。

| 工具名称（如 hooks 所见）           | 它的作用                                              | 写入？ |
| -------------------------- | ------------------------------------------------- | --- |
| `mcp__ide__getDiagnostics` | 返回语言服务器诊断 — VS Code 问题面板中的错误和警告。可选地限定到一个文件。       | 否   |
| `mcp__ide__executeCode`    | 在活动 Jupyter notebook 的内核中运行 Python 代码。请参阅下面的确认流程。 | 是   |

**Jupyter 执行总是先询问。** `mcp__ide__executeCode` 无法静默运行任何内容。在每次调用时，代码被插入为活动 notebook 末尾的新单元格，VS Code 将其滚动到视图中，本地 Quick Pick 要求您**执行**或**取消**。取消 — 或用 `Esc` 关闭选择器 — 向 Claude 返回错误，什么都不运行。当没有活动 notebook、Jupyter 扩展（`ms-toolsai.jupyter`）未安装或内核不是 Python 时，该工具也会直接拒绝。

<Note>
  Quick Pick 确认与 `PreToolUse` hooks 分开。`mcp__ide__executeCode` 的允许列表条目让 Claude *提议*运行单元格；VS Code 内的 Quick Pick 是让它*实际*运行的原因。
</Note>

## 修复常见问题

### 扩展无法安装

* 确保您拥有兼容的 VS Code 版本（1.98.0 或更高版本）
* 检查 VS Code 是否有权安装扩展
* 尝试从 [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) 直接安装

### Spark 图标不可见

Spark 图标在**编辑器工具栏**（编辑器右上角）中出现，当您打开文件时。如果您看不到它：

1. **打开文件**：该图标需要打开文件。仅打开文件夹是不够的。
2. **检查 VS Code 版本**：需要 1.98.0 或更高版本（帮助 → 关于）
3. **重启 VS Code**：从命令面板运行"Developer: Reload Window"
4. **禁用冲突的扩展**：临时禁用其他 AI 扩展（Cline、Continue 等）
5. **检查工作区信任**：扩展在受限模式下不工作

或者，点击**状态栏**（右下角）中的"✱ Claude Code"。即使没有打开文件也可以使用。您也可以使用**命令面板**（`Cmd+Shift+P` / `Ctrl+Shift+P`）并输入"Claude Code"。

### Claude Code 从不响应

如果 Claude Code 没有响应您的提示：

1. **检查您的互联网连接**：确保您有稳定的互联网连接
2. **开始新对话**：尝试开始新的对话以查看问题是否仍然存在
3. **尝试 CLI**：从终端运行 `claude` 以查看是否获得更详细的错误消息

如果问题仍然存在，请[在 GitHub 上提交问题](https://github.com/anthropics/claude-code/issues)，并提供有关错误的详细信息。

## 卸载扩展

要卸载 Claude Code 扩展：

1. 打开扩展视图（Mac 上为 `Cmd+Shift+X` 或 Windows/Linux 上为 `Ctrl+Shift+X`）
2. 搜索"Claude Code"
3. 点击**卸载**

要也删除扩展数据并重置所有设置：

```bash  theme={null}
rm -rf ~/.vscode/globalStorage/anthropic.claude-code
```

如需更多帮助，请参阅[故障排除指南](../51-故障排除.md)。

## 后续步骤

现在您已在 VS Code 中设置了 Claude Code：

* [探索常见工作流](../使用 Claude Code/02-常见工作流程.md)以充分利用 Claude Code
* [设置 MCP servers](../29-通过MCP将ClaudeCode连接到工具.md)以使用外部工具扩展 Claude 的功能。使用 CLI 添加服务器，然后使用聊天面板中的 `/mcp` 管理它们。
* [配置 Claude Code 设置](../43-ClaudeCode设置.md)以自定义允许的命令、hooks 等。这些设置在扩展和 CLI 之间共享。
