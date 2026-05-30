$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$today = Get-Date -Format "yyyy-MM-dd"
python -m autocut.cli --date $today
