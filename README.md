# TuPhuongVoLo-ArtPipeline

Semi-automated art pipeline for **Tứ Phương Vô Lộ**, focused on helping a Vietnamese-speaking artist move quickly from reference images to editable Maya scenes.

## Daily Workflow

```text
Reference image + Vietnamese description
-> Codex creates an Illustrator JSX draft
-> Artist opens the JSX result in Illustrator, edits by eye, exports SVG
-> Desktop app checks SVG, runs dry-run, builds editable Maya .ma
-> Optional Visual Fidelity pass
-> Maya sandbox copy
-> Codex creates Maya Python polish script
-> Artist reviews by toggling groups, keeps changes or rolls back
```

The repo is the safe production spine. Codex helps at two high-friction points: making an Illustrator draft from a reference and adding sandbox-only Maya polish.

## Start Here

For the artist/operator:

- [Daily workflow for wife/artist](docs/WORKFLOW_FOR_WIFE_VI.md)
- [Copyable Codex prompts](docs/CODEX_PROMPTS_VI.md)
- [Launcher guide](launchers/README_LAUNCHERS_VI.md)

Open the desktop app:

```powershell
launchers\09_artist_desktop_app.bat
```

The app wraps the verified CLI pipeline. It also includes buttons for `Tự tìm output mới nhất`, `Tạo Visual Fidelity`, `Tạo Maya Sandbox`, and `Mở working/scene_agent_work.ma`. It does not edit source `.ai` or `.svg` files.

## Core Commands

Check environment:

```powershell
launchers\00_maya_env_check.bat
```

Preflight an exported SVG:

```powershell
python scripts\python\svg_preflight_check.py --input "drops\scene_export.svg"
```

Run a safe Maya dry-run:

```powershell
python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --dry-run
```

Build the editable Maya scene when dry-run looks right:

```powershell
python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --render-preview
```

Optional Visual Fidelity pass, easiest from the desktop app button `Tạo Visual Fidelity`:

```powershell
python scripts\python\maya_visual_fidelity_pass.py `
  --input-scene "outputs\maya\scene.ma" `
  --geometry-json "outputs\tmp\scene.json" `
  --output-scene "outputs\maya\scene_visual_fidelity.ma" `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

Create a Maya sandbox before any AI/Codex polish, easiest from the desktop app button `Tạo Maya Sandbox` or the launcher:

```powershell
launchers\08_create_maya_sandbox.bat
```

CLI fallback:

```powershell
python scripts\python\maya_agent_sandbox.py `
  --maya-scene "outputs\maya\scene.ma" `
  --room phong_kho `
  --backup-root "D:\TuPhuongVoLo_AgentBackups"
```

Only open the sandbox working file in Maya:

```text
...\working\scene_agent_work.ma
```

## Output Folders

```text
outputs\maya\       editable Maya .ma scenes
outputs\preview\    PNG previews
outputs\tmp\        geometry JSON handoff files
outputs\reports\    preflight/batch reports
```

Generated outputs are local working files. Do not commit `.ma`, generated `.svg`, `.json`, `.png`, `.zip`, `.exe`, or sandbox backups unless a feature explicitly turns one into a test fixture.

## Templates

Codex can copy these starters and customize them for each reference image or scene:

- `scripts\illustrator\templates\reference_to_layout_draft.jsx`
- `scripts\maya\agent_polish_templates\agent_polish_additive_template.py`

Use [docs/CODEX_PROMPTS_VI.md](docs/CODEX_PROMPTS_VI.md) when asking Codex to create a scene-specific JSX or Maya Python script.

## Core Files To Keep In Mind

```text
scripts\python\svg_preflight_check.py
scripts\python\build_maya_room.py
scripts\python\artist_desktop_app.py
scripts\python\maya_visual_fidelity_pass.py
scripts\python\maya_agent_sandbox.py
scripts\maya\build_maya_room_scene.py
scripts\maya\apply_visual_fidelity_pass.py
config\naming_convention.yaml
config\pipeline.yaml
```

## Legacy And Optional Work

Older experiments and optional workflows are intentionally out of the daily path. See [archive/README.md](archive/README.md).

Blender/isometric code is retained as a tested legacy fallback, but Maya is the primary production DCC backend. AI polish preview, natural-language MCP control, packaging experiments, old verification notes, and long research docs are reference material, not daily artist steps.

## Developer Verification

Install dependencies as needed:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run focused checks for the current production spine:

```powershell
python -m pytest `
  tests\test_svg_preflight_check.py `
  tests\test_build_maya_room.py `
  tests\test_artist_desktop_app.py `
  tests\test_maya_visual_fidelity_pass.py `
  tests\test_maya_agent_sandbox.py `
  -q
```

Full local suite, ignoring a Windows temp folder that can be permission-locked by previous runs:

```powershell
python -m pytest tests --ignore=tests/tmp -q
```

## Development Rules

Follow Spec-Driven Development:

```text
specs/NNN-feature/spec.md
-> specs/NNN-feature/plan.md
-> specs/NNN-feature/tasks.md
-> implementation
-> quickstart verification
```

Read `AGENTS.md` and `.specify/constitution.md` before coding. Artist-facing docs stay Vietnamese. Windows `.bat` launchers stay the friendly entry point.
