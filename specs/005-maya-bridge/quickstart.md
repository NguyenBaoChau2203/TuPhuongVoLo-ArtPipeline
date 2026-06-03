# Quickstart: Maya Bridge

Feature 005 is the Maya-first DCC bridge for the Illustrator + Maya artist workflow. It does not require Blender.

## Prerequisites

- Python 3.11+
- A clean SVG with closed room boundary paths
- Optional: Autodesk Maya 2024+ with `mayapy.exe` for actual `.ma` generation

Dry-run verification does not require Maya.

## Step 1: Prepare or Reuse a Test SVG

Use the existing fixture:

```powershell
tests/in/feature001_kho.svg
```

Or create a simple clean SVG in `tests/in/` with a group such as `room_kho` and one closed rectangular path.

## Step 2: Single-Room Dry-Run

```powershell
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --dry-run
```

Expected:

- Selected room is `kho`
- Planned geometry JSON is under `outputs/tmp/`
- Planned Maya scene output is under `outputs/maya/`
- Command includes `scripts/maya/build_maya_room_scene.py`
- Manifest is not updated

Expected planned `.ma` path:

```text
outputs/maya/tu_phuong_vo_lo_kho_main_maya_v001.ma
```

## Step 3: Batch Dry-Run

```powershell
python scripts/python/batch_maya_room.py --input-dir tests/in --dry-run --json-report outputs/reports/batch_maya_report.json
```

Expected:

- Batch scans SVG files non-recursively
- Bad/corrupt SVGs are reported as failed but do not stop the batch unless `--stop-on-error` is used
- Report is written to `outputs/reports/batch_maya_report.json`
- Manifest is not updated

## Step 4: Actual Maya Run

Actual execution is environment-dependent and requires `mayapy.exe`:

```powershell
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

Feature 005 MVP actual run supports `mayapy.exe` only. Direct `maya.exe` or
`mayabatch.exe` execution is future work.

`mayapy.exe` runs headless, so the Maya script creates and saves the
orthographic isometric camera but does not call viewport switching commands.

Expected after success:

- Geometry JSON is written
- Maya creates an editable `.ma` scene in `outputs/maya/`
- The `.ma` file exists
- Manifest is appended only after the `.ma` file is verified

## Step 5: Validation Commands

```powershell
python scripts/python/build_maya_room.py --help
python scripts/python/batch_maya_room.py --help
python -m pytest tests/test_build_maya_room.py tests/test_batch_maya_room.py -v
python -m compileall scripts/python
```

## Step 6: Prop Marker Dry-Run (Phase 005.3)

Use the prop-marker fixture to verify artist-authored placeholder placement without Maya:

```powershell
python scripts/python/build_maya_room.py `
  --input tests/in/illustrator_prop_markers.svg `
  --room phong_kho `
  --output-dir outputs `
  --render-preview `
  --dry-run
```

Expected:

- Detected room is `phong_kho`
- `prop_shelf_unit` becomes `shelf_unit`
- `prop_wooden_crate` becomes `wooden_crate`
- Known placeholder keywords use deterministic dimensions from the internal prop
  definition table: `shelf_unit`, `wooden_crate`, `table`, `chair`, `bed`,
  `cabinet`, `barrel`, and `box`.
- Unknown prop names still create the simple generic cube fallback instead of
  failing. No external 3D asset, texture, or new material file is required.
- Optional material/color tag suffixes can be added to prop, wall, or floor
  group names: `_mat_<name>`, `_material_<name>`, and `_color_<name>`.
  Supported material names are `wood`, `metal`, `stone`, `fabric`, and `paper`.
  Supported color names are `red`, `blue`, `green`, `yellow`, `white`, `black`,
  and `gray`. Examples: `prop_wooden_crate_01_mat_wood`,
  `prop_table_material_metal`, `prop_box_color_red`, `wall_mat_stone`,
  and `floor_material_wood`.
- Unknown material/color hints are safe and may fall back to default blockout
  materials. This phase does not add texture files, real asset materials, or
  renderer changes.
- Prop marker rotation suffixes are optional. Supported suffixes are `_rot90`,
  `_rot180`, `_rot270`, `_rotation_90`, `_rotation_180`, and `_rotation_270`.
  For example, `prop_shelf_unit_rot90` becomes `shelf_unit` with
  `rotation_y_degrees: 90`, and `item_box_rotation_90` becomes `box` with
  `rotation_y_degrees: 90`.
- The primary artist-facing marker naming guide lives in
  `docs/artist_workflow_cat_guide_vi.html`
- The Illustrator copy/paste template lives in
  `assets/2d/templates/illustrator_prop_marker_template.svg`
- Dry-run prints planned `.ma`, geometry JSON, and preview PNG paths
- Manifest is not updated

Run this dry-run check before actual Maya execution when adding rotation
suffixes, then inspect the printed prop marker list and planned `.ma` path.

Door/window marker dry-run for Phase 005.3S:

```powershell
python scripts/python/build_maya_room.py `
  --input tests/in/illustrator_opening_markers.svg `
  --room kho `
  --output-dir outputs `
  --dry-run
```

Marker groups/layers whose normalized names start with `door_` or `window_`
are written to geometry JSON as `opening_markers`. Maya creates simple
placeholder cubes under an `openings` group, with deterministic names such as
`door_main_01` and `window_back_01`. This phase intentionally does not cut
walls, run booleans, or create real architectural holes; inspect the markers in
Maya after the build.

Template dry-run for Phase 005.3Q:

```powershell
python scripts/python/build_maya_room.py `
  --input assets/2d/templates/illustrator_prop_marker_template.svg `
  --room phong_marker_template `
  --output-dir outputs `
  --dry-run
```

Expected:

- Dry-run reports 12 prop markers
- Manifest is not updated
- No Maya execution is required

`tests/in/illustrator_prop_markers.svg` is a technical fixture with only a few
markers, so a real PNG render can look sparse. For a clearer visual sanity
smoke test with more procedural prop variety, use the showcase fixture:

```powershell
python scripts/python/build_maya_room.py `
  --input tests/in/illustrator_prop_showcase.svg `
  --room phong_showcase `
  --output-dir outputs `
  --render-preview `
  --dry-run
```

Expected:

- Dry-run reports 12 prop markers
- Planned PNG path is `outputs/preview/tu_phuong_vo_lo_phong_showcase_main_preview_v001.png`
- Manifest is not updated
- The fixture remains blockout-only; it is for visual/DCC smoke testing, not final art

Actual Maya render on a DCC machine:

```powershell
python scripts/python/build_maya_room.py `
  --input tests/in/illustrator_prop_showcase.svg `
  --room phong_showcase `
  --output-dir outputs `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --render-preview `
  --render-width 1280 `
  --render-height 720
```

Optional if installed:

```powershell
python -m ruff check scripts/python tests
```

## Step 7: Optional AI Polish Preview fal Provider (Phase 005.5C)

AI polish preview is reference-only. It does not modify clean SVG, geometry
JSON, Maya `.ma`, manifest, render logic, prop placement, or source assets.

Mock dry-run:

```powershell
python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png
```

fal dry-run, no API call:

```powershell
python scripts/python/ai_polish_preview.py --dry-run --provider fal --input tests/in/sample_preview.png --model fal-ai/flux-pro/kontext
```

fal missing-key skip path, no API call when `FAL_KEY` is absent:

```powershell
python scripts/python/ai_polish_preview.py --provider fal --input tests/in/sample_preview.png --skip-on-missing-config
```

Optional dependency for real fal runs only:

```powershell
python -m pip install fal-client
```

Real fal calls require the user to set `FAL_KEY` in the environment and run
`--provider fal` without `--dry-run`. Generated reference PNG/report artifacts
go under `outputs/ai_preview/` and must not be committed.

## Artist Launchers

- Environment check: `launchers/00_maya_env_check.bat`
- Single room dry-run or actual run: `launchers/07_build_maya_room.bat`
- Batch dry-run/report or actual run: `launchers/08_batch_maya_room.bat`

Phase 005.4 launcher verification:

1. Run `launchers/00_maya_env_check.bat` to check Python, PyYAML, and mayapy discovery.
2. Run `launchers/07_build_maya_room.bat`, accept dry-run, use `tests/in/illustrator_prop_markers.svg`, room `phong_kho`, and optionally enable render-preview planning.
3. Confirm the dry-run prints the selected room, detected prop markers, planned `.ma`, planned geometry JSON, optional PNG preview path, and the exact Python command.
4. On a DCC machine with Maya, rerun `07_build_maya_room.bat`, choose no dry-run, provide `mayapy.exe` if config/PATH does not resolve it, and enable render preview if needed.
5. Run `launchers/08_batch_maya_room.bat`, choose an input directory or file, keep dry-run/report enabled, and confirm the JSON report path is printed.
6. Open the generated `.ma` in Maya after an actual run and check the Outliner for `walls`, `props`, prop placeholders such as `prop_shelf_unit_01`, `lights`, and `floor_blockout`.

Generated outputs are expected under `outputs/maya/`, `outputs/preview/`, `outputs/tmp/`, and `outputs/reports/`. Do not commit generated `.ma`, `.png`, temporary handoff JSON, or batch reports unless intentionally adding a fixture.

Actual Maya execution was verified manually on the artist/DCC machine with
Autodesk Maya 2024 and `mayapy.exe`. Launcher 07 was verified with
`tests/in/illustrator_prop_markers.svg`, room `phong_kho`, dry-run first, actual
run after dry-run, and render preview enabled. The generated `.ma` opened
successfully in Maya and contained floor, walls, props, camera, and lights.
