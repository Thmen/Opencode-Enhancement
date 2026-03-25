import argparse
from pathlib import Path

try:
    from scripts.scraper_core import ScraperConfig, scrape_all
except ModuleNotFoundError:
    from scraper_core import ScraperConfig, scrape_all

CONFIG = ScraperConfig(
    base_url="https://opencode.ai/docs/en",
    docs_prefix="/docs/en/",
    output_dir=Path("docs/en/opencode"),
    readme_title="OpenCode English Docs (Offline)",
    readme_source_label="Source",
    default_section_title="Getting Started",
    home_label="Home",
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


if __name__ == "__main__":
    main()
