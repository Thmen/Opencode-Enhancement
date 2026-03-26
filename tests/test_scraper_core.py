from dataclasses import replace
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.scraper_core import (
    Page,
    ScraperConfig,
    _slug_from_href,
    build_breadcrumb,
    discover_pages_from_html,
    extract_content,
    generate_category_indexes,
    generate_index,
    prepend_breadcrumb,
    postprocess,
    scrape_all,
)


class CoreHelperTests(unittest.TestCase):
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

    def test_slug_from_href_returns_empty_for_language_root(self) -> None:
        self.assertEqual(_slug_from_href("/docs/en/", self.config.docs_prefix), "")

    def test_slug_from_href_returns_empty_for_generic_docs_root(self) -> None:
        self.assertEqual(_slug_from_href("/docs/", self.config.docs_prefix), "")

    def test_slug_from_href_strips_language_prefix(self) -> None:
        self.assertEqual(_slug_from_href("/docs/en/config/", self.config.docs_prefix), "config")

    def test_postprocess_localizes_cross_category_links(self) -> None:
        page = Page(slug="intro", title="Intro", category="", filename="01-Intro.md")
        target = Page(slug="cli", title="CLI", category="Usage", filename="03-CLI.md")
        text = "[CLI](/docs/cli)"
        self.assertEqual(
            postprocess(text, page, {"cli": target}, self.config),
            "[CLI](Usage/03-CLI.md)\n",
        )

    def test_postprocess_preserves_anchor_for_generic_docs_links(self) -> None:
        page = Page(slug="sdk", title="SDK", category="Develop", filename="01-SDK.md")
        target = Page(slug="ecosystem", title="Ecosystem", category="Develop", filename="04-Ecosystem.md")
        text = "[projects](/docs/ecosystem#projects)"
        self.assertEqual(
            postprocess(text, page, {"ecosystem": target}, self.config),
            "[projects](04-Ecosystem.md#projects)\n",
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


class DiscoveryTests(unittest.TestCase):
    def test_discover_pages_from_html_uses_sidebar_and_category_titles(self) -> None:
        html = """
        <nav class="sidebar">
          <ul class="top-level">
            <li><a href="/docs/">Intro</a></li>
            <li>
              <details>
                <summary>Usage</summary>
                <a href="/docs/cli/">CLI</a>
                <a href="/docs/web/">Web</a>
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
            home_label="Home",
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

    def test_scrape_all_exits_nonzero_when_any_page_fails(self) -> None:
        page = Page(slug="missing", title="Missing", category="", filename="01-Missing.md")
        with tempfile.TemporaryDirectory() as tmp:
            config = replace(self.config, output_dir=Path(tmp))
            with (
                patch("scripts.scraper_core.discover_pages", return_value=[page]),
                patch("scripts.scraper_core.fetch_html", return_value=None),
                self.assertRaises(SystemExit) as ctx,
            ):
                scrape_all(config)
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
