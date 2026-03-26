# ClaudeCode Stable Numbering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 `scripts/claudecode_scraper_core.py`，让页面抓取失败时保留编号空位，避免后续文件名整体顺延。

**Architecture:** 在 `_build_pages()` 中先按 `records` 原始顺序为每个分类预分配固定编号，再仅对成功抓取的页面写盘。测试先行，先锁定“前页失败、后页不补位”的行为，再做最小实现。

**Tech Stack:** Python 3.10+, 标准库 `unittest`, `uv`

---

### Task 1: 写失败测试锁定稳定编号行为

**Files:**
- Modify: `tests/test_claudecode_scraper_core.py`
- Modify: `scripts/claudecode_scraper_core.py`

- [ ] **Step 1: 写失败测试**

新增测试，模拟同一分类中前一页抓取失败、后一页抓取成功，断言后一页仍使用原始顺序编号。

- [ ] **Step 2: 运行测试确认先失败**

Run: `uv run -m unittest tests.test_claudecode_scraper_core.ClaudeCoreTests -v`

Expected: FAIL，当前实现会让成功页补位编号。

- [ ] **Step 3: 写最小实现**

在 `_build_pages()` 中预分配每条记录的固定分类序号，再用该序号生成文件名。

- [ ] **Step 4: 重新运行测试确认通过**

Run: `uv run -m unittest tests.test_claudecode_scraper_core.ClaudeCoreTests -v`

Expected: PASS。

### Task 2: 回归验证

**Files:**
- Modify: `scripts/claudecode_scraper_core.py`
- Modify: `tests/test_claudecode_scraper_core.py`

- [ ] **Step 1: 运行全部相关测试**

Run: `uv run -m unittest tests.test_claudecode_entrypoints tests.test_claudecode_scraper_core`

Expected: PASS。

- [ ] **Step 2: 重建 ClaudeCode 中英文文档**

Run:

- `uv run scripts/scrape_claudecode_docs_en.py`
- `uv run scripts/scrape_claudecode_docs_zh.py`

- [ ] **Step 3: 抽查编号是否稳定**

重点确认中文根目录页面在失败页之后不再整体顺延，例如：

- `checkpointing`
- `输出样式`
- `故障排除`

Expected: 前页失败时，后续页面仍保留原始编号空位。
