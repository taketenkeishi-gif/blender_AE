$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $root "mv_layer_tools"
$addons = Join-Path $env:APPDATA "Blender Foundation\Blender\3.6\scripts\addons"
$dest = Join-Path $addons "mv_layer_tools"

if (-not (Test-Path $source)) {
    throw "Source addon folder not found: $source"
}

New-Item -ItemType Directory -Force -Path $addons | Out-Null

if (Test-Path $dest) {
    Remove-Item -LiteralPath $dest -Recurse -Force
}

Copy-Item -LiteralPath $source -Destination $dest -Recurse -Force
Write-Host "Synced addon to $dest"
