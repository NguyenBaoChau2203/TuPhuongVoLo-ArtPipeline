# Quickstart: Artist Desktop App MVP

## Run From Source

```powershell
python scripts/python/artist_desktop_app.py
```

## Run With Launcher

```powershell
launchers/09_artist_desktop_app.bat
```

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
pytest tests/test_artist_desktop_app.py -v
```

## Notes

The app is a local MVP wrapper. It does not replace Maya, does not parse SVG
directly, and does not modify source SVG files.

