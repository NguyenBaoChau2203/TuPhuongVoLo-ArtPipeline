# TuPhuongVoLo-ArtPipeline

> Semi-automated art pipeline for the indie game **Tứ Phương Vô Lộ**

## Project Purpose

This repository provides semi-automated tooling for an indie game art pipeline. The production workflow is Illustrator-first and Maya-first: artists draw in Adobe Illustrator, Python validates/translates clean SVG geometry, and Autodesk Maya receives editable `.ma` blockout scenes for polish.

Blender support remains in the repo as the previous MVP/fallback backend. It is not required for Feature 005.

## Pipeline Flow

```text
Illustrator authoring / clean SVG export
    -> Python SVG cleanup + validation
    -> Python room detection + geometry JSON handoff
    -> Maya .ma room blockout
    -> artist polish in Maya
```

Optional/fallback path:

```text
clean SVG -> Blender MVP isometric draft / batch dry-run
```

## Feature Status

| Order | Feature | Spec | Status |
|-------|---------|------|--------|
| 1 | Illustrator Export & Clean SVG | `specs/002-illustrator-export-clean-svg/` | Done |
| 2 | Asset Naming & Manifest | `specs/003-asset-naming-and-manifest/` | Done |
| 3 | Floorplan to Isometric Room | `specs/001-floorplan-to-isometric-room/` | MVP done; Blender optional/fallback |
| 4 | Batch Isometric Render | `specs/004-batch-isometric-render/` | MVP dry-run/report for previous backend |
| 5 | Maya Bridge | `specs/005-maya-bridge/` | Primary DCC backend MVP |
| 6 | Natural Language Agent Control | `specs/006-natural-language-agent-control/` | Spec only; not implemented |

## Developer Quickstart

Prerequisites:

- Python 3.11+
- Git
- Optional: Adobe Illustrator for Feature 002 authoring/export
- Optional: Autodesk Maya with `mayapy.exe` for actual Feature 005 `.ma` generation
- Optional: Blender 4.x for legacy/fallback Feature 001/004 execution

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest tests/ -v
```

Feature 005 dry-run without Maya:

```powershell
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --dry-run
python scripts/python/batch_maya_room.py --input-dir tests/in --dry-run --json-report outputs/reports/batch_maya_report.json
```

Actual Maya run, when `mayapy.exe` is available:

```powershell
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --maya-path "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe"
```

Feature 005 MVP actual execution supports `mayapy.exe` only. `maya.exe` and
`mayabatch.exe` support is future work.

## Artist Quickstart

Vietnamese guides:

- [Hướng dẫn cài đặt](docs/INSTALL_VI.md)
- [Hướng dẫn sử dụng](docs/HOW_TO_USE_FOR_ARTIST_VI.md)
- [Xử lý sự cố](docs/TROUBLESHOOTING_VI.md)
- [Launchers](launchers/README_LAUNCHERS_VI.md)

Core artist flow:

1. Draw/export clean SVG from Illustrator.
2. Run `launchers/07_build_maya_room.bat` for one room dry-run.
3. Run `launchers/08_batch_maya_room.bat` for multi-SVG or multi-room planning.
4. Open generated `.ma` scenes from `outputs/maya/` in Maya after actual Maya execution.

## Repository Structure

```text
TuPhuongVoLo-ArtPipeline/
├─ specs/                       # Feature specifications (SDD)
├─ scripts/
│  ├─ illustrator/              # JSX/ExtendScript
│  ├─ python/                   # Python CLI tools
│  ├─ blender/                  # Legacy/fallback Blender Python
│  └─ maya/                     # Maya Python scripts
├─ launchers/                   # Windows .bat launchers
├─ config/                      # YAML configuration
├─ assets/                      # Source art assets
├─ drops/                       # Artist drop folder
├─ outputs/                     # Generated outputs
├─ tests/                       # Python tests and fixtures
└─ docs/                        # Vietnamese artist docs + developer docs
```

## Not Implemented

Feature 006 natural-language control/MCP is not implemented. Actual Maya scene generation requires local Autodesk Maya with `mayapy.exe` and is environment-dependent.

## License

Internal project — not for public distribution.

## Contributing

Follow the Spec-Driven Development workflow:

1. Read `AGENTS.md` and `.specify/constitution.md`.
2. Pick or create a feature under `specs/`.
3. Follow spec -> plan -> tasks -> implement.
4. Run tests before committing.
5. Update manifest only for generated outputs that actually exist.
