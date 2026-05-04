$ErrorActionPreference = "Continue"

$workDir = "C:\mvlt_c1_live"
New-Item -ItemType Directory -Path $workDir -Force | Out-Null
"stop" | Set-Content -Path (Join-Path $workDir "stop.txt") -Encoding UTF8

try {
  $listeners = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
  foreach ($l in $listeners) {
    Stop-Process -Id $l.OwningProcess -Force -ErrorAction SilentlyContinue
  }
} catch {
}

Get-CimInstance Win32_Process |
  Where-Object {
    ($_.Name -eq "blender.exe" -and $_.CommandLine -match "c1_blender_backend|mvlt_c1_live")
  } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

Write-Host "C1 Drag MVP stopped."
