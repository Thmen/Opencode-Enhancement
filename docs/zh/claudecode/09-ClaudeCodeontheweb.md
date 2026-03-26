[首页](README.md) / Claude Code on the web

# Claude Code on the web

> 在安全的云基础设施上异步运行 Claude Code 任务

**Note:**
Claude Code on the web 目前处于研究预览阶段。

## Claude Code on the web 是什么？

Claude Code on the web 让开发者可以从 Claude 应用中启动 Claude Code。这非常适合：

* **回答问题**：询问代码架构和功能实现方式
* **错误修复和日常任务**：不需要频繁调整的明确定义的任务
* **并行工作**：同时处理多个错误修复
* **不在本地机器上的存储库**：处理你没有本地检出的代码
* **后端更改**：Claude Code 可以编写测试，然后编写代码来通过这些测试

Claude Code 也可在 Claude 应用中用于 [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 和 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)，用于随时启动任务和监控进行中的工作。

你可以[从终端使用 `--remote` 在网络上启动新任务](快速开始/01-ClaudeCode概述.md#from-terminal-to-web)，或[将网络会话传送回你的终端](快速开始/01-ClaudeCode概述.md#from-web-to-terminal)以在本地继续。要在运行 Claude Code 在自己的机器上而不是云基础设施上时使用网络界面，请参阅[远程控制](平台和集成/04-使用RemoteControl从任何设备继续本地会话.md)。

## 谁可以使用 Claude Code on the web？

Claude Code on the web 在研究预览中可供以下用户使用：

* **Pro 用户**
* **Max 用户**
* **Team 用户**
* **Enterprise 用户**（拥有高级席位或 Chat + Claude Code 席位）

## 入门

1. 访问 [claude.ai/code](https://claude.ai/code)
2. 连接你的 GitHub 账户
3. 在你的存储库中安装 Claude GitHub 应用
4. 选择你的默认环境
5. 提交你的编码任务
6. 在 diff 视图中审查更改，通过评论进行迭代，然后创建拉取请求

## 工作原理

当你在 Claude Code on the web 上启动任务时：

1. **存储库克隆**：你的存储库被克隆到 Anthropic 管理的虚拟机
2. **环境设置**：Claude 准备一个安全的云环境，包含你的代码，然后运行你的[设置脚本](快速开始/01-ClaudeCode概述.md#setup-scripts)（如果已配置）
3. **网络配置**：根据你的设置配置互联网访问
4. **任务执行**：Claude 分析代码、进行更改、运行测试并检查其工作
5. **完成**：你会收到完成通知，可以使用更改创建 PR
6. **结果**：更改被推送到一个分支，准备好创建拉取请求

## 使用 diff 视图审查更改

Diff 视图让你在创建拉取请求之前看到 Claude 更改的确切内容。与其点击"创建 PR"在 GitHub 中审查更改，不如直接在应用中查看 diff 并与 Claude 迭代，直到更改准备好。

当 Claude 对文件进行更改时，会出现一个 diff 统计指示器，显示添加和删除的行数（例如，`+12 -1`）。选择此指示器打开 diff 查看器，左侧显示文件列表，右侧显示每个文件的更改。

从 diff 视图中，你可以：

* 逐个文件审查更改
* 对特定更改进行评论以请求修改
* 根据你看到的内容继续与 Claude 迭代

这让你可以通过多轮反馈来完善更改，而无需创建草稿 PR 或切换到 GitHub。

## 在网络和终端之间移动任务

你可以从终端在网络上启动新任务，或将网络会话拉入你的终端以在本地继续。网络会话即使在你关闭笔记本电脑后也会持续，你可以从任何地方（包括 Claude 移动应用）监控它们。

**Note:**
会话切换是单向的：你可以将网络会话拉入你的终端，但不能将现有的终端会话推送到网络。`--remote` 标志为你的当前存储库创建一个*新的*网络会话。

### 从终端到网络

使用 `--remote` 标志从命令行启动网络会话：

```bash
claude --remote "Fix the authentication bug in src/auth/login.ts"
```

这在 claude.ai 上创建一个新的网络会话。任务在云中运行，而你继续在本地工作。使用 `/tasks` 检查进度，或在 claude.ai 或 Claude 移动应用上打开会话以直接交互。从那里你可以引导 Claude、提供反馈或回答问题，就像任何其他对话一样。

#### 远程任务的提示

**在本地规划，远程执行**：对于复杂的任务，在 Plan Mode 中启动 Claude 以协作制定方法，然后将工作发送到网络：

```bash
claude --permission-mode plan
```

在 Plan Mode 中，Claude 只能读取文件和探索代码库。一旦你对计划满意，为自主执行启动远程会话：

```bash
claude --remote "Execute the migration plan in docs/migration-plan.md"
```

这种模式让你可以控制策略，同时让 Claude 在云中自主执行。

**并行运行任务**：每个 `--remote` 命令创建自己的网络会话，独立运行。你可以启动多个任务，它们都将在单独的会话中同时运行：

```bash
claude --remote "Fix the flaky test in auth.spec.ts"
claude --remote "Update the API documentation"
claude --remote "Refactor the logger to use structured output"
```

使用 `/tasks` 监控所有会话。当会话完成时，你可以从网络界面创建 PR 或[传送](快速开始/01-ClaudeCode概述.md#from-web-to-terminal)会话到你的终端以继续工作。

### 从网络到终端

有几种方法可以将网络会话拉入你的终端：

* **使用 `/teleport`**：在 Claude Code 中，运行 `/teleport`（或 `/tp`）以查看你的网络会话的交互式选择器。如果你有未提交的更改，系统会提示你先隐藏它们。
* **使用 `--teleport`**：从命令行，运行 `claude --teleport` 以获得交互式会话选择器，或 `claude --teleport <session-id>` 以直接恢复特定会话。
* **从 `/tasks`**：运行 `/tasks` 以查看你的后台会话，然后按 `t` 传送到其中一个
* **从网络界面**：点击"在 CLI 中打开"以复制可以粘贴到你的终端中的命令

当你传送一个会话时，Claude 验证你在正确的存储库中，从远程会话获取并检出分支，并将完整的对话历史加载到你的终端中。

#### 传送的要求

传送在恢复会话之前检查这些要求。如果任何要求未满足，你会看到错误或被提示解决问题。

| 要求         | 详情                                    |
| ---------- | ------------------------------------- |
| 干净的 git 状态 | 你的工作目录必须没有未提交的更改。如果需要，传送会提示你隐藏更改。     |
| 正确的存储库     | 你必须从同一存储库的检出运行 `--teleport`，而不是从分叉运行。 |
| 分支可用       | 网络会话中的分支必须已被推送到远程。传送会自动获取并检出它。        |
| 相同账户       | 你必须认证到网络会话中使用的相同 Claude.ai 账户。        |

### 共享会话

要共享会话，请根据下面的账户类型切换其可见性。之后，按原样共享会话链接。打开你的共享会话的收件人将在加载时看到会话的最新状态，但收件人的页面不会实时更新。

#### 从 Enterprise 或 Teams 账户共享

对于 Enterprise 和 Teams 账户，两个可见性选项是**私有**和**团队**。团队可见性使会话对你的 Claude.ai 组织的其他成员可见。默认情况下启用存储库访问验证，基于连接到收件人账户的 GitHub 账户。你的账户显示名称对所有有访问权限的收件人可见。[Claude in Slack](平台和集成/05-Slack中的ClaudeCode.md) 会话会自动以团队可见性共享。

#### 从 Max 或 Pro 账户共享

对于 Max 和 Pro 账户，两个可见性选项是**私有**和**公开**。公开可见性使会话对任何登录到 claude.ai 的用户可见。

在共享之前检查你的会话是否包含敏感内容。会话可能包含来自私有 GitHub 存储库的代码和凭证。默认情况下不启用存储库访问验证。

通过转到设置 > Claude Code > 共享设置来启用存储库访问验证和/或从你的共享会话中隐瞒你的名称。

## 管理会话

### 归档会话

你可以归档会话以保持你的会话列表有序。归档的会话从默认会话列表中隐藏，但可以通过筛选已归档会话来查看。

要归档会话，请在侧边栏中悬停在会话上并点击归档图标。

### 删除会话

删除会话会永久删除会话及其数据。此操作无法撤销。你可以通过两种方式删除会话：

* **从侧边栏**：筛选已归档会话，然后悬停在你想删除的会话上并点击删除图标
* **从会话菜单**：打开会话，点击会话标题旁的下拉菜单，然后选择**删除**

删除会话前会要求你确认。

## 云环境

### 默认镜像

我们构建并维护一个通用镜像，其中预装了常见的工具链和语言生态系统。此镜像包括：

* 流行的编程语言和运行时
* 常见的构建工具和包管理器
* 测试框架和 linters

#### 检查可用工具

要查看你的环境中预装了什么，请要求 Claude Code 运行：

```bash
check-tools
```

此命令显示：

* 编程语言及其版本
* 可用的包管理器
* 已安装的开发工具

#### 特定于语言的设置

通用镜像包括以下预配置的环境：

* **Python**：Python 3.x，带有 pip、poetry 和常见的科学库
* **Node.js**：最新 LTS 版本，带有 npm、yarn、pnpm 和 bun
* **Ruby**：版本 3.1.6、3.2.6、3.3.6（默认：3.3.6），带有 gem、bundler 和 rbenv 用于版本管理
* **PHP**：版本 8.4.14
* **Java**：OpenJDK，带有 Maven 和 Gradle
* **Go**：最新稳定版本，带有模块支持
* **Rust**：Rust 工具链，带有 cargo
* **C++**：GCC 和 Clang 编译器

#### 数据库

通用镜像包括以下数据库：

* **PostgreSQL**：版本 16
* **Redis**：版本 7.0

### 环境配置

当你在 Claude Code on the web 中启动会话时，以下是幕后发生的情况：

1. **环境准备**：我们克隆你的存储库并运行任何已配置的[设置脚本](快速开始/01-ClaudeCode概述.md#setup-scripts)。存储库将使用你的 GitHub 存储库上的默认分支进行克隆。如果你想检出特定分支，可以在提示中指定。

2. **网络配置**：我们为代理配置互联网访问。默认情况下互联网访问受限，但你可以根据需要配置环境以禁用互联网或完全互联网访问。

3. **Claude Code 执行**：Claude Code 运行以完成你的任务，编写代码、运行测试并检查其工作。你可以通过网络界面在整个会话中指导和引导 Claude。Claude 尊重你在 `CLAUDE.md` 中定义的上下文。

4. **结果**：当 Claude 完成其工作时，它将推送分支到远程。你将能够为分支创建 PR。

**Note:**
Claude 完全通过环境中可用的终端和 CLI 工具运行。它使用通用镜像中的预装工具和你通过 hooks 或依赖管理安装的任何其他工具。

**要添加新环境**：选择当前环境以打开环境选择器，然后选择"添加环境"。这将打开一个对话框，你可以在其中指定环境名称、网络访问级别、环境变量和[设置脚本](快速开始/01-ClaudeCode概述.md#setup-scripts)。

**要更新现有环境**：选择当前环境，在环境名称的右侧，然后选择设置按钮。这将打开一个对话框，你可以在其中更新环境名称、网络访问、环境变量和设置脚本。

**要从终端选择你的默认环境**：如果你配置了多个环境，运行 `/remote-env` 以选择在使用 `--remote` 从终端启动网络会话时使用哪个环境。使用单个环境时，此命令显示你的当前配置。

**Note:**
环境变量必须指定为键值对，采用[`.env` 格式](https://www.dotenv.org/)。例如：

```text
  API_KEY=your_api_key
  DEBUG=true
  ```

### 设置脚本

设置脚本是一个 Bash 脚本，在新的云会话启动时运行，在 Claude Code 启动之前。使用设置脚本来安装依赖、配置工具或准备云环境需要的任何东西，这些东西不在[默认镜像](快速开始/01-ClaudeCode概述.md#default-image)中。

脚本在 Ubuntu 24.04 上以 root 身份运行，所以 `apt install` 和大多数语言包管理器都可以工作。

**Tip:**
要在将其添加到你的脚本之前检查已安装的内容，请要求 Claude 在云会话中运行 `check-tools`。

要添加设置脚本，请打开环境设置对话框并在**设置脚本**字段中输入你的脚本。

此示例安装 `gh` CLI，它不在默认镜像中：

```bash
#!/bin/bash
apt update && apt install -y gh
```

设置脚本仅在创建新会话时运行。恢复现有会话时会跳过它们。

如果脚本以非零值退出，会话将无法启动。将 `|| true` 附加到非关键命令以避免在不稳定的安装上阻止会话。

**Note:**
安装包的设置脚本需要网络访问才能到达注册表。默认网络访问允许连接到[常见包注册表](快速开始/01-ClaudeCode概述.md#default-allowed-domains)，包括 npm、PyPI、RubyGems 和 crates.io。如果你的环境禁用了网络访问，脚本将无法安装包。

#### 设置脚本与 SessionStart hooks

使用设置脚本来安装云需要但你的笔记本电脑已有的东西，如语言运行时或 CLI 工具。使用[SessionStart hook](25-Hooks参考.md#sessionstart)进行应该在任何地方运行的项目设置，云和本地，如 `npm install`。

两者都在会话开始时运行，但它们属于不同的地方：

|     | 设置脚本                      | SessionStart hooks               |
| --- | ------------------------- | -------------------------------- |
| 附加到 | 云环境                       | 你的存储库                            |
| 配置在 | 云环境 UI                    | 你的存储库中的 `.claude/settings.json`  |
| 运行  | 在 Claude Code 启动之前，仅在新会话上 | 在 Claude Code 启动之后，在每个会话上，包括已恢复的 |
| 范围  | 仅云环境                      | 本地和云                             |

SessionStart hooks 也可以在你的用户级 `~/.claude/settings.json` 中本地定义，但用户级设置不会传送到云会话。在云中，只有提交到存储库的 hooks 运行。

### 依赖管理

自定义环境镜像和快照尚不支持。使用[设置脚本](快速开始/01-ClaudeCode概述.md#setup-scripts)在会话启动时安装包，或使用[SessionStart hooks](25-Hooks参考.md#sessionstart)进行也应在本地环境中运行的依赖安装。SessionStart hooks 有[已知限制](快速开始/01-ClaudeCode概述.md#dependency-management-limitations)。

要使用设置脚本配置自动依赖安装，请打开你的环境设置并添加脚本：

```bash
#!/bin/bash
npm install
pip install -r requirements.txt
```

或者，你可以在你的存储库的 `.claude/settings.json` 文件中使用 SessionStart hooks 进行也应在本地环境中运行的依赖安装：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/install_pkgs.sh"
          }
        ]
      }
    ]
  }
}
```

在 `scripts/install_pkgs.sh` 创建相应的脚本：

```bash
#!/bin/bash

# Only run in remote environments
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

npm install
pip install -r requirements.txt
exit 0
```

使其可执行：`chmod +x scripts/install_pkgs.sh`

#### 持久化环境变量

SessionStart hooks 可以通过写入 `CLAUDE_ENV_FILE` 环境变量中指定的文件来为后续 Bash 命令持久化环境变量。有关详情，请参阅 hooks 参考中的[SessionStart hooks](25-Hooks参考.md#sessionstart)。

#### 依赖管理限制

* **Hooks 对所有会话触发**：SessionStart hooks 在本地和远程环境中都运行。没有 hook 配置来仅将 hook 限定到远程会话。要跳过本地执行，请在你的脚本中检查 `CLAUDE_CODE_REMOTE` 环境变量，如上所示。
* **需要网络访问**：安装命令需要网络访问才能到达包注册表。如果你的环境配置为"无互联网"访问，这些 hooks 将失败。使用"受限"（默认）或"完全"网络访问。[默认允许列表](快速开始/01-ClaudeCode概述.md#default-allowed-domains)包括常见的注册表，如 npm、PyPI、RubyGems 和 crates.io。
* **代理兼容性**：远程环境中的所有出站流量都通过[安全代理](快速开始/01-ClaudeCode概述.md#security-proxy)。某些包管理器不能与此代理正确配合使用。Bun 是一个已知的例子。
* **在每个会话启动时运行**：Hooks 在每次会话启动或恢复时运行，增加启动延迟。通过在重新安装之前检查依赖是否已存在来保持安装脚本快速。

## 网络访问和安全

### 网络策略

#### GitHub 代理

为了安全起见，所有 GitHub 操作都通过专用代理服务进行，该服务透明地处理所有 git 交互。在沙箱内，git 客户端使用自定义构建的作用域凭证进行身份验证。此代理：

* 安全地管理 GitHub 身份验证 - git 客户端在沙箱内使用作用域凭证，代理验证并将其转换为你的实际 GitHub 身份验证令牌
* 限制 git push 操作到当前工作分支以确保安全
* 启用无缝克隆、获取和 PR 操作，同时维护安全边界

#### 安全代理

环境在 HTTP/HTTPS 网络代理后面运行，用于安全和滥用防止目的。所有出站互联网流量都通过此代理，该代理提供：

* 防止恶意请求
* 速率限制和滥用防止
* 增强安全性的内容过滤

### 访问级别

默认情况下，网络访问仅限于[允许列表域](快速开始/01-ClaudeCode概述.md#default-allowed-domains)。

你可以配置自定义网络访问，包括禁用网络访问。

### 默认允许的域

使用"受限"网络访问时，默认允许以下域：

#### Anthropic 服务

* api.anthropic.com
* statsig.anthropic.com
* platform.claude.com
* code.claude.com
* claude.ai

#### 版本控制

* github.com
* [www.github.com](http://www.github.com)
* api.github.com
* npm.pkg.github.com
* raw\.githubusercontent.com
* pkg-npm.githubusercontent.com
* objects.githubusercontent.com
* codeload.github.com
* avatars.githubusercontent.com
* camo.githubusercontent.com
* gist.github.com
* gitlab.com
* [www.gitlab.com](http://www.gitlab.com)
* registry.gitlab.com
* bitbucket.org
* [www.bitbucket.org](http://www.bitbucket.org)
* api.bitbucket.org

#### 容器注册表

* registry-1.docker.io
* auth.docker.io
* index.docker.io
* hub.docker.com
* [www.docker.com](http://www.docker.com)
* production.cloudflare.docker.com
* download.docker.com
* gcr.io
* \*.gcr.io
* ghcr.io
* mcr.microsoft.com
* \*.data.mcr.microsoft.com
* public.ecr.aws

#### 云平台

* cloud.google.com
* accounts.google.com
* gcloud.google.com
* \*.googleapis.com
* storage.googleapis.com
* compute.googleapis.com
* container.googleapis.com
* azure.com
* portal.azure.com
* microsoft.com
* [www.microsoft.com](http://www.microsoft.com)
* \*.microsoftonline.com
* packages.microsoft.com
* dotnet.microsoft.com
* dot.net
* visualstudio.com
* dev.azure.com
* \*.amazonaws.com
* \*.api.aws
* oracle.com
* [www.oracle.com](http://www.oracle.com)
* java.com
* [www.java.com](http://www.java.com)
* java.net
* [www.java.net](http://www.java.net)
* download.oracle.com
* yum.oracle.com

#### 包管理器 - JavaScript/Node

* registry.npmjs.org
* [www.npmjs.com](http://www.npmjs.com)
* [www.npmjs.org](http://www.npmjs.org)
* npmjs.com
* npmjs.org
* yarnpkg.com
* registry.yarnpkg.com

#### 包管理器 - Python

* pypi.org
* [www.pypi.org](http://www.pypi.org)
* files.pythonhosted.org
* pythonhosted.org
* test.pypi.org
* pypi.python.org
* pypa.io
* [www.pypa.io](http://www.pypa.io)

#### 包管理器 - Ruby

* rubygems.org
* [www.rubygems.org](http://www.rubygems.org)
* api.rubygems.org
* index.rubygems.org
* ruby-lang.org
* [www.ruby-lang.org](http://www.ruby-lang.org)
* rubyforge.org
* [www.rubyforge.org](http://www.rubyforge.org)
* rubyonrails.org
* [www.rubyonrails.org](http://www.rubyonrails.org)
* rvm.io
* get.rvm.io

#### 包管理器 - Rust

* crates.io
* [www.crates.io](http://www.crates.io)
* index.crates.io
* static.crates.io
* rustup.rs
* static.rust-lang.org
* [www.rust-lang.org](http://www.rust-lang.org)

#### 包管理器 - Go

* proxy.golang.org
* sum.golang.org
* index.golang.org
* golang.org
* [www.golang.org](http://www.golang.org)
* goproxy.io
* pkg.go.dev

#### 包管理器 - JVM

* maven.org
* repo.maven.org
* central.maven.org
* repo1.maven.org
* jcenter.bintray.com
* gradle.org
* [www.gradle.org](http://www.gradle.org)
* services.gradle.org
* plugins.gradle.org
* kotlin.org
* [www.kotlin.org](http://www.kotlin.org)
* spring.io
* repo.spring.io

#### 包管理器 - 其他语言

* packagist.org (PHP Composer)
* [www.packagist.org](http://www.packagist.org)
* repo.packagist.org
* nuget.org (.NET NuGet)
* [www.nuget.org](http://www.nuget.org)
* api.nuget.org
* pub.dev (Dart/Flutter)
* api.pub.dev
* hex.pm (Elixir/Erlang)
* [www.hex.pm](http://www.hex.pm)
* cpan.org (Perl CPAN)
* [www.cpan.org](http://www.cpan.org)
* metacpan.org
* [www.metacpan.org](http://www.metacpan.org)
* api.metacpan.org
* cocoapods.org (iOS/macOS)
* [www.cocoapods.org](http://www.cocoapods.org)
* cdn.cocoapods.org
* haskell.org
* [www.haskell.org](http://www.haskell.org)
* hackage.haskell.org
* swift.org
* [www.swift.org](http://www.swift.org)

#### Linux 发行版

* archive.ubuntu.com
* security.ubuntu.com
* ubuntu.com
* [www.ubuntu.com](http://www.ubuntu.com)
* \*.ubuntu.com
* ppa.launchpad.net
* launchpad.net
* [www.launchpad.net](http://www.launchpad.net)

#### 开发工具和平台

* dl.k8s.io (Kubernetes)
* pkgs.k8s.io
* k8s.io
* [www.k8s.io](http://www.k8s.io)
* releases.hashicorp.com (HashiCorp)
* apt.releases.hashicorp.com
* rpm.releases.hashicorp.com
* archive.releases.hashicorp.com
* hashicorp.com
* [www.hashicorp.com](http://www.hashicorp.com)
* repo.anaconda.com (Anaconda/Conda)
* conda.anaconda.org
* anaconda.org
* [www.anaconda.com](http://www.anaconda.com)
* anaconda.com
* continuum.io
* apache.org (Apache)
* [www.apache.org](http://www.apache.org)
* archive.apache.org
* downloads.apache.org
* eclipse.org (Eclipse)
* [www.eclipse.org](http://www.eclipse.org)
* download.eclipse.org
* nodejs.org (Node.js)
* [www.nodejs.org](http://www.nodejs.org)

#### 云服务和监控

* statsig.com
* [www.statsig.com](http://www.statsig.com)
* api.statsig.com
* sentry.io
* \*.sentry.io
* http-intake.logs.datadoghq.com
* \*.datadoghq.com
* \*.datadoghq.eu

#### 内容交付和镜像

* sourceforge.net
* \*.sourceforge.net
* packagecloud.io
* \*.packagecloud.io

#### 架构和配置

* json-schema.org
* [www.json-schema.org](http://www.json-schema.org)
* json.schemastore.org
* [www.schemastore.org](http://www.schemastore.org)

#### Model Context Protocol

* \*.modelcontextprotocol.io

**Note:**
标记为 `*` 的域表示通配符子域匹配。例如，`*.gcr.io` 允许访问 `gcr.io` 的任何子域。

### 自定义网络访问的安全最佳实践

1. **最小权限原则**：仅启用所需的最小网络访问
2. **定期审计**：定期审查允许的域
3. **使用 HTTPS**：始终优先使用 HTTPS 端点而不是 HTTP

## 安全和隔离

Claude Code on the web 提供强大的安全保证：

* **隔离的虚拟机**：每个会话在隔离的、Anthropic 管理的 VM 中运行
* **网络访问控制**：网络访问默认受限，可以禁用

**Note:**
在禁用网络访问的情况下运行时，Claude Code 被允许与 Anthropic API 通信，这可能仍然允许数据从隔离的 Claude Code VM 中退出。

* **凭证保护**：敏感凭证（如 git 凭证或签名密钥）永远不会在沙箱内与 Claude Code 一起。身份验证通过使用作用域凭证的安全代理处理
* **安全分析**：代码在隔离的 VM 内分析和修改，然后创建 PR

## 定价和速率限制

Claude Code on the web 与你账户内所有其他 Claude 和 Claude Code 使用共享速率限制。并行运行多个任务将按比例消耗更多速率限制。

## 限制

* **存储库身份验证**：你只能在认证到相同账户时将会话从网络移动到本地
* **平台限制**：Claude Code on the web 仅适用于托管在 GitHub 中的代码。GitLab 和其他非 GitHub 存储库不能与云会话一起使用

## 最佳实践

1. **自动化环境设置**：使用[设置脚本](快速开始/01-ClaudeCode概述.md#setup-scripts)在 Claude Code 启动之前安装依赖和配置工具。对于更高级的场景，配置[SessionStart hooks](25-Hooks参考.md#sessionstart)。
2. **记录要求**：在你的 `CLAUDE.md` 文件中清楚地指定依赖和命令。如果你有 `AGENTS.md` 文件，你可以在你的 `CLAUDE.md` 中使用 `@AGENTS.md` 来源它以维护单一的真实来源。

## 相关资源

* [Hooks 配置](25-Hooks参考.md)
* [设置参考](45-ClaudeCode设置.md)
* [安全](43-安全性.md)
* [数据使用](14-数据使用.md)
