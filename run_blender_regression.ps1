$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$blender = Join-Path $root "Blender Foundation\Blender 3.6\blender.exe"
$testScript = Join-Path $root "blender_addon_regression_test.py"

if (-not (Test-Path $blender)) {
    throw "Blender executable not found: $blender"
}

if (-not (Test-Path $testScript)) {
    throw "Regression script not found: $testScript"
}

& $blender --background --factory-startup --python $testScript
exit $LASTEXITCODE
