import argparse
from pathlib import Path

try:
    from scripts.claudecode_scraper_core import ScraperConfig, scrape_all
except ModuleNotFoundError:
    from claudecode_scraper_core import ScraperConfig, scrape_all


CONFIG = ScraperConfig(
    docs_base_url="https://code.claude.com/docs",
    llms_index_url="https://code.claude.com/docs/llms.txt",
    lang="zh-CN",
    output_dir=Path("docs/zh/claudecode"),
    readme_title="Claude Code 中文文档（离线版）",
    readme_source_label="来源",
    home_label="首页",
    request_delay=1.0,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="抓取 Claude Code 中文文档")
    parser.add_argument("--update", action="store_true", help="增量模式，跳过输出目录清理")
    args = parser.parse_args(argv)
    scrape_all(CONFIG, update_only=args.update)


if __name__ == "__main__":
    main()
