from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from autocut.config import load_config
from autocut.editor import render_plan
from autocut.planner import EditPlan


class EditorTests(unittest.TestCase):
    def test_dry_run_writes_overlay_subtitles(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config = load_config(Path(temp_dir))
            plan = EditPlan(
                date="2026-05-30",
                prompt="剪一个 30 秒短视频，开头加标题，结尾加关注提示",
                videos=[Path(temp_dir) / "clip.mp4"],
                music=None,
                target_duration_seconds=30,
                resolution="1080x1920",
                pace="normal",
                title="今日精彩片段",
                outro="关注我，查看更多",
                keep_original_audio=True,
            )

            render_plan(plan, config, dry_run=True)

            log_dir = Path(temp_dir) / "logs" / "2026-05-30"
            overlay = (log_dir / "overlay.ass").read_text(encoding="utf-8-sig")
            plan_log = json.loads((log_dir / "plan.json").read_text(encoding="utf-8"))

            self.assertIn("今日精彩片段", overlay)
            self.assertIn("关注我，查看更多", overlay)
            self.assertTrue(any("subtitles=" in item for item in plan_log["command"]))


if __name__ == "__main__":
    unittest.main()
