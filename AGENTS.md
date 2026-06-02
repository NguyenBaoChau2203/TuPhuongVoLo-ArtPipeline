<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

# TuPhuongVoLo-ArtPipeline — AI Agent Instructions

> **Project**: Art pipeline automation for the indie game "Tứ Phương Vô Lộ"
> **Phase**: Maya-first production workflow verified through 007J-F1
> **Owner**: Artist-developer hybrid workflow

---

## Project Context

This repository contains semi-automated tooling for an indie game art pipeline.
The primary user is a **Vietnamese-speaking artist** working on Windows with:
- **Adobe Illustrator** — 2D vector art, floor plans, top-down maps, isometric illustration
- **Autodesk Maya** — Primary production DCC backend (Python geometry JSON → `.ma` blockout → artist polish)
- **Blender** — Legacy/fallback isometric draft bridge (retained, not required for production)
- **Python** — CLI tools, SVG processing, manifest management, asset naming

The production pipeline flow is:
```
Illustrator authoring / clean SVG export
→ Python SVG cleanup + validation
→ Python room detection + geometry JSON handoff
→ Autodesk Maya .ma blockout (primary production DCC)
→ artist polish in Maya
```

Optional/fallback path (legacy, retained but not required):
```
clean SVG → Blender MVP isometric draft / batch dry-run
```

---

## Core Principles

### 1. Artist-First Automation
Every tool must serve the artist. The artist is NOT a programmer. Tools must:
- Have simple `.bat` launchers on Windows
- Produce clear Vietnamese-language instructions and error messages
- Never require command-line expertise to use basic features

### 2. Windows-First
All scripts, paths, and launchers MUST work on Windows 10/11.
- Use `pathlib` in Python — never hardcode Unix paths
- Use `.bat` launchers — not bash scripts
- Test path separators and long path edge cases
- PowerShell is acceptable for developer tooling; `.bat` for artist-facing tooling

### 3. Script-First / API-First
Prefer programmatic automation over fragile UI automation:
- ✅ Illustrator JSX / ExtendScript
- ✅ Python CLI with `argparse` or `click`
- ✅ Maya Python / MEL / `mayapy` — primary production DCC
- ✅ Blender Python (`bpy`) — legacy/fallback headless batch
- ✅ `.bat` launchers calling scripts
- ❌ No mouse-click macro recording
- ❌ No screen-scraping or pixel-based automation
- ❌ No `pyautogui` or similar fragile approaches

### 4. Non-Destructive Output
- Never overwrite source files (`.ai`, `.svg` originals)
- Always write outputs to `outputs/` or designated output folders
- Every generated file must include version in its filename
- Source folders (`assets/2d/ai_src/`, `assets/2d/svg_raw/`) are read-only targets

### 5. Editable Outputs
Generated outputs must remain editable:
- SVG outputs must be valid, clean SVG that Illustrator can reopen
- Maya outputs must be `.ma` scene files the artist can modify
- Blender outputs (legacy) must be `.blend` scene files the artist can modify
- PNG renders are previews — the editable source must always be preserved

### 6. Manifest & Versioning
- Every pipeline run must produce or update a manifest (CSV/JSON)
- Assets must follow the naming convention in `config/naming_convention.yaml`
- Pattern: `tu_phuong_vo_lo_{asset_name}_{variant}_{stage}_v{version}`
- Stages: raw → traced → svgraw → svgclean → blockout → iso → preview → final_candidate

### 7. Vietnamese Documentation
- All artist-facing documentation must be in Vietnamese
- Developer/agent documentation may be in English
- Error messages shown to the artist should include Vietnamese text
- Files ending in `_VI.md` are Vietnamese documents

### 8. Testing
- Every Python module must have a corresponding test file
- Tests must be runnable with `pytest`
- Test inputs go in `tests/in/`, expected outputs in `tests/out_expected/`
- SVG validation tests must check structure, not pixel-perfect rendering

---

## Spec-Driven Development (SDD) Workflow

Every coding task MUST map to a spec before implementation:

1. **Specify** → `specs/NNN-feature/spec.md`
2. **Plan** → `specs/NNN-feature/plan.md`
3. **Tasks** → `specs/NNN-feature/tasks.md`
4. **Implement** → code changes referencing task IDs
5. **Validate** → `specs/NNN-feature/quickstart.md` verification

Read the current plan at `specs/` before starting any coding work.

---

## Recommended Commands

```powershell
# Run tests
pytest tests/ -v

# Potrace + vpype tracing pipeline (B&W line art)
mkbitmap -f 2 -s 2 -t 0.45 tests/in/motel_room_mask.png -o tests/tmp/motel_room_mask.pbm
potrace tests/tmp/motel_room_mask.pbm -s --group --flat --tight -t 3 -a 1 -O 0.2 -o tests/tmp/motel_room_trace.svg
vpype read tests/tmp/motel_room_trace.svg linemerge --tolerance 0.2mm linesort reloop linesimplify write tests/out/motel_room_clean.svg

# Validate SVG structure (future)
python scripts/python/validate_svg_contract.py --input drops/

# Build Maya room (dry-run)
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --dry-run

# Build Maya room (actual, needs mayapy)
python scripts/python/build_maya_room.py --input tests/in/feature001_kho.svg --room kho --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

---

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `specs/` | Feature specifications (SDD artifacts) |
| `scripts/illustrator/` | Illustrator JSX/ExtendScript automation |
| `scripts/python/` | Python CLI tools |
| `scripts/blender/` | Blender Python automation |
| `scripts/maya/` | Maya Python/MEL automation |
| `launchers/` | Windows `.bat` launchers for artist |
| `config/` | YAML configuration files |
| `assets/` | Source art assets (read-only for pipeline) |
| `drops/` | Artist drops files here for processing |
| `outputs/` | All generated outputs go here |
| `tests/` | Test files and fixtures |
| `docs/` | Documentation (Vietnamese artist docs + English dev docs) |
| `docs/research/` | Research source documents (English + Vietnamese) |
| `skills/` | Reusable AI agent skill definitions |
| `.cursor/rules/` | Cursor IDE rule files |

---

## DO NOT

- ❌ Do NOT implement production algorithms in placeholder scripts
- ❌ Do NOT install Python packages without updating `requirements.txt`
- ❌ Do NOT hardcode absolute paths — use `pathlib.Path` and config
- ❌ Do NOT overwrite files in `assets/` or `drops/`
- ❌ Do NOT assume Blender/Maya/Illustrator are installed — check and warn
- ❌ Do NOT use `pyautogui`, `keyboard`, or screen-based automation
- ❌ Do NOT write English-only artist documentation
- ❌ Do NOT skip creating a manifest entry for generated outputs
- ❌ Do NOT create features without a spec/plan/tasks first
- ❌ Do NOT delete or move the artist's original source files
- ❌ Do NOT call external APIs without explicit approval
- ❌ Do NOT generate outputs directly into source folders
- ❌ Do NOT skip the naming convention — all outputs must follow the pattern

---

## Research Incorporated

The following research documents inform this project's architecture and tooling decisions:

| Document | Language | Key Contributions |
|----------|----------|--------------------|
| `docs/research/Indie Game Art Workflow Automation Research.md` | English | Tool comparison tables (AI vectorizers, 2D map generators, 2D-to-3D pipelines), GitHub repo registry (Illustrator_MCP, illustrator-scripts, FloorplanToBlender3d, IsometricTransform.jsx), three-tier workflow (Beginner / Semi-Automated / Advanced Agentic), 7-day and 30-day setup plans, contextual prompt engineering suite |
| `docs/research/Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ.md` | Vietnamese | Version-locked toolchain recommendations, three-layer architecture (2D authoring / cleanup-vector-processing / 3D-isometric), SVG quality-gate criteria, concrete code samples for Potrace+vpype+svgpathtools pipeline, Maya SVG import limitation analysis, naming agent CLI design, test case design (motel room + island map) |

Research-confirmed decisions:
- **Tier B (Semi-Automated)** is the recommended production baseline
- **Potrace 1.16** for B&W deterministic tracing; **Vectorizer.AI** for color/transparency
- **vpype 1.15.0** pipeline: `read → linemerge → linesort → reloop → linesimplify → write`
- **svgpathtools 1.7.2** for rule-based cleanup: filter by path length, bbox size, area
- **Maya** as primary production DCC backend; **Blender LTS 4.x** as legacy/fallback
- **Illustrator 29.8.7 LTS** for production; 30.4 for R&D only
- Two mandatory test cases: **motel room** (interior, walls, furniture) and **island map** (coastline, paths, cleanup)

