# auto-cut

本地自动剪辑脚本工具。每天把素材放进指定日期目录，写一个简单效果描述，工具生成剪辑计划并调用 ffmpeg 输出成片。

## 目录约定

```text
materials/2026-05-30/
  clip-1.mp4
  clip-2.mp4
  music.mp3
  prompt.txt
outputs/
logs/
```

`prompt.txt` 示例：

```text
剪一个 60 秒短视频，节奏快，开头加标题，配轻快音乐，结尾加关注提示。
```

## 使用

先安装 ffmpeg，并确认命令行可执行：

```bash
ffmpeg -version
```

检查运行环境：

```bash
python -m autocut.cli --doctor
```

如果 ffmpeg 没有加入 PATH，可以直接指定：

```bash
python -m autocut.cli --date 2026-05-30 --ffmpeg D:\tools\ffmpeg\bin\ffmpeg.exe
```

生成剪辑计划，不实际渲染：

```bash
python -m autocut.cli --date 2026-05-30 --dry-run
```

执行剪辑：

```bash
python -m autocut.cli --date 2026-05-30
```

真实渲染冒烟测试：

```powershell
.\scripts\smoke_test.ps1 -Ffmpeg D:\tools\ffmpeg\bin\ffmpeg.exe -Ffprobe D:\tools\ffmpeg\bin\ffprobe.exe
```

处理 `materials` 下所有日期目录：

```bash
python -m autocut.cli --all
```

使用自定义素材目录：

```bash
python -m autocut.cli --date 2026-05-30 --materials-dir D:\video-materials
```

输出：

```text
outputs/2026-05-30/final.mp4
logs/2026-05-30/plan.json
```

## 当前能力

- 扫描指定日期素材目录
- 读取 `prompt.txt`
- 识别时长、快慢节奏、是否配乐、是否保留原声
- 多视频顺序拼接
- 统一输出竖屏 `1080x1920`
- 支持片头标题和片尾关注提示字幕烧录
- 生成剪辑计划日志
- 支持按日期处理或批量处理所有素材目录
- 支持自定义素材、输出、日志目录
- 批量处理时单个日期失败会写 `error.log`
- 支持 `--doctor` 检查本地 ffmpeg 环境
- 支持真实渲染冒烟测试脚本

## 下一步

- 转场模板
- 素材自动筛选
- OpenAI API 把自然语言描述转成结构化剪辑方案
- 定时任务，每天自动扫描新目录
