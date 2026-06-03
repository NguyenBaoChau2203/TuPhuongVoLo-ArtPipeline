# TuPhuongVoLo-ArtPipeline Constitution

## Core Principles

### I. Artist-First Automation
The pipeline exists to reduce the artist's repetitive manual work, not to replace artistic decisions. Every tool, script, and workflow must be usable by a non-programmer artist on Windows. If a tool requires terminal expertise to use, it must also have a `.bat` launcher. Artist-facing instructions and error messages must be in Vietnamese.

### II. Non-Destructive Generation
No script or tool may overwrite, delete, or modify the artist's original source files (`.ai`, raw `.svg`, reference images). All generated outputs go to `outputs/` or designated output directories. Every output file includes a version number in its name.

### III. Rebuildable Outputs
Any generated output (PNG preview, Maya scene, cleaned SVG) must be fully reproducible from the clean SVG source + config + presets. If the source and config are intact, the output can be regenerated. No "magic" one-time transforms.

### IV. SVG as Clean Source of Truth
The clean, validated SVG is the canonical intermediate format between Illustrator and 3D tools. All downstream tools (Blender, Maya, renderers) consume clean SVG. The SVG cleaning pipeline (vpype + svgpathtools validation) is the quality gate.

A clean SVG must satisfy these gate criteria:
- Walls and room boundaries are **closed paths** (no open endpoints)
- No self-intersecting paths on wall geometry
- No zero-length paths or sub-pixel runt paths from tracing errors
- All transforms flattened (no nested `transform` attributes)
- Layer/group names describe the element (e.g., `room_kho`, not `Layer 1`)
- No embedded raster images in geometry layers
- No live Illustrator effects — appearances must be expanded before export

### V. Windows-First Setup
All tools, paths, scripts, and launchers must work on Windows 10/11 as the primary platform. Use `pathlib` for paths in Python. Provide `.bat` launchers for common operations. Never assume Unix-only tools.

### VI. Script/API-First Automation
Automation must use scripting APIs, not fragile UI macro recording:
- Illustrator: JSX / ExtendScript
- Python: CLI tools with argparse/click
- Blender: bpy Python API (headless batch mode preferred)
- Maya: mayapy / Maya Python / MEL
- No pyautogui, no mouse-click recording, no screen scraping

### VII. Illustrator as 2D Authoring Tool
Adobe Illustrator remains the artist's primary 2D authoring tool. The pipeline does not replace Illustrator — it automates export, cleanup, and downstream processing. Illustrator JSX scripts assist but do not alter the artist's creative workflow.

### VIII. Maya as Primary Production DCC Backend
Maya is the primary production DCC backend for SVG → 3D blockout generation. The verified production workflow is:
- Python SVG parser extracts geometry JSON from clean SVG (Python owns all SVG parsing)
- `mayapy` consumes geometry JSON to build editable `.ma` blockout scenes
- Artist polishes the `.ma` scene directly in Maya
- Optional PNG preview rendering via `mayapy`
- `mayapy.exe` path is user-configurable

Maya scripts live in `scripts/maya/` and `specs/005-maya-bridge/`.

> **Research finding**: No first-party SVG import for Maya was confirmed in official Autodesk product help. The production path uses a custom Python parser (`svgpathtools` + `room_geometry.py`) → geometry JSON → `mayapy` scene builder.

### IX. Blender as Legacy/Fallback Draft Bridge
Blender is retained as a legacy/fallback isometric draft bridge. It is not required for the primary production workflow but must not be removed or broken. Blender integration uses `bpy` Python API in headless batch mode. Blender scripts live in `scripts/blender/` and related launchers remain functional.

### X. Natural-Language Control is Future Layer
MCP-based or agent-based natural language control of the pipeline is a roadmap feature (Feature 006), not a v1 requirement. It must depend on Features 001–004 being functional first. Do not implement NLC before the core pipeline works.

> **Research reference**: Two MCP server implementations for Illustrator exist — `jinkeda/Illustrator_MCP` (CEP WebSocket + ExtendScript, MIT) and `krVatsal/illustrator-mcp` (COM automation on Windows, stdio transport, MIT). These may serve as future integration points for Tier C / Advanced Agentic workflow.

### XI. Spec-Driven Development (SDD)
Every feature must have:
- `spec.md` — what and why
- `plan.md` — how (technical design)
- `tasks.md` — actionable checklist
- `quickstart.md` — how to verify it works
No coding work begins without an approved spec. The spec is the contract.

### XII. Naming Convention & Manifest
Every generated asset must follow the naming convention defined in `config/naming_convention.yaml`:
```
tu_phuong_vo_lo_{asset_name}_{variant}_{stage}_v{version}
```
Every pipeline run must produce or update a manifest (CSV/JSON) in `outputs/manifest/`.

### XIII. Vietnamese Artist Documentation
All artist-facing documentation must be written in Vietnamese. This includes:
- Installation guides (`docs/INSTALL_VI.md`)
- Usage guides (`docs/HOW_TO_USE_FOR_ARTIST_VI.md`)
- Troubleshooting (`docs/TROUBLESHOOTING_VI.md`)
- Launcher READMEs (`launchers/README_LAUNCHERS_VI.md`)
- Drop folder instructions (`drops/README_DROP_FILES_HERE_VI.md`)

## Technology Stack (Version-Locked)

Research recommends locking specific versions for production stability.

| Layer | Tool | Locked Version | Role |
|-------|------|----------------|------|
| 2D Authoring | Adobe Illustrator | **29.8.7 LTS** (prod) / **30.4** (R&D only) | Source art creation |
| 2D Export | Illustrator JSX/ExtendScript | (bundled with Illustrator) | Automated clean SVG export |
| Vectorization (B&W) | Potrace + mkbitmap | **1.16** | Deterministic line-art tracing |
| Vectorization (Color) | Vectorizer.AI | Web/API (current) | Color/transparency-aware tracing |
| SVG Cleanup | vpype | **1.15.0** (Python ≥3.11,<3.14) | CLI batch path optimization |
| SVG Validation | svgpathtools | **1.7.2** (Python ≥3.8) | Rule-based QA and geometry analysis |
| 3D Production (Primary) | Maya + mayapy | **2024+** | Primary DCC: geometry JSON → editable .ma blockout |
| 3D Draft (Legacy/Fallback) | Blender + bpy | **LTS 4.x** | Retained legacy isometric draft bridge |
| CLI & Glue | Python | **3.11+** | Asset management, naming, manifest |
| Config | YAML | — | Pipeline, room presets, style presets |
| Launchers | Windows .bat | — | Artist-facing one-click operations |
| Future NLC | MCP / Local Agents | — | Natural language pipeline control |

## Development Workflow

1. **Specify**: Create or update `specs/NNN-feature/spec.md`
2. **Clarify**: Resolve ambiguities via clarification questions
3. **Plan**: Produce `specs/NNN-feature/plan.md` with technical design
4. **Tasks**: Generate `specs/NNN-feature/tasks.md` with actionable items
5. **Implement**: Write code referencing task IDs, following constitution
6. **Test**: Run `pytest tests/` and manual verification via `quickstart.md`
7. **Manifest**: Update manifest with generated outputs
8. **Commit**: Git commit with descriptive message referencing spec/task

## Governance

This constitution supersedes all ad-hoc decisions. Amendments require:
1. A written proposal explaining the change
2. Impact assessment on existing specs and code
3. Update to this document with version bump
4. Update to AGENTS.md if agent behavior is affected

All code reviews and AI agent actions must verify compliance with these principles.
Use AGENTS.md as the runtime development guidance file.

## Research Incorporated

This constitution has been updated with findings from two research documents:

- **Indie Game Art Workflow Automation Research** (`docs/research/`) — English. Tool comparison tables, three-tier production pipeline (Beginner/Semi-Automated/Advanced Agentic), GitHub repository registry, 7-day and 30-day setup plans, MCP server integrations.
- **Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ** (`docs/research/`) — Vietnamese. Semi-automated architecture, version-locked toolchain, SVG quality gate criteria, Potrace/vpype/svgpathtools pipeline details, Maya SVG import limitations, concrete code samples.

Key research conclusions encoded in this constitution:
1. Version-lock the toolchain rather than chasing "latest" (see Technology Stack table).
2. Potrace for B&W line art; Vectorizer.AI for color/transparency — never a single tracing path for all inputs.
3. Maya has no confirmed first-party SVG import — the production path uses Python parser → geometry JSON → `mayapy`.
4. SVG must meet explicit quality-gate criteria before entering DCC tools (see Principle IV).
5. Recommended production tier is **Semi-Automated** (Tier B) — not full agentic.

**Version**: 1.2.0 | **Ratified**: 2026-05-29 | **Last Amended**: 2026-06-03
