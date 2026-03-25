from dataclasses import replace
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from scripts.claudecode_scraper_core import (
    _build_pages,
    Page,
    ScraperConfig,
    build_breadcrumb,
    clean_markdown,
    extract_title,
    fetch_text,
    generate_category_indexes,
    generate_index,
    localize_links,
    parse_llms_index,
    parse_sidebar_categories,
    parse_sidebar_groups,
    prepend_breadcrumb,
)

SAMPLE_LLMS = """# Claude Code Docs

## Docs

- [Claude Code overview](https://code.claude.com/docs/en/overview.md): Claude Code is an agentic coding tool.
- [Quickstart](https://code.claude.com/docs/en/quickstart.md): Welcome to Claude Code!
- [Common workflows](https://code.claude.com/docs/en/common-workflows.md): Everyday tasks with Claude Code.
- [Platforms and integrations](https://code.claude.com/docs/en/platforms.md): Choose where to run Claude Code.
"""

SAMPLE_SIDEBAR_HTML = """
<div class="sidebar-group-header"><h5>Getting started</h5></div>
<ul class="sidebar-group">
  <li><a href="/docs/en/overview">Overview</a></li>
  <li><a href="/docs/en/quickstart">Quickstart</a></li>
</ul>
<div class="sidebar-group-header"><h5>Use Claude Code</h5></div>
<ul class="sidebar-group">
  <li><a href="/docs/en/common-workflows">Common workflows</a></li>
</ul>
<div class="sidebar-group-header"><h5>Platforms and integrations</h5></div>
<ul class="sidebar-group">
  <li><a href="/docs/en/platforms">Overview</a></li>
</ul>
"""

SAMPLE_MARKDOWN = """> ## Documentation Index
>
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Code overview

See [Quickstart](https://code.claude.com/en/quickstart) and [Platforms](https://code.claude.com/docs/en/platforms#connect-your-tools).
"""

SAMPLE_MARKDOWN_NO_BLANK_QUOTE = """> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Quickstart

Body text.
"""


class ClaudeCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ScraperConfig(
            docs_base_url="https://code.claude.com/docs",
            llms_index_url="https://code.claude.com/docs/llms.txt",
            lang="en",
            output_dir=Path("docs/en/claudecode"),
            readme_title="Claude Code English Docs (Offline)",
            readme_source_label="Source",
            home_label="Home",
            request_delay=0.0,
            user_agent="test-agent",
        )

    def test_parse_llms_index_extracts_ordered_slugs(self) -> None:
        pages = parse_llms_index(SAMPLE_LLMS)
        self.assertEqual([page["slug"] for page in pages], ["overview", "quickstart", "common-workflows", "platforms"])
        self.assertEqual([page["title"] for page in pages], ["Claude Code overview", "Quickstart", "Common workflows", "Platforms and integrations"])

    def test_parse_sidebar_categories_maps_slugs_to_groups(self) -> None:
        categories = parse_sidebar_categories(SAMPLE_SIDEBAR_HTML, lang="en")
        self.assertEqual(categories["overview"], "Getting started")
        self.assertEqual(categories["common-workflows"], "Use Claude Code")
        self.assertEqual(categories["platforms"], "Platforms and integrations")

    def test_parse_sidebar_groups_preserves_group_order(self) -> None:
        groups = parse_sidebar_groups(SAMPLE_SIDEBAR_HTML, lang="en")
        self.assertEqual([group["title"] for group in groups], ["Getting started", "Use Claude Code", "Platforms and integrations"])
        self.assertEqual(groups[0]["slugs"], ["overview", "quickstart"])
        self.assertEqual(groups[1]["slugs"], ["common-workflows"])

    def test_clean_markdown_removes_documentation_index_preamble(self) -> None:
        cleaned = clean_markdown(SAMPLE_MARKDOWN)
        self.assertNotIn("Documentation Index", cleaned)
        self.assertTrue(cleaned.startswith("# Claude Code overview"))

    def test_clean_markdown_removes_preamble_without_blank_quote_line(self) -> None:
        cleaned = clean_markdown(SAMPLE_MARKDOWN_NO_BLANK_QUOTE)
        self.assertEqual(cleaned, "# Quickstart\n\nBody text.\n")

    def test_extract_title_reads_first_h1(self) -> None:
        cleaned = clean_markdown(SAMPLE_MARKDOWN)
        self.assertEqual(extract_title(cleaned), "Claude Code overview")

    def test_localize_links_rewrites_site_urls_and_preserves_anchor(self) -> None:
        current = Page(slug="overview", title="Claude Code overview", category="Getting started", filename="01-ClaudeCodeoverview.md")
        quickstart = Page(slug="quickstart", title="Quickstart", category="Getting started", filename="02-Quickstart.md")
        platforms = Page(slug="platforms", title="Platforms and integrations", category="Platforms and integrations", filename="01-Platformsandintegrations.md")
        text = clean_markdown(SAMPLE_MARKDOWN)
        localized = localize_links(
            text,
            current,
            {"overview": current, "quickstart": quickstart, "platforms": platforms},
            self.config,
        )
        self.assertIn("[Quickstart](02-Quickstart.md)", localized)
        self.assertIn("[Platforms](../Platforms and integrations/01-Platformsandintegrations.md#connect-your-tools)", localized)

    def test_build_breadcrumb_for_top_level_page(self) -> None:
        page = Page(slug="overview", title="Claude Code overview", category="", filename="01-ClaudeCodeoverview.md")
        self.assertEqual(build_breadcrumb(page, self.config), "[Home](README.md) / Claude Code overview\n\n")

    def test_build_breadcrumb_for_categorized_page(self) -> None:
        page = Page(slug="quickstart", title="Quickstart", category="Getting started", filename="02-Quickstart.md")
        self.assertEqual(
            build_breadcrumb(page, self.config),
            "[Home](../README.md) / [Getting started](README.md) / Quickstart\n\n",
        )

    def test_prepend_breadcrumb_places_navigation_before_title(self) -> None:
        page = Page(slug="quickstart", title="Quickstart", category="Getting started", filename="02-Quickstart.md")
        content = "# Quickstart\n\nBody text.\n"
        expected = "[Home](../README.md) / [Getting started](README.md) / Quickstart\n\n# Quickstart\n\nBody text.\n"
        self.assertEqual(prepend_breadcrumb(content, page, self.config), expected)

    def test_generate_index_groups_pages_by_category(self) -> None:
        pages = [
            Page(slug="overview", title="Claude Code overview", category="", filename="01-ClaudeCodeoverview.md"),
            Page(slug="quickstart", title="Quickstart", category="Getting started", filename="02-Quickstart.md"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            config = replace(self.config, output_dir=Path(tmp))
            generate_index(pages, config)
            readme = Path(tmp) / "README.md"
            content = readme.read_text(encoding="utf-8")
        self.assertIn("# Claude Code English Docs (Offline)", content)
        self.assertIn("- [Claude Code overview](01-ClaudeCodeoverview.md)", content)
        self.assertIn("## Getting started", content)
        self.assertIn("- [Quickstart](Getting started/02-Quickstart.md)", content)

    def test_generate_index_aggregates_sections_in_sidebar_order(self) -> None:
        pages = [
            Page(slug="agent-teams", title="Agent teams", category="", filename="01-Agentteams.md"),
            Page(slug="best-practices", title="Best Practices", category="Use Claude Code", filename="01-BestPractices.md"),
            Page(slug="overview", title="Overview", category="Getting started", filename="01-Overview.md"),
            Page(slug="quickstart", title="Quickstart", category="Getting started", filename="02-Quickstart.md"),
            Page(slug="platforms", title="Platforms", category="Platforms and integrations", filename="01-Platforms.md"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            config = replace(self.config, output_dir=Path(tmp))
            generate_index(
                pages,
                config,
                category_order=["Getting started", "Use Claude Code", "Platforms and integrations"],
            )
            content = (Path(tmp) / "README.md").read_text(encoding="utf-8")
        self.assertLess(content.index("## Getting started"), content.index("## Use Claude Code"))
        self.assertEqual(content.count("## Pages"), 1)
        self.assertLess(content.index("## Platforms and integrations"), content.index("## Pages"))

    def test_generate_category_indexes_writes_category_readme(self) -> None:
        pages = [
            Page(slug="quickstart", title="Quickstart", category="Getting started", filename="02-Quickstart.md"),
            Page(slug="common-workflows", title="Common workflows", category="Use Claude Code", filename="01-Commonworkflows.md"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            config = replace(self.config, output_dir=Path(tmp))
            generate_category_indexes(pages, config)
            readme = Path(tmp) / "Getting started" / "README.md"
            content = readme.read_text(encoding="utf-8")
        self.assertIn("[Home](../README.md) / Getting started", content)
        self.assertIn("# Getting started", content)
        self.assertIn("- [Quickstart](02-Quickstart.md)", content)

    def test_fetch_text_retries_after_rate_limit(self) -> None:
        too_many = Mock()
        too_many.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=429))
        success = Mock()
        success.raise_for_status.return_value = None
        success.text = "# Quickstart\n"
        success.encoding = None

        with patch("scripts.claudecode_scraper_core.requests.get", side_effect=[too_many, success]) as mock_get:
            with patch("scripts.claudecode_scraper_core.time.sleep") as mock_sleep:
                text = fetch_text("https://code.claude.com/docs/zh-CN/quickstart.md", self.config)

        self.assertEqual(text, "# Quickstart\n")
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called()

    def test_fetch_text_skips_html_response_for_markdown_endpoint(self) -> None:
        html_response = Mock()
        html_response.raise_for_status.return_value = None
        html_response.headers = {"content-type": "text/html; charset=utf-8"}
        html_response.text = "<!DOCTYPE html><html><body>Not markdown</body></html>"
        html_response.encoding = None

        with patch("scripts.claudecode_scraper_core.requests.get", return_value=html_response):
            text = fetch_text("https://code.claude.com/docs/zh-CN/changelog.md", self.config)

        self.assertIsNone(text)

    def test_build_pages_skips_markdown_without_h1(self) -> None:
        records = [{"slug": "broken-page", "category": "Getting started"}]

        with patch("scripts.claudecode_scraper_core.fetch_text", return_value="Body only\n\nNo title here.\n"):
            with patch("scripts.claudecode_scraper_core.time.sleep"):
                pages = _build_pages(records, self.config)

        self.assertEqual(pages, [])


if __name__ == "__main__":
    unittest.main()
