from pathlib import Path
import unittest

from autocut.config import load_config, with_overrides


class ConfigTests(unittest.TestCase):
    def test_with_overrides_resolves_relative_paths(self) -> None:
        root = Path("project").resolve()
        config = with_overrides(
            load_config(root),
            materials_dir="daily",
            outputs_dir="done",
            logs_dir="run-logs",
            prompt_name="idea.txt",
            default_duration_seconds=45,
            default_resolution="1920x1080",
        )

        self.assertEqual(config.materials_dir, root / "daily")
        self.assertEqual(config.outputs_dir, root / "done")
        self.assertEqual(config.logs_dir, root / "run-logs")
        self.assertEqual(config.prompt_name, "idea.txt")
        self.assertEqual(config.default_duration_seconds, 45)
        self.assertEqual(config.default_resolution, "1920x1080")


if __name__ == "__main__":
    unittest.main()
