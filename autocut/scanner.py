from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}


@dataclass(frozen=True)
class MaterialSet:
    date: str
    source_dir: Path
    prompt: str
    videos: list[Path]
    audios: list[Path]


def scan_materials(config: AppConfig, date: str) -> MaterialSet:
    source_dir = config.materials_dir / date
    if not source_dir.exists():
        raise FileNotFoundError(f"素材目录不存在: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"素材路径不是目录: {source_dir}")

    prompt_path = source_dir / config.prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"缺少描述文件: {prompt_path}")

    files = [path for path in source_dir.iterdir() if path.is_file()]
    videos = sorted(path for path in files if path.suffix.lower() in VIDEO_EXTENSIONS)
    audios = sorted(path for path in files if path.suffix.lower() in AUDIO_EXTENSIONS)
    if not videos:
        raise FileNotFoundError(f"素材目录没有视频文件: {source_dir}")

    prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
    if not prompt:
        raise ValueError(f"描述文件为空: {prompt_path}")

    return MaterialSet(
        date=date,
        source_dir=source_dir,
        prompt=prompt,
        videos=videos,
        audios=audios,
    )


def list_material_dates(config: AppConfig) -> list[str]:
    if not config.materials_dir.exists():
        return []
    return sorted(
        path.name
        for path in config.materials_dir.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )
