# Quickstart: Visual Fidelity MVP

## Dry-Run Without Maya

```powershell
python scripts/python/maya_visual_fidelity_pass.py `
  --geometry-json "D:\path\to\tu_phuong_vo_lo_phong_kho_main_blockout_v017.json" `
  --preset warehouse_v0 `
  --dry-run `
  --report-json "D:\path\to\visual_fidelity_report_014A.json"
```

Expected:

- Exit code 0.
- Report JSON exists.
- No `.ma` scene is created.
- Report contains `room_name`, `prop_counts`, `planned_additions`, `warnings`, and `safety_status`.

## Actual Apply With Maya

```powershell
python scripts/python/maya_visual_fidelity_pass.py `
  --input-scene "D:\path\to\source_scene.ma" `
  --geometry-json "D:\path\to\blockout.json" `
  --output-scene "D:\path\to\tu_phuong_vo_lo_phong_kho_main_maya_visual_fidelity_v018.ma" `
  --preset warehouse_v0 `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --verbose
```

Expected:

- Source `.ma` is unchanged.
- Output `.ma` exists at a different path.
- Maya Outliner contains top-level `GRP_visual_fidelity_v0`.
- Crates, barrels, shelves, floor grate, electrical cabinet, camera, lights, and notes are agent-owned.

## Validation Commands

```powershell
python scripts/python/maya_visual_fidelity_pass.py --help
python scripts/python/maya_visual_fidelity_pass.py --geometry-json outputs/tmp/tu_phuong_vo_lo_phong_kho_main_blockout_v017.json --preset warehouse_v0 --dry-run
python -m pytest tests/test_maya_visual_fidelity_pass.py -v
python -m pytest tests/ -v
```

Note: replace the geometry JSON path with the actual `outputs/tmp/*.json` produced by `build_maya_room.py`.
