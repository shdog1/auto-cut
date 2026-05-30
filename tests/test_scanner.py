from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from autocut.config import load_config
from autocut.scanner import scan_materials


class ScannerTests(unittest.TestCase):
    def test_scan_materials_accepts_utf8_bom_prompt(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            material_dir = root / "materials" / "2026-05-30"
            material_dir.mkdir(parents=True)
            (material_dir / "prompt.txt").write_text("剪一个 30 秒短视频", encoding="utf-8-sig")
            (material_dir / "clip.mp4").write_text("", encoding="utf-8")

            materials = scan_materials(load_config(root), "2026-05-30")

            self.assertEqual(materials.prompt, "剪一个 30 秒短视频")
            self.assertEqual(materials.videos, [material_dir / "clip.mp4"])


if __name__ == "__main__":
    unittest.main()
