# Quickstart: Door/Window SVG Marker Diagnostics

## Artist Check

1. Export the Illustrator room SVG without minifying names.
2. Run preflight:

```powershell
python scripts/python/svg_preflight_check.py --input drops/ten_file.svg
```

3. If the output says `Door/window marker: 1` and lists `door_main` or
   `window_*`, the Maya dry-run can emit opening markers.
4. If the output says `Door/window marker: 0`, the SVG export did not preserve
   any explicit `door_` or `window_` marker name. Maya will not create a door.

## Developer Validation

```powershell
python scripts/python/svg_preflight_check.py --help
python scripts/python/build_maya_room.py --help
python scripts/python/artist_desktop_app.py --version
pytest tests/ -v --ignore=tests/tmp
```

Expected behavior:

- `id="door_main"` emits `marker_type=door`, `marker_name=main`.
- `data-name="door_main"` with a generic id also emits the marker.
- `aria-label`, `title`, and child `<title>` marker names are detected.
- A rectangle that only looks like a door is ignored unless it has an explicit
  `door_` or `window_` label/name.
