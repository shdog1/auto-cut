from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .config import AppConfig
from .planner import EditPlan


def render_plan(plan: EditPlan, config: AppConfig, dry_run: bool = False) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg and not dry_run:
        raise RuntimeError("未找到 ffmpeg。请先安装 ffmpeg，并确保命令行可执行 `ffmpeg`。")

    output_dir = config.outputs_dir / plan.date
    log_dir = config.logs_dir / plan.date
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "final.mp4"
    command = _build_ffmpeg_command(ffmpeg or "ffmpeg", plan, output_path, log_dir)
    _write_plan_log(plan, command, log_dir)

    if dry_run:
        return output_path

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    (log_dir / "ffmpeg.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (log_dir / "ffmpeg.stderr.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg 剪辑失败，查看日志: {log_dir / 'ffmpeg.stderr.log'}")
    return output_path


def _build_ffmpeg_command(ffmpeg: str, plan: EditPlan, output_path: Path, log_dir: Path) -> list[str]:
    concat_file = log_dir / "inputs.txt"
    concat_file.write_text(
        "".join(f"file '{_escape_concat_path(path)}'\n" for path in plan.videos),
        encoding="utf-8",
    )

    width, height = plan.resolution.split("x", maxsplit=1)
    subtitle_file = _write_overlay_subtitles(plan, log_dir)
    video_filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "setsar=1",
        "format=yuv420p",
    ]
    if plan.pace == "fast":
        video_filters.append("setpts=0.85*PTS")
    elif plan.pace == "slow":
        video_filters.append("setpts=1.15*PTS")
    if subtitle_file:
        video_filters.append(f"subtitles='{_escape_filter_path(subtitle_file)}'")

    command = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
    ]

    if plan.music:
        command.extend(["-stream_loop", "-1", "-i", str(plan.music)])

    command.extend([
        "-t",
        str(plan.target_duration_seconds),
        "-vf",
        ",".join(video_filters),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
    ])

    if plan.music:
        if plan.keep_original_audio:
            command.extend([
                "-filter_complex",
                "[0:a]volume=0.75[a0];[1:a]volume=0.25[a1];[a0][a1]amix=inputs=2:duration=first[aout]",
                "-map",
                "0:v",
                "-map",
                "[aout]",
            ])
        else:
            command.extend(["-map", "0:v", "-map", "1:a", "-shortest"])
        command.extend(["-c:a", "aac", "-b:a", "192k"])
    else:
        command.extend(["-map", "0:v", "-map", "0:a?", "-c:a", "aac", "-b:a", "192k"])

    command.extend(["-movflags", "+faststart", str(output_path)])
    return command


def _write_plan_log(plan: EditPlan, command: list[str], log_dir: Path) -> None:
    data = {
        "date": plan.date,
        "prompt": plan.prompt,
        "videos": [str(path) for path in plan.videos],
        "music": str(plan.music) if plan.music else None,
        "target_duration_seconds": plan.target_duration_seconds,
        "resolution": plan.resolution,
        "pace": plan.pace,
        "title": plan.title,
        "outro": plan.outro,
        "keep_original_audio": plan.keep_original_audio,
        "command": command,
    }
    (log_dir / "plan.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_overlay_subtitles(plan: EditPlan, log_dir: Path) -> Path | None:
    events: list[str] = []
    if plan.title:
        events.append(_ass_dialogue("0:00:00.00", "0:00:03.00", plan.title))
    if plan.outro:
        start = max(0, plan.target_duration_seconds - 4)
        end = plan.target_duration_seconds
        events.append(_ass_dialogue(_ass_time(start), _ass_time(end), plan.outro))
    if not events:
        return None

    overlay_path = log_dir / "overlay.ass"
    overlay_path.write_text(
        "\n".join(
            [
                "[Script Info]",
                "ScriptType: v4.00+",
                "WrapStyle: 0",
                "ScaledBorderAndShadow: yes",
                "PlayResX: 1080",
                "PlayResY: 1920",
                "",
                "[V4+ Styles]",
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
                "Style: Default,Microsoft YaHei,72,&H00FFFFFF,&H000000FF,&H00000000,&H66000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,220,1",
                "",
                "[Events]",
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
                *events,
                "",
            ]
        ),
        encoding="utf-8-sig",
    )
    return overlay_path


def _ass_dialogue(start: str, end: str, text: str) -> str:
    return f"Dialogue: 0,{start},{end},Default,,0,0,0,,{_escape_ass_text(text)}"


def _ass_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}.00"


def _escape_ass_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")


def _escape_concat_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace("'", "'\\''")


def _escape_filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
