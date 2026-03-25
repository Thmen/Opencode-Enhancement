import argparse
from pathlib import Path

try:
    from scripts.scraper_core import ScraperConfig, scrape_all
except ModuleNotFoundError:
    from scraper_core import ScraperConfig, scrape_all

CONFIG = ScraperConfig(
    base_url="https://opencode.ai/docs/zh-cn",
    docs_prefix="/docs/zh-cn/",
    output_dir=Path("docs/zh/opencode"),
    readme_title="OpenCode 中文文档（离线版）",
    readme_source_label="来源",
    default_section_title="入门",
    home_label="首页",
    request_delay=1.0,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="抓取 OpenCode 中文文档")
    parser.add_argument("--update", action="store_true", help="增量更新模式，跳过已存在的文件")
    args = parser.parse_args(argv)
    scrape_all(CONFIG, update_only=args.update)


if __name__ == "__main__":
    main()
