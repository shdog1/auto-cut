from pathlib import Path
import unittest

from autocut.config import load_config
from autocut.planner import build_plan
from autocut.scanner import MaterialSet


class PlannerTests(unittest.TestCase):
    def test_build_plan_from_chinese_prompt(self) -> None:
        config = load_config(Path("."))
        materials = MaterialSet(
            date="2026-05-30",
            source_dir=Path("materials/2026-05-30"),
            prompt="剪一个 30 秒短视频，节奏快，配音乐，结尾加关注提示",
            videos=[Path("clip.mp4")],
            audios=[Path("music.mp3")],
        )

        plan = build_plan(materials, config)

        self.assertEqual(plan.target_duration_seconds, 30)
        self.assertEqual(plan.pace, "fast")
        self.assertEqual(plan.music, Path("music.mp3"))
        self.assertEqual(plan.outro, "关注我，查看更多")


if __name__ == "__main__":
    unittest.main()
