"""
OpenCode 中文文档离线抓取工具

用法:
    uv run scrape_opencode_docs.py           # 全量重建
    uv run scrape_opencode_docs.py --update  # 增量更新（跳过已有文件）

输出目录: docs/opencode/
"""

import argparse
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

BASE_URL = "https://opencode.ai/docs/zh-cn"
OUTPUT_DIR = Path("docs/opencode")
REQUEST_DELAY = 1.0
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# 页面清单 — 从侧边栏动态抓取
# ---------------------------------------------------------------------------

DOCS_PREFIX = "/docs/zh-cn/"


@dataclass
class Page:
    slug: str       # URL 路径（空字符串表示首页）
    title: str      # 标题
    category: str   # 所属分类（空字符串表示顶层）
    filename: str   # 输出文件名


def _make_filename(index: int, title: str) -> str:
    """生成带序号的文件名，移除空格和文件系统非法字符。"""
    safe = re.sub(r"[\\/:*?\"<>|\s]+", "", title)
    return f"{index:02d}-{safe}.md"


def _slug_from_href(href: str) -> str:
    """从 href 提取 slug。/docs/zh-cn/config/ → config"""
    path = href.rstrip("/")
    if path.endswith("/zh-cn") or path == DOCS_PREFIX.rstrip("/"):
        return ""
    prefix = "/docs/zh-cn/"
    if path.startswith(prefix):
        return path[len(prefix):]
    prefix_no_lang = "/docs/"
    if path.startswith(prefix_no_lang):
        return path[len(prefix_no_lang):]
    return path.rsplit("/", 1)[-1]


def discover_pages() -> list[Page]:
    """从文档首页的侧边栏导航动态发现所有页面。"""
    print("[发现] 正在从侧边栏抓取页面清单...")
    html = fetch_html(BASE_URL)
    if html is None:
        print("[错误] 无法获取首页，无法发现页面清单")
        sys.exit(1)

    soup = BeautifulSoup(html, "html.parser")
    sidebar = soup.select_one("nav.sidebar")
    if sidebar is None:
        print("[错误] 未找到侧边栏导航 (nav.sidebar)")
        sys.exit(1)

    top_ul = sidebar.select_one("ul.top-level") or sidebar.select_one("ul")
    if top_ul is None:
        print("[错误] 未找到侧边栏列表 (ul)")
        sys.exit(1)

    pages: list[Page] = []
    cat_counter: dict[str, int] = {}  # category -> next index

    def _add_page(title: str, href: str, category: str) -> None:
        slug = _slug_from_href(href)
        idx = cat_counter.get(category, 0) + 1
        cat_counter[category] = idx
        filename = _make_filename(idx, title)
        pages.append(Page(slug=slug, title=title, category=category, filename=filename))

    for li in top_ul.find_all("li", recursive=False):
        details = li.find("details", recursive=False)
        if details:
            summary = details.find("summary")
            cat_name = summary.get_text(strip=True) if summary else ""
            for sub_link in details.select("a[href]"):
                href = sub_link.get("href", "")
                if not href.startswith("/docs"):
                    continue
                title = sub_link.get_text(strip=True)
                _add_page(title, href, cat_name)
        else:
            link = li.find("a", recursive=False)
            if link is None:
                continue
            href = link.get("href", "")
            if not href.startswith("/docs"):
                continue
            title = link.get_text(strip=True)
            _add_page(title, href, "")

    print(f"[发现] 共找到 {len(pages)} 个页面，分为 {len(set(p.category for p in pages))} 个分类")
    for p in pages:
        cat_label = f"  [{p.category}]" if p.category else ""
        print(f"       {p.filename:30s}{cat_label}")

    return pages

# ---------------------------------------------------------------------------
# Pipeline 阶段
# ---------------------------------------------------------------------------


def fetch_html(url: str) -> str | None:
    """HTTP 抓取，返回 HTML 文本，失败返回 None。"""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text
    except requests.RequestException as e:
        print(f"  [错误] 请求失败: {e}")
        return None


def extract_content(html: str) -> str:
    """从完整 HTML 中提取正文区域的 HTML 片段。"""
    soup = BeautifulSoup(html, "html.parser")

    content = soup.select_one("article") or soup.select_one("main")
    if content is None:
        content = soup.select_one(".content-container, .page-content, [class*='content']")
    if content is None:
        content = soup.body or soup

    for sel in ["nav", "header", "footer", ".sidebar", ".toc", ".breadcrumb",
                "[class*='nav']", "[class*='footer']", "[class*='header']",
                "script", "style"]:
        for tag in content.select(sel):
            tag.decompose()

    _normalize_code_blocks(content)
    return str(content)


def _normalize_code_blocks(soup_node) -> None:
    """将 <pre> 内的 ec-line div 结构还原为纯文本，保留缩进。"""
    from bs4 import NavigableString, Tag

    for pre in list(soup_node.select("pre")):
        lang = pre.get("data-language", "")
        ec_lines = pre.select("div.ec-line")
        if not ec_lines:
            continue
        text_lines = [line.get_text() for line in ec_lines]
        code_text = "\n".join(text_lines)

        pre.clear()
        if lang:
            pre["data-language"] = lang
        code_tag = Tag(name="code")
        code_tag.append(NavigableString(code_text))
        pre.append(code_tag)


def html_to_markdown(html_fragment: str) -> str:
    """将 HTML 片段转换为 Markdown。"""
    return md(
        html_fragment,
        heading_style="ATX",
        code_language_callback=_detect_code_lang,
        strip=["img", "svg", "picture", "source", "video", "audio", "iframe"],
    )


def _detect_code_lang(el) -> str | None:
    """从 <code>/<pre> 元素的 class 或 data-language 属性中提取语言标记。"""
    if lang := el.get("data-language"):
        return lang
    classes = el.get("class", [])
    for cls in classes:
        if cls.startswith("language-"):
            return cls.removeprefix("language-")
    parent = el.parent
    if parent and parent.name == "pre":
        if lang := parent.get("data-language"):
            return lang
        for cls in parent.get("class", []):
            if cls.startswith("language-"):
                return cls.removeprefix("language-")
    return None


def _ensure_title(text: str, title: str) -> str:
    """确保文档以正确的一级标题开头，避免重复。"""
    stripped = text.lstrip()
    if stripped.startswith("# "):
        return text
    return f"# {title}\n\n{text}"


def postprocess(text: str, page: Page, slug_map: dict[str, Page]) -> str:
    """后处理: 清理格式、转换站内链接。"""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)

    # 移除标题中的自引用锚点链接: ## [标题](#标题) → ## 标题
    text = re.sub(r"(#{1,6})\s*\[([^\]]+)\]\(#[^)]*\)", r"\1 \2", text)

    # 移除 tab-panel 引用链接: [npm](#tab-panel-112) → npm
    text = re.sub(r"\[([^\]]+)\]\(#tab-panel-\d+\)", r"\1", text)

    # 站内链接本地化
    def _replace_link(m: re.Match) -> str:
        link_text = m.group(1)
        slug = m.group(2)
        target = slug_map.get(slug)
        if target is None:
            return m.group(0)
        if target.category == page.category:
            return f"[{link_text}]({target.filename})"
        if target.category:
            prefix = f"../{target.category}/" if page.category else f"{target.category}/"
        else:
            prefix = "../" if page.category else ""
        return f"[{link_text}]({prefix}{target.filename})"

    text = re.sub(
        r"\[([^\]]+)\]\((?:https://opencode\.ai)?/docs/(?:zh-cn/)?([a-z0-9_-]*)\)",
        _replace_link,
        text,
    )

    text = text.strip() + "\n"
    return text


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------


def write_page(page: Page, content: str) -> Path:
    """将 Markdown 内容写入文件，返回文件路径。"""
    if page.category:
        out_dir = OUTPUT_DIR / page.category
    else:
        out_dir = OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / page.filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def generate_index(pages: list[Page]) -> None:
    """生成 README.md 目录索引。"""
    lines = [
        "# OpenCode 中文文档（离线版）\n",
        f"> 来源: {BASE_URL}\n",
        "",
    ]

    current_cat = None
    for p in pages:
        if p.category != current_cat:
            current_cat = p.category
            if current_cat:
                lines.append(f"\n## {current_cat}\n")
            else:
                lines.append("\n## 入门\n")

        if p.category:
            link = f"{p.category}/{p.filename}"
        else:
            link = p.filename
        lines.append(f"- [{p.title}]({link})")

    readme = OUTPUT_DIR / "README.md"
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[索引] {readme}")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def scrape_all(update_only: bool = False) -> None:
    pages = discover_pages()
    if not pages:
        print("[错误] 未发现任何页面")
        sys.exit(1)

    slug_map: dict[str, Page] = {p.slug: p for p in pages}

    if not update_only and OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        print(f"[清理] 已删除 {OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    success, skipped, failed = 0, 0, 0
    total = len(pages)

    for i, page in enumerate(pages, 1):
        out_path = (OUTPUT_DIR / page.category / page.filename
                    if page.category else OUTPUT_DIR / page.filename)

        if update_only and out_path.exists():
            print(f"[{i}/{total}] 跳过 {page.title} (已存在)")
            skipped += 1
            continue

        url = f"{BASE_URL}/{page.slug}" if page.slug else BASE_URL
        print(f"[{i}/{total}] 抓取 {page.title}  ← {url}")

        html = fetch_html(url)
        if html is None:
            failed += 1
            continue

        content_html = extract_content(html)
        markdown = html_to_markdown(content_html)
        markdown = _ensure_title(markdown, page.title)
        markdown = postprocess(markdown, page, slug_map)
        filepath = write_page(page, markdown)

        print(f"         → {filepath}")
        success += 1

        if i < total:
            time.sleep(REQUEST_DELAY)

    generate_index(pages)
    print(f"\n完成: 成功 {success}, 跳过 {skipped}, 失败 {failed}, 共 {total} 页")


def main():
    parser = argparse.ArgumentParser(description="抓取 OpenCode 中文文档")
    parser.add_argument("--update", action="store_true",
                        help="增量更新模式，跳过已存在的文件")
    args = parser.parse_args()
    scrape_all(update_only=args.update)


if __name__ == "__main__":
    main()
