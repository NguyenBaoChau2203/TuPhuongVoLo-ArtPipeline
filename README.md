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
| 5 | Maya Bridge | `specs/005-maya-bridge/` | Primary DCC backend; launcher workflow verified |
| 5.5A | AI Polish Preview Evaluation | `docs/ai_polish_preview_evaluation_vi.md` | Documentation only; evaluation complete |
| 5.5B | AI Polish Preview Local Mock | `docs/ai_polish_preview_mock_vi.md` | Mock-only local workflow; no external API |
| 5.5C | AI Polish Preview fal Provider | `docs/ai_polish_preview_fal_vi.md` | Optional fal.ai reference workflow; no required dependency |
| 6 | Natural Language Agent Control | `specs/006-natural-language-agent-control/` | Spec only; not implemented |
| 7 | Artist Desktop App MVP | `specs/007-artist-desktop-app-mvp/` | Local Tkinter wrapper; packaged `.exe` verified on artist/DCC machine |

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

Artist desktop app MVP:

```powershell
python scripts/python/artist_desktop_app.py
python scripts/python/artist_desktop_app.py --version
```

Desktop app packaging dry-run:

```powershell
python scripts/python/package_artist_app.py --dry-run
python scripts/python/package_artist_app.py --version
```

PyInstaller is optional and dev-only. To build a local wrapper executable on a
dev machine that already has PyInstaller installed:

```powershell
python scripts/python/package_artist_app.py --build
```

Generated `build/`, `dist/`, `.spec`, and `.exe` artifacts are local packaging
outputs and must not be committed. The MVP executable still requires the local
repo/pipeline files; it does not bundle Maya or `mayapy.exe`.

AI polish preview optional workflow:

```powershell
python scripts/python/ai_polish_preview.py --help
python scripts/python/ai_polish_preview.py --version
python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png
python scripts/python/ai_polish_preview.py --dry-run --provider fal --input tests/in/sample_preview.png --model fal-ai/flux-pro/kontext
python scripts/python/ai_polish_preview.py --provider fal --input tests/in/sample_preview.png --skip-on-missing-config
```

Phase 005.5B keeps the local `mock` provider. Phase 005.5C adds an optional
`fal` provider for `fal-ai/flux-pro/kontext`. `fal-client` is not a required
dependency; install it only on a machine that will call fal.ai:

```powershell
python -m pip install fal-client
```

Provider `fal` reads the API key only from `FAL_KEY`, never from code or `.env`.
Dry-run does not call API. Missing `FAL_KEY` can be skipped with
`--skip-on-missing-config`, and the Maya-first pipeline continues to work
without AI, API keys, `fal-client`, or internet. AI output is reference-only and
is written under `outputs/ai_preview/` with a versioned `_fal_ai_preview.png`
name plus a JSON report. See `docs/ai_polish_preview_fal_vi.md`.
Phase 005.5B-R verification is recorded in
`docs/verification/005_5B_ai_polish_mock_verified.md`.

Phase 007E adds small release metadata polish. The desktop app shows
`TuPhuongVoLo Maya Artist App v0.7.5 (007E)` in the app title/UI and the
packaging helper prints the same app version during dry-run. See
`docs/release_packaging_checklist_vi.md` for the Vietnamese release packaging
checklist. Phase 007E-R verification is recorded in
`docs/verification/007E_packaging_metadata_verified.md`.

Phase 007B-R verification confirms `dist/TuPhuongVoLo_MayaArtistApp.exe`
launches on the artist/DCC machine, dry-run returns exit code 0, actual Maya
execution returns exit code 0, and generated `.ma` plus PNG preview outputs open
successfully. See `docs/verification/007B_desktop_app_exe_verified.md`.

Phase 007C-R verification confirms the polished packaged `.exe` was rebuilt and
tested on the artist/DCC machine with repo root display, command preview,
dry-run exit code 0, actual Maya run exit code 0, PNG preview generation, and
the expected Maya Outliner structure. See
`docs/verification/007C_desktop_app_polish_verified.md`.

Actual Maya run, when `mayapy.exe` is available:

```powershell
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

Feature 005 MVP actual execution supports `mayapy.exe` only. `maya.exe` and
`mayabatch.exe` support is future work.

## Artist Quickstart

Vietnamese guides:

- [Bàn giao desktop app Maya](docs/artist_handoff_desktop_app_vi.md)
- [Checklist release/packaging desktop app](docs/release_packaging_checklist_vi.md)
- [Hướng dẫn cài đặt](docs/INSTALL_VI.md)
- [Hướng dẫn sử dụng](docs/HOW_TO_USE_FOR_ARTIST_VI.md)
- [Xử lý sự cố](docs/TROUBLESHOOTING_VI.md)
- [Launchers](launchers/README_LAUNCHERS_VI.md)

Core artist flow:

1. Draw/export clean SVG from Illustrator.
2. Optional: run `launchers/00_maya_env_check.bat` to check Python, PyYAML, and `mayapy.exe`.
3. Recommended: run `launchers/09_artist_desktop_app.bat` for a friendly local app wrapper.
4. Developer-only: run `launchers/10_package_artist_app.bat` to dry-run desktop app packaging.
5. Alternative CLI launcher: run `launchers/07_build_maya_room.bat` for one room dry-run before creating `.ma`.
6. Run `launchers/08_batch_maya_room.bat` for multi-SVG or multi-room dry-run/report.
7. After dry-run looks correct, run actual Maya execution and open generated `.ma` scenes from `outputs/maya/` in Maya.

Generated `.ma`, `.png`, `outputs/tmp/`, and normal batch reports are local outputs and should not be committed unless intentionally added as test fixtures.

Phase 005.5A documents the optional AI polish preview stage. Phase 005.5B adds
a local mock preview workflow. Phase 005.5C adds optional fal.ai integration
behind `--provider fal`; it remains reference-only and does not change the Maya
source-of-truth workflow. Feature 006 natural-language control remains deferred.

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

Feature 006 natural-language control/MCP is not implemented. AI polish preview
has a local mock provider and an optional fal.ai provider, but it is still only
a reference-image workflow and does not drive pipeline automation. Actual Maya
scene generation requires local Autodesk Maya with `mayapy.exe`; the 005.4
launcher workflow has been verified on the artist/DCC machine with Maya 2024.

## License

Internal project — not for public distribution.

## Contributing

Follow the Spec-Driven Development workflow:

1. Read `AGENTS.md` and `.specify/constitution.md`.
2. Pick or create a feature under `specs/`.
3. Follow spec -> plan -> tasks -> implement.
4. Run tests before committing.
5. Update manifest only for generated outputs that actually exist.
