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

Optional if installed:

```powershell
python -m ruff check scripts/python tests
```

## Artist Launchers

- Single room dry-run: `launchers/07_build_maya_room.bat`
- Batch dry-run/report: `launchers/08_batch_maya_room.bat`

Actual Maya execution pending local Maya verification.
