from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    materials_dir: Path
    outputs_dir: Path
    logs_dir: Path
    prompt_name: str = "prompt.txt"
    default_duration_seconds: int = 60
    default_resolution: str = "1080x1920"
    ffmpeg_path: str = "ffmpeg"


def load_config(root_dir: Path | None = None) -> AppConfig:
    root = (root_dir or Path.cwd()).resolve()
    return AppConfig(
        root_dir=root,
        materials_dir=root / "materials",
        outputs_dir=root / "outputs",
        logs_dir=root / "logs",
        ffmpeg_path=os.environ.get("AUTOCUT_FFMPEG", "ffmpeg"),
    )


def with_overrides(
    config: AppConfig,
    materials_dir: str | None = None,
    outputs_dir: str | None = None,
    logs_dir: str | None = None,
    prompt_name: str | None = None,
    default_duration_seconds: int | None = None,
    default_resolution: str | None = None,
    ffmpeg_path: str | None = None,
) -> AppConfig:
    return AppConfig(
        root_dir=config.root_dir,
        materials_dir=_resolve(config.root_dir, materials_dir) if materials_dir else config.materials_dir,
        outputs_dir=_resolve(config.root_dir, outputs_dir) if outputs_dir else config.outputs_dir,
        logs_dir=_resolve(config.root_dir, logs_dir) if logs_dir else config.logs_dir,
        prompt_name=prompt_name or config.prompt_name,
        default_duration_seconds=default_duration_seconds or config.default_duration_seconds,
        default_resolution=default_resolution or config.default_resolution,
        ffmpeg_path=ffmpeg_path or config.ffmpeg_path,
    )


def _resolve(root_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root_dir / path
