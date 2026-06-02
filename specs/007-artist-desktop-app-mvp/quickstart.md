# Quickstart: Artist Desktop App MVP

## Run From Source

```powershell
python scripts/python/artist_desktop_app.py
python scripts/python/artist_desktop_app.py --version
```

## Run With Launcher

```powershell
launchers/09_artist_desktop_app.bat
```

## Package App Dry-Run

```powershell
launchers/10_package_artist_app.bat
python scripts/python/package_artist_app.py --dry-run
python scripts/python/package_artist_app.py --version
```

## Package App Build

```powershell
python scripts/python/package_artist_app.py --build
```

PyInstaller is optional and dev-only. Generated `build/`, `dist/`, `.spec`, and
`.exe` files are local packaging outputs and should not be committed. The MVP
`.exe` still needs the local repo/pipeline files and does not bundle Maya or
`mayapy.exe`.

## Phase 007E Packaging Metadata Polish

The desktop app has a small version constant and shows
`TuPhuongVoLo Maya Artist App v0.7.7 (007I)` in the app title/UI. The app CLI
supports `--version`, and the packaging helper prints the same app version
during dry-run and supports its own `--version`.

Vietnamese release packaging checklist:

```text
docs/release_packaging_checklist_vi.md
```

## Phase 007G Optional AI Polish Preview

The desktop app now includes a separate AI polish preview section. The artist or
dev operator must explicitly select an existing PNG preview and click
`Tạo AI polish preview`; AI is not called automatically after a Maya run.

The AI button wraps the existing CLI:

```powershell
python scripts/python/ai_polish_preview.py
```

Default desktop behavior is safe: provider `mock`, `AI dry-run` enabled, and
`Bỏ qua nếu thiếu cấu hình AI` enabled. Provider `fal` remains optional and
requires optional `fal-client` plus `FAL_KEY` only when the operator chooses a
real non-dry-run fal call. AI output is reference-only and goes to:

```text
outputs/ai_preview/
```

The Maya `.ma` scene remains the source of truth. The AI workflow does not
modify SVG, geometry JSON, Maya scene generation, render logic, manifests,
source assets, or Feature 006 natural-language control.

## Phase 007I Guide and Template UX Polish

The desktop app groups controls into clearer sections:

- `Step 1: Chọn SVG và phòng`
- `Step 2: Maya output / render preview`
- `Step 3: Hướng dẫn & template`
- `Step 4: AI polish preview tùy chọn`
- `Log / trạng thái`

The guide/template section opens:

- `docs/artist_workflow_cat_guide_vi.html`
- `assets/2d/templates/illustrator_prop_marker_template.svg`
- `assets/2d/templates/`

It can also copy the SVG template path to the clipboard. Missing guide/template
files should produce friendly Vietnamese status/log messages instead of
crashing.

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

## Phase 007C-R Verification Checkpoint

Phase 007C-R verified the polished packaged `.exe` on the artist/DCC machine.
The rebuilt app launched successfully, showed repo root and command preview,
dry-run returned exit code 0, actual Maya execution returned exit code 0, and
the generated `.ma` opened in Maya with the expected Outliner structure. Details
are documented in `docs/verification/007C_desktop_app_polish_verified.md`.

## Phase 007D Handoff Checklist

The artist/developer handoff checklist is documented in
`docs/artist_handoff_desktop_app_vi.md`. It covers DCC repo update commands,
safe dry-run and actual Maya run steps, expected `phong_kho` Outliner contents,
local packaging notes, and generated artifacts that must not be committed.

## Recommended Artist Flow

1. Select a clean SVG file.
2. Keep dry-run enabled for the first run.
3. Enter the room name, for example `phong_kho`.
4. Enable PNG preview if a preview image is needed.
5. Use `Mở hướng dẫn` or `Mở SVG mẫu marker` if marker naming help is needed.
6. Review the command and log output in the app.
7. For actual Maya execution, disable dry-run and provide `mayapy.exe`.

## Validation

```powershell
python scripts/python/artist_desktop_app.py --help
python scripts/python/artist_desktop_app.py --version
python scripts/python/ai_polish_preview.py --help
python scripts/python/ai_polish_preview.py --version
python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png
python scripts/python/ai_polish_preview.py --dry-run --provider fal --input tests/in/sample_preview.png --model fal-ai/flux-pro/kontext
python scripts/python/ai_polish_preview.py --provider fal --input tests/in/sample_preview.png --skip-on-missing-config
python scripts/python/package_artist_app.py --dry-run
python scripts/python/package_artist_app.py --version
pytest tests/test_artist_desktop_app.py tests/test_ai_polish_preview.py tests/test_package_artist_app.py -v
pytest tests/ -v --ignore=tests/tmp
```

## Notes

The app is a local MVP wrapper. It does not replace Maya, does not parse SVG
directly, and does not modify source SVG files.
