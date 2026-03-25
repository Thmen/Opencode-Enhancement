import re
import shutil
import sys
import time
from urllib.parse import urlparse
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


@dataclass(frozen=True)
class ScraperConfig:
    base_url: str
    docs_prefix: str
    output_dir: Path
    readme_title: str
    readme_source_label: str
    default_section_title: str
    home_label: str
    request_delay: float
    user_agent: str


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    category: str
    filename: str


def _make_filename(index: int, title: str) -> str:
    safe = re.sub(r"[\\/:*?\"<>|\s]+", "", title)
    return f"{index:02d}-{safe}.md"


def _slug_from_href(href: str, docs_prefix: str) -> str:
    path = href.rstrip("/")
    prefix_root = docs_prefix.rstrip("/")
    if path in {prefix_root, "/docs"}:
        return ""
    if path.startswith(docs_prefix):
        return path[len(docs_prefix):].strip("/")
    if path.startswith("/docs/"):
        remainder = path[len("/docs/"):].lstrip("/")
        if "/" in remainder:
            return remainder.split("/", 1)[1]
        return remainder
    return path.rsplit("/", 1)[-1]


def postprocess(text: str, page: Page, slug_map: dict[str, Page], config: ScraperConfig) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"(#{1,6})\s*\[([^\]]+)\]\(#[^)]*\)", r"\1 \2", text)
    text = re.sub(r"\[([^\]]+)\]\(#tab-panel-\d+\)", r"\1", text)

    docs_prefix = re.escape(config.docs_prefix.rstrip("/"))

    def _replace_link(match: re.Match[str]) -> str:
        link_text = match.group(1)
        raw_url = match.group(2)
        parsed = urlparse(raw_url)
        slug = _slug_from_href(parsed.path, config.docs_prefix)
        target = slug_map.get(slug)
        if target is None:
            return match.group(0)

        anchor = f"#{parsed.fragment}" if parsed.fragment else ""
        if target.category == page.category:
            return f"[{link_text}]({target.filename}{anchor})"
        if target.category:
            prefix = f"../{target.category}/" if page.category else f"{target.category}/"
        else:
            prefix = "../" if page.category else ""
        return f"[{link_text}]({prefix}{target.filename}{anchor})"

    text = re.sub(
        rf"\[([^\]]+)\]\(((?:https://opencode\.ai)?(?:{docs_prefix}|/docs)[^)]*)\)",
        _replace_link,
        text,
    )
    return text.strip() + "\n"


def fetch_html(url: str, config: ScraperConfig) -> str | None:
    try:
        resp = requests.get(url, headers={"User-Agent": config.user_agent}, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text
    except requests.RequestException as exc:
        print(f"  [错误] 请求失败: {exc}")
        return None


def discover_pages_from_html(html: str, config: ScraperConfig) -> list[Page]:
    soup = BeautifulSoup(html, "html.parser")
    sidebar = soup.select_one("nav.sidebar")
    if sidebar is None:
        raise ValueError("未找到侧边栏导航 (nav.sidebar)")

    top_ul = sidebar.select_one("ul.top-level") or sidebar.select_one("ul")
    if top_ul is None:
        raise ValueError("未找到侧边栏列表 (ul)")

    pages: list[Page] = []
    cat_counter: dict[str, int] = {}

    def _add_page(title: str, href: str, category: str) -> None:
        slug = _slug_from_href(href, config.docs_prefix)
        index = cat_counter.get(category, 0) + 1
        cat_counter[category] = index
        filename = _make_filename(index, title)
        pages.append(Page(slug=slug, title=title, category=category, filename=filename))

    for li in top_ul.find_all("li", recursive=False):
        details = li.find("details", recursive=False)
        if details:
            summary = details.find("summary")
            category = summary.get_text(strip=True) if summary else ""
            for sub_link in details.select("a[href]"):
                href = sub_link.get("href", "")
                if not href.startswith("/docs"):
                    continue
                title = sub_link.get_text(strip=True)
                _add_page(title, href, category)
        else:
            link = li.find("a", recursive=False)
            if link is None:
                continue
            href = link.get("href", "")
            if not href.startswith("/docs"):
                continue
            title = link.get_text(strip=True)
            _add_page(title, href, "")

    return pages


def discover_pages(config: ScraperConfig) -> list[Page]:
    print("[发现] 正在从侧边栏抓取页面清单...")
    html = fetch_html(config.base_url, config)
    if html is None:
        print("[错误] 无法获取首页，无法发现页面清单")
        sys.exit(1)

    try:
        pages = discover_pages_from_html(html, config)
    except ValueError as exc:
        print(f"[错误] {exc}")
        sys.exit(1)

    print(f"[发现] 共找到 {len(pages)} 个页面，分为 {len(set(page.category for page in pages))} 个分类")
    for page in pages:
        cat_label = f"  [{page.category}]" if page.category else ""
        print(f"       {page.filename:30s}{cat_label}")
    return pages


def _normalize_code_blocks(soup_node) -> None:
    from bs4 import NavigableString, Tag

    for pre in list(soup_node.select("pre")):
        lang = pre.get("data-language", "")
        ec_lines = pre.select("div.ec-line")
        if not ec_lines:
            continue

        code_text = "\n".join(line.get_text() for line in ec_lines)
        pre.clear()
        if lang:
            pre["data-language"] = lang
        code_tag = Tag(name="code")
        code_tag.append(NavigableString(code_text))
        pre.append(code_tag)


def extract_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    content = soup.select_one("article") or soup.select_one("main")
    if content is None:
        content = soup.select_one(".content-container, .page-content, [class*='content']")
    if content is None:
        content = soup.body or soup

    for selector in [
        "nav",
        "header",
        "footer",
        ".sidebar",
        ".toc",
        ".breadcrumb",
        "[class*='nav']",
        "[class*='footer']",
        "[class*='header']",
        "script",
        "style",
    ]:
        for tag in content.select(selector):
            tag.decompose()

    _normalize_code_blocks(content)
    return str(content)


def _detect_code_lang(el) -> str | None:
    if lang := el.get("data-language"):
        return lang

    for cls in el.get("class", []):
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


def html_to_markdown(html_fragment: str) -> str:
    return md(
        html_fragment,
        heading_style="ATX",
        code_language_callback=_detect_code_lang,
        strip=["img", "svg", "picture", "source", "video", "audio", "iframe"],
    )


def _ensure_title(text: str, title: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("# "):
        return text
    return f"# {title}\n\n{text}"


def build_breadcrumb(page: Page, config: ScraperConfig) -> str:
    if page.category:
        return f"[{config.home_label}](../README.md) / [{page.category}](README.md) / {page.title}\n\n"
    return f"[{config.home_label}](README.md) / {page.title}\n\n"


def prepend_breadcrumb(content: str, page: Page, config: ScraperConfig) -> str:
    return f"{build_breadcrumb(page, config)}{content}"


def generate_category_indexes(pages: list[Page], config: ScraperConfig) -> None:
    categories: dict[str, list[Page]] = {}
    for page in pages:
        if not page.category:
            continue
        categories.setdefault(page.category, []).append(page)

    for category, category_pages in categories.items():
        out_dir = config.output_dir / category
        out_dir.mkdir(parents=True, exist_ok=True)
        lines = [
            f"[{config.home_label}](../README.md) / {category}",
            "",
            f"# {category}",
            "",
        ]
        for page in category_pages:
            lines.append(f"- [{page.title}]({page.filename})")
        readme = out_dir / "README.md"
        readme.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_page(page: Page, content: str, config: ScraperConfig) -> Path:
    out_dir = config.output_dir / page.category if page.category else config.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / page.filename
    content = prepend_breadcrumb(content, page, config)
    filepath.write_text(content, encoding="utf-8")
    return filepath


def generate_index(pages: list[Page], config: ScraperConfig) -> None:
    lines = [
        f"# {config.readme_title}\n",
        f"> {config.readme_source_label}: {config.base_url}\n",
        "",
    ]

    current_cat = None
    for page in pages:
        if page.category != current_cat:
            current_cat = page.category
            if current_cat:
                lines.append(f"\n## {current_cat}\n")
            else:
                lines.append(f"\n## {config.default_section_title}\n")

        link = f"{page.category}/{page.filename}" if page.category else page.filename
        lines.append(f"- [{page.title}]({link})")

    config.output_dir.mkdir(parents=True, exist_ok=True)
    readme = config.output_dir / "README.md"
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[索引] {readme}")


def scrape_all(config: ScraperConfig, update_only: bool = False) -> None:
    pages = discover_pages(config)
    if not pages:
        print("[错误] 未发现任何页面")
        sys.exit(1)

    slug_map = {page.slug: page for page in pages}

    if not update_only and config.output_dir.exists():
        shutil.rmtree(config.output_dir)
        print(f"[清理] 已删除 {config.output_dir}")

    config.output_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    skipped = 0
    failed = 0
    total = len(pages)

    for index, page in enumerate(pages, 1):
        out_path = config.output_dir / page.category / page.filename if page.category else config.output_dir / page.filename

        if update_only and out_path.exists():
            print(f"[{index}/{total}] 跳过 {page.title} (已存在)")
            skipped += 1
            continue

        url = f"{config.base_url}/{page.slug}" if page.slug else config.base_url
        print(f"[{index}/{total}] 抓取 {page.title}  ← {url}")

        html = fetch_html(url, config)
        if html is None:
            failed += 1
            continue

        content_html = extract_content(html)
        markdown = html_to_markdown(content_html)
        markdown = _ensure_title(markdown, page.title)
        markdown = postprocess(markdown, page, slug_map, config)
        filepath = write_page(page, markdown, config)

        print(f"         → {filepath}")
        success += 1

        if index < total:
            time.sleep(config.request_delay)

    generate_index(pages, config)
    generate_category_indexes(pages, config)
    print(f"\n完成: 成功 {success}, 跳过 {skipped}, 失败 {failed}, 共 {total} 页")
