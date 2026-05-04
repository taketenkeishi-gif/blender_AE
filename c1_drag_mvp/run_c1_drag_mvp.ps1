$ErrorActionPreference = "Stop"

$sourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $sourceRoot
$blender = Join-Path $projectRoot "Blender Foundation\Blender 3.6\blender.exe"

$workDir = "C:\mvlt_c1_live"
$appRoot = Join-Path $workDir "app"
$out = "C:\ポートフォリオ\抽出結果.txt"

$backendOut = Join-Path $workDir "backend_stdout.log"
$backendErr = Join-Path $workDir "backend_stderr.log"
$serverOut = Join-Path $workDir "server_stdout.log"
$serverErr = Join-Path $workDir "server_stderr.log"

$preview = Join-Path $workDir "preview.jpg"
$state = Join-Path $workDir "state.json"
$stop = Join-Path $workDir "stop.txt"
$command = Join-Path $workDir "command.json"

function Write-Report {
  param([string]$Text)
  $Text | Out-File $out -Append -Encoding UTF8
  Write-Host $Text
}

function Add-FileTail {
  param(
    [string]$Title,
    [string]$Path
  )

  Write-Report ""
  Write-Report "=== $Title ==="

  if (-not (Test-Path $Path)) {
    Write-Report "NOT FOUND: $Path"
    return
  }

  Get-Content $Path -Tail 120 -Encoding UTF8 | Out-File $out -Append -Encoding UTF8
}

Remove-Item $out -Force -ErrorAction SilentlyContinue

"=== C1 Drag MVP v3 Launch ===" | Out-File $out -Encoding UTF8
"実行日時: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $out -Append -Encoding UTF8
"sourceRoot: $sourceRoot" | Out-File $out -Append -Encoding UTF8
"projectRoot: $projectRoot" | Out-File $out -Append -Encoding UTF8
"blender: $blender" | Out-File $out -Append -Encoding UTF8
"workDir: $workDir" | Out-File $out -Append -Encoding UTF8
"appRoot: $appRoot" | Out-File $out -Append -Encoding UTF8

if (-not (Test-Path $blender)) {
  throw "blender.exe not found: $blender"
}
if (-not (Test-Path (Join-Path $sourceRoot "c1_blender_backend.py"))) {
  throw "backend source not found"
}
if (-not (Test-Path (Join-Path $sourceRoot "c1_drag_ui_server.py"))) {
  throw "server source not found"
}

New-Item -ItemType Directory -Path $workDir -Force | Out-Null

"stop" | Set-Content -Path $stop -Encoding UTF8

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

Start-Sleep -Seconds 1

if (Test-Path $appRoot) {
  Remove-Item $appRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $appRoot -Force | Out-Null

Copy-Item -Path (Join-Path $sourceRoot "*") -Destination $appRoot -Recurse -Force

$backendScript = Join-Path $appRoot "c1_blender_backend.py"
$serverScript = Join-Path $appRoot "c1_drag_ui_server.py"

Remove-Item $stop -Force -ErrorAction SilentlyContinue
Remove-Item $command -Force -ErrorAction SilentlyContinue
Remove-Item $preview -Force -ErrorAction SilentlyContinue
Remove-Item $state -Force -ErrorAction SilentlyContinue
Remove-Item $backendOut -Force -ErrorAction SilentlyContinue
Remove-Item $backendErr -Force -ErrorAction SilentlyContinue
Remove-Item $serverOut -Force -ErrorAction SilentlyContinue
Remove-Item $serverErr -Force -ErrorAction SilentlyContinue

$py = Get-Command py -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

if ($py -ne $null) {
  $serverExe = $py.Source
  $serverArgs = @("-3", $serverScript)
} elseif ($python -ne $null) {
  $serverExe = $python.Source
  $serverArgs = @($serverScript)
} else {
  throw "Python launcher not found. py/python がPATHにありません。"
}

Write-Report ""
Write-Report "=== Starting UI server ==="
Write-Report "serverExe: $serverExe"
Write-Report "serverScript: $serverScript"

$serverProcess = Start-Process `
  -FilePath $serverExe `
  -ArgumentList $serverArgs `
  -WorkingDirectory $appRoot `
  -RedirectStandardOutput $serverOut `
  -RedirectStandardError $serverErr `
  -PassThru `
  -WindowStyle Hidden

Start-Sleep -Milliseconds 800

if ($serverProcess.HasExited) {
  Write-Report "SERVER_EXITED_EARLY ExitCode=$($serverProcess.ExitCode)"
  Add-FileTail "server stdout" $serverOut
  Add-FileTail "server stderr" $serverErr
  notepad $out
  throw "UI server exited early. See $out"
}

$serverReady = $false
for ($i = 0; $i -lt 30; $i++) {
  try {
    $res = Invoke-WebRequest -Uri "http://127.0.0.1:8765/" -UseBasicParsing -TimeoutSec 1
    if ($res.StatusCode -eq 200) {
      $serverReady = $true
      break
    }
  } catch {
    Start-Sleep -Milliseconds 200
  }
}

if (-not $serverReady) {
  Write-Report "SERVER_NOT_READY"
  Add-FileTail "server stdout" $serverOut
  Add-FileTail "server stderr" $serverErr
  notepad $out
  throw "UI server did not become ready. See $out"
}

Write-Report "SERVER_READY"

Write-Report ""
Write-Report "=== Starting Blender backend ==="
Write-Report "backendScript: $backendScript"

$backendProcess = Start-Process `
  -FilePath $blender `
  -ArgumentList @("--factory-startup", "--python", $backendScript) `
  -WorkingDirectory $appRoot `
  -RedirectStandardOutput $backendOut `
  -RedirectStandardError $backendErr `
  -PassThru

$previewReady = $false
$stateReady = $false

for ($i = 0; $i -lt 100; $i++) {
  if ($backendProcess.HasExited) {
    Write-Report "BACKEND_EXITED_EARLY ExitCode=$($backendProcess.ExitCode)"
    Add-FileTail "backend stdout" $backendOut
    Add-FileTail "backend stderr" $backendErr
    Add-FileTail "server stdout" $serverOut
    Add-FileTail "server stderr" $serverErr
    notepad $out
    throw "Blender backend exited early. See $out"
  }

  if (Test-Path $preview) {
    $previewInfo = Get-Item $preview
    if ($previewInfo.Length -gt 1000) {
      $previewReady = $true
    }
  }

  if (Test-Path $state) {
    $stateInfo = Get-Item $state
    if ($stateInfo.Length -gt 50) {
      $stateReady = $true
    }
  }

  if ($previewReady -and $stateReady) {
    break
  }

  Start-Sleep -Milliseconds 250
}

Write-Report ""
Write-Report "=== Self-test result ==="
Write-Report "server pid: $($serverProcess.Id)"
Write-Report "backend pid: $($backendProcess.Id)"
Write-Report "preview exists: $(Test-Path $preview)"
if (Test-Path $preview) {
  Write-Report "preview size: $((Get-Item $preview).Length)"
}
Write-Report "state exists: $(Test-Path $state)"
if (Test-Path $state) {
  Write-Report "state size: $((Get-Item $state).Length)"
}

if (-not ($previewReady -and $stateReady)) {
  Write-Report "PREVIEW_OR_STATE_NOT_READY"
  Add-FileTail "backend stdout" $backendOut
  Add-FileTail "backend stderr" $backendErr
  Add-FileTail "server stdout" $serverOut
  Add-FileTail "server stderr" $serverErr
  notepad $out
  throw "Preview/state not ready. See $out"
}

Write-Report "READY_OK"
Write-Report "UI: http://127.0.0.1:8765/"
Write-Report "WorkDir: $workDir"

Start-Process "http://127.0.0.1:8765/"

Write-Report ""
Write-Report "ブラウザが開いたら、青い矩形をドラッグしてください。"
Write-Report "落ちた場合は、このファイルを貼ってください: $out"
