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
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --maya-path "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe"
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
- Dry-run prints planned `.ma`, geometry JSON, and preview PNG paths
- Manifest is not updated

Actual Maya render on a DCC machine:

```powershell
python scripts/python/build_maya_room.py `
  --input tests/in/illustrator_prop_markers.svg `
  --room phong_kho `
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
Autodesk Maya 2024 and `mayapy.exe`. The generated `.ma` opened successfully in
Maya and contained floor, walls, props, camera, and lights.
