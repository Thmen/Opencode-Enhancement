# Offline Doc Breadcrumb Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为离线中英文文档增加页首面包屑导航和分类目录 `README.md`，让用户能从正文页稳定返回首页和上级分类。

**Architecture:** 在 `scripts/scraper_core.py` 中扩展共享生成逻辑，而不是改入口脚本。通过给 `ScraperConfig` 增加首页文案、给正文页增加统一的面包屑注入、并为每个分类目录生成独立 `README.md`，实现中英文一致的导航结构。测试仍使用标准库 `unittest`，先锁定导航文本与文件输出，再补最小实现。

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4`, `markdownify`, 标准库 `unittest`, `uv`

---

**Implementation Notes**

- 本计划遵循 TDD：先写失败测试，再补最小实现。
- 本仓库当前流程要求只有在用户明确要求时才创建 git commit，因此本计划把每个任务的最后一步定义为“验证检查点”，不包含自动提交。
- 统一从包含 `pyproject.toml` 的仓库根目录运行命令。
- 之前已获用户同意直接在主干实现，本次沿用同一工作方式，不再切换到 worktree。

## File Structure

### Modify

- `scripts/scraper_core.py`
- `scripts/scrape_opencode_docs_zh.py`
- `scripts/scrape_opencode_docs_en.py`
- `tests/test_scraper_core.py`
- `tests/test_entrypoints.py`

### Generated Output

- `docs/zh/opencode/**`
- `docs/en/opencode/**`

### Responsibilities

- `scripts/scraper_core.py`
  - 为 `ScraperConfig` 增加首页文案配置
  - 生成正文页面包屑
  - 生成分类目录 `README.md`
  - 控制根目录首页、分类首页、正文页三类文件的生成边界
- `scripts/scrape_opencode_docs_zh.py`
  - 为中文配置新增 `home_label="首页"`
- `scripts/scrape_opencode_docs_en.py`
  - 为英文配置新增 `home_label="Home"`
- `tests/test_scraper_core.py`
  - 覆盖顶层页面包屑、分类页面包屑、分类目录 `README.md`、导航插入位置
- `tests/test_entrypoints.py`
  - 覆盖中英文入口的 `home_label` 配置

### Task 1: 为导航结构写失败测试

**Files:**
- Modify: `tests/test_scraper_core.py`
- Modify: `tests/test_entrypoints.py`

- [ ] **Step 1: 为共享核心补失败测试，锁定面包屑与分类 README 行为**

在 `tests/test_scraper_core.py` 中追加以下测试：

```python
class NavigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ScraperConfig(
            base_url="https://opencode.ai/docs/en",
            docs_prefix="/docs/en/",
            output_dir=Path("docs/en/opencode"),
            readme_title="OpenCode English Docs (Offline)",
            readme_source_label="Source",
            default_section_title="Getting Started",
            home_label="Home",
            request_delay=0.0,
            user_agent="test-agent",
        )

    def test_build_breadcrumb_for_top_level_page(self) -> None:
        page = Page(slug="", title="Intro", category="", filename="01-Intro.md")
        self.assertEqual(
            build_breadcrumb(page, self.config),
            "[Home](README.md) / Intro\n\n",
        )

    def test_build_breadcrumb_for_categorized_page(self) -> None:
        page = Page(slug="share", title="Share", category="Usage", filename="07-Share.md")
        self.assertEqual(
            build_breadcrumb(page, self.config),
            "[Home](../README.md) / [Usage](README.md) / Share\n\n",
        )

    def test_prepend_breadcrumb_places_navigation_before_title(self) -> None:
        page = Page(slug="share", title="Share", category="Usage", filename="07-Share.md")
        content = "# Share\n\nBody text.\n"
        expected = "[Home](../README.md) / [Usage](README.md) / Share\n\n# Share\n\nBody text.\n"
        self.assertEqual(prepend_breadcrumb(content, page, self.config), expected)

    def test_generate_category_indexes_writes_category_readme(self) -> None:
        pages = [
            Page(slug="cli", title="CLI", category="Usage", filename="03-CLI.md"),
            Page(slug="share", title="Share", category="Usage", filename="07-Share.md"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            config = replace(self.config, output_dir=Path(tmp))
            generate_category_indexes(pages, config)
            readme = Path(tmp) / "Usage" / "README.md"
            content = readme.read_text(encoding="utf-8")
        self.assertIn("[Home](../README.md) / Usage", content)
        self.assertIn("# Usage", content)
        self.assertIn("- [CLI](03-CLI.md)", content)
        self.assertIn("- [Share](07-Share.md)", content)
```

同步在 `tests/test_entrypoints.py` 中追加：

```python
class EntrypointTests(unittest.TestCase):
    ...

    def test_zh_config_has_home_label(self) -> None:
        self.assertEqual(zh_entry.CONFIG.home_label, "首页")

    def test_en_config_has_home_label(self) -> None:
        self.assertEqual(en_entry.CONFIG.home_label, "Home")
```

注意：这两个 `def` 必须作为现有 `EntrypointTests` 类的方法追加，保持与其它 `test_*` 方法同级缩进。

同时，把 `tests/test_scraper_core.py` 里现有的所有 `ScraperConfig(...)` 构造一并补上：

```python
home_label="Home",
```

至少包括：

- `CoreHelperTests.setUp(...)`
- `DiscoveryTests.test_discover_pages_from_html_uses_sidebar_and_category_titles(...)`

- [ ] **Step 2: 运行测试，确认先失败**

Run: `uv run -m unittest discover -s tests -p "test_*.py" -v`

Expected: FAIL，且失败应直接指向导航能力尚未实现。常见失败形式包括：

- `ImportError`：`build_breadcrumb` / `prepend_breadcrumb` / `generate_category_indexes` 尚不存在
- `AttributeError`：入口配置还没有 `CONFIG.home_label`
- `TypeError`：`ScraperConfig(...)` 传入了尚未声明的 `home_label`

- [ ] **Step 3: 验证检查点**

确认失败原因确实指向“导航能力尚未实现”，而不是测试代码拼写或导入错误。

### Task 2: 在共享核心中实现面包屑与分类 README 生成

**Files:**
- Modify: `scripts/scraper_core.py`
- Modify: `scripts/scrape_opencode_docs_zh.py`
- Modify: `scripts/scrape_opencode_docs_en.py`
- Modify: `tests/test_scraper_core.py`

- [ ] **Step 1: 为导航扩展 `ScraperConfig` 最小结构**

在 `scripts/scraper_core.py` 的 `ScraperConfig` 中新增：

```python
home_label: str
```

并在同一个变更批次内，立刻补齐当前仓库里所有 `ScraperConfig(...)` 调用处，避免测试在中途因为 dataclass 参数不匹配而导入失败。至少包括：

- `scripts/scrape_opencode_docs_zh.py`
- `scripts/scrape_opencode_docs_en.py`
- `tests/test_scraper_core.py`

保持现有字段顺序尽量稳定，避免入口配置和测试大面积漂移。

- [ ] **Step 2: 实现最小导航辅助函数**

在 `scripts/scraper_core.py` 中新增以下函数：

```python
def build_breadcrumb(page: Page, config: ScraperConfig) -> str:
    ...

def prepend_breadcrumb(content: str, page: Page, config: ScraperConfig) -> str:
    ...

def generate_category_indexes(pages: list[Page], config: ScraperConfig) -> None:
    ...
```

实现规则必须与 spec 一致：

- 顶层正文页：`[Home](README.md) / Title`
- 分类正文页：`[Home](../README.md) / [Category](README.md) / Title`
- 分类目录 `README.md` 顶部：`[Home](../README.md) / Category`
- 根目录 `README.md` 不加面包屑
- 分类目录 `README.md` 只由 `generate_category_indexes(...)` 整文件生成
- 正文页只由 `write_page(...)` 调用 `prepend_breadcrumb(...)` 注入一次

- [ ] **Step 3: 把正文页写入流程接上导航**

只在 `write_page(...)` 中做这件事：

```python
content = prepend_breadcrumb(content, page, config)
```

不要在 `postprocess(...)` 或 `scrape_all(...)` 里重复拼接导航，避免职责混乱。

- [ ] **Step 4: 把分类目录 README 接入全流程**

在 `scrape_all(...)` 中，在 `generate_index(pages, config)` 之后调用：

```python
generate_category_indexes(pages, config)
```

要求：

- 全量模式下分类目录 `README.md` 随输出目录一起重建
- 增量模式下即使正文页被跳过，分类目录 `README.md` 仍按当前页面清单重写

- [ ] **Step 5: 运行测试，确认通过**

Run: `uv run -m unittest discover -s tests -p "test_*.py" -v`

Expected: PASS，新增导航测试与现有抓取测试全部通过。

- [ ] **Step 6: 验证检查点**

人工检查 `scripts/scraper_core.py`，确认三类文件职责边界成立：

- 根目录 `README.md` 仅 `generate_index(...)`
- 分类目录 `README.md` 仅 `generate_category_indexes(...)`
- 正文页导航仅 `write_page(...)`

### Task 3: 更新中英文入口配置

**Files:**
- Modify: `scripts/scrape_opencode_docs_zh.py`
- Modify: `scripts/scrape_opencode_docs_en.py`
- Modify: `tests/test_entrypoints.py`

- [ ] **Step 1: 复核两个入口的导航配置值**

中文入口：

```python
home_label="首页",
```

英文入口：

```python
home_label="Home",
```

如果 Task 2 Step 1 中尚未补齐，这一步完成补齐；如果已补齐，这一步只核对字段值和顺序。

- [ ] **Step 2: 运行入口与全量测试，确认通过**

Run: `uv run -m unittest discover -s tests -p "test_*.py" -v`

Expected: PASS，入口配置测试和脚本路径执行测试保持通过。

- [ ] **Step 3: 验证检查点**

确认中英文入口除新增 `home_label` 外，没有引入其他行为变化。

### Task 4: 运行脚本级验证并全量重建离线文档

**Files:**
- Modify: `docs/zh/opencode/**`
- Modify: `docs/en/opencode/**`

- [ ] **Step 1: 全量重建英文离线文档**

Run: `uv run scripts/scrape_opencode_docs_en.py`

Expected: 成功抓取全部英文页面，生成 `docs/en/opencode/README.md`、`docs/en/opencode/Usage/README.md`、`docs/en/opencode/Configure/README.md`、`docs/en/opencode/Develop/README.md`。

- [ ] **Step 2: 全量重建中文离线文档**

Run: `uv run scripts/scrape_opencode_docs_zh.py`

Expected: 成功抓取全部中文页面，生成 `docs/zh/opencode/README.md`、`docs/zh/opencode/使用/README.md`、`docs/zh/opencode/配置/README.md`、`docs/zh/opencode/开发/README.md`。

- [ ] **Step 3: 抽查英文导航样例**

检查：

- `docs/en/opencode/01-Intro.md` 顶部为 `[Home](README.md) / Intro`
- `docs/en/opencode/Usage/07-Share.md` 顶部为 `[Home](../README.md) / [Usage](README.md) / Share`
- `docs/en/opencode/Usage/README.md` 存在并列出本分类页面

- [ ] **Step 4: 抽查中文导航样例**

检查：

- `docs/zh/opencode/01-简介.md` 顶部为 `[首页](README.md) / 简介`
- `docs/zh/opencode/使用/07-分享.md` 顶部为 `[首页](../README.md) / [使用](README.md) / 分享`
- `docs/zh/opencode/使用/README.md` 存在并列出本分类页面

- [ ] **Step 5: 检查没有重复导航**

Run:

```powershell
$script = @'
from pathlib import Path

checks = [
    (Path("docs/zh/opencode"), "[首页]("),
    (Path("docs/en/opencode"), "[Home]("),
]
errors = []

for root, prefix in checks:
    for path in root.rglob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        first = next((line for line in lines if line.strip()), "")
        matches = sum(1 for line in lines[:5] if line.startswith(prefix))
        if path == root / "README.md":
            if matches:
                errors.append(f"root README has breadcrumb: {path}")
        else:
            if not first.startswith(prefix):
                errors.append(f"missing breadcrumb: {path}")
            if matches != 1:
                errors.append(f"duplicate breadcrumb: {path}")

print("breadcrumb check passed" if not errors else "\n".join(errors))
raise SystemExit(1 if errors else 0)
'@
uv run python -c $script
```

Expected: 输出 `breadcrumb check passed`，且退出码为 0。这样能覆盖所有非根目录 Markdown 文件，而不只是一两个样例页。

- [ ] **Step 6: 验证检查点**

记录最终结果：测试通过、英文和中文全量重建通过、分类目录 `README.md` 已生成、样例页能回到首页和分类首页。
