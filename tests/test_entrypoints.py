import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.scrape_opencode_docs_en as en_entry
import scripts.scrape_opencode_docs_zh as zh_entry

REPO_ROOT = Path(__file__).resolve().parent.parent


class EntrypointTests(unittest.TestCase):
    def test_zh_config_points_to_zh_docs(self) -> None:
        self.assertEqual(zh_entry.CONFIG.base_url, "https://opencode.ai/docs/zh-cn")
        self.assertEqual(zh_entry.CONFIG.docs_prefix, "/docs/zh-cn/")
        self.assertEqual(zh_entry.CONFIG.output_dir, Path("docs/zh/opencode"))
        self.assertEqual(zh_entry.CONFIG.readme_title, "OpenCode 中文文档（离线版）")
        self.assertEqual(zh_entry.CONFIG.readme_source_label, "来源")
        self.assertEqual(zh_entry.CONFIG.default_section_title, "入门")

    def test_en_config_points_to_en_docs(self) -> None:
        self.assertEqual(en_entry.CONFIG.base_url, "https://opencode.ai/docs/en")
        self.assertEqual(en_entry.CONFIG.docs_prefix, "/docs/en/")
        self.assertEqual(en_entry.CONFIG.output_dir, Path("docs/en/opencode"))
        self.assertEqual(en_entry.CONFIG.readme_title, "OpenCode English Docs (Offline)")
        self.assertEqual(en_entry.CONFIG.readme_source_label, "Source")
        self.assertEqual(en_entry.CONFIG.default_section_title, "Getting Started")

    def test_zh_config_has_home_label(self) -> None:
        self.assertEqual(zh_entry.CONFIG.home_label, "首页")

    def test_en_config_has_home_label(self) -> None:
        self.assertEqual(en_entry.CONFIG.home_label, "Home")

    def test_en_main_passes_update_flag_to_scrape_all(self) -> None:
        with patch.object(en_entry, "scrape_all") as mock_scrape_all:
            en_entry.main(["--update"])
        mock_scrape_all.assert_called_once_with(en_entry.CONFIG, update_only=True)

    def test_en_script_runs_via_file_path(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "scrape_opencode_docs_en.py"), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage:", result.stdout.lower())

    def test_zh_script_runs_via_file_path(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "scrape_opencode_docs_zh.py"), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage:", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
