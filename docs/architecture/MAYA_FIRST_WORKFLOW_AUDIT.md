# Maya-First Workflow Audit

> **Document type**: Architecture audit / developer reference (English)
> **Phase**: 005.0A — Workflow alignment / architecture cleanup
> **Audience**: AI coding agents and human developers
> **Last updated**: 2026-06-01

This document is the authoritative reference for the project's current strategic
direction. Any AI agent or developer starting work on this repository should read
this file first to understand that the project is now **Maya-first** and
**Illustrator/SVG-first**, with Blender reduced to a legacy/fallback backend.

---

## 1. Current Repository Status

The repository is past the bootstrap phase. Several features are implemented as
working, tested Python tooling. The Maya-first workflow is verified through the
launcher-based artist workflow in Phase 005.4 on the artist/DCC machine.

### Implemented features

| Order | Feature | Spec | Status |
|-------|---------|------|--------|
| 1 | Illustrator Export & Clean SVG | `specs/002-illustrator-export-clean-svg/` | Done |
| 2 | Asset Naming & Manifest | `specs/003-asset-naming-and-manifest/` | Done |
| 3 | Floorplan to Isometric Room | `specs/001-floorplan-to-isometric-room/` | MVP done; Blender path is legacy/fallback |
| 4 | Batch Isometric Render | `specs/004-batch-isometric-render/` | MVP dry-run/report for legacy backend |
| 5 | Maya Bridge | `specs/005-maya-bridge/` | **Primary DCC backend; verified through 005.4 launcher workflow** |
| 6 | Natural Language Agent Control | `specs/006-natural-language-agent-control/` | Spec only — DO NOT implement yet |

### Key scripts (Python source-of-truth layer)

- `scripts/python/clean_svg_paths.py` — SVG cleanup + stdio config
- `scripts/python/validate_svg_contract.py` — rule-based SVG validation
- `scripts/python/detect_rooms_from_svg.py` — room detection + Vietnamese name normalization
- `scripts/python/room_geometry.py` — pure-Python geometry (points, walls, scaling)
- `scripts/python/manifest.py` — naming convention + manifest tracking
- `scripts/python/asset_agent.py` — asset ingest into manifest

### Maya-first layer (current primary backend)

- `scripts/python/build_maya_room.py` — plans + runs a single Maya `.ma` blockout
- `scripts/python/batch_maya_room.py` — batch planning/execution wrapper
- `scripts/maya/build_maya_room_scene.py` — `mayapy` scene builder (floor, walls, props, camera, lights)
- `scripts/maya/import_svg_walls.py`, `setup_iso_camera.py`, `batch_render.py` — supporting Maya scripts
- Launchers: `launchers/07_build_maya_room.bat`, `launchers/08_batch_maya_room.bat`

### Legacy/fallback layer (Blender)

- `scripts/python/build_isometric_room.py` — Blender room build wrapper
- `scripts/python/batch_isometric_render.py` — Blender batch wrapper
- `scripts/blender/build_isometric_room.py`, `build_isometric_room_blender.py`,
  `batch_render_rooms.py`, `props_library.py`
- Launchers: `launchers/03_build_isometric_room.bat`, `launchers/04_batch_isometric_render.bat`, `launchers/04_batch_render.bat`

---

## 2. Final Target Workflow

The intended long-term production workflow is:

```text
Adobe Illustrator (clean SVG authoring/export)
  -> Python SVG cleanup + validation        (clean SVG = source of truth)
  -> Python room detection + geometry JSON   (Python is the only SVG parser)
  -> Autodesk Maya .ma blockout              (primary production DCC)
  -> artist polish in Maya                   (final artistic decisions)
```

Optional / fallback path (legacy, must not be removed):

```text
clean SVG -> Blender MVP isometric draft / batch dry-run
```

### Pipeline principles that remain unchanged

- **Illustrator is the primary 2D authoring tool.**
- **Clean SVG is the single source of truth.** Downstream scenes are rebuilt from
  SVG rather than hand-edited at the geometry level.
- **Python owns all SVG parsing.** Maya never parses SVG directly; it consumes the
  geometry JSON handoff produced by Python.
- **Maya is the main production DCC backend.**
- **Blender is legacy/fallback only.**
- **Outputs are non-destructive, versioned, and editable.**

---

## 3. Maya-First Decision Summary

| Decision | Rationale |
|----------|-----------|
| Maya is the primary DCC backend | This matches the real artist's production toolchain (Illustrator + Maya). |
| Blender becomes legacy/fallback | Blender remains useful as a free MVP/draft path but is no longer the production target. It is not removed and not required. |
| Python remains the SVG parser | Keeps clean SVG as source of truth and avoids fragile DCC-side parsing. The same geometry JSON can feed Maya, Blender, or future backends. |
| `mayapy.exe` is the only supported actual-run runtime (MVP) | `maya.exe` / `mayabatch.exe` support is deferred. Dry-run never needs Maya at all. |
| Dry-run never writes manifest | Manifest entries are only created when a real output file exists and is verified. |

This supersedes the older "Blender default, Maya optional" framing in
`docs/PIPELINE_OVERVIEW.md`. Where the two documents disagree on backend
priority, **this audit is authoritative** for current direction.

---

## 4. What Is Already Implemented

### SVG / geometry layer (shared, backend-agnostic)

- SVG cleanup (`clean_svg_paths.py`) and validation (`validate_svg_contract.py`)
- Room detection with Vietnamese layer/group name normalization (`detect_rooms_from_svg.py`)
- Pure-Python geometry: closed-boundary detection, normalization to origin,
  unit scaling, wall-segment generation (`room_geometry.py`)
- Naming convention + manifest tracking (`manifest.py`, `asset_agent.py`)

### Maya-first backend

- `build_maya_room.py`:
  - Validates a clean SVG input without modifying it.
  - Reuses the Python geometry layer to build a geometry JSON handoff
    (`boundary_points`, `wall_segments`, style/room presets, unit mapping
    `SVG x/y -> Maya x/z`, scale `0.01`).
  - Resolves convention-compliant `.ma` output path and version.
  - Resolves `mayapy` from CLI / `config/pipeline.yaml` / `PATH`.
  - **Dry-run** prints the full plan and Maya command without touching Maya or the manifest.
  - **Actual run** launches `mayapy`, verifies the `.ma` exists, then appends a manifest entry.
- `build_maya_room_scene.py` (runs inside `mayapy`):
  - Builds floor, walls, placeholder props, isometric orthographic camera, and lights.
  - Saves an editable `mayaAscii` `.ma` scene.
  - Headless-safe (does not switch viewports).
- `batch_maya_room.py`:
  - Scans an input dir / single file / job file.
  - Reuses single-build planning for consistent dry-run vs actual behavior.
  - Writes `outputs/reports/batch_maya_report.json`.

### Tests

- `tests/test_build_maya_room.py`, `tests/test_batch_maya_room.py` cover Maya
  planning, dry-run, naming, geometry payload, and graceful failure without Maya.
- All Maya unit tests run **without** Maya installed.

---

## 5. What Is Still Legacy / Fallback

The following remain in the repository and **must not be deleted, rewritten, or
broken** in this phase. They are conceptually reclassified as legacy/fallback in
documentation only:

- `scripts/python/build_isometric_room.py`
- `scripts/python/batch_isometric_render.py`
- `scripts/blender/build_isometric_room.py`
- `scripts/blender/build_isometric_room_blender.py`
- `scripts/blender/batch_render_rooms.py`
- `scripts/blender/props_library.py`
- `launchers/03_build_isometric_room.bat`
- `launchers/04_batch_isometric_render.bat`
- `launchers/04_batch_render.bat`
- Blender-related tests (`test_build_isometric_room.py`, `test_batch_isometric_render.py`)

These continue to be tested and supported as a fallback draft path.

---

## 6. What Must NOT Be Changed In Checkpoint Cleanup

The following are explicitly out of scope for Phase 005.4R checkpoint cleanup and
must not be started as part of documentation/state cleanup:

- **Feature 006** natural-language agent control / MCP integration.
- **Phase 005.5** AI polish implementation or production integration.
- **Feature 007A** desktop app implementation.
- SVG parser logic changes.
- Maya scene generation logic changes.
- External AI API integration (FLUX, fal.ai, or any cloud model).
- TencentDB-Agent-Memory integration (evaluation only — see `docs/dev/TENCENTDB_AGENT_MEMORY_EVALUATION.md`).
- Switching the project back to a Blender-first default.

Production Python/Maya/Blender logic should not be changed in this checkpoint
except a tiny documentation mismatch fix that is required to keep the docs honest.

---

## 7. Current Safety Rules

These rules apply to every agent and developer touching this repository:

- **Never modify, delete, overwrite, or clean up** original artist `.ai` files,
  raw SVG files, reference images, or production assets.
- **Source folders are read-only targets**: `assets/2d/ai_src/`,
  `assets/2d/svg_raw/`, `assets/`, `drops/`.
- **Dry-run must never update the manifest.**
- **Manifest updates are allowed only when a real output file exists** and is verified.
- **Do not commit secrets**, `.env`, credentials, API keys, memory databases,
  vector stores, embeddings, caches, or generated CodeGraph databases.
- **All outputs go to `outputs/`** and follow the naming convention
  `tu_phuong_vo_lo_{asset_name}_{variant}_{stage}_v{version}`.
- **Artist-facing docs and error messages should be Vietnamese** where applicable.
- **Do not call external APIs without explicit approval.**

---

## 8. Phase Roadmap (from 005.0A onward)

| Phase | Title | Scope summary | Status |
|-------|-------|---------------|--------|
| **005.0A** | Workflow alignment / architecture cleanup | Documentation + architecture notes + dev workflow docs + `.gitignore`. No production logic changes. | Complete |
| **005.1** | Real Illustrator SVG compatibility hardening | Make room detection / geometry robust against real Illustrator SVG exports. | Complete |
| **005.2** | Maya isometric base render PNG | Add PNG preview rendering from the Maya `.ma` blockout via `mayapy`. | Complete |
| **005.3** | Prop placement from SVG group/layer names | Place props in Maya based on named SVG groups/layers, not just room presets. | Complete |
| **005.4** | Artist-friendly launchers | Polish `.bat` launchers and Vietnamese guidance for the Maya-first flow. | Complete and verified |
| **005.5A** | Optional AI polish evaluation/prototype | Optional evaluation only. External API/cost/privacy/secrets policy must be ready before any production integration. | Optional / deferred |
| **007A** | Friendly desktop app MVP packaged as `.exe` | Wrap the verified Maya-first workflow in an artist-friendly local desktop app. | Recommended next |

> Note: Feature **006** (natural-language control) remains spec-only and is **not**
> on the near-term path. It must not be started until the pipeline/app workflow is stable.

---

## 9. Next Recommended Phase

**007A — Friendly desktop app MVP packaged as `.exe`.**

Rationale: The Maya-first backend has been verified through launcher-based artist
workflow, including real Maya `.ma` output and PNG preview generation. The next
production usability step is to wrap the local workflow in a friendly desktop app
so the artist does not need command-line knowledge.

Phase **005.5A** AI polish should remain optional/evaluation-only until API cost,
privacy, secrets handling, and opt-in policy are ready. Feature **006**
natural-language control remains deferred.

The final 005.4R verification checkpoint is recorded in
`docs/verification/005_4_maya_artist_workflow_verified.md`.
