# OC_Doc

一个用于抓取 `OpenCode` 与 `Claude Code` 中英文官方文档，并生成离线 Markdown 文档的仓库。

## 支持范围

- `OpenCode` 英文文档 -> `docs/en/opencode`
- `OpenCode` 中文文档 -> `docs/zh/opencode`
- `Claude Code` 英文文档 -> `docs/en/claudecode`
- `Claude Code` 中文文档 -> `docs/zh/claudecode`

## 环境要求

- Python `>=3.10`
- `uv`

安装依赖：

```powershell
uv sync
```

## 快速开始

抓取 `OpenCode`：

```powershell
uv run scripts/scrape_opencode_docs_en.py
uv run scripts/scrape_opencode_docs_zh.py
```

抓取 `Claude Code`：

```powershell
uv run scripts/scrape_claudecode_docs_en.py
uv run scripts/scrape_claudecode_docs_zh.py
```

增量更新模式：

```powershell
uv run scripts/scrape_opencode_docs_en.py --update
uv run scripts/scrape_opencode_docs_zh.py --update
uv run scripts/scrape_claudecode_docs_en.py --update
uv run scripts/scrape_claudecode_docs_zh.py --update
```

## 测试

运行全部测试：

```powershell
uv run -m unittest discover -s tests
```

也可以只运行相关测试：

```powershell
uv run -m unittest tests.test_entrypoints tests.test_scraper_core
uv run -m unittest tests.test_claudecode_entrypoints tests.test_claudecode_scraper_core
```

## 目录结构

```text
scripts/   抓取入口脚本与核心实现
tests/     单元测试
docs/      生成后的离线文档
```

## 已知说明

- 抓取结果依赖上游站点可用性；部分页面可能返回 `404`、限流或 HTML 回退内容。
- 抓取脚本在出现部分失败时会返回非零退出码，便于自动化检测异常。
- 仓库当前同时包含抓取脚本与生成后的离线文档产物。
