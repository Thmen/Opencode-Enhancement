# Doc Scraper Failure And MDX Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复抓取器对部分失败的退出码行为，并清理 Claude Code 离线文档中的 MDX/主题残留，然后重新全量构建文档。

**Architecture:** 在两套抓取核心中统一“有失败则非零退出”的收尾策略；在 `scripts/claudecode_scraper_core.py` 中增强 `clean_markdown()`，将最常见的 MDX 包装转换为普通 Markdown。测试先行，先锁定失败，再补最小实现。

**Tech Stack:** Python 3.10+, `requests`, 标准库 `unittest`, `uv`

---

### Task 1: 为清洗逻辑补失败测试

**Files:**
- Modify: `tests/test_claudecode_scraper_core.py`

- [ ] **Step 1: 写失败测试**

补三类测试：

- `theme={null}` 会从代码块 fence 中移除
- `<Tabs>/<Tab>` 会转成普通标题结构
- `<Update>` 会转成 changelog 段落标题

- [ ] **Step 2: 运行测试确认先失败**

Run: `uv run -m unittest tests.test_claudecode_scraper_core.ClaudeCoreTests -v`

Expected: FAIL，新增断言尚未满足。

- [ ] **Step 3: 写最小实现**

在 `scripts/claudecode_scraper_core.py` 的 `clean_markdown()` 增加文本转换逻辑。

- [ ] **Step 4: 重新运行测试确认通过**

Run: `uv run -m unittest tests.test_claudecode_scraper_core.ClaudeCoreTests -v`

Expected: PASS。

### Task 2: 为部分失败退出码补失败测试

**Files:**
- Modify: `tests/test_claudecode_scraper_core.py`
- Modify: `tests/test_scraper_core.py`

- [ ] **Step 1: 写失败测试**

分别为 `claudecode` 和 `opencode` 增加测试，模拟存在失败页时 `scrape_all()` 最终抛出 `SystemExit(1)`。

- [ ] **Step 2: 运行测试确认先失败**

Run: `uv run -m unittest tests.test_scraper_core tests.test_claudecode_scraper_core -v`

Expected: FAIL，当前实现不会抛出非零退出。

- [ ] **Step 3: 写最小实现**

在两个核心文件的 `scrape_all()` 结尾加入失败检查并抛出 `SystemExit(1)`。

- [ ] **Step 4: 重新运行测试确认通过**

Run: `uv run -m unittest tests.test_scraper_core tests.test_claudecode_scraper_core -v`

Expected: PASS。

### Task 3: 跑回归测试与静态检查

**Files:**
- Modify: `scripts/claudecode_scraper_core.py`
- Modify: `scripts/scraper_core.py`
- Modify: `tests/test_claudecode_scraper_core.py`
- Modify: `tests/test_scraper_core.py`

- [ ] **Step 1: 运行相关单测**

Run: `uv run -m unittest tests.test_entrypoints tests.test_scraper_core tests.test_claudecode_entrypoints tests.test_claudecode_scraper_core`

Expected: PASS。

- [ ] **Step 2: 读取最近改动文件的 lint**

Expected: 没有新引入问题；若有则先修复。

### Task 4: 重建文档并抽查

**Files:**
- Modify: `docs/en/opencode/**`
- Modify: `docs/zh/opencode/**`
- Modify: `docs/en/claudecode/**`
- Modify: `docs/zh/claudecode/**`

- [ ] **Step 1: 全量运行四个抓取脚本**

Run:

- `uv run scripts/scrape_opencode_docs_en.py`
- `uv run scripts/scrape_opencode_docs_zh.py`
- `uv run scripts/scrape_claudecode_docs_en.py`
- `uv run scripts/scrape_claudecode_docs_zh.py`

- [ ] **Step 2: 记录退出码与统计结果**

Expected:

- `opencode` 中英文成功且退出码为 0
- `claudecode en` 成功且退出码为 0
- `claudecode zh` 若上游仍缺页，应以非零退出码结束

- [ ] **Step 3: 抽查生成文档**

检查：

- `docs/zh/claudecode/34-输出样式.md`
- `docs/zh/claudecode/51-故障排除.md`
- `docs/en/claudecode/Getting started/01-Changelog.md`

Expected: 不再出现 `theme={null}`；`Tabs/Tab` 与 `Update` 结构可读。
