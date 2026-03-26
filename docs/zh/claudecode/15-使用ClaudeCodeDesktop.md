[首页](README.md) / 使用 Claude Code Desktop

# 使用 Claude Code Desktop

> 充分利用 Claude Code Desktop：计算机使用、从手机 Dispatch 会话、使用 Git 隔离的并行会话、可视化 diff 审查、应用预览、PR 监控、连接器和企业配置。

Claude Desktop 应用中的 Code 选项卡让你可以通过图形界面而不是终端来使用 Claude Code。

Desktop 在标准 Claude Code 体验的基础上添加了这些功能：

* [可视化 diff 审查](快速开始/01-ClaudeCode概述.md#review-changes-with-diff-view)，支持内联注释
* [实时应用预览](快速开始/01-ClaudeCode概述.md#preview-your-app)，支持开发服务器
* [计算机使用](快速开始/01-ClaudeCode概述.md#let-claude-use-your-computer)，在 macOS 上打开应用和控制屏幕
* [GitHub PR 监控](快速开始/01-ClaudeCode概述.md#monitor-pull-request-status)，支持自动修复和自动合并
* [并行会话](快速开始/01-ClaudeCode概述.md#work-in-parallel-with-sessions)，支持自动 Git worktree 隔离
* [Dispatch](快速开始/01-ClaudeCode概述.md#sessions-from-dispatch) 集成：从手机发送任务，在此处获得会话
* [计划任务](快速开始/01-ClaudeCode概述.md#schedule-recurring-tasks)，按定期计划运行 Claude
* [连接器](快速开始/01-ClaudeCode概述.md#connect-external-tools)，支持 GitHub、Slack、Linear 等
* 本地、[SSH](快速开始/01-ClaudeCode概述.md#ssh-sessions) 和[云](快速开始/01-ClaudeCode概述.md#run-long-running-tasks-remotely)环境

**Tip:**
初次使用 Desktop？从[快速开始](16-开始使用桌面应用.md)开始安装应用并进行首次编辑。

本页涵盖[使用代码](快速开始/01-ClaudeCode概述.md#work-with-code)、[计算机使用](快速开始/01-ClaudeCode概述.md#let-claude-use-your-computer)、[管理会话](快速开始/01-ClaudeCode概述.md#manage-sessions)、[扩展 Claude Code](快速开始/01-ClaudeCode概述.md#extend-claude-code)、[计划任务](快速开始/01-ClaudeCode概述.md#schedule-recurring-tasks)和[配置](快速开始/01-ClaudeCode概述.md#environment-configuration)。它还包括 [CLI 比较](快速开始/01-ClaudeCode概述.md#coming-from-the-cli)和[故障排除](快速开始/01-ClaudeCode概述.md#troubleshooting)。

## 启动会话

在发送第一条消息之前，在提示区域配置四件事：

* **环境**：选择 Claude 运行的位置。选择**本地**用于你的机器，**远程**用于 Anthropic 托管的云会话，或[**SSH 连接**](快速开始/01-ClaudeCode概述.md#ssh-sessions)用于你管理的远程机器。请参阅[环境配置](快速开始/01-ClaudeCode概述.md#environment-configuration)。
* **项目文件夹**：选择 Claude 工作的文件夹或存储库。对于远程会话，你可以添加[多个存储库](快速开始/01-ClaudeCode概述.md#run-long-running-tasks-remotely)。
* **模型**：从发送按钮旁的下拉菜单中选择一个[模型](33-模型配置.md#available-models)。会话启动后，模型将被锁定。
* **权限模式**：从[模式选择器](快速开始/01-ClaudeCode概述.md#choose-a-permission-mode)中选择 Claude 拥有多少自主权。你可以在会话期间更改此设置。

输入你的任务并按 **Enter** 启动。每个会话独立跟踪其自己的上下文和更改。

## 使用代码

为 Claude 提供正确的上下文，控制它自己做多少工作，并审查它更改的内容。

### 使用提示框

输入你想让 Claude 做的事情并按 **Enter** 发送。Claude 读取你的项目文件，进行更改，并根据你的[权限模式](快速开始/01-ClaudeCode概述.md#choose-a-permission-mode)运行命令。你可以随时中断 Claude：点击停止按钮或输入你的更正并按 **Enter**。Claude 停止正在做的事情并根据你的输入进行调整。

提示框旁的 **+** 按钮让你可以访问文件附件、[skills](快速开始/01-ClaudeCode概述.md#use-skills)、[连接器](快速开始/01-ClaudeCode概述.md#connect-external-tools)和[插件](快速开始/01-ClaudeCode概述.md#install-plugins)。

### 向提示添加文件和上下文

提示框支持两种方式来引入外部上下文：

* **@mention 文件**：输入 `@` 后跟文件名，将文件添加到对话上下文。Claude 然后可以读取和引用该文件。@mention 在远程会话中不可用。
* **附加文件**：使用附件按钮将图像、PDF 和其他文件附加到你的提示，或直接将文件拖放到提示中。这对于共享错误的屏幕截图、设计模型或参考文档很有用。

### 选择权限模式

权限模式控制 Claude 在会话期间拥有多少自主权：它是否在编辑文件、运行命令或两者之前询问。你可以随时使用发送按钮旁的模式选择器切换模式。从"询问权限"开始以准确查看 Claude 的操作，然后随着你变得更舒适，转移到"自动接受编辑"或 Plan Mode。

| 模式            | 设置键                 | 行为                                                                                                                                                |
| ------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **询问权限**      | `default`           | Claude 在编辑文件或运行命令之前询问。你会看到一个 diff，可以接受或拒绝每个更改。推荐给新用户。                                                                                             |
| **自动接受编辑**    | `acceptEdits`       | Claude 自动接受文件编辑，但在运行终端命令之前仍然询问。当你信任文件更改并想要更快的迭代时，使用此选项。                                                                                           |
| **Plan Mode** | `plan`              | Claude 分析你的代码并创建计划，而不修改文件或运行命令。适合复杂任务，你想先审查方法。                                                                                                    |
| **Auto**      | `auto`              | Claude 执行所有操作，并进行后台安全检查以验证与你的请求的一致性。减少权限提示，同时保持监督。目前是研究预览版。在 Team 计划上可用（Enterprise 即将推出）。需要 Claude Sonnet 4.6 或 Opus 4.6。在你的设置 → Claude Code 中启用。 |
| **绕过权限**      | `bypassPermissions` | Claude 运行时没有任何权限提示，等同于 CLI 中的 `--dangerously-skip-permissions`。在设置 → Claude Code 中的"允许绕过权限模式"下启用。仅在沙箱容器或虚拟机中使用。企业管理员可以禁用此选项。                      |

`dontAsk` 权限模式仅在 [CLI](使用 Claude Code/04-选择权限模式.md#allow-only-pre-approved-tools-with-dontask-mode) 中可用。

**Tip (最佳实践):**
在 Plan Mode 中启动复杂任务，以便 Claude 在进行更改之前制定方法。一旦你批准计划，切换到"自动接受编辑"或"询问权限"来执行它。有关此工作流的更多信息，请参阅[先探索，然后计划，然后编码](使用 Claude Code/01-ClaudeCode最佳实践.md#explore-first-then-plan-then-code)。

远程会话支持"自动接受编辑"和 Plan Mode。"询问权限"不可用，因为远程会话默认自动接受文件编辑，"绕过权限"不可用，因为远程环境已经是沙箱化的。

企业管理员可以限制哪些权限模式可用。有关详细信息，请参阅[企业配置](快速开始/01-ClaudeCode概述.md#enterprise-configuration)。

### 预览你的应用

Claude 可以启动开发服务器并打开嵌入式浏览器来验证其更改。这适用于前端 Web 应用以及后端服务器：Claude 可以测试 API 端点、查看服务器日志并迭代它发现的问题。在大多数情况下，Claude 在编辑项目文件后自动启动服务器。你也可以随时要求 Claude 预览。默认情况下，Claude [自动验证](快速开始/01-ClaudeCode概述.md#auto-verify-changes)每次编辑后的更改。

从预览面板，你可以：

* 在嵌入式浏览器中直接与你运行的应用交互
* 观看 Claude 自动验证其自己的更改：它拍摄屏幕截图、检查 DOM、点击元素、填充表单并修复它发现的问题
* 从会话工具栏中的 **Preview** 下拉菜单启动或停止服务器
* 通过在下拉菜单中选择 **Persist sessions** 来在服务器重启时保持 cookie 和本地存储，这样你就不必在开发期间重新登录
* 编辑服务器配置或一次停止所有服务器

Claude 根据你的项目创建初始服务器配置。如果你的应用使用自定义开发命令，编辑 `.claude/launch.json` 以匹配你的设置。有关完整参考，请参阅[配置预览服务器](快速开始/01-ClaudeCode概述.md#configure-preview-servers)。

要清除保存的会话数据，在设置 → Claude Code 中切换 **Persist preview sessions** 关闭。要完全禁用预览，在设置 → Claude Code 中切换 **Preview** 关闭。

### 使用 diff 视图审查更改

Claude 对你的代码进行更改后，diff 视图让你在创建拉取请求之前逐个文件审查修改。

当 Claude 更改文件时，会出现一个 diff 统计指示器，显示添加和删除的行数，例如 `+12 -1`。点击此指示器打开 diff 查看器，它在左侧显示文件列表，在右侧显示每个文件的更改。

要对特定行进行注释，点击 diff 中的任何行以打开注释框。输入你的反馈并按 **Enter** 添加注释。在多行添加注释后，一次提交所有注释：

* **macOS**：按 **Cmd+Enter**
* **Windows**：按 **Ctrl+Enter**

Claude 读取你的注释并进行请求的更改，这些更改显示为你可以审查的新 diff。

### 审查你的代码

在 diff 视图中，点击右上角工具栏中的 **Review code** 来要求 Claude 在你提交之前评估更改。Claude 检查当前 diff 并直接在 diff 视图中留下注释。你可以回复任何注释或要求 Claude 修改。

审查侧重于高信号问题：编译错误、明确的逻辑错误、安全漏洞和明显的错误。它不标记样式、格式、预先存在的问题或 linter 会捕获的任何内容。

### 监控拉取请求状态

打开拉取请求后，CI 状态栏出现在会话中。Claude Code 使用 GitHub CLI 轮询检查结果并显示失败。

* **自动修复**：启用后，Claude 通过读取失败输出并迭代来自动尝试修复失败的 CI 检查。
* **自动合并**：启用后，Claude 在所有检查通过后合并 PR。合并方法是压缩。自动合并必须在你的 GitHub 存储库设置中[启用](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository)才能工作。

使用 CI 状态栏中的 **Auto-fix** 和 **Auto-merge** 切换来启用任一选项。Claude Code 还在 CI 完成时发送桌面通知。

**Note:**
PR 监控需要在你的机器上安装并验证 [GitHub CLI (`gh`)](https://cli.github.com/)。如果未安装 `gh`，Desktop 会在你第一次尝试创建 PR 时提示你安装它。

## 让 Claude 使用你的计算机

计算机使用让 Claude 打开你的应用、控制你的屏幕，并像你一样直接在你的机器上工作。要求 Claude 在 iOS 模拟器中测试原生应用、与没有 CLI 的桌面工具交互，或自动化只能通过 GUI 工作的东西。

**Note:**
计算机使用是 macOS 上的研究预览版，需要 Pro 或 Max 计划。它在 Team 或 Enterprise 计划上不可用。Claude Desktop 应用必须运行。

计算机使用默认关闭。[在设置中启用它](快速开始/01-ClaudeCode概述.md#enable-computer-use)并授予所需的 macOS 权限，然后 Claude 才能控制你的屏幕。

**Warning:**
与[沙箱化 Bash 工具](41-Sandboxing.md)不同，计算机使用在你的实际桌面上运行，可以访问你批准的任何内容。Claude 检查每个操作并标记来自屏幕内容的潜在提示注入，但信任边界不同。有关最佳实践，请参阅[计算机使用安全指南](https://support.claude.com/en/articles/14128542)。

### 何时应用计算机使用

Claude 有多种方式与应用或服务交互，计算机使用是最广泛和最慢的。它首先尝试最精确的工具：

* 如果你有一个服务的[连接器](快速开始/01-ClaudeCode概述.md#connect-external-tools)，Claude 使用连接器。
* 如果任务是 shell 命令，Claude 使用 Bash。
* 如果任务是浏览器工作且你已设置[Chrome 中的 Claude](平台和集成/01-在Chrome中使用ClaudeCode（测试版）.md)，Claude 使用那个。
* 如果以上都不适用，Claude 使用计算机使用。

[按应用访问层](快速开始/01-ClaudeCode概述.md#app-permissions)强化了这一点：浏览器限制为仅查看，终端和 IDE 限制为仅点击，即使计算机使用处于活跃状态，也会引导 Claude 使用专用工具。屏幕控制保留给其他工具无法到达的东西，如原生应用、硬件控制面板、iOS 模拟器或没有 API 的专有工具。

### 启用计算机使用

计算机使用默认关闭。如果你要求 Claude 做需要它的事情而它关闭时，Claude 会告诉你如果在设置中启用计算机使用，它可以完成任务。要启用它，打开**设置 > Desktop app > General** 并切换**计算机使用**打开。在切换生效之前，你需要授予两个 macOS 系统权限：

* **Accessibility**：让 Claude 点击、输入和滚动
* **Screen Recording**：让 Claude 看到你屏幕上的内容

设置页面显示每个权限的当前状态。如果任一被拒绝，点击徽章打开相关的系统设置窗格。

### 应用权限

Claude 第一次需要使用应用时，会话中会出现提示。点击**允许此会话**或**拒绝**。批准持续当前会话，或在 [Dispatch 生成的会话](快速开始/01-ClaudeCode概述.md#sessions-from-dispatch)中持续 30 分钟。

提示还显示 Claude 为该应用获得的控制级别。这些层由应用类别固定，无法更改：

| 层    | Claude 可以做什么      | 适用于      |
| :--- | :---------------- | :------- |
| 仅查看  | 在屏幕截图中看到应用        | 浏览器、交易平台 |
| 仅点击  | 点击和滚动，但不能输入或使用快捷键 | 终端、IDE   |
| 完全控制 | 点击、输入、拖动和使用快捷键    | 其他所有内容   |

像 Terminal、Finder 和 System Settings 这样具有广泛影响的应用在提示中显示额外警告，以便你知道批准它们授予什么。

你可以在**设置 > Desktop app > General** 中配置两个设置：

* **拒绝的应用**：在此处添加应用以拒绝它们而不提示。Claude 可能仍然通过允许应用中的操作间接影响被拒绝的应用，但它无法直接与被拒绝的应用交互。
* **Claude 完成时取消隐藏应用**：当 Claude 工作时，你的其他窗口被隐藏，以便它仅与批准的应用交互。当 Claude 完成时，隐藏的窗口被恢复，除非你关闭此设置。

## 管理会话

每个会话是一个独立的对话，拥有自己的上下文和更改。你可以并行运行多个会话，将工作发送到云，或让 Dispatch 从你的手机为你启动会话。

### 使用会话并行工作

点击侧边栏中的 **+ New session** 来并行处理多个任务。对于 Git 存储库，每个会话使用 [Git worktrees](使用 Claude Code/02-常见工作流程.md#run-parallel-claude-code-sessions-with-git-worktrees) 获得自己的项目隔离副本，因此一个会话中的更改不会影响其他会话，直到你提交它们。

Worktrees 默认存储在 `<project-root>/.claude/worktrees/` 中。你可以在设置 → Claude Code 中的"Worktree location"下将其更改为自定义目录。你也可以设置一个分支前缀，该前缀会添加到每个 worktree 分支名称前面，这对于保持 Claude 创建的分支有组织很有用。要在完成后删除 worktree，请将鼠标悬停在侧边栏中的会话上并点击存档图标。

**Note:**
会话隔离需要 [Git](https://git-scm.com/downloads)。大多数 Mac 默认包含 Git。在终端中运行 `git --version` 来检查。在 Windows 上，Git 是 Code 选项卡工作所必需的：[下载 Git for Windows](https://git-scm.com/downloads/win)，安装它，然后重启应用。如果你遇到 Git 错误，请尝试 Cowork 会话来帮助排除你的设置。

使用侧边栏顶部的过滤器图标按状态（活跃、已存档）和环境（本地、云）过滤会话。要重命名会话或检查上下文使用情况，点击活跃会话顶部工具栏中的会话标题。当上下文填满时，Claude 自动总结对话并继续工作。你也可以输入 `/compact` 来更早触发总结并释放上下文空间。有关压缩工作原理的详细信息，请参阅[上下文窗口](核心概念/02-ClaudeCode如何工作.md#the-context-window)。

### 远程运行长时间运行的任务

对于大型重构、测试套件、迁移或其他长时间运行的任务，在启动会话时选择 **Remote** 而不是 **Local**。远程会话在 Anthropic 的云基础设施上运行，即使你关闭应用或关闭计算机，也会继续运行。随时检查进度或引导 Claude 朝不同方向发展。你也可以从 [claude.ai/code](https://claude.ai/code) 或 Claude iOS 应用监控远程会话。

远程会话也支持多个存储库。选择云环境后，点击存储库 pill 旁的 **+** 按钮向会话添加其他存储库。每个存储库都有自己的分支选择器。这对于跨越多个代码库的任务很有用，例如更新共享库及其使用者。

有关远程会话如何工作的更多信息，请参阅[Web 上的 Claude Code](09-ClaudeCodeontheweb.md)。

### 在另一个表面继续

**Continue in** 菜单，可从会话工具栏右下角的 VS Code 图标访问，让你将会话移动到另一个表面：

* **Web 上的 Claude Code**：将你的本地会话发送到远程继续运行。Desktop 推送你的分支，生成对话摘要，并创建具有完整上下文的新远程会话。然后你可以选择存档本地会话或保留它。这需要干净的工作树，对于 SSH 会话不可用。
* **你的 IDE**：在当前工作目录的支持的 IDE 中打开你的项目。

### 来自 Dispatch 的会话

[Dispatch](https://support.claude.com/en/articles/13947068) 是一个与 Claude 的持久对话，存在于 [Cowork](https://claude.com/product/cowork#dispatch-and-computer-use) 选项卡中。你向 Dispatch 发送任务消息，它决定如何处理。

任务可以通过两种方式成为 Code 会话：你直接要求一个，例如"打开 Claude Code 会话并修复登录错误"，或 Dispatch 决定任务是开发工作并自己生成一个。通常路由到 Code 的任务包括修复错误、更新依赖项、运行测试或打开拉取请求。研究、文档编辑和电子表格工作保留在 Cowork 中。

无论哪种方式，Code 会话都会在 Code 选项卡的侧边栏中出现，带有 **Dispatch** 徽章。当它完成或需要你的批准时，你会在手机上收到推送通知。

如果你启用了[计算机使用](快速开始/01-ClaudeCode概述.md#let-claude-use-your-computer)，Dispatch 生成的 Code 会话也可以使用它。这些会话中的应用批准在 30 分钟后过期并重新提示，而不是像常规 Code 会话那样持续整个会话。

有关设置、配对和 Dispatch 设置，请参阅 [Dispatch 帮助文章](https://support.claude.com/en/articles/13947068)。Dispatch 需要 Pro 或 Max 计划，在 Team 或 Enterprise 计划上不可用。

Dispatch 是远离终端时与 Claude 合作的几种方式之一。请参阅[平台和集成](平台和集成/03-平台和集成.md#work-when-you-are-away-from-your-terminal)来比较它与远程控制、Channels、Slack 和计划任务。

## 扩展 Claude Code

连接外部服务、添加可重用工作流、自定义 Claude 的行为并配置预览服务器。

### 连接外部工具

对于本地和 [SSH](快速开始/01-ClaudeCode概述.md#ssh-sessions) 会话，点击提示框旁的 **+** 按钮并选择 **Connectors** 来添加集成，如 Google Calendar、Slack、GitHub、Linear、Notion 等。你可以在会话之前或期间添加连接器。远程会话不支持 **+** 按钮，但[计划任务](55-在网络上安排任务.md)在任务创建时配置连接器。

要管理或断开连接器，请在桌面应用中转到设置 → Connectors，或从提示框中的 Connectors 菜单中选择 **Manage connectors**。

连接后，Claude 可以读取你的日历、发送消息、创建问题并直接与你的工具交互。你可以询问 Claude 在你的会话中配置了哪些连接器。

连接器是[MCP servers](31-通过MCP将ClaudeCode连接到工具.md)，具有图形设置流程。使用它们快速与支持的服务集成。对于连接器中未列出的集成，通过[设置文件](31-通过MCP将ClaudeCode连接到工具.md#installing-mcp-servers)手动添加 MCP servers。你也可以[创建自定义连接器](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp)。

### 使用 skills

[Skills](47-使用skills扩展Claude.md)扩展 Claude 可以做的事情。Claude 在相关时自动加载它们，或者你可以直接调用一个：在提示框中输入 `/` 或点击 **+** 按钮并选择 **Slash commands** 来浏览可用的内容。这包括[内置命令](12-内置命令.md)、你的[自定义 skills](47-使用skills扩展Claude.md#create-custom-skills)、来自你的代码库的项目 skills 以及来自任何[已安装插件](39-创建插件.md)的 skills。选择一个，它会在输入字段中突出显示。在它之后输入你的任务并照常发送。

### 安装插件

[Plugins](39-创建插件.md)是可重用的包，为 Claude Code 添加 skills、agents、hooks、MCP servers 和 LSP 配置。你可以从桌面应用安装插件，而无需使用终端。

对于本地和 [SSH](快速开始/01-ClaudeCode概述.md#ssh-sessions) 会话，点击提示框旁的 **+** 按钮并选择 **Plugins** 来查看你已安装的插件及其命令。要添加插件，从子菜单中选择 **Add plugin** 来打开插件浏览器，它显示来自你配置的[市场](38-创建和分发pluginmarketplace.md)的可用插件，包括官方 Anthropic 市场。选择 **Manage plugins** 来启用、禁用或卸载插件。

插件可以限定到你的用户账户、特定项目或仅本地。远程会话不支持插件。有关完整的插件参考，包括创建你自己的插件，请参阅[插件](39-创建插件.md)。

### 配置预览服务器

Claude 自动检测你的开发服务器设置并将配置存储在启动会话时选择的文件夹根目录的 `.claude/launch.json` 中。Preview 使用此文件夹作为其工作目录，因此如果你选择了父文件夹，具有自己开发服务器的子文件夹将不会自动检测。要使用子文件夹的服务器，要么直接在该文件夹中启动会话，要么手动添加配置。

要自定义服务器的启动方式，例如使用 `yarn dev` 而不是 `npm run dev` 或更改端口，手动编辑文件或点击 Preview 下拉菜单中的 **Edit configuration** 在你的代码编辑器中打开它。该文件支持带注释的 JSON。

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "my-app",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 3000
    }
  ]
}
```

你可以定义多个配置来从同一项目运行不同的服务器，例如前端和 API。请参阅下面的[示例](快速开始/01-ClaudeCode概述.md#examples)。

#### 自动验证更改

启用 `autoVerify` 时，Claude 在编辑文件后自动验证代码更改。它拍摄屏幕截图、检查错误并在完成响应之前确认更改有效。

自动验证默认打开。通过在 `.claude/launch.json` 中添加 `"autoVerify": false` 来按项目禁用它，或从 **Preview** 下拉菜单切换它。

```json
{
  "version": "0.0.1",
  "autoVerify": false,
  "configurations": [...]
}
```

禁用时，预览工具仍然可用，你可以随时要求 Claude 验证。自动验证使其在每次编辑后自动进行。

#### 配置字段

`configurations` 数组中的每个条目接受以下字段：

| 字段                  | 类型        | 描述                                                                                                   |
| ------------------- | --------- | ---------------------------------------------------------------------------------------------------- |
| `name`              | string    | 此服务器的唯一标识符                                                                                           |
| `runtimeExecutable` | string    | 要运行的命令，例如 `npm`、`yarn` 或 `node`                                                                      |
| `runtimeArgs`       | string\[] | 传递给 `runtimeExecutable` 的参数，例如 `["run", "dev"]`                                                      |
| `port`              | number    | 你的服务器监听的端口。默认为 3000                                                                                  |
| `cwd`               | string    | 相对于你的项目根目录的工作目录。默认为项目根目录。使用 `${workspaceFolder}` 显式引用项目根目录                                           |
| `env`               | object    | 其他环境变量作为键值对，例如 `{ "NODE_ENV": "development" }`。不要在这里放置秘密，因为此文件被提交到你的存储库。在你的 shell 配置文件中设置的秘密会自动继承。   |
| `autoPort`          | boolean   | 如何处理端口冲突。见下文                                                                                         |
| `program`           | string    | 用 `node` 运行的脚本。请参阅[何时使用 `program` vs `runtimeExecutable`](快速开始/01-ClaudeCode概述.md#when-to-use-program-vs-runtimeexecutable) |
| `args`              | string\[] | 传递给 `program` 的参数。仅在设置 `program` 时使用                                                                 |

##### 何时使用 `program` vs `runtimeExecutable`

使用 `runtimeExecutable` 和 `runtimeArgs` 通过包管理器启动开发服务器。例如，`"runtimeExecutable": "npm"` 和 `"runtimeArgs": ["run", "dev"]` 运行 `npm run dev`。

当你有一个想用 `node` 直接运行的独立脚本时，使用 `program`。例如，`"program": "server.js"` 运行 `node server.js`。使用 `args` 传递其他标志。

#### 端口冲突

`autoPort` 字段控制当你的首选端口已在使用时会发生什么：

* **`true`**：Claude 自动查找并使用空闲端口。适合大多数开发服务器。
* **`false`**：Claude 失败并出现错误。当你的服务器必须使用特定端口时使用此选项，例如 OAuth 回调或 CORS 允许列表。
* **未设置（默认）**：Claude 询问服务器是否需要该确切端口，然后保存你的答案。

当 Claude 选择不同的端口时，它通过 `PORT` 环境变量将分配的端口传递给你的服务器。

#### 示例

这些配置显示了不同项目类型的常见设置：

#### Next.js
此配置使用 Yarn 在端口 3000 上运行 Next.js 应用：

```json
    {
      "version": "0.0.1",
      "configurations": [
        {
          "name": "web",
          "runtimeExecutable": "yarn",
          "runtimeArgs": ["dev"],
          "port": 3000
        }
      ]
    }
    ```

#### 多个服务器
对于具有前端和 API 服务器的 monorepo，定义多个配置。前端使用 `autoPort: true`，因此如果 3000 被占用，它会选择空闲端口，而 API 服务器需要端口 8080：

```json
    {
      "version": "0.0.1",
      "configurations": [
        {
          "name": "frontend",
          "runtimeExecutable": "npm",
          "runtimeArgs": ["run", "dev"],
          "cwd": "apps/web",
          "port": 3000,
          "autoPort": true
        },
        {
          "name": "api",
          "runtimeExecutable": "npm",
          "runtimeArgs": ["run", "start"],
          "cwd": "server",
          "port": 8080,
          "env": { "NODE_ENV": "development" },
          "autoPort": false
        }
      ]
    }
    ```

#### Node.js 脚本
要直接运行 Node.js 脚本而不是使用包管理器命令，使用 `program` 字段：

```json
    {
      "version": "0.0.1",
      "configurations": [
        {
          "name": "server",
          "program": "server.js",
          "args": ["--verbose"],
          "port": 4000
        }
      ]
    }
    ```

## 计划定期任务

默认情况下，计划任务在你选择的时间和频率自动启动新会话。使用它们进行定期工作，如每日代码审查、依赖项更新检查或从你的日历和收件箱提取的早晨简报。

### 比较计划选项

Claude Code offers three ways to schedule recurring work:

|                            | [Cloud](55-在网络上安排任务.md) | [Desktop](15-使用ClaudeCodeDesktop.md#schedule-recurring-tasks) | [`/loop`](42-按计划运行提示词.md) |
| :------------------------- | :------------------------------- | :---------------------------------------------- | :----------------------------- |
| Runs on                    | Anthropic cloud                  | Your machine                                    | Your machine                   |
| Requires machine on        | No                               | Yes                                             | Yes                            |
| Requires open session      | No                               | No                                              | Yes                            |
| Persistent across restarts | Yes                              | Yes                                             | No (session-scoped)            |
| Access to local files      | No (fresh clone)                 | Yes                                             | Yes                            |
| MCP servers                | Connectors configured per task   | [Config files](31-通过MCP将ClaudeCode连接到工具.md) and connectors          | Inherits from session          |
| Permission prompts         | No (runs autonomously)           | Configurable per task                           | Inherits from session          |
| Customizable schedule      | Via `/schedule` in the CLI       | Yes                                             | Yes                            |
| Minimum interval           | 1 hour                           | 1 minute                                        | 1 minute                       |

**Tip:**
Use **cloud tasks** for work that should run reliably without your machine. Use **Desktop tasks** when you need access to local files and tools. Use **`/loop`** for quick polling during a session.

计划页面支持两种任务：

* **本地任务**：在你的机器上运行。它们可以直接访问你的本地文件和工具，但桌面应用必须打开且你的计算机处于唤醒状态才能运行。
* **远程任务**：在 Anthropic 管理的云基础设施上运行。即使你的计算机关闭，它们也会继续运行，但针对你的存储库的新克隆而不是你的本地检出工作。

两种类型都出现在同一任务网格中。点击 **New task** 来选择要创建的类型。本节的其余部分涵盖本地任务；对于远程任务，请参阅[云计划任务](55-在网络上安排任务.md)。

有关本地任务的错过运行和追赶行为的详细信息，请参阅[计划任务如何运行](快速开始/01-ClaudeCode概述.md#how-scheduled-tasks-run)。

**Note:**
默认情况下，本地计划任务针对你的工作目录的任何状态运行，包括未提交的更改。在提示输入中启用 worktree 切换，为每次运行提供自己的隔离 Git worktree，与[并行会话](快速开始/01-ClaudeCode概述.md#work-in-parallel-with-sessions)相同。

要创建本地计划任务，点击侧边栏中的 **Schedule**，点击 **New task**，然后选择 **New local task**。配置这些字段：

| 字段          | 描述                                                                              |
| ----------- | ------------------------------------------------------------------------------- |
| Name        | 任务的标识符。转换为小写 kebab-case 并用作磁盘上的文件夹名称。必须在你的任务中唯一。                                |
| Description | 任务列表中显示的简短摘要。                                                                   |
| Prompt      | 任务运行时发送给 Claude 的指令。以你在提示框中编写任何消息的相同方式编写此内容。提示输入还包括模型、权限模式、工作文件夹和 worktree 的控制。 |
| Frequency   | 任务运行的频率。请参阅下面的[频率选项](快速开始/01-ClaudeCode概述.md#frequency-options)。                                       |

你也可以通过在任何会话中描述你想要的内容来创建任务。例如，"设置一个每天早上 9 点运行的每日代码审查。"

### 频率选项

* **Manual**：无计划，仅在你点击 **Run now** 时运行。对于保存你按需触发的提示很有用
* **Hourly**：每小时运行一次。每个任务从整点获得最多 10 分钟的固定偏移，以错开 API 流量
* **Daily**：显示时间选择器，默认为上午 9:00 本地时间
* **Weekdays**：与 Daily 相同，但跳过星期六和星期日
* **Weekly**：显示时间选择器和日期选择器

对于选择器不提供的间隔（每 15 分钟、每月第一天等），在任何 Desktop 会话中询问 Claude 来设置计划。使用纯语言；例如，"安排一个任务每 6 小时运行所有测试。"

### 计划任务如何运行

本地计划任务在你的机器上本地运行。Desktop 在应用打开时每分钟检查一次计划，并在任务到期时启动新会话，独立于你打开的任何手动会话。每个任务在计划时间后获得最多 10 分钟的固定延迟，以错开 API 流量。延迟是确定性的：同一任务总是在相同的偏移处启动。

当任务触发时，你会收到桌面通知，新会话出现在侧边栏的 **Scheduled** 部分下。打开它以查看 Claude 做了什么、审查更改或回复权限提示。会话像任何其他会话一样工作：Claude 可以编辑文件、运行命令、创建提交和打开拉取请求。

任务仅在桌面应用运行且你的计算机处于唤醒状态时运行。如果你的计算机在计划时间睡眠，运行将被跳过。要防止空闲睡眠，在设置中的 **Desktop app → General** 下启用 **Keep computer awake**。关闭笔记本电脑盖仍会使其睡眠。对于需要在计算机关闭时运行的任务，请改用[远程任务](55-在网络上安排任务.md)。

### 错过的运行

当应用启动或你的计算机唤醒时，Desktop 检查每个任务是否在过去七天内错过了任何运行。如果有，Desktop 为最近错过的时间启动恰好一次追赶运行，并丢弃任何更旧的。一个错过六天的每日任务在唤醒时运行一次。Desktop 在追赶运行启动时显示通知。

在编写提示时记住这一点。计划在上午 9 点的任务可能在晚上 11 点运行，如果你的计算机整天睡眠。如果时间很重要，向提示本身添加护栏，例如："仅审查今天的提交。如果已经是下午 5 点后，跳过审查，只发布错过的摘要。"

### 计划任务的权限

每个任务都有自己的权限模式，你在创建或编辑任务时设置。来自 `~/.claude/settings.json` 的允许规则也适用于计划任务会话。如果任务在询问模式下运行并需要运行它没有权限的工具，运行将停滞，直到你批准它。会话保持在侧边栏中打开，以便你稍后可以回答。

要避免停滞，在创建任务后点击 **Run now**，观察权限提示，并为每个提示选择"总是允许"。该任务的未来运行自动批准相同的工具，而无需提示。你可以从任务的详细页面审查和撤销这些批准。

### 管理计划任务

点击 **Schedule** 列表中的任务来打开其详细页面。从这里你可以：

* **Run now**：立即启动任务，而无需等待下一个计划时间
* **Toggle repeats**：暂停或恢复计划运行，而无需删除任务
* **Edit**：更改提示、频率、文件夹或其他设置
* **Review history**：查看每次过去的运行，包括因你的计算机睡眠而被跳过的运行
* **Review allowed permissions**：从 **Always allowed** 面板查看和撤销此任务的保存工具批准
* **Delete**：删除任务并存档它创建的所有会话

你也可以通过在任何 Desktop 会话中询问 Claude 来管理任务。例如，"暂停我的 dependency-audit 任务"、"删除 standup-prep 任务"或"显示我的计划任务。"

要在磁盘上编辑任务的提示，打开 `~/.claude/scheduled-tasks/<task-name>/SKILL.md`（或在设置 [`CLAUDE_CONFIG_DIR`](19-环境变量.md) 时在其下）。该文件对 `name` 和 `description` 使用 YAML frontmatter，提示作为正文。更改在下一次运行时生效。计划、文件夹、模型和启用状态不在此文件中：通过编辑表单或询问 Claude 来更改它们。

## 环境配置

你在[启动会话](快速开始/01-ClaudeCode概述.md#start-a-session)时选择的环境决定了 Claude 执行的位置以及你如何连接：

* **Local**：在你的机器上运行，直接访问你的文件
* **Remote**：在 Anthropic 的云基础设施上运行。即使你关闭应用，会话也会继续。
* **SSH**：在你通过 SSH 连接的远程机器上运行，例如你自己的服务器、云虚拟机或开发容器

### 本地会话

本地会话从你的 shell 继承环境变量。如果你需要其他变量，在你的 shell 配置文件中设置它们，例如 `~/.zshrc` 或 `~/.bashrc`，并重启桌面应用。有关支持的变量的完整列表，请参阅[环境变量](19-环境变量.md)。

[扩展思考](使用 Claude Code/02-常见工作流程.md#use-extended-thinking-thinking-mode)默认启用，这改进了复杂推理任务的性能，但使用额外的令牌。要完全禁用思考，在你的 shell 配置文件中设置 `MAX_THINKING_TOKENS=0`。在 Opus 上，`MAX_THINKING_TOKENS` 被忽略，除了 `0`，因为自适应推理控制思考深度。

### 远程会话

远程会话即使在你关闭应用后也会在后台继续。使用计入你的[订阅计划限制](13-有效管理成本.md)，没有单独的计算费用。

你可以创建具有不同网络访问级别和环境变量的自定义云环境。在启动远程会话时选择环境下拉菜单并选择 **Add environment**。有关配置网络访问和环境变量的详细信息，请参阅[云环境](09-ClaudeCodeontheweb.md#cloud-environment)。

### SSH 会话

SSH 会话让你在远程机器上运行 Claude Code，同时使用桌面应用作为你的界面。这对于使用存在于云虚拟机、开发容器或具有特定硬件或依赖项的服务器上的代码库很有用。

要添加 SSH 连接，在启动会话之前点击环境下拉菜单并选择 **+ Add SSH connection**。对话框要求：

* **Name**：此连接的友好标签
* **SSH Host**：`user@hostname` 或在 `~/.ssh/config` 中定义的主机
* **SSH Port**：如果留空，默认为 22，或使用你的 SSH 配置中的端口
* **Identity File**：你的私钥的路径，例如 `~/.ssh/id_rsa`。留空以使用默认密钥或你的 SSH 配置。

添加后，连接出现在环境下拉菜单中。选择它在该机器上启动会话。Claude 在远程机器上运行，可以访问其文件和工具。

Claude Code 必须安装在远程机器上。连接后，SSH 会话支持权限模式、连接器、插件和 MCP servers。

## 企业配置

Teams 或 Enterprise 计划上的组织可以通过管理员控制台控制、托管设置文件和设备管理策略来管理桌面应用行为。

### 管理员控制台控制

这些设置通过[管理员设置控制台](https://claude.ai/admin-settings/claude-code)配置：

* **Desktop 中的 Code**：控制你的组织中的用户是否可以在桌面应用中访问 Claude Code
* **Web 中的 Code**：为你的组织启用或禁用[Web 会话](09-ClaudeCodeontheweb.md)
* **Remote Control**：为你的组织启用或禁用[远程控制](平台和集成/04-使用RemoteControl从任何设备继续本地会话.md)
* **禁用绕过权限模式**：防止你的组织中的用户启用绕过权限模式

### 托管设置

托管设置覆盖项目和用户设置，并在 Desktop 生成 CLI 会话时应用。你可以在你的组织的[托管设置](45-ClaudeCode设置.md#settings-precedence)文件中设置这些键，或通过管理员控制台远程推送它们。

| 键                                          | 描述                                                                                                                               |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `permissions.disableBypassPermissionsMode` | 设置为 `"disable"` 以防止用户启用绕过权限模式。                                                                                                   |
| `disableAutoMode`                          | 设置为 `"disable"` 以防止用户启用 [Auto](使用 Claude Code/04-选择权限模式.md#eliminate-prompts-with-auto-mode) 模式。从模式选择器中删除 Auto。也在 `permissions` 下接受。 |
| `autoMode`                                 | 自定义 auto 模式分类器在你的组织中信任和阻止的内容。请参阅[配置 auto 模式分类器](37-配置权限.md#configure-the-auto-mode-classifier)。                          |

`permissions.disableBypassPermissionsMode` 和 `disableAutoMode` 也在用户和项目设置中工作，但将它们放在托管设置中可防止用户覆盖它们。`autoMode` 从用户设置、`.claude/settings.local.json` 和托管设置中读取，但不从已检入的 `.claude/settings.json` 中读取：克隆的存储库无法注入其自己的分类器规则。有关托管专用设置的完整列表，包括 `allowManagedPermissionRulesOnly` 和 `allowManagedHooksOnly`，请参阅[托管专用设置](37-配置权限.md#managed-only-settings)。

通过管理员控制台上传的远程托管设置目前仅适用于 CLI 和 IDE 会话。对于 Desktop 特定的限制，使用上面的管理员控制台控制。

### 设备管理策略

IT 团队可以通过 macOS 上的 MDM 或 Windows 上的组策略管理桌面应用。可用的策略包括启用或禁用 Claude Code 功能、控制自动更新和设置自定义部署 URL。

* **macOS**：通过使用 Jamf 或 Kandji 等工具的 `com.anthropic.Claude` 偏好域配置
* **Windows**：通过 `SOFTWARE\Policies\Claude` 处的注册表配置

### 身份验证和 SSO

企业组织可以要求所有用户使用 SSO。有关计划级别的详细信息，请参阅[身份验证](04-身份验证.md)，有关 SAML 和 OIDC 配置，请参阅[设置 SSO](https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso)。

### 数据处理

Claude Code 在本地会话中本地处理你的代码，或在远程会话中在 Anthropic 的云基础设施上处理。对话和代码上下文被发送到 Anthropic 的 API 进行处理。有关数据保留、隐私和合规性的详细信息，请参阅[数据处理](14-数据使用.md)。

### 部署

Desktop 可以通过企业部署工具分发：

* **macOS**：通过 MDM（如 Jamf 或 Kandji）使用 `.dmg` 安装程序分发
* **Windows**：通过 MSIX 包或 `.exe` 安装程序部署。有关企业部署选项（包括静默安装），请参阅[为 Windows 部署 Claude Desktop](https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows)

有关网络配置，如代理设置、防火墙允许列表和 LLM 网关，请参阅[网络配置](35-企业网络配置.md)。

有关完整的企业配置参考，请参阅[企业配置指南](https://support.claude.com/en/articles/12622667-enterprise-configuration)。

## 来自 CLI？

如果你已经使用 Claude Code CLI，Desktop 运行相同的底层引擎，具有图形界面。你可以在同一机器上同时运行两者，甚至在同一项目上。每个维护单独的会话历史，但它们通过 CLAUDE.md 文件共享配置和项目内存。

要将 CLI 会话移动到 Desktop，在终端中运行 `/desktop`。Claude 保存你的会话并在桌面应用中打开它，然后退出 CLI。此命令仅在 macOS 和 Windows 上可用。

**Tip:**
何时使用 Desktop vs CLI：当你想要可视化 diff 审查、文件附件或侧边栏中的会话管理时，使用 Desktop。当你需要脚本、自动化、第三方提供商或更喜欢终端工作流时，使用 CLI。

### CLI 标志等效项

此表显示了常见 CLI 标志的桌面应用等效项。未列出的标志没有桌面等效项，因为它们是为脚本或自动化设计的。

| CLI                                   | Desktop 等效项                                                         |
| ------------------------------------- | ------------------------------------------------------------------- |
| `--model sonnet`                      | 发送按钮旁的模型下拉菜单，在启动会话之前                                                |
| `--resume`, `--continue`              | 点击侧边栏中的会话                                                           |
| `--permission-mode`                   | 发送按钮旁的模式选择器                                                         |
| `--dangerously-skip-permissions`      | 绕过权限模式。在设置 → Claude Code → "允许绕过权限模式"中启用。企业管理员可以禁用此设置。              |
| `--add-dir`                           | 在远程会话中使用 **+** 按钮添加多个存储库                                            |
| `--allowedTools`, `--disallowedTools` | 在 Desktop 中不可用                                                      |
| `--verbose`                           | 不可用。检查系统日志：macOS 上的 Console.app，Windows 上的事件查看器 → Windows 日志 → 应用程序 |
| `--print`, `--output-format`          | 不可用。Desktop 仅是交互式的。                                                 |
| `ANTHROPIC_MODEL` 环境变量                | 发送按钮旁的模型下拉菜单                                                        |
| `MAX_THINKING_TOKENS` 环境变量            | 在 shell 配置文件中设置；适用于本地会话。请参阅[环境配置](快速开始/01-ClaudeCode概述.md#environment-configuration)。      |

### 共享配置

Desktop 和 CLI 读取相同的配置文件，因此你的设置会转移：

* **[CLAUDE.md](使用 Claude Code/03-Claude如何记住你的项目.md)** 文件在你的项目中被两者使用
* **[MCP servers](31-通过MCP将ClaudeCode连接到工具.md)** 在 `~/.claude.json` 或 `.mcp.json` 中配置在两者中工作
* **[Hooks](25-Hooks参考.md)** 和 **[skills](47-使用skills扩展Claude.md)** 在设置中定义适用于两者
* **[Settings](45-ClaudeCode设置.md)** 在 `~/.claude.json` 和 `~/.claude/settings.json` 中是共享的。权限规则、允许的工具和 `settings.json` 中的其他设置适用于 Desktop 会话。
* **Models**：Sonnet、Opus 和 Haiku 在两者中都可用。在 Desktop 中，在启动会话之前从发送按钮旁的下拉菜单中选择模型。你无法在活跃会话期间更改模型。

**Note:**
**MCP servers：桌面聊天应用 vs Claude Code**：在 `claude_desktop_config.json` 中为 Claude Desktop 聊天应用配置的 MCP servers 与 Claude Code 分开，不会出现在 Code 选项卡中。要在 Claude Code 中使用 MCP servers，在 `~/.claude.json` 或你的项目的 `.mcp.json` 文件中配置它们。有关详细信息，请参阅 [MCP 配置](31-通过MCP将ClaudeCode连接到工具.md#installing-mcp-servers)。

### 功能比较

此表比较了 CLI 和 Desktop 之间的核心功能。有关 CLI 标志的完整列表，请参阅 [CLI 参考](10-CLI参考.md)。

| 功能                                        | CLI                                                            | Desktop                                           |
| ----------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| 权限模式                                      | 所有模式，包括 `dontAsk`                                              | 询问权限、自动接受编辑、Plan Mode、Auto 和通过设置的绕过权限             |
| `--dangerously-skip-permissions`          | CLI 标志                                                         | 绕过权限模式。在设置 → Claude Code → "允许绕过权限模式"中启用          |
| [第三方提供商](51-企业部署概览.md) | Bedrock、Vertex、Foundry                                         | 不可用。Desktop 直接连接到 Anthropic 的 API。                |
| [MCP servers](31-通过MCP将ClaudeCode连接到工具.md)                 | 在设置文件中配置                                                       | 本地和 SSH 会话的连接器 UI，或设置文件                           |
| [Plugins](39-创建插件.md)                 | `/plugin` 命令                                                   | 插件管理器 UI                                          |
| @mention 文件                               | 基于文本                                                           | 带自动完成                                             |
| 文件附件                                      | 不可用                                                            | 图像、PDF                                            |
| 会话隔离                                      | [`--worktree`](10-CLI参考.md) 标志                        | 自动 worktrees                                      |
| 多个会话                                      | 单独的终端                                                          | 侧边栏选项卡                                            |
| 定期任务                                      | cron 作业、CI 管道                                                  | [计划任务](快速开始/01-ClaudeCode概述.md#schedule-recurring-tasks)                 |
| 计算机使用                                     | 不可用                                                            | [应用和屏幕控制](快速开始/01-ClaudeCode概述.md#let-claude-use-your-computer)在 macOS 上 |
| Dispatch 集成                               | 不可用                                                            | [Dispatch 会话](快速开始/01-ClaudeCode概述.md#sessions-from-dispatch)在侧边栏中       |
| 脚本和自动化                                    | [`--print`](10-CLI参考.md)、[Agent SDK](24-以编程方式运行ClaudeCode.md) | 不可用                                               |

### Desktop 中不可用的内容

以下功能仅在 CLI 或 VS Code 扩展中可用：

* **第三方提供商**：Desktop 直接连接到 Anthropic 的 API。改用 [CLI](快速开始/02-快速开始.md) 与 Bedrock、Vertex 或 Foundry。
* **Linux**：桌面应用仅在 macOS 和 Windows 上可用。
* **内联代码建议**：Desktop 不提供自动完成风格的建议。它通过对话提示和显式代码更改工作。
* **Agent teams**：多 agent 编排通过 [CLI](01-协调ClaudeCode会话团队.md) 和 [Agent SDK](24-以编程方式运行ClaudeCode.md) 可用，不在 Desktop 中。

## 故障排除

### 检查你的版本

要查看你运行的桌面应用版本：

* **macOS**：点击菜单栏中的 **Claude**，然后点击 **About Claude**
* **Windows**：点击 **Help**，然后点击 **About**

点击版本号将其复制到你的剪贴板。

### Code 选项卡中的 403 或身份验证错误

如果在使用 Code 选项卡时看到 `Error 403: Forbidden` 或其他身份验证失败：

1. 从应用菜单中注销并重新登录。这是最常见的修复。
2. 验证你有活跃的付费订阅：Pro、Max、Teams 或 Enterprise。
3. 如果 CLI 工作但 Desktop 不工作，完全退出桌面应用，而不仅仅是关闭窗口，然后重新打开并登录。
4. 检查你的互联网连接和代理设置。

### 启动时屏幕空白或卡住

如果应用打开但显示空白或无响应的屏幕：

1. 重启应用。
2. 检查待处理的更新。应用在启动时自动更新。
3. 在 Windows 上，在 **Windows 日志 → 应用程序** 下的事件查看器中检查崩溃日志。

### "Failed to load session"

如果你看到 `Failed to load session`，选定的文件夹可能不再存在，Git 存储库可能需要未安装的 Git LFS，或文件权限可能阻止访问。尝试选择不同的文件夹或重启应用。

### 会话找不到已安装的工具

如果 Claude 找不到 `npm`、`node` 或其他 CLI 命令等工具，验证工具在你的常规终端中工作，检查你的 shell 配置文件是否正确设置 PATH，并重启桌面应用以重新加载环境变量。

### Git 和 Git LFS 错误

在 Windows 上，Git 是启动本地会话的 Code 选项卡所必需的。如果你看到"Git is required"，安装 [Git for Windows](https://git-scm.com/downloads/win) 并重启应用。

如果你看到"Git LFS is required by this repository but is not installed"，从 [git-lfs.com](https://git-lfs.com/) 安装 Git LFS，运行 `git lfs install`，并重启应用。

### MCP servers 在 Windows 上不工作

如果 MCP server 切换不响应或服务器在 Windows 上连接失败，检查服务器在你的设置中是否正确配置，重启应用，验证服务器进程在任务管理器中运行，并查看服务器日志以获取连接错误。

### 应用无法退出

* **macOS**：按 Cmd+Q。如果应用不响应，使用 Cmd+Option+Esc 强制退出，选择 Claude，然后点击强制退出。
* **Windows**：使用 Ctrl+Shift+Esc 的任务管理器来结束 Claude 进程。

### Windows 特定问题

* **安装后 PATH 未更新**：打开新的终端窗口。PATH 更新仅适用于新的终端会话。
* **并发安装错误**：如果你看到关于另一个安装正在进行的错误，但实际上没有，尝试以管理员身份运行安装程序。
* **ARM64**：Windows ARM64 设备完全支持。

### Intel Mac 上 Cowork 选项卡不可用

Cowork 选项卡在 macOS 上需要 Apple Silicon（M1 或更高版本）。在 Windows 上，Cowork 在所有支持的硬件上可用。Chat 和 Code 选项卡在 Intel Mac 上正常工作。

### 在 CLI 中打开时"Branch doesn't exist yet"

远程会话可以创建在你的本地机器上不存在的分支。点击会话工具栏中的分支名称来复制它，然后在本地获取它：

```bash
git fetch origin <branch-name>
git checkout <branch-name>
```

### 仍然卡住？

* 在 [GitHub Issues](https://github.com/anthropics/claude-code/issues) 上搜索或提交错误
* 访问 [Claude 支持中心](https://support.claude.com/)

提交错误时，包括你的桌面应用版本、你的操作系统、确切的错误消息和相关日志。在 macOS 上，检查 Console.app。在 Windows 上，检查事件查看器 → Windows 日志 → 应用程序。
