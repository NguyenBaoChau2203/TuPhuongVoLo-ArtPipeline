# Quickstart: Artist Desktop App MVP

## Run From Source

```powershell
python scripts/python/artist_desktop_app.py
```

## Run With Launcher

```powershell
launchers/09_artist_desktop_app.bat
```

## Package App Dry-Run

```powershell
launchers/10_package_artist_app.bat
python scripts/python/package_artist_app.py --dry-run
```

## Package App Build

```powershell
python scripts/python/package_artist_app.py --build
```

PyInstaller is optional and dev-only. Generated `build/`, `dist/`, `.spec`, and
`.exe` files are local packaging outputs and should not be committed. The MVP
`.exe` still needs the local repo/pipeline files and does not bundle Maya or
`mayapy.exe`.

## Package App Verification Checkpoint

Phase 007B-R verified `dist/TuPhuongVoLo_MayaArtistApp.exe` on the artist/DCC
machine. The app launched successfully, dry-run returned exit code 0, actual
Maya execution returned exit code 0, and the run generated an editable `.ma`
scene plus PNG preview. Details are documented in
`docs/verification/007B_desktop_app_exe_verified.md`.

## Phase 007C UX/Reliability Polish

The app now validates common artist mistakes before launching subprocesses:
missing SVG, missing SVG file, empty room name, empty output folder, missing repo
root, missing `build_maya_room.py`, actual run without valid `mayapy.exe`, and
frozen `.exe` mode without an external Python command.

It also shows the detected repo root, keeps relative paths predictable from the
repo root, previews/copies the exact command, logs the command and exit code,
shows run status, and disables the run button while the command is active.

The packaged `.exe` remains a local wrapper. It still needs repo files, external
Python, Maya, and a valid `mayapy.exe` path for actual runs. Generated `build/`,
`dist/`, `.exe`, `.spec`, `.ma`, `.png`, and normal `outputs/` artifacts must not
be committed.

## Recommended Artist Flow

1. Select a clean SVG file.
2. Keep dry-run enabled for the first run.
3. Enter the room name, for example `phong_kho`.
4. Enable PNG preview if a preview image is needed.
5. Review the command and log output in the app.
6. For actual Maya execution, disable dry-run and provide `mayapy.exe`.

## Validation

```powershell
python scripts/python/artist_desktop_app.py --help
python scripts/python/package_artist_app.py --dry-run
pytest tests/test_artist_desktop_app.py tests/test_package_artist_app.py -v
pytest tests/ -v --ignore=tests/tmp
```

## Notes

The app is a local MVP wrapper. It does not replace Maya, does not parse SVG
directly, and does not modify source SVG files.
