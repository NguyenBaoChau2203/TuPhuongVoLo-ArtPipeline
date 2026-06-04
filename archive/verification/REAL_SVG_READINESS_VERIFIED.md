# Real SVG Readiness Verification Checkpoint

Date: 2026-06-03

Branch: `workflow/maya-first-artist-pipeline`

Status: verified as a documentation-only checkpoint after the real-SVG readiness roadmap.

## Scope

This checkpoint summarizes the current Maya-first real SVG testing workflow after these completed phases:

- 007M SVG preflight checker
- 007L guided desktop workflow
- 005.3R prop orientation markers
- 005.3S door/window markers
- 005.3T prop library v2
- 005.3U material/color tags

No Python code, Maya logic, SVG parser logic, tests, generated outputs, textures, renderer behavior, AI behavior, web UI behavior, or Feature 006 work is changed by this checkpoint.

## Current Workflow

The production-safe path for real artist SVG testing is:

```text
Copy/export clean SVG from Illustrator
-> run read-only SVG preflight
-> run Maya dry-run
-> run actual Maya build only after dry-run succeeds
-> inspect editable .ma in Maya
-> keep real SVG, .ma, PNG, temporary JSON, reports, and outputs uncommitted
```

The Maya-first pipeline remains the production path. Blender remains legacy/fallback and is not required for this checkpoint.

## App Guided Flow

Artists and operators should run the guided desktop app from Python to avoid stale packaged executables:

```powershell
python scripts/python/artist_desktop_app.py
```

Current app version:

```text
TuPhuongVoLo Maya Artist App v0.7.10 (007L)
```

The app guides the operator through selecting a clean SVG, choosing a room, running dry-run first, and only then running an actual Maya build when `mayapy.exe` is available. The packaged `.exe` remains optional and should not be treated as the source of truth during readiness testing.

## Preflight Flow

Run preflight before Maya dry-run:

```powershell
python scripts/python/svg_preflight_check.py --input drops/ten_file.svg
```

Optional JSON report:

```powershell
python scripts/python/svg_preflight_check.py --input drops/ten_file.svg --json-output outputs/reports/svg_preflight_report.json
```

Preflight is read-only. It reports `OK`, `WARNING`, or `FATAL` and highlights risky SVG elements before the file reaches the Maya bridge.

Current preflight version:

```text
svg-preflight-check 0.7.10 (007M)
```

## Marker Syntax

Prop marker prefixes remain:

- `prop_`
- `item_`
- `object_`

Prop orientation suffixes:

- `_rot90`
- `_rot180`
- `_rot270`
- `_rotation_90`
- `_rotation_180`
- `_rotation_270`

Examples:

- `prop_shelf_unit_rot90`
- `prop_wooden_crate_rot180`
- `item_box_rotation_90`

Door/window marker prefixes:

- `door_`
- `window_`

Examples:

- `door_main`
- `door_left`
- `window_small`
- `window_back_01`

Door/window markers create simple Maya placeholder blocks under `openings`. They do not cut walls, run booleans, or create real architectural holes.

## Prop Library Keywords

Known prop placeholder keywords with deterministic dimensions:

- `shelf_unit`
- `wooden_crate`
- `table`
- `chair`
- `bed`
- `cabinet`
- `barrel`
- `box`

Unknown prop names remain safe and fall back to the generic cube placeholder.

## Material And Color Tags

Supported suffix grammar:

- `_mat_<name>`
- `_material_<name>`
- `_color_<name>`

Supported material names:

- `wood`
- `metal`
- `stone`
- `fabric`
- `paper`

Supported color names:

- `red`
- `blue`
- `green`
- `yellow`
- `white`
- `black`
- `gray`

Examples:

- `prop_wooden_crate_01_mat_wood`
- `prop_table_material_metal`
- `prop_box_color_red`
- `wall_mat_stone`
- `floor_material_wood`

Unknown material/color tags are safe and may use the default Maya blockout material. Texture support is intentionally not implemented.

## Safety Rules For Real Artist SVG

- Never edit, delete, or overwrite the original `.ai` file.
- Always work from a copy/exported SVG.
- Run the app using Python to avoid stale `.exe` behavior:
  `python scripts/python/artist_desktop_app.py`
- Run preflight first.
- Run Maya dry-run first.
- Run an actual Maya build only after dry-run succeeds.
- Do not commit real artist SVG files.
- Do not commit generated `.ma`, `.png`, geometry JSON, reports, or anything under `outputs/`.
- Do not call AI APIs during real SVG readiness testing.
- Do not use a web UI.
- Feature 006 remains deferred.

## Validation Commands And Results

The following commands were run on 2026-06-03:

```powershell
python scripts/python/artist_desktop_app.py --help
python scripts/python/artist_desktop_app.py --version
python scripts/python/svg_preflight_check.py --help
python scripts/python/svg_preflight_check.py --version
python scripts/python/build_maya_room.py --help
python scripts/python/batch_maya_room.py --help
python scripts/python/package_artist_app.py --dry-run
pytest tests/ -v --ignore=tests/tmp
git status
git log --oneline -12
```

Results:

- `artist_desktop_app.py --help`: passed
- `artist_desktop_app.py --version`: `TuPhuongVoLo Maya Artist App v0.7.10 (007L)`
- `svg_preflight_check.py --help`: passed
- `svg_preflight_check.py --version`: `svg-preflight-check 0.7.10 (007M)`
- `build_maya_room.py --help`: passed
- `batch_maya_room.py --help`: passed
- `package_artist_app.py --dry-run`: passed; planned PyInstaller command printed, no package built
- `pytest tests/ -v --ignore=tests/tmp`: 258 passed, 1 local pytest cache permission warning
- `git status`: clean before creating this documentation checkpoint; after creation, only this checkpoint document changed

Latest git log at checkpoint creation:

```text
8f2888c feat: support material and color tags
1c16dca feat: expand placeholder prop library
b2e02e9 fix: improve desktop app log readability
9f3fa2a fix: improve desktop app log readability
6ca171e fix: simplify guided desktop app layout
6194de2 feat: add door and window markers
fbfbbf2 feat: support prop orientation markers
6b9d8c5 feat: add guided artist workflow to desktop app
9537d75 feat: add SVG preflight checker
7caa6ec docs: de-emphasize paid AI preview in artist workflow
1902dc6 docs: audit SDD alignment for artist workflow roadmap
49c84f7 fix: improve artist app button contrast and guide details
```

## Intentionally Not Implemented

- No AI API calls.
- No web UI.
- No Feature 006 work.
- No real 3D assets.
- No texture files.
- No production material asset library.
- No renderer changes.
- No lighting, camera, or render preview behavior changes.
- No wall cutting or boolean operations for doors/windows.
- No advanced CSS/style parsing for Illustrator colors.
- No guarantee that every arbitrary Illustrator SVG construct is supported.
- No commitment of real artist SVGs or generated Maya/PNG/output artifacts.

## Conclusion

The current repository is ready for controlled real SVG readiness testing with a copy of artist-exported SVG files, provided operators follow the preflight-first and dry-run-first safety workflow. This checkpoint is documentation-only and records the verified state after the real-SVG readiness roadmap.
