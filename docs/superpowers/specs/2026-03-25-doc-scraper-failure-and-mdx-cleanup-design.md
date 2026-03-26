# 文档抓取器失败退出与 Markdown 清洗修复设计

## 背景

本仓库当前包含两套离线文档抓取器：

- `scripts/scraper_core.py`：OpenCode 文档抓取核心
- `scripts/claudecode_scraper_core.py`：Claude Code 文档抓取核心

在最近一次全量执行中，确认存在两个实际问题：

1. `claudecode` 中文抓取出现 3 个失败页面，但脚本仍以退出码 `0` 结束，自动化无法区分“全部成功”和“部分失败”。
2. `claudecode` 生成文档中仍残留大量 `theme={null}`、`<Tabs>/<Tab>`、`<Update>` 等 MDX/主题标记，导致离线 Markdown 可读性明显下降。

## 目标

- 统一抓取器在“存在失败页面”时的退出行为：成功产物可以保留，但进程必须以非零退出码结束。
- 增强 `claudecode` Markdown 清洗逻辑，去掉无意义残留，并保留必要结构信息。
- 为上述行为补充回归测试，避免后续重构再次引入同类问题。
- 修复后重新全量构建 `opencode` 和 `claudecode` 的中英文文档，并抽查结果。

## 非目标

- 不重构两套抓取器为单一公共实现。
- 不处理源站本身缺失的页面内容翻译问题。
- 不引入并发抓取、缓存或更复杂的重试系统。
- 不改动现有离线目录结构和文件命名策略。

## 方案概览

### 1. 部分失败返回非零退出码

保留当前“尽量继续抓取其他页面”的策略，但在抓取结束后检查失败计数：

- `failed == 0`：正常结束。
- `failed > 0`：仍然生成已成功页面与 README，但最后抛出 `SystemExit(1)`。

这样做的好处是：

- 人工运行时仍能拿到尽可能完整的结果；
- 自动化脚本和 CI 可以准确识别失败；
- 行为对 `opencode` 与 `claudecode` 一致。

### 2. Claude Code Markdown 清洗增强

在 `scripts/claudecode_scraper_core.py` 的 `clean_markdown()` 中增加文本级后处理：

- 去掉 fenced code block info string 后面的 `theme={null}`
- 删除 `<Tabs>`、`</Tabs>` 包装
- 将 `<Tab title="...">` 转成普通 Markdown 小标题，例如 `#### Windows PowerShell`
- 删除 `</Tab>`
- 将 `<Update label="..." description="...">` 转成普通 Markdown 小标题，例如 `### 2.1.50 (February 20, 2026)`
- 删除 `</Update>`

这能保留内容语义，同时避免离线文档中残留原站点专用组件语法。

## 数据流与行为

### 抓取失败行为

1. 发现页面列表
2. 逐页抓取并统计成功/失败
3. 写入已成功页面
4. 生成索引
5. 若存在失败页，则以 `SystemExit(1)` 结束

### Markdown 清洗行为

1. 标准化换行
2. 去掉 `Documentation Index` 前导块
3. 清理主题参数 `theme={null}`
4. 将常见 MDX 包装转换为普通 Markdown 结构
5. 输出清洗后的文本供后续标题解析与写盘

## 测试设计

新增或更新以下测试：

- `tests/test_claudecode_scraper_core.py`
  - `clean_markdown()` 能移除 `theme={null}`
  - `clean_markdown()` 能把 `Tabs/Tab` 转为标题结构
  - `clean_markdown()` 能把 `Update` 转为标题结构
  - `scrape_all()` 在存在失败记录时抛出 `SystemExit(1)`
- `tests/test_scraper_core.py`
  - `scrape_all()` 在存在失败记录时抛出 `SystemExit(1)`

测试顺序遵循 TDD：

1. 先写测试
2. 运行并确认失败
3. 再做最小实现
4. 再跑测试直到通过

## 风险与控制

- 风险：把 MDX 标签简单删除后丢失结构信息
  - 控制：对 `Tab` 和 `Update` 做结构化转换，而不是只删除
- 风险：改变退出策略影响现有人工使用习惯
  - 控制：仍保留已成功抓取的文档与索引，只在最终退出码上变严格
- 风险：中文源站缺页导致全量构建仍有失败
  - 控制：这是预期外部条件，不属于本次修复失败；脚本会明确以非零退出码报告

## 验证计划

- 运行相关单测，确认新增行为受控
- 重新全量运行四个抓取脚本
- 核对每套脚本的成功/失败统计与退出码
- 抽查生成后的 `claudecode` 文档，确认 `theme={null}`、`Tabs/Tab`、`Update` 残留明显减少或消失
