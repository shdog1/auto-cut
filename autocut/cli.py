from __future__ import annotations

import argparse
from datetime import date as date_type
from pathlib import Path
import subprocess

from .config import AppConfig, load_config, with_overrides
from .editor import render_plan, resolve_ffmpeg
from .planner import build_plan
from .scanner import list_material_dates, scan_materials


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-cut daily materials into a finished video.")
    parser.add_argument("--date", default=date_type.today().isoformat(), help="素材日期目录，例如 2026-05-30")
    parser.add_argument("--all", action="store_true", help="处理 materials 下所有日期目录")
    parser.add_argument("--root", default=".", help="项目根目录")
    parser.add_argument("--materials-dir", help="素材根目录，默认 materials")
    parser.add_argument("--outputs-dir", help="输出根目录，默认 outputs")
    parser.add_argument("--logs-dir", help="日志根目录，默认 logs")
    parser.add_argument("--prompt-name", help="描述文件名，默认 prompt.txt")
    parser.add_argument("--duration", type=int, help="默认输出时长秒数，prompt 未写时使用")
    parser.add_argument("--resolution", help="输出分辨率，默认 1080x1920")
    parser.add_argument("--ffmpeg", help="ffmpeg 可执行文件路径，默认读取 PATH 或 AUTOCUT_FFMPEG")
    parser.add_argument("--doctor", action="store_true", help="检查运行环境")
    parser.add_argument("--dry-run", action="store_true", help="只生成计划和日志，不执行 ffmpeg")
    args = parser.parse_args()

    config = with_overrides(
        load_config(Path(args.root)),
        materials_dir=args.materials_dir,
        outputs_dir=args.outputs_dir,
        logs_dir=args.logs_dir,
        prompt_name=args.prompt_name,
        default_duration_seconds=args.duration,
        default_resolution=args.resolution,
        ffmpeg_path=args.ffmpeg,
    )
    if args.doctor:
        return doctor(config)

    dates = list_material_dates(config) if args.all else [args.date]
    if not dates:
        print(f"没有找到素材目录: {config.materials_dir}")
        return 1

    failed = 0
    for material_date in dates:
        try:
            output_path = process_date(config, material_date, dry_run=args.dry_run)
        except Exception as exc:
            failed += 1
            _write_error_log(config, material_date, exc)
            print(f"剪辑失败: {material_date}: {exc}")
            continue

        if args.dry_run:
            print(f"计划已生成: {config.logs_dir / material_date / 'plan.json'}")
            print(f"预计输出: {output_path}")
        else:
            print(f"剪辑完成: {output_path}")
    return 1 if failed else 0


def process_date(config: AppConfig, material_date: str, dry_run: bool = False) -> Path:
    materials = scan_materials(config, material_date)
    plan = build_plan(materials, config)
    return render_plan(plan, config, dry_run=dry_run)


def _write_error_log(config: AppConfig, material_date: str, error: Exception) -> None:
    log_dir = config.logs_dir / material_date
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "error.log").write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")


def doctor(config: AppConfig) -> int:
    print(f"项目目录: {config.root_dir}")
    print(f"素材目录: {config.materials_dir}")
    print(f"输出目录: {config.outputs_dir}")
    print(f"日志目录: {config.logs_dir}")

    ffmpeg = resolve_ffmpeg(config.ffmpeg_path)
    if not ffmpeg:
        print("ffmpeg: 未找到")
        print("修复: 安装 ffmpeg，或用 --ffmpeg / AUTOCUT_FFMPEG 指向 ffmpeg.exe")
        return 1

    print(f"ffmpeg: {ffmpeg}")
    completed = subprocess.run([ffmpeg, "-version"], capture_output=True, text=True, check=False)
    first_line = completed.stdout.splitlines()[0] if completed.stdout else "版本信息为空"
    print(first_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
