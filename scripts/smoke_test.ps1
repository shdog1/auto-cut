param(
    [string]$Ffmpeg = "ffmpeg",
    [string]$Ffprobe = "ffprobe"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$date = "smoke-test"
$materialDir = Join-Path $root "materials\$date"
$outputPath = Join-Path $root "outputs\$date\final.mp4"

New-Item -ItemType Directory -Force $materialDir | Out-Null
Set-Content -Encoding UTF8 (Join-Path $materialDir "prompt.txt") "2 s BGM"

& $Ffmpeg -v error -y `
    -f lavfi -i "testsrc2=size=720x1280:rate=30" `
    -f lavfi -i "sine=frequency=440:sample_rate=44100" `
    -t 2 `
    -c:v libx264 -pix_fmt yuv420p `
    -c:a aac `
    (Join-Path $materialDir "clip.mp4")

& $Ffmpeg -v error -y `
    -f lavfi -i "sine=frequency=880:sample_rate=44100" `
    -t 2 `
    -c:a mp3 `
    (Join-Path $materialDir "music.mp3")

python -m autocut.cli --date $date --ffmpeg $Ffmpeg

$width = & $Ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 $outputPath
$height = & $Ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 $outputPath
$audioCodec = & $Ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 $outputPath
$duration = [double](& $Ffprobe -v error -show_entries format=duration -of csv=p=0 $outputPath)

if ($width -ne "1080" -or $height -ne "1920") {
    throw "Unexpected output size: ${width}x${height}"
}
if (-not $audioCodec) {
    throw "Missing audio stream"
}
if ($duration -lt 1.8 -or $duration -gt 2.5) {
    throw "Unexpected output duration: $duration"
}

Write-Host "Smoke test passed: $outputPath"
