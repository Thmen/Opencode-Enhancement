import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class ScraperConfig:
    docs_base_url: str
    llms_index_url: str
    lang: str
    output_dir: Path
    readme_title: str
    readme_source_label: str
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


def _extract_slug_from_path(path: str) -> str:
    normalized = path.strip().rstrip("/")
    if not normalized:
        return "overview"

    segments = [segment for segment in normalized.split("/") if segment]
    if segments and segments[0] == "docs":
        segments = segments[1:]
    if segments and segments[0] in {"en", "zh-CN"}:
        segments = segments[1:]
    if not segments:
        return "overview"

    slug = "/".join(segments)
    return slug[:-3] if slug.endswith(".md") else slug


def parse_llms_index(text: str) -> list[dict[str, str]]:
    pattern = re.compile(r"^- \[(?P<title>[^\]]+)\]\((?P<url>https://code\.claude\.com/docs/en/(?P<slug>[^)#]+)\.md)\):", re.MULTILINE)
    pages: list[dict[str, str]] = []
    for match in pattern.finditer(text):
        pages.append(
            {
                "slug": match.group("slug"),
                "title": match.group("title"),
                "url": match.group("url"),
            }
        )
    return pages


def parse_sidebar_groups(html: str, lang: str) -> list[dict[str, object]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    prefix = f"/docs/{lang}/"
    groups: list[dict[str, object]] = []

    for header in soup.select("div.sidebar-group-header"):
        heading = header.select_one("h5")
        if heading is None:
            continue
        category = heading.get_text(" ", strip=True)
        group = header.find_next_sibling("ul")
        if group is None or "sidebar-group" not in (group.get("class") or []):
            continue

        slugs: list[str] = []
        for link in group.select("a[href]"):
            href = link.get("href", "")
            if not href.startswith(prefix):
                continue
            slug = _extract_slug_from_path(href)
            if slug not in slugs:
                slugs.append(slug)

        if slugs:
            groups.append({"title": category, "slugs": slugs})

    return groups


def parse_sidebar_categories(html: str, lang: str) -> dict[str, str]:
    categories: dict[str, str] = {}
    for group in parse_sidebar_groups(html, lang):
        for slug in group["slugs"]:
            categories.setdefault(slug, group["title"])

    return categories


def clean_markdown(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")

    if lines and lines[0].strip() == "> ## Documentation Index":
        index = 1
        while index < len(lines) and lines[index].lstrip().startswith(">"):
            index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        lines = lines[index:]

    def _dedent_wrapper_line(line: str) -> str:
        return re.sub(r"^ {1,4}", "", line)

    def _callout_label(kind: str, title: str | None = None) -> str:
        suffix = f" ({title})" if title else ""
        return f"**{kind}{suffix}:**"

    def _replace_inline_callouts(line: str) -> str:
        def _repl(match: re.Match[str]) -> str:
            kind = match.group(1)
            attrs = match.group(2) or ""
            body = match.group(3).strip()
            title_match = re.search(r'title="([^"]+)"', attrs)
            title = title_match.group(1) if title_match else None
            prefix = _callout_label(kind, title)
            return f"{prefix} {body}" if body else prefix

        return re.sub(
            r"<(Tip|Note|Warning|Info|Danger|Callout)\b([^>]*)>(.*?)</\1>",
            _repl,
            line,
        )

    cleaned_lines: list[str] = []
    wrapper_depth = 0
    in_fence = False
    card_context: dict[str, object] | None = None

    for raw_line in lines:
        stripped = raw_line.strip()

        if card_context is not None and not in_fence:
            if stripped == "</Card>":
                title = str(card_context["title"])
                href = str(card_context["href"])
                body = " ".join(part for part in card_context["body"] if part)
                bullet = f"- [{title}]({href})"
                if body:
                    bullet += f": {body}"
                cleaned_lines.append(bullet)
                card_context = None
                continue

            line = _replace_inline_callouts(_dedent_wrapper_line(raw_line)).rstrip()
            if line:
                card_context["body"].append(line.strip())
            continue

        if not in_fence:
            if match := re.match(r"^<Frame\b([^>]*)>$", stripped):
                caption_match = re.search(r'caption="([^"]+)"', match.group(1) or "")
                if caption_match:
                    cleaned_lines.append(f"*{caption_match.group(1)}*")
                continue

            if stripped in {
                "<Tabs>",
                "</Tabs>",
                "<Steps>",
                "</Steps>",
                "<AccordionGroup>",
                "</AccordionGroup>",
                "<CardGroup>",
                "</CardGroup>",
                "<CodeGroup>",
                "</CodeGroup>",
                "</Frame>",
            } or stripped.startswith("<CardGroup"):
                continue

            if stripped.startswith("<Card "):
                title_match = re.search(r'title="([^"]+)"', stripped)
                href_match = re.search(r'href="([^"]+)"', stripped)
                if title_match and href_match:
                    card_context = {
                        "title": title_match.group(1),
                        "href": href_match.group(1),
                        "body": [],
                    }
                    continue

            if re.match(r"^<[A-Z][A-Za-z0-9]*\b.*?/\s*>$", stripped):
                continue

            if match := re.match(r'^<Tab\b[^>]*title="([^"]+)"[^>]*>$', stripped):
                cleaned_lines.append(f"#### {match.group(1)}")
                wrapper_depth += 1
                continue
            if stripped == "</Tab>":
                wrapper_depth = max(0, wrapper_depth - 1)
                continue

            if match := re.match(r'^<Step\b[^>]*title="([^"]+)"[^>]*>$', stripped):
                cleaned_lines.append(f"#### {match.group(1)}")
                wrapper_depth += 1
                continue
            if stripped == "</Step>":
                wrapper_depth = max(0, wrapper_depth - 1)
                continue

            if match := re.match(r'^<Accordion\b[^>]*title="([^"]+)"[^>]*>$', stripped):
                cleaned_lines.append(f"### {match.group(1)}")
                wrapper_depth += 1
                continue
            if stripped == "</Accordion>":
                wrapper_depth = max(0, wrapper_depth - 1)
                continue

            if match := re.match(r'^<Update\b[^>]*label="([^"]+)"(?:[^>]*description="([^"]+)")?[^>]*>$', stripped):
                label = match.group(1)
                description = match.group(2)
                suffix = f" ({description})" if description else ""
                cleaned_lines.append(f"### {label}{suffix}")
                wrapper_depth += 1
                continue
            if stripped == "</Update>":
                wrapper_depth = max(0, wrapper_depth - 1)
                continue

            if match := re.match(r'^<(Tip|Note|Warning|Info|Danger|Callout)\b([^>]*)>$', stripped):
                title_match = re.search(r'title="([^"]+)"', match.group(2) or "")
                title = title_match.group(1) if title_match else None
                cleaned_lines.append(_callout_label(match.group(1), title))
                wrapper_depth += 1
                continue
            if stripped in {"</Tip>", "</Note>", "</Warning>", "</Info>", "</Danger>", "</Callout>"}:
                wrapper_depth = max(0, wrapper_depth - 1)
                continue

        line = raw_line
        if wrapper_depth > 0 and not in_fence:
            line = _dedent_wrapper_line(line)

        if not in_fence:
            line = _replace_inline_callouts(line)

        if line.lstrip().startswith("```"):
            line = re.sub(r"(?:\s+theme=\{null\})+\s*$", "", line.rstrip())
            cleaned_lines.append(line)
            in_fence = not in_fence
            continue

        cleaned_lines.append(line.rstrip())

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip() + "\n"


def extract_title(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if match is None:
        raise ValueError("Markdown 缺少一级标题")
    return match.group(1).strip()


def build_breadcrumb(page: Page, config: ScraperConfig) -> str:
    if page.category:
        return f"[{config.home_label}](../README.md) / [{page.category}](README.md) / {page.title}\n\n"
    return f"[{config.home_label}](README.md) / {page.title}\n\n"


def prepend_breadcrumb(content: str, page: Page, config: ScraperConfig) -> str:
    return f"{build_breadcrumb(page, config)}{content}"


def generate_index(pages: list[Page], config: ScraperConfig, category_order: list[str] | None = None) -> None:
    lines = [
        f"# {config.readme_title}\n",
        f"> {config.readme_source_label}: {config.docs_base_url}/{config.lang}\n",
        "",
    ]

    grouped: dict[str, list[Page]] = {}
    ungrouped: list[Page] = []
    for page in pages:
        if page.category:
            grouped.setdefault(page.category, []).append(page)
        else:
            ungrouped.append(page)

    ordered_categories: list[str] = []
    if category_order:
        ordered_categories.extend([category for category in category_order if category in grouped])
    ordered_categories.extend(category for category in grouped if category not in ordered_categories)

    for category in ordered_categories:
        lines.append(f"\n## {category}\n")
        for page in grouped[category]:
            lines.append(f"- [{page.title}]({page.category}/{page.filename})")

    if ungrouped:
        heading = "Pages" if config.lang == "en" else "页面"
        lines.append(f"\n## {heading}\n")
        for page in ungrouped:
            lines.append(f"- [{page.title}]({page.filename})")

    config.output_dir.mkdir(parents=True, exist_ok=True)
    (config.output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_category_indexes(pages: list[Page], config: ScraperConfig) -> None:
    grouped: dict[str, list[Page]] = {}
    for page in pages:
        if not page.category:
            continue
        grouped.setdefault(page.category, []).append(page)

    for category, category_pages in grouped.items():
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
        (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def localize_links(text: str, page: Page, slug_map: dict[str, Page], config: ScraperConfig) -> str:
    def _replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        raw_url = match.group(2)
        parsed = urlparse(raw_url)
        if parsed.scheme and parsed.netloc and parsed.netloc != "code.claude.com":
            return match.group(0)
        if parsed.scheme in {"vscode", "cursor"}:
            return match.group(0)

        slug = _extract_slug_from_path(parsed.path)
        target = slug_map.get(slug)
        if target is None:
            return match.group(0)

        anchor = f"#{parsed.fragment}" if parsed.fragment else ""
        if target.category == page.category:
            return f"[{label}]({target.filename}{anchor})"
        if target.category:
            prefix = f"../{target.category}/" if page.category else f"{target.category}/"
        else:
            prefix = "../" if page.category else ""
        return f"[{label}]({prefix}{target.filename}{anchor})"

    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", _replace_link, text)


def fetch_text(url: str, config: ScraperConfig) -> str | None:
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": config.user_agent}, timeout=30)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            headers = getattr(resp, "headers", {}) or {}
            content_type = str(headers.get("content-type", "")).lower()
            looks_like_html = resp.text.lstrip().startswith("<!DOCTYPE html>") or resp.text.lstrip().startswith("<html")
            if url.endswith(".md") and ("html" in content_type or looks_like_html):
                print(f"  [跳过] Markdown 端点返回 HTML: {url}")
                return None
            return resp.text
        except requests.HTTPError as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            should_retry = status_code == 429 or (status_code is not None and status_code >= 500)
            if should_retry and attempt < max_attempts:
                wait_seconds = max(config.request_delay, 1.0) * attempt
                print(f"  [重试] {status_code}，{wait_seconds:.1f}s 后重试: {url}")
                time.sleep(wait_seconds)
                continue
            print(f"  [错误] 请求失败: {exc}")
            return None
        except requests.RequestException as exc:
            print(f"  [错误] 请求失败: {exc}")
            return None


def discover_source_pages(config: ScraperConfig) -> tuple[list[dict[str, str]], list[str]]:
    llms_text = fetch_text(config.llms_index_url, config)
    if llms_text is None:
        raise RuntimeError("无法获取 llms.txt")

    pages = parse_llms_index(llms_text)

    sidebar_html = fetch_text(f"{config.docs_base_url}/{config.lang}", config)
    if sidebar_html is None:
        raise RuntimeError(f"无法获取 {config.lang} 侧边栏页面")

    sidebar_groups = parse_sidebar_groups(sidebar_html, config.lang)
    categories = parse_sidebar_categories(sidebar_html, config.lang)
    merged: list[dict[str, str]] = []
    for page in pages:
        merged.append(
            {
                "slug": page["slug"],
                "source_title": page["title"],
                "category": categories.get(page["slug"], ""),
            }
        )
    return merged, [group["title"] for group in sidebar_groups]


def _build_pages(records: list[dict[str, str]], config: ScraperConfig) -> list[tuple[Page, str]]:
    fetched: list[dict[str, str]] = []
    total = len(records)
    reserved_counters: dict[str, int] = {}
    reserved_indices: list[int] = []

    for record in records:
        category = record["category"]
        next_index = reserved_counters.get(category, 0) + 1
        reserved_counters[category] = next_index
        reserved_indices.append(next_index)

    for index, (record, reserved_index) in enumerate(zip(records, reserved_indices, strict=False), 1):
        url = f"{config.docs_base_url}/{config.lang}/{record['slug']}.md"
        print(f"[{index}/{total}] 抓取 {record['slug']}  ← {url}")
        markdown = fetch_text(url, config)
        if markdown is None:
            continue
        cleaned = clean_markdown(markdown)
        try:
            title = extract_title(cleaned)
        except ValueError as exc:
            print(f"  [跳过] 标题解析失败: {record['slug']} ({exc})")
            continue
        fetched.append(
            {
                "slug": record["slug"],
                "title": title,
                "category": record["category"],
                "content": cleaned,
                "reserved_index": reserved_index,
            }
        )
        if index < total:
            time.sleep(config.request_delay)

    pages: list[tuple[Page, str]] = []
    for record in fetched:
        filename = _make_filename(int(record["reserved_index"]), record["title"])
        pages.append(
            (
                Page(
                    slug=record["slug"],
                    title=record["title"],
                    category=record["category"],
                    filename=filename,
                ),
                record["content"],
            )
        )
    return pages


def write_page(page: Page, content: str, config: ScraperConfig) -> Path:
    out_dir = config.output_dir / page.category if page.category else config.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / page.filename
    filepath.write_text(prepend_breadcrumb(content, page, config), encoding="utf-8")
    return filepath


def scrape_all(config: ScraperConfig, update_only: bool = False) -> None:
    records, category_order = discover_source_pages(config)
    if not update_only and config.output_dir.exists():
        shutil.rmtree(config.output_dir)
        print(f"[清理] 已删除 {config.output_dir}")
    config.output_dir.mkdir(parents=True, exist_ok=True)

    pages_with_content = _build_pages(records, config)
    pages = [page for page, _ in pages_with_content]
    slug_map = {page.slug: page for page in pages}

    for page, content in pages_with_content:
        localized = localize_links(content, page, slug_map, config)
        filepath = write_page(page, localized, config)
        print(f"         → {filepath}")

    generate_index(pages, config, category_order=category_order)
    generate_category_indexes(pages, config)
    print(f"\n完成: 成功 {len(pages)}, 失败 {len(records) - len(pages)}, 共 {len(records)} 页")
    if len(pages) != len(records):
        raise SystemExit(1)
