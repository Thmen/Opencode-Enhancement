# OpenCode Scraper Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 OpenCode 中文抓取脚本重构为共享核心 `scripts/scraper_core.py`，并提供独立的中文与英文入口脚本，输出到 `docs/zh/opencode` 与 `docs/en/opencode`。

**Architecture:** 保留现有抓取流程与页面解析策略，但把语言无关的逻辑下沉到 `scripts/scraper_core.py`。两个入口脚本只暴露配置常量 `CONFIG` 和命令行入口 `main(argv=None)`，用标准库 `unittest` 覆盖配置化后的纯函数、README 生成、侧边栏页面发现和入口脚本调度行为。

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4`, `markdownify`, 标准库 `unittest`, `uv`

---

**Implementation Notes**

- 本计划遵循 TDD：先写失败测试，再补最小实现。
- 本仓库当前流程要求只有在用户明确要求时才创建 git commit，因此本计划把每个任务的最后一步定义为“验证检查点”，不包含自动提交。
- 统一从包含 `pyproject.toml` 的仓库根目录运行命令。

## File Structure

### Create

- `scripts/scraper_core.py`
- `scripts/scrape_opencode_docs_zh.py`
- `scripts/scrape_opencode_docs_en.py`
- `tests/test_scraper_core.py`
- `tests/test_entrypoints.py`

### Delete

- `scripts/scrape_opencode_docs.py`

### Responsibilities

- `scripts/scraper_core.py`
  - 定义 `Page`、`ScraperConfig`
  - 提供与语言无关的抓取、解析、转换、输出逻辑
  - 暴露 `scrape_all(config, update_only=False)` 作为共享入口
- `scripts/scrape_opencode_docs_zh.py`
  - 定义中文 `CONFIG`
  - 解析 `--update`
  - 调用 `scrape_all(CONFIG, update_only=...)`
- `scripts/scrape_opencode_docs_en.py`
  - 定义英文 `CONFIG`
  - 解析 `--update`
  - 调用 `scrape_all(CONFIG, update_only=...)`
- `tests/test_scraper_core.py`
  - 测试 prefix 感知的 slug 解析、README 生成、站内链接本地化、侧边栏页面发现
- `tests/test_entrypoints.py`
  - 测试中英文入口脚本的 `CONFIG` 值与 `main(argv=None)` 调度行为

### Task 1: 搭建共享核心的可测试骨架

**Files:**
- Create: `tests/test_scraper_core.py`
- Create: `scripts/scraper_core.py`

- [ ] **Step 1: 写失败测试，锁定配置化的纯函数接口**

```python
from dataclasses import replace
import tempfile
import unittest
from pathlib import Path

from scripts.scraper_core import Page, ScraperConfig, _slug_from_href, generate_index, postprocess


class CoreHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ScraperConfig(
            base_url="https://opencode.ai/docs/en",
            docs_prefix="/docs/en/",
            output_dir=Path("docs/en/opencode"),
            readme_title="OpenCode English Docs (Offline)",
            readme_source_label="Source",
            default_section_title="Getting Started",
            request_delay=0.0,
            user_agent="test-agent",
        )

    def test_slug_from_href_returns_empty_for_language_root(self) -> None:
        self.assertEqual(_slug_from_href("/docs/en/", self.config.docs_prefix), "")

    def test_slug_from_href_strips_language_prefix(self) -> None:
        self.assertEqual(_slug_from_href("/docs/en/config/", self.config.docs_prefix), "config")

    def test_postprocess_localizes_cross_category_links(self) -> None:
        page = Page(slug="intro", title="Intro", category="", filename="01-Intro.md")
        target = Page(slug="cli", title="CLI", category="Usage", filename="03-CLI.md")
        text = "[CLI](/docs/en/cli)"
        self.assertEqual(
            postprocess(text, page, {"cli": target}, self.config),
            "[CLI](Usage/03-CLI.md)\n",
        )

    def test_generate_index_uses_language_specific_labels(self) -> None:
        page = Page(slug="", title="Intro", category="", filename="01-Intro.md")
        with tempfile.TemporaryDirectory() as tmp:
            config = replace(self.config, output_dir=Path(tmp))
            generate_index([page], config)
            readme = Path(tmp) / "README.md"
            content = readme.read_text(encoding="utf-8")
        self.assertIn("# OpenCode English Docs (Offline)", content)
        self.assertIn("> Source: https://opencode.ai/docs/en", content)
        self.assertIn("## Getting Started", content)
```

- [ ] **Step 2: 运行测试，确认先失败**

Run: `uv run -m unittest discover -s tests -p "test_scraper_core.py" -v`

Expected: FAIL，报 `ModuleNotFoundError: No module named 'scripts.scraper_core'` 或缺失符号错误，因为共享核心文件还不存在。

- [ ] **Step 3: 在 `scripts/scraper_core.py` 中写最小实现以通过这些测试**

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScraperConfig:
    base_url: str
    docs_prefix: str
    output_dir: Path
    readme_title: str
    readme_source_label: str
    default_section_title: str
    request_delay: float
    user_agent: str


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    category: str
    filename: str
```

同时补齐以下最小函数，使测试能通过：

- `_make_filename(index: int, title: str) -> str`
- `_slug_from_href(href: str, docs_prefix: str) -> str`
- `postprocess(text: str, page: Page, slug_map: dict[str, Page], config: ScraperConfig) -> str`
- `generate_index(pages: list[Page], config: ScraperConfig) -> None`

- [ ] **Step 4: 重新运行测试，确认通过**

Run: `uv run -m unittest discover -s tests -p "test_scraper_core.py" -v`

Expected: PASS，4 个测试全部通过。

- [ ] **Step 5: 验证检查点**

确认 `scripts/scraper_core.py` 中的 README 文案、prefix 解析和链接重写都已经配置化，不再写死中文路径和中文文案。

### Task 2: 将页面发现与抓取流程迁入共享核心

**Files:**
- Modify: `tests/test_scraper_core.py`
- Modify: `scripts/scraper_core.py`

- [ ] **Step 1: 写失败测试，覆盖可复用的页面发现与正文解析辅助函数**

在 `tests/test_scraper_core.py` 追加以下测试，要求把“网络抓取”与“HTML 解析”拆开，便于无网络测试：

```python
class DiscoveryTests(unittest.TestCase):
    def test_discover_pages_from_html_uses_sidebar_and_category_titles(self) -> None:
        html = """
        <nav class="sidebar">
          <ul class="top-level">
            <li><a href="/docs/en">Intro</a></li>
            <li>
              <details>
                <summary>Usage</summary>
                <a href="/docs/en/cli">CLI</a>
                <a href="/docs/en/web">Web</a>
              </details>
            </li>
          </ul>
        </nav>
        """
        config = ScraperConfig(
            base_url="https://opencode.ai/docs/en",
            docs_prefix="/docs/en/",
            output_dir=Path("docs/en/opencode"),
            readme_title="OpenCode English Docs (Offline)",
            readme_source_label="Source",
            default_section_title="Getting Started",
            request_delay=0.0,
            user_agent="test-agent",
        )

        pages = discover_pages_from_html(html, config)

        self.assertEqual([page.slug for page in pages], ["", "cli", "web"])
        self.assertEqual([page.filename for page in pages], ["01-Intro.md", "01-CLI.md", "02-Web.md"])
        self.assertEqual([page.category for page in pages], ["", "Usage", "Usage"])

    def test_extract_content_keeps_article_and_removes_layout_noise(self) -> None:
        html = """
        <html>
          <body>
            <nav>sidebar</nav>
            <article>
              <h1>Intro</h1>
              <p>Hello docs</p>
              <footer>article footer</footer>
            </article>
            <footer>page footer</footer>
          </body>
        </html>
        """

        content = extract_content(html)

        self.assertIn("<article>", content)
        self.assertIn("Hello docs", content)
        self.assertNotIn("sidebar", content)
        self.assertNotIn("page footer", content)
        self.assertNotIn("article footer", content)
```

- [ ] **Step 2: 运行测试，确认因为新函数不存在或行为未满足而失败**

Run: `uv run -m unittest discover -s tests -p "test_scraper_core.py" -v`

Expected: FAIL，报 `NameError`、`ImportError` 或断言失败，说明 `discover_pages_from_html()` / `extract_content()` 仍未完成。

- [ ] **Step 3: 从旧脚本迁移核心流程到 `scripts/scraper_core.py`**

按现有 `scripts/scrape_opencode_docs.py` 的行为迁移以下函数，并把语言差异收口到 `ScraperConfig`：

- `fetch_html(url: str, config: ScraperConfig) -> str | None`
- `discover_pages_from_html(html: str, config: ScraperConfig) -> list[Page]`
- `discover_pages(config: ScraperConfig) -> list[Page]`
- `_normalize_code_blocks(soup_node) -> None`
- `extract_content(html: str) -> str`
- `_detect_code_lang(el) -> str | None`
- `html_to_markdown(html_fragment: str) -> str`
- `_ensure_title(text: str, title: str) -> str`
- `write_page(page: Page, content: str, config: ScraperConfig) -> Path`
- `scrape_all(config: ScraperConfig, update_only: bool = False) -> None`

迁移时保留旧脚本已有行为：

- 侧边栏页面发现方式不变
- 分类内文件名仍按序号生成
- `--update` 仍然跳过已存在文件
- 全量模式仍然只清理当前 `config.output_dir`
- 请求头与请求间隔来自 `config.user_agent` 和 `config.request_delay`

- [ ] **Step 4: 重新运行测试，确认共享核心通过**

Run: `uv run -m unittest discover -s tests -p "test_scraper_core.py" -v`

Expected: PASS，新增的页面发现与正文提取测试通过。

- [ ] **Step 5: 验证检查点**

人工检查 `scripts/scraper_core.py`，确认除配置值外不再出现写死的 `/docs/zh-cn/`、`docs/opencode` 或中文 README 文案。

### Task 3: 创建中英文入口脚本并移除旧入口

**Files:**
- Create: `tests/test_entrypoints.py`
- Create: `scripts/scrape_opencode_docs_zh.py`
- Create: `scripts/scrape_opencode_docs_en.py`
- Delete: `scripts/scrape_opencode_docs.py`

- [ ] **Step 1: 写失败测试，锁定中英文入口配置和调度行为**

```python
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.scrape_opencode_docs_en as en_entry
import scripts.scrape_opencode_docs_zh as zh_entry


class EntrypointTests(unittest.TestCase):
    def test_zh_config_points_to_zh_docs(self) -> None:
        self.assertEqual(zh_entry.CONFIG.base_url, "https://opencode.ai/docs/zh-cn")
        self.assertEqual(zh_entry.CONFIG.docs_prefix, "/docs/zh-cn/")
        self.assertEqual(zh_entry.CONFIG.output_dir, Path("docs/zh/opencode"))
        self.assertEqual(zh_entry.CONFIG.readme_title, "OpenCode 中文文档（离线版）")
        self.assertEqual(zh_entry.CONFIG.readme_source_label, "来源")
        self.assertEqual(zh_entry.CONFIG.default_section_title, "入门")

    def test_en_config_points_to_en_docs(self) -> None:
        self.assertEqual(en_entry.CONFIG.base_url, "https://opencode.ai/docs/en")
        self.assertEqual(en_entry.CONFIG.docs_prefix, "/docs/en/")
        self.assertEqual(en_entry.CONFIG.output_dir, Path("docs/en/opencode"))
        self.assertEqual(en_entry.CONFIG.readme_title, "OpenCode English Docs (Offline)")
        self.assertEqual(en_entry.CONFIG.readme_source_label, "Source")
        self.assertEqual(en_entry.CONFIG.default_section_title, "Getting Started")

    def test_en_main_passes_update_flag_to_scrape_all(self) -> None:
        with patch.object(en_entry, "scrape_all") as mock_scrape_all:
            en_entry.main(["--update"])
        mock_scrape_all.assert_called_once_with(en_entry.CONFIG, update_only=True)
```

- [ ] **Step 2: 运行测试，确认先失败**

Run: `uv run -m unittest discover -s tests -p "test_entrypoints.py" -v`

Expected: FAIL，报入口模块不存在或 `CONFIG` / `main()` 尚未实现。

- [ ] **Step 3: 编写两个入口脚本，并删除旧的单文件入口**

两个入口脚本都遵循相同结构：

```python
import argparse
from pathlib import Path

from scripts.scraper_core import ScraperConfig, scrape_all

CONFIG = ScraperConfig(
    base_url="https://opencode.ai/docs/en",
    docs_prefix="/docs/en/",
    output_dir=Path("docs/en/opencode"),
    readme_title="OpenCode English Docs (Offline)",
    readme_source_label="Source",
    default_section_title="Getting Started",
    request_delay=1.0,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Scrape OpenCode English documentation")
    parser.add_argument("--update", action="store_true", help="Skip files that already exist")
    args = parser.parse_args(argv)
    scrape_all(CONFIG, update_only=args.update)
```

中文入口使用对应的中文配置与中文描述文案；然后删除旧文件 `scripts/scrape_opencode_docs.py`，避免入口名混乱。

中文入口的配置值必须逐项固定为：

```python
CONFIG = ScraperConfig(
    base_url="https://opencode.ai/docs/zh-cn",
    docs_prefix="/docs/zh-cn/",
    output_dir=Path("docs/zh/opencode"),
    readme_title="OpenCode 中文文档（离线版）",
    readme_source_label="来源",
    default_section_title="入门",
    request_delay=1.0,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
)
```

中文 CLI 文案也固定为：

- `description="抓取 OpenCode 中文文档"`
- `help="增量更新模式，跳过已存在的文件"`

- [ ] **Step 4: 重新运行入口测试，确认通过**

Run: `uv run -m unittest discover -s tests -p "test_entrypoints.py" -v`

Expected: PASS，配置与 `main(argv=None)` 调度行为正确。

- [ ] **Step 5: 验证检查点**

确认仓库中只保留 `scripts/scrape_opencode_docs_zh.py` 与 `scripts/scrape_opencode_docs_en.py` 作为正式入口，旧的 `scripts/scrape_opencode_docs.py` 已被移除。

### Task 4: 完成联调与脚本级验证

**Files:**
- Modify: `docs/en/opencode/**`（脚本运行后生成）
- Modify: `docs/zh/opencode/**`（仅在需要验证中文时生成或更新）

- [ ] **Step 1: 运行全部自动化测试**

Run: `uv run -m unittest discover -s tests -p "test_*.py" -v`

Expected: PASS，`tests/test_scraper_core.py` 与 `tests/test_entrypoints.py` 全部通过。

- [ ] **Step 2: 运行英文入口做一次抓取验证**

Run: `uv run scripts/scrape_opencode_docs_en.py --update`

Expected: 终端输出页面发现与抓取进度，最终生成或更新 `docs/en/opencode/README.md` 且统计信息中失败数为 0。

- [ ] **Step 3: 抽查英文 README 与链接**

检查以下内容：

- `docs/en/opencode/README.md` 存在
- 标题为英文
- 来源标签为 `Source`
- 顶层分组标题为 `Getting Started`
- 分类内链接路径指向相对 Markdown 文件

- [ ] **Step 4: 可选地运行中文入口做回归验证**

Run: `uv run scripts/scrape_opencode_docs_zh.py --update`

Expected: 中文 README 仍落在 `docs/zh/opencode/README.md`，抓取流程无回归。

- [ ] **Step 5: 验证检查点**

记录最终结果：测试是否通过、英文 README 是否生成、是否发现中文回归。如果任何命令失败，先修复再继续，不要跳过验证。

- [ ] **Step 6: 搜索并确认仓库内没有残留旧入口引用**

优先使用：

Run: `git grep -n "scrape_opencode_docs\\.py"`

如果当前环境没有可用的 git grep 结果展示，再退回到 PowerShell：

Run: `Get-ChildItem -Recurse -File | Select-String -Pattern "scrape_opencode_docs\\.py"`

Expected: 没有命中；如果有命中，只更新仍然面向用户或开发者的说明文本，不增加额外功能改动。
