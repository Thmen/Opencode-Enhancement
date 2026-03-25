[首页](README.md) / Code Review

# Code Review

> 设置自动化 PR 审查，通过对完整代码库的多代理分析来捕获逻辑错误、安全漏洞和回归问题

<Note>
  Code Review 处于研究预览阶段，仅适用于 [Teams 和 Enterprise](https://claude.ai/admin-settings/claude-code) 订阅。对于启用了 [Zero Data Retention](53-零数据保留.md) 的组织，此功能不可用。
</Note>

Code Review 分析您的 GitHub pull request，并在发现问题的代码行上发布内联评论。一支由专业代理组成的团队在完整代码库的上下文中检查代码更改，寻找逻辑错误、安全漏洞、破损的边界情况和微妙的回归问题。

发现结果按严重程度标记，不会批准或阻止您的 PR，因此现有的审查工作流保持不变。您可以通过向存储库添加 `CLAUDE.md` 或 `REVIEW.md` 文件来调整 Claude 标记的内容。

要在您自己的 CI 基础设施中运行 Claude 而不是使用此托管服务，请参阅 [GitHub Actions](19-ClaudeCodeGitHubActions.md) 或 [GitLab CI/CD](20-ClaudeCodeGitLabCICD.md)。

本页涵盖：

* [审查工作原理](快速开始/01-ClaudeCode概述.md#how-reviews-work)
* [设置](快速开始/01-ClaudeCode概述.md#set-up-code-review)
* [自定义审查](快速开始/01-ClaudeCode概述.md#customize-reviews)，使用 `CLAUDE.md` 和 `REVIEW.md`
* [定价](快速开始/01-ClaudeCode概述.md#pricing)

## 审查工作原理

一旦管理员为您的组织[启用 Code Review](快速开始/01-ClaudeCode概述.md#set-up-code-review)，审查将在 PR 打开时、每次推送时或手动请求时触发，具体取决于存储库的配置行为。在任何模式下，注释 `@claude review` 可以[在 PR 上启动审查](快速开始/01-ClaudeCode概述.md#manually-trigger-reviews)。

当审查运行时，多个代理在 Anthropic 基础设施上并行分析差异和周围代码。每个代理寻找不同类别的问题，然后验证步骤检查候选项是否与实际代码行为相符，以过滤掉误报。结果被去重、按严重程度排序，并作为内联评论发布在发现问题的特定行上。如果未发现问题，Claude 会在 PR 上发布简短的确认评论。

审查成本随 PR 大小和复杂性而扩展，平均在 20 分钟内完成。管理员可以通过[分析仪表板](快速开始/01-ClaudeCode概述.md#view-usage)监控审查活动和支出。

### 严重程度级别

每个发现都标有严重程度级别：

| 标记 | 严重程度 | 含义                   |
| :- | :--- | :------------------- |
| 🔴 | 正常   | 应在合并前修复的错误           |
| 🟡 | 小问题  | 轻微问题，值得修复但不阻止        |
| 🟣 | 预先存在 | 代码库中存在但不是由此 PR 引入的错误 |

发现包括可折叠的扩展推理部分，您可以展开以了解 Claude 为什么标记该问题以及它如何验证问题。

### Code Review 检查的内容

默认情况下，Code Review 专注于正确性：会破坏生产的错误，而不是格式偏好或缺失的测试覆盖。您可以通过[向存储库添加指导文件](快速开始/01-ClaudeCode概述.md#customize-reviews)来扩展其检查范围。

## 设置 Code Review

管理员为组织启用一次 Code Review，并选择要包含的存储库。

<Steps>
  <Step title="打开 Claude Code 管理员设置">
    转到 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 并找到 Code Review 部分。您需要对 Claude 组织具有管理员访问权限，并有权在 GitHub 组织中安装 GitHub Apps。
  </Step>

  <Step title="开始设置">
    点击**设置**。这将开始 GitHub App 安装流程。
  </Step>

  <Step title="安装 Claude GitHub App">
    按照提示将 Claude GitHub App 安装到您的 GitHub 组织。该应用请求这些存储库权限：

    * **Contents**：读写
    * **Issues**：读写
    * **Pull requests**：读写

    Code Review 使用对内容的读取访问权限和对 pull request 的写入访问权限。更广泛的权限集也支持 [GitHub Actions](19-ClaudeCodeGitHubActions.md)，如果您稍后启用的话。
  </Step>

  <Step title="选择存储库">
    选择要为 Code Review 启用的存储库。如果您看不到存储库，请确保在安装期间为 Claude GitHub App 提供了对其的访问权限。您可以稍后添加更多存储库。
  </Step>

  <Step title="为每个存储库设置审查触发器">
    设置完成后，Code Review 部分在表格中显示您的存储库。对于每个存储库，使用**审查行为**下拉菜单选择何时运行审查：

    * **PR 创建后一次**：当 PR 打开或标记为准备审查时运行一次审查
    * **每次推送后**：在每次推送到 PR 分支时运行审查，在 PR 演变时捕获新问题，并在您修复标记的问题时自动解决线程
    * **手动**：仅当有人[在 PR 上注释 `@claude review`](快速开始/01-ClaudeCode概述.md#manually-trigger-reviews) 时才启动审查；之后对该 PR 的后续推送会自动审查

    每次推送时审查会运行最多审查并花费最多。手动模式对于高流量存储库很有用，您可以选择特定 PR 进行审查，或仅在 PR 准备好后才开始审查。
  </Step>
</Steps>

存储库表还显示每个存储库基于最近活动的平均审查成本。使用行操作菜单为每个存储库打开或关闭 Code Review，或完全删除存储库。

要验证设置，请打开测试 PR。如果您选择了自动触发器，在几分钟内会出现名为 **Claude Code Review** 的检查运行。如果您选择了手动，在 PR 上注释 `@claude review` 以启动第一次审查。如果没有出现检查运行，请确认存储库在您的管理员设置中列出，并且 Claude GitHub App 有权访问它。

## 手动触发审查

在 pull request 上注释 `@claude review` 以启动审查，并选择该 PR 进入后续的推送触发审查。这适用于存储库的配置触发器，无论如何：在手动模式下使用它来选择特定 PR 进行审查，或在其他模式下获得立即重新审查。无论哪种方式，对该 PR 的推送从那时起就会触发审查。

要使注释触发审查：

* 将其作为顶级 PR 评论发布，而不是差异行上的内联评论
* 在注释开头放置 `@claude review`
* 您必须对存储库具有所有者、成员或协作者访问权限
* PR 必须打开且不是草稿

如果该 PR 上已有审查正在运行，请求将排队等待进行中的审查完成。您可以通过 PR 上的检查运行监控进度。

## 自定义审查

Code Review 从您的存储库读取两个文件来指导它标记的内容。两者都是在默认正确性检查之上的附加内容：

* **`CLAUDE.md`**：共享项目说明，Claude Code 用于所有任务，不仅仅是审查。当指导也适用于交互式 Claude Code 会话时使用它。
* **`REVIEW.md`**：仅审查指导，在代码审查期间专门读取。对于严格关于在审查期间标记或跳过什么的规则，以及会使您的常规 `CLAUDE.md` 混乱的规则，使用它。

### CLAUDE.md

Code Review 读取您的存储库的 `CLAUDE.md` 文件，并将新引入的违规视为小问题级别的发现。这是双向工作的：如果您的 PR 以使 `CLAUDE.md` 语句过时的方式更改代码，Claude 会标记文档需要更新。

Claude 在目录层次结构的每个级别读取 `CLAUDE.md` 文件，因此子目录的 `CLAUDE.md` 中的规则仅适用于该路径下的文件。有关 `CLAUDE.md` 如何工作的更多信息，请参阅[内存文档](使用 Claude Code/03-Claude如何记住你的项目.md)。

对于您不想应用于常规 Claude Code 会话的仅审查指导，请改用 [`REVIEW.md`](快速开始/01-ClaudeCode概述.md#review-md)。

### REVIEW\.md

将 `REVIEW.md` 文件添加到您的存储库根目录以获取仅审查规则。使用它来编码：

* 公司或团队风格指南："优先使用早期返回而不是嵌套条件"
* 语言或框架特定的约定，不被 linter 覆盖
* Claude 应始终标记的内容："任何新 API 路由必须有集成测试"
* Claude 应跳过的内容："不要对 `/gen/` 下生成的代码中的格式进行注释"

示例 `REVIEW.md`：

```markdown  theme={null}
# Code Review Guidelines

## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible
- Error messages don't leak internal details to users

## Style
- Prefer `match` statements over chained `isinstance` checks
- Use structured logging, not f-string interpolation in log calls

## Skip
- Generated files under `src/gen/`
- Formatting-only changes in `*.lock` files
```

Claude 在存储库根目录自动发现 `REVIEW.md`。无需配置。

## 查看使用情况

转到 [claude.ai/analytics/code-review](https://claude.ai/analytics/code-review) 以查看整个组织的 Code Review 活动。仪表板显示：

| 部分     | 显示内容                         |
| :----- | :--------------------------- |
| 审查的 PR | 所选时间范围内每日审查的 pull request 计数 |
| 每周成本   | Code Review 的每周支出            |
| 反馈     | 因开发人员解决问题而自动解决的审查评论计数        |
| 存储库分解  | 每个存储库的审查 PR 计数和已解决评论         |

管理员设置中的存储库表也显示每个存储库的平均审查成本。

## 定价

Code Review 根据令牌使用情况计费。审查平均花费 \$15-25，随 PR 大小、代码库复杂性和需要验证的问题数量而扩展。Code Review 使用通过[额外使用](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)单独计费，不计入您的计划包含的使用。

您选择的审查触发器影响总成本：

* **PR 创建后一次**：每个 PR 运行一次
* **每次推送后**：在每次推送时运行，将成本乘以推送次数
* **手动**：在有人在 PR 上注释 `@claude review` 之前没有审查

在任何模式下，注释 `@claude review` [选择 PR 进入推送触发审查](快速开始/01-ClaudeCode概述.md#manually-trigger-reviews)，因此在该注释后每次推送都会产生额外成本。

无论您的组织是否为其他 Claude Code 功能使用 AWS Bedrock 或 Google Vertex AI，成本都会出现在您的 Anthropic 账单上。要为 Code Review 设置每月支出上限，请转到 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 并为 Claude Code Review 服务配置限制。

通过[分析](快速开始/01-ClaudeCode概述.md#view-usage)中的每周成本图表或管理员设置中的每个存储库平均成本列监控支出。

## 相关资源

Code Review 旨在与 Claude Code 的其余部分一起工作。如果您想在打开 PR 之前在本地运行审查、需要自托管设置或想深入了解 `CLAUDE.md` 如何在工具中塑造 Claude 的行为，这些页面是很好的下一步：

* [Plugins](16-通过市场发现和安装预构建插件.md)：浏览插件市场，包括用于在推送前本地运行按需审查的 `code-review` 插件
* [GitHub Actions](19-ClaudeCodeGitHubActions.md)：在您自己的 GitHub Actions 工作流中运行 Claude，以实现超越代码审查的自定义自动化
* [GitLab CI/CD](20-ClaudeCodeGitLabCICD.md)：GitLab 管道的自托管 Claude 集成
* [Memory](使用 Claude Code/03-Claude如何记住你的项目.md)：`CLAUDE.md` 文件如何在 Claude Code 中工作
* [Analytics](03-使用分析跟踪团队使用情况.md)：跟踪超越代码审查的 Claude Code 使用情况
