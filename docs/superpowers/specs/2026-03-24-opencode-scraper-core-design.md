# OpenCode 文档抓取器重构设计

## 背景

当前仓库已有一个中文文档抓取脚本，能够从 OpenCode 文档站点抓取页面、抽取正文并生成离线 Markdown 文档。新的需求是在保留中文抓取能力的基础上，增加英文版文档抓取，并避免简单复制整份脚本导致的重复维护成本。

本次改动需要把中英文共享的抓取能力下沉到公共模块，同时提供两个清晰的语言入口脚本。

## 目标

- 抽取一个共享核心模块 `scripts/scraper_core.py`
- 提供中文入口脚本 `scripts/scrape_opencode_docs_zh.py`
- 提供英文入口脚本 `scripts/scrape_opencode_docs_en.py`
- 中文输出到 `docs/zh/opencode`
- 英文输出到 `docs/en/opencode`
- 保持现有抓取能力不变：页面发现、正文抽取、Markdown 转换、站内链接本地化、README 生成、`--update` 增量模式

## 非目标

- 不引入额外语言支持
- 不重写抓取策略或页面解析策略
- 不改变离线文档目录的组织方式
- 不额外加入网络缓存、并发抓取或复杂重试机制

## 方案概览

将现有脚本拆成“共享核心 + 两个语言入口”：

- `scripts/scraper_core.py`
  - 放置与语言无关的核心逻辑
  - 包括配置模型、页面发现、HTML 抓取、正文抽取、Markdown 转换、后处理、文件写入和 README 生成
- `scripts/scrape_opencode_docs_zh.py`
  - 只定义中文配置并调用共享核心
- `scripts/scrape_opencode_docs_en.py`
  - 只定义英文配置并调用共享核心

现有 `scripts/scrape_opencode_docs.py` 将被替换为新的中文入口文件 `scripts/scrape_opencode_docs_zh.py`，不再保留旧文件名，避免入口命名混乱。

## 模块设计

### 数据结构

共享模块中保留页面模型 `Page`，并新增一个配置模型，例如 `ScraperConfig`，用于承载语言差异配置：

- `base_url`
- `docs_prefix`
- `output_dir`
- `readme_title`
- `readme_source_label`
- `default_section_title`
- `request_delay`
- `user_agent`

通用流程只依赖 `ScraperConfig`，不再硬编码中文路径或中文标题。

### 共享核心职责

`scripts/scraper_core.py` 负责以下内容：

- 根据 `base_url` 抓取文档首页
- 根据 `docs_prefix` 解析侧边栏中的页面列表
- 提取页面正文区域
- 规范化代码块结构
- 将 HTML 转换为 Markdown
- 将站内链接转换为离线相对路径
- 按分类写入 Markdown 文件
- 生成语言对应的 `README.md`
- 提供完整抓取入口，例如 `scrape_all(config, update_only=False)`

### 语言入口职责

两个入口脚本仅负责：

- 定义各自的 `ScraperConfig`
- 解析 `--update` 参数
- 调用共享核心

中英文差异限定在配置层：

- 中文
  - `BASE_URL = https://opencode.ai/docs/zh-cn`
  - `DOCS_PREFIX = /docs/zh-cn/`
  - `OUTPUT_DIR = docs/zh/opencode`
  - `README` 标题为中文
  - `README` 来源标签为 `来源`
  - 顶层默认分组标题为 `入门`
- 英文
  - `BASE_URL = https://opencode.ai/docs/en`
  - `DOCS_PREFIX = /docs/en/`
  - `OUTPUT_DIR = docs/en/opencode`
  - `README` 标题为英文
  - `README` 来源标签为 `Source`
  - 顶层默认分组标题为 `Getting Started`

## 数据流

单次抓取流程如下：

1. 入口脚本创建语言配置并解析命令行参数
2. 共享核心抓取首页并发现页面列表
3. 共享核心遍历页面并逐个抓取 HTML
4. 对正文进行抽取和代码块规范化
5. 将 HTML 转换为 Markdown
6. 根据当前页面和目标页面分类，重写站内链接
7. 写入语言目录下的离线文件
8. 生成该语言自己的 `README.md`

## 错误处理

保持现有脚本风格，继续使用“打印错误并统计结果”的处理方式：

- 首页抓取失败时直接退出
- 单页抓取失败时记录失败数并继续处理其他页面
- 在全量模式下先清理目标输出目录
- 在增量模式下跳过已存在文件

本次不新增复杂异常分层，以控制改动面。

共享核心还统一持有抓取级公共参数，例如请求间隔与 `User-Agent`。入口脚本不重复定义这类抓取行为参数，避免两个语言入口在抓取节奏或请求头上出现意外分叉。

## 测试设计

仓库当前没有现成测试框架配置，因此优先使用标准库 `unittest`，避免为这次改动引入额外依赖。

这里的测试属于工程质量保障，不属于新增产品功能；本次仍然不新增第三方测试依赖，也不扩展抓取器的产品能力边界。

测试重点覆盖共享核心中最容易因多语言重构而出错的逻辑：

- 不同 `docs_prefix` 下的 slug 提取
- 站内链接本地化
- README 生成路径和标题
- 语言配置是否正确指向 `docs/zh/opencode` 与 `docs/en/opencode`

实现顺序遵循测试优先：

1. 先为共享核心提炼出的纯函数或轻量函数补测试
2. 运行测试并确认先失败
3. 再进行重构和新增英文入口实现
4. 最后执行脚本级验证，确认英文抓取输出落到 `docs/en/opencode`

## 兼容性与迁移

本次会将中文入口文件名调整为 `scripts/scrape_opencode_docs_zh.py`。这意味着旧命令：

`uv run scripts/scrape_opencode_docs.py`

将不再作为正式入口。新的命令为：

- `uv run scripts/scrape_opencode_docs_zh.py`
- `uv run scripts/scrape_opencode_docs_en.py`

如果后续需要兼容旧命令，可以单独再加一个薄包装脚本，但这不在本次范围内。

输出目录以本次确认的语言目录为准：

- 中文写入 `docs/zh/opencode`
- 英文写入 `docs/en/opencode`

如果仓库或本地环境中存在历史路径 `docs/opencode`，本次实现不会自动迁移、删除或兼容该目录。全量模式只会清理当前语言配置对应的 `output_dir`，避免误删其他目录。这里“`不改变离线文档目录的组织方式`”指的是文档内部的分类与文件编号规则保持不变，不是指继续沿用历史父目录路径。

## 验证计划

完成实现后执行以下验证：

- 运行新增测试，确认共享核心在中英文配置下均通过
- 运行中文入口脚本的帮助或最小验证，确认入口可执行
- 运行英文入口脚本进行抓取，确认生成 `docs/en/opencode/README.md`
- 抽查 README 中首页链接和分类链接是否正确

## 风险与控制

- 风险：重构共享核心时破坏中文现有行为
  - 控制：优先抽离纯逻辑并补测试，尽量保持函数行为一致
- 风险：英文路径前缀与中文路径前缀处理不一致
  - 控制：将路径前缀统一配置化，并针对不同前缀补测试
- 风险：入口重命名导致旧命令失效
  - 控制：在文档和最终说明中明确新的脚本名
