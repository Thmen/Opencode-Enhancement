import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.scrape_claudecode_docs_en as en_entry
import scripts.scrape_claudecode_docs_zh as zh_entry

REPO_ROOT = Path(__file__).resolve().parent.parent


class ClaudeEntrypointTests(unittest.TestCase):
    def test_en_config_points_to_en_docs(self) -> None:
        self.assertEqual(en_entry.CONFIG.lang, "en")
        self.assertEqual(en_entry.CONFIG.output_dir, Path("docs/en/claudecode"))
        self.assertEqual(en_entry.CONFIG.home_label, "Home")

    def test_zh_config_points_to_zh_docs(self) -> None:
        self.assertEqual(zh_entry.CONFIG.lang, "zh-CN")
        self.assertEqual(zh_entry.CONFIG.output_dir, Path("docs/zh/claudecode"))
        self.assertEqual(zh_entry.CONFIG.home_label, "首页")

    def test_en_main_passes_update_flag_to_scrape_all(self) -> None:
        with patch.object(en_entry, "scrape_all") as mock_scrape_all:
            en_entry.main(["--update"])
        mock_scrape_all.assert_called_once_with(en_entry.CONFIG, update_only=True)

    def test_en_script_runs_via_file_path(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "scrape_claudecode_docs_en.py"), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage:", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
