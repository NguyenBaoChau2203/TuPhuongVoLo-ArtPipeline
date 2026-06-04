# Phase 007B-R Verification Checkpoint: Packaged Desktop App .exe

## Branch

`workflow/maya-first-artist-pipeline`

## Verification Environment

- Windows artist/DCC machine
- Repo path: `D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline`
- Maya 2024
- `mayapy.exe`: `C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`

## Related Commits

- `6d5a3b6` feat: add artist desktop app MVP
- `c1854aa` chore: add desktop app packaging workflow
- `26e0216` fix: allow PyInstaller module fallback for app packaging
- `e6bd05b` fix: resolve repo root and Python command for packaged app

## Packaging Verification Flow

1. Pulled the latest `workflow/maya-first-artist-pipeline` branch on the DCC machine.
2. Installed or confirmed PyInstaller on the DCC machine.
3. Built the local executable:

```powershell
python scripts/python/package_artist_app.py --clean-output --build
```

4. Launched the packaged app:

```powershell
dist/TuPhuongVoLo_MayaArtistApp.exe
```

## App Verification Flow

- SVG: `tests\in\illustrator_prop_markers.svg`
- Room: `phong_kho`
- Output folder: `outputs`
- Render preview: enabled
- First run: dry-run enabled
- Dry-run result: exit code 0
- Second run: dry-run disabled for actual Maya execution
- Actual run result: exit code 0

## Verified Outputs

- `.ma` scene generated under `outputs/maya/`
- PNG preview generated under `outputs/preview/`
- Generated `.ma` opened in Maya successfully
- Maya Outliner includes:
  - `GRP_phong_kho_blockout`
  - `walls`
  - `props`
  - `prop_shelf_unit_01`
  - `prop_wooden_crate_01`
  - `lights`
  - `floor_blockout`

## Safety Confirmations

- The `.exe` is a generated local build artifact and is not committed.
- `build/` is not committed.
- `dist/` is not committed.
- `*.exe` is not committed.
- `*.spec` is not committed.
- `outputs/tmp/`, `outputs/maya/`, `outputs/preview/`, and `outputs/reports/` generated files are not committed.
- The app still wraps the verified CLI pipeline.
- The app does not parse SVG directly.
- The app does not bundle Maya or `mayapy.exe`.
- The app does not call external APIs.

## Known Limitations

- The `.exe` is still a local wrapper and needs the repo/pipeline files available.
- Python is still needed by the packaged wrapper to run pipeline scripts unless a future packaging design changes this.
- Maya and `mayapy.exe` must be installed separately.
- The UI is MVP/basic Tkinter, not final polished UX.

## Recommended Next Step

- Continue with 007C desktop app UX/reliability polish.
- 005.5A AI polish remains optional/evaluation-only.
- Feature 006 remains deferred.
