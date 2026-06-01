# Phase 005.4R Verification Checkpoint: Maya Artist Workflow

> **Document type**: Final verification checkpoint / developer reference
> **Branch**: `workflow/maya-first-artist-pipeline`
> **Checkpoint date**: 2026-06-01
> **Scope**: Documentation/state cleanup only. No production logic changes.

## Current Verified State

The Maya-first artist workflow is verified through Phase 005.4. The project is now aligned around Illustrator clean SVG input, Python validation/geometry handoff, Autodesk Maya `.ma` blockout generation, optional PNG preview rendering, and artist polish in Maya.

Blender remains available as the legacy/fallback backend. It is not the production DCC target for Feature 005.

## Key Commits

- `00fd06f` - docs: align architecture around Maya-first workflow
- `af04e91` - feat: harden Illustrator SVG compatibility for Maya pipeline
- `5179853` - feat: add Maya isometric preview render
- `3c85cf0` - fix: make Maya preview camera renderable
- `65f7ea9` - fix: improve Maya preview camera framing
- `7247810` - fix: widen Maya preview camera framing
- `2f2ae0a` - feat: place Maya props from SVG group markers
- `b3e9c8e` - chore: polish Maya artist launchers

## Real DCC Verification Environment

- Autodesk Maya: Maya 2024
- `mayapy.exe`: `C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`
- Artist/DCC repo path: `D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline`
- `MAYA_APP_DIR`: `D:\Maya_UserData`

## Verified Flow

1. Used an Illustrator-style SVG fixture: `tests/in/illustrator_prop_markers.svg`
2. Ran launcher 07 in dry-run mode first.
3. Ran launcher 07 again as an actual Maya run.
4. Verified editable `.ma` output under `outputs/maya/`.
5. Verified PNG preview output under `outputs/preview/`.
6. Opened/inspected the generated Maya scene in the Outliner.

Verified launcher settings:

- Room: `phong_kho`
- Dry-run first: yes
- Actual run after dry-run: yes
- Render preview enabled: yes

## Verified Maya Outliner Structure

- `GRP_phong_kho_blockout`
- `walls`
- `props`
- `prop_shelf_unit_01`
- `prop_wooden_crate_01`
- `lights`
- `floor_blockout`

## Safety Confirmations

- Dry-run does not update the manifest.
- Manifest updates only after real outputs exist and are verified.
- Original `.ai`, SVG, reference, and artist source files are not modified.
- Generated outputs such as `.ma`, `.png`, temporary handoff JSON, and batch reports are local runtime artifacts and should not be committed.

## Known Limitations

- PNG preview is still a technical blockout, not final art.
- Placeholder props are cubes, not final production models.
- Prop markers currently work for nested markers under the selected room group.
- Actual Maya execution requires Autodesk Maya `mayapy.exe`.
- Phase 005.5 AI polish is optional/evaluation-only and is not integrated.
- Feature 006 natural-language control remains blocked/deferred until the pipeline and app workflow are stable.

## Recommended Next Phase

1. **007A - Friendly desktop app MVP packaged as `.exe`**
2. **005.5A - Optional AI polish evaluation/prototype** after the checkpoint/app foundation, not production integration yet
3. **Feature 006 - Natural-language control**, still deferred until the pipeline/app is stable

Do not integrate external AI APIs, FLUX/fal.ai, TencentDB-Agent-Memory, or Feature 006 as part of this checkpoint.
