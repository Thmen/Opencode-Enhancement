import argparse
from pathlib import Path

try:
    from scripts.claudecode_scraper_core import ScraperConfig, scrape_all
except ModuleNotFoundError:
    from claudecode_scraper_core import ScraperConfig, scrape_all


CONFIG = ScraperConfig(
    docs_base_url="https://code.claude.com/docs",
    llms_index_url="https://code.claude.com/docs/llms.txt",
    lang="en",
    output_dir=Path("docs/en/claudecode"),
    readme_title="Claude Code English Docs (Offline)",
    readme_source_label="Source",
    home_label="Home",
    request_delay=1.0,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Scrape Claude Code English documentation")
    parser.add_argument("--update", action="store_true", help="Skip output cleanup before scraping")
    args = parser.parse_args(argv)
    scrape_all(CONFIG, update_only=args.update)


if __name__ == "__main__":
    main()
