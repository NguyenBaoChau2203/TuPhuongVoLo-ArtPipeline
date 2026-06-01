# Phase 007C-R Verification Checkpoint: Desktop App UX/Reliability Polish

## Branch

`workflow/maya-first-artist-pipeline`

## Related Commits

- `d81fe74` docs: add desktop app exe verification checkpoint
- `3d278b8` feat: polish artist desktop app reliability

No later relevant implementation commit was present in `git log --oneline -15`
before this checkpoint document was created.

## What 007C Changed

- Repo root display
- Command preview
- Clear log button
- Copy command button
- Status label
- Run button lock/unlock while subprocess is running
- Command and exit code logging
- Vietnamese pre-run validation for common artist-facing errors

## DCC Verification Environment

- Windows artist/DCC machine
- Repo path: `D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline`
- Maya 2024
- `mayapy.exe`: `C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`

## Rebuild Command

```powershell
python scripts/python/package_artist_app.py --clean-output --build
```

## App Test Inputs

- SVG: `tests\in\illustrator_prop_markers.svg`
- Room: `phong_kho`
- Output: `outputs`
- Render preview: enabled
- First run: dry-run enabled
- Second run: dry-run disabled for actual Maya execution
- `mayapy.exe`: `C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`

## Verified Results

- Packaged `.exe` launches.
- Repo root display appears.
- Command preview appears.
- Dry-run returns exit code 0.
- Actual Maya run returns exit code 0.
- Generated `.ma` opens successfully in Maya.
- PNG preview is generated.
- Expected Outliner hierarchy appears.

## Verified Outliner Structure

- `GRP_phong_kho_blockout`
- `walls`
- `wall_01`
- `wall_02`
- `wall_03`
- `wall_04`
- `props`
- `prop_shelf_unit_01`
- `prop_wooden_crate_01`
- `lights`
- `cam_phong_kho_iso1`
- `key_light`
- `ambient_light`
- `floor_blockout`

Maya default sets such as `defaultLightSet` and `defaultObjectSet` may also
appear in the Outliner. They are normal Maya defaults, not pipeline errors.

## Safety Confirmations

- Generated `.exe` is not committed.
- `build/` is not committed.
- `dist/` is not committed.
- `*.spec` is not committed.
- Generated files under `outputs/maya/`, `outputs/preview/`, `outputs/tmp/`,
  and `outputs/reports/` are not committed.
- The app remains a wrapper around `scripts/python/build_maya_room.py`.
- The app does not parse SVG directly.
- The app does not bundle Maya or `mayapy.exe`.
- The app does not call external APIs.

## Known Limitations

- UI is improved but still MVP Tkinter.
- `.exe` still needs local repo/pipeline files.
- `.exe` still needs external Python.
- Actual run still needs Autodesk Maya and `mayapy.exe` installed.
- Generated blockout is not final art; artist polish in Maya is still required.

## Recommended Next Step

Preferred:

- 007D artist handoff / release packaging notes / usability checklist

Optional later:

- 005.5A AI polish evaluation only, after API/cost/privacy/secrets policy is ready

Still deferred:

- Feature 006 natural-language control
