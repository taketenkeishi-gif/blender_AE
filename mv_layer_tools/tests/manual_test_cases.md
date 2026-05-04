# Manual Test Cases

## Import and Layer List

1. Start from a new Blender file.
2. Enable the add-on.
3. Initialize the MV scene.
4. Import at least three PNG assets with transparency.
5. Confirm three managed layer objects are created and listed.
6. Confirm category collection(s) are created under `MVLT_Master`.

## Timeline and Keying

1. Select an imported layer.
2. Set `frame_start` and `frame_end`.
3. Move to a frame in range and press `Add Primary Keys`.
4. Confirm location, rotation, scale, and custom opacity keys are inserted.

## Effects

1. Apply `Fade In`.
2. Apply `Fade Out`.
3. Apply `Shake`.
4. Optionally apply `Zoom`.
5. Inspect keyframes and material alpha behavior in the Action Editor / Material nodes.

## Blender 3.6 Regression

1. Run [run_blender_regression.ps1](/c:/ポートフォリオ/Blender%20AE%20mode/run_blender_regression.ps1).
2. Confirm Blender 3.6 launches in background mode.
3. Confirm the script prints `ALL_TESTS_PASSED`.
4. If it fails, use the failing section label such as `IMPORT_OK` or `EFFECTS_OK` to narrow the broken area quickly.
