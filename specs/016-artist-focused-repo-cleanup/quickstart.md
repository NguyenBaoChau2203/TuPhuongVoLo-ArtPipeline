# Quickstart: Artist-Focused Repo Cleanup Verification

## 1. Confirm Daily Entry Points

Open these files:

```powershell
notepad README.md
notepad docs\WORKFLOW_FOR_WIFE_VI.md
notepad docs\CODEX_PROMPTS_VI.md
```

Expected:

- README starts with the single daily workflow.
- `docs\WORKFLOW_FOR_WIFE_VI.md` explains the artist/operator steps in Vietnamese.
- `docs\CODEX_PROMPTS_VI.md` contains copyable prompts for JSX draft and Maya polish.

## 2. Confirm Templates Exist

```powershell
Test-Path scripts\illustrator\templates\reference_to_layout_draft.jsx
Test-Path scripts\maya\agent_polish_templates\agent_polish_additive_template.py
Test-Path launchers\08_create_maya_sandbox.bat
```

Expected: all commands print `True`.

## 3. Run Core Dry-Run Workflow Without Maya

```powershell
python scripts\python\svg_preflight_check.py --input tests\in\illustrator_prop_markers.svg

python scripts\python\build_maya_room.py `
  --input tests\in\illustrator_prop_markers.svg `
  --room phong_kho `
  --dry-run
```

Expected:

- Preflight returns `OK` or `WARNING`, not `FATAL`.
- Maya build dry-run prints planned `.ma` and geometry JSON paths.
- No Maya process is launched and no manifest is written.

## 4. Run Targeted Tests

```powershell
python -m pytest `
  tests\test_svg_preflight_check.py `
  tests\test_build_maya_room.py `
  tests\test_artist_desktop_app.py `
  tests\test_maya_visual_fidelity_pass.py `
  tests\test_maya_agent_sandbox.py `
  -q
```

Expected: all targeted tests pass.

## 5. Confirm Post-Build App/Launcher Surface

Open the desktop app:

```powershell
launchers\09_artist_desktop_app.bat
```

Expected:

- The app contains buttons for `Tự tìm output mới nhất`, `Tạo Visual Fidelity`, `Tạo Maya Sandbox`, and `Mở working/scene_agent_work.ma`.
- The sandbox launcher `launchers\08_create_maya_sandbox.bat` exists as the no-app fallback.

## 6. Optional Full Test Suite

```powershell
python -m pytest tests --ignore=tests/tmp -q
```

Expected: full source tests pass. The `--ignore=tests/tmp` flag avoids local Windows temp permission issues from prior pytest runs.

## 7. Confirm No Generated Output Was Added

```powershell
git status --short
```

Expected: only intentional docs/spec/template/archive cleanup files appear. Generated outputs under `outputs/`, `tests/tmp/`, `.pytest_cache/`, external Maya/Illustrator backups, or source `.ai` files must not appear.
