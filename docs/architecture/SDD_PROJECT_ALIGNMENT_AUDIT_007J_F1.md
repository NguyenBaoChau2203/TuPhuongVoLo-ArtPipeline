# SDD Project Alignment Audit after 007J-F1

> **Document type**: Architecture alignment audit (English)
> **Phase**: Post-007J-F1 checkpoint
> **Branch**: `workflow/maya-first-artist-pipeline`
> **Date**: 2026-06-03
> **Audience**: AI coding agents and human developer/operator

---

## 1. Current Verified Direction

| Principle | Current status |
|-----------|---------------|
| Illustrator → SVG → Python geometry → Maya `.ma` → artist polish | **Production workflow** |
| Desktop app (Tkinter) is current artist-facing UI | **Active** — v0.7.9 (007J-F1) |
| Cat-themed HTML guide is main artist guide | **Active** — `docs/artist_workflow_cat_guide_vi.html` |
| AI image/API preview is optional/reference-only | **Deferred** — mock provider is safe default; fal provider optional |
| Local web UI | **Dropped from near-term roadmap** |
| Feature 006 natural-language control | **Deferred** — spec-only, do not implement |

---

## 2. Repo State Summary

| Item | Value |
|------|-------|
| Branch | `workflow/maya-first-artist-pipeline` |
| Ahead of origin | 4 commits |
| Latest local commit | `49c84f7` — fix: improve artist app button contrast and guide details |
| App version (verified) | `TuPhuongVoLo Maya Artist App v0.7.9 (007J-F1)` |
| Desktop app tests | 38 passed (0.18s) |
| Maya build tests | 48 passed (1.44s) |
| Working tree | Clean |

Recent commits inspected:

```
49c84f7 fix: improve artist app button contrast and guide details
6088821 feat: polish artist app with cat themed UI
b1c560f feat: add artist guide and marker template shortcuts
16e9b8e docs: add procedural prop preview verification checkpoint
1f2f7f6 fix: improve procedural prop preview framing
8364793 docs: add procedural prop blockout verification checkpoint
187375d fix: use Maya-safe procedural prop part names
107a2fc feat: add procedural Maya prop blockout library
9c5e729 docs: add cat-themed artist workflow guide (007H)
0d71550 docs: add desktop app AI preview verification checkpoint
```

---

## 3. Alignment Table

| Area | Expected direction | Current repo state | Status | Recommended action |
|------|-------------------|--------------------|--------|--------------------|
| **AGENTS.md** | Maya-first production DCC | Says "Blender — Default isometric draft bridge" and "Maya — Advanced/studio 3D branch (optional, not default)"; pipeline flow lists Blender as primary, Maya as optional | **Stale** | Update to reflect Maya-first; Blender legacy/fallback |
| **`.cursor/rules/00-project-context.mdc`** | Maya-first | Says "Pipeline: Illustrator SVG export → cleanup → Blender isometric render → editable outputs"; lists "Blender (default 3D bridge)", "Maya (optional advanced)" | **Stale** | Update pipeline summary and tool roles |
| **`.cursor/rules/50-maya-pipeline.mdc`** | Maya is primary DCC | Says "Maya is an OPTIONAL ADVANCED branch. It must NOT block the primary Blender pipeline." | **Stale** | Update to primary-DCC framing |
| **`.cursor/rules/40-blender-pipeline.mdc`** | Blender is legacy/fallback | Still reads as the primary pipeline rules | **Risky** | Add legacy/fallback note at top |
| **README.md** | Maya-first; app v0.7.9 | Maya-first workflow clearly stated; app version says `v0.7.8 (007J)` in Feature Status table and body text | **Minor stale** | Update version references to v0.7.9 (007J-F1) |
| **Feature 005 specs/tasks** | All phases through 005.3Q complete | All tasks [X] checked; correction note present at top of tasks.md | **OK** | None |
| **Feature 007 specs/tasks** | All phases through 007J-F1 complete | All tasks [X] checked; 007J-F1 phase documented | **OK** | None |
| **Feature 006 specs** | Deferred, spec-only | Spec/plan/tasks exist but tasks are not started; all mentions say deferred | **OK** | None |
| **Artist HTML guide** | Main guide, cat-themed, Vietnamese | Active at `docs/artist_workflow_cat_guide_vi.html`; linked from README, app, launcher docs | **OK** | None |
| **Desktop app docs** (`desktop_app_mvp_vi.md`) | v0.7.9 (007J-F1); AI optional | Body mentions `v0.7.8 (007J)` from 007J section but 007J-F1 phase exists in tasks | **Minor stale** | None critical; version text is contextual to 007J section |
| **`docs/HOW_TO_USE_FOR_ARTIST_VI.md`** | v0.7.9; AI optional | Bottom says `v0.7.8 (007J)` | **Minor stale** | Update version |
| **Launcher docs** | v0.7.9 | Says `v0.7.8 (007J)` | **Minor stale** | Update version |
| **AI preview docs** | Optional/reference-only | All three docs (evaluation, mock, fal) say optional/reference-only | **OK** | None |
| **`docs/NATURAL_LANGUAGE_CONTROL_ROADMAP.md`** | Deferred; do not implement | Clearly states deferred; prerequisites not met | **OK** | None |
| **`docs/PIPELINE_OVERVIEW.md`** | Maya-first | Says "Blender default, Maya optional"; architecture diagram shows Maya as optional | **Stale** | Superseded by `MAYA_FIRST_WORKFLOW_AUDIT.md`; add note |
| **`docs/architecture/MAYA_FIRST_WORKFLOW_AUDIT.md`** | Authoritative Maya-first reference | Correctly states Maya-first; notes that it supersedes PIPELINE_OVERVIEW | **OK** | None |
| **`bootstrap_summary.md`** | Historical record | Says "Blender is default" — this is a historical bootstrap document | **Acceptable** | No change; it records the original bootstrap state |
| **Generated artifact policy** | Do not commit .ma, .png, build/dist/exe/spec | README, HOW_TO_USE, launcher docs, desktop_app_mvp all state this | **OK** | None |
| **Testing policy** | Tests run without Maya; 86+ tests pass | 38 + 48 = 86 tests verified in desktop app + Maya build alone | **OK** | None |
| **DCC verification policy** | Artist/DCC machine for verification only | Multiple verification checkpoints reference this | **OK** | None |
| **Dry-run manifest safety** | Dry-run never writes manifest | Documented in MAYA_FIRST_WORKFLOW_AUDIT, spec FR-005, tasks T029, tests, artist guide | **OK** | None |

---

## 4. Stale Mention Summary

### Mentions that need correction

| Pattern | Location | Issue | Priority |
|---------|----------|-------|----------|
| "Blender — Default isometric draft bridge" | `AGENTS.md` L19 | Should say legacy/fallback | High |
| "Maya — Advanced/studio 3D branch (optional, not default)" | `AGENTS.md` L20 | Should say primary production DCC | High |
| Blender-first pipeline flow | `AGENTS.md` L24-34 | Should list Maya-first flow | High |
| "Blender LTS 4.x as default 3D bridge" | `AGENTS.md` L188 | Should say legacy/fallback | High |
| "Blender (default 3D bridge)" | `.cursor/rules/00-project-context.mdc` L19 | Should say legacy/fallback | High |
| "Maya (optional advanced)" | `.cursor/rules/00-project-context.mdc` L20 | Should say primary production DCC | High |
| Pipeline summary in context rule | `.cursor/rules/00-project-context.mdc` L14 | Should reference Maya | High |
| "Maya is an OPTIONAL ADVANCED branch" | `.cursor/rules/50-maya-pipeline.mdc` L10 | Should say primary production DCC | High |
| "Blender default, Maya optional" | `docs/PIPELINE_OVERVIEW.md` L80 | Superseded; add note | Medium |
| `v0.7.8 (007J)` in several docs | README, launchers, HOW_TO_USE, desktop_app_mvp | Should reference v0.7.9 (007J-F1) | Low |

### Mentions that are correctly deferred/blocked

| Pattern | Count | Verdict |
|---------|-------|---------|
| "Feature 006 deferred" | 40+ mentions | ✅ Consistently deferred |
| "local web UI" in exclusion lists | 3 mentions | ✅ Correctly excluded |
| "paid API" / "ComfyUI" | 0 mentions | ✅ Not present |
| "007K" / "007L" | 0 mentions | ✅ Not present (unplanned phases) |
| "005.3R" | 1 mention (future audit) | ✅ Mentioned as candidate only |

---

## 5. Feasibility Assessment for Next Improvements

### A. 007J-F2 — De-emphasize paid AI preview in app/docs

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Reduce confusion; mark AI as optional/deferred in remaining docs |
| **Risk** | Very low — docs-only changes |
| **Expected files** | `docs/desktop_app_mvp_vi.md`, `docs/HOW_TO_USE_FOR_ARTIST_VI.md`, `docs/artist_workflow_cat_guide_vi.html`, possibly `README.md` |
| **Tests** | Existing tests remain passing; no new tests needed |
| **DCC needed** | No |
| **Notes** | Current AI docs already say "optional/reference-only" but the presence of detailed fal.ai docs could still confuse the artist. Softening wording in the cat guide Step 4 heading and adding "không cần dùng ngay" emphasis would help. |

### B. 007L — One-click guided workflow in desktop app

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Reduce artist clicks and confusion with preset workflow buttons |
| **Possible UX** | "Kiểm tra SVG trước" (dry-run), "Dựng Maya thật" (actual run), "Dựng Maya + render PNG", "Mở file Maya mới nhất", "Mở PNG preview mới nhất" |
| **Risk** | Low-medium — modifies `artist_desktop_app.py` UI layout but reuses existing CLI wrappers |
| **Expected files** | `scripts/python/artist_desktop_app.py`, `tests/test_artist_desktop_app.py`, `docs/desktop_app_mvp_vi.md`, `docs/HOW_TO_USE_FOR_ARTIST_VI.md` |
| **Tests** | New helper tests for one-click command building; existing tests must remain passing |
| **DCC needed** | No for dev/test; DCC verification recommended for packaged `.exe` |

### C. 005.3R — Prop orientation support

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Support `prop_bed_rot90`, `prop_table_rot180`, `prop_chair_rot270` naming |
| **Risk** | Low — extends existing marker name parsing and Maya prop placement |
| **Expected files** | `scripts/python/build_maya_room.py` or `scripts/python/detect_rooms_from_svg.py` (marker parsing), `scripts/maya/build_maya_room_scene.py` (rotation application), tests, docs |
| **Tests** | New marker parsing tests, rotation geometry tests; no Maya required |
| **DCC needed** | Yes for final visual verification |

### D. 005.3S — Door/window marker support

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Add `prop_door`, `prop_window`, `prop_arch`, `prop_opening` placeholders |
| **Risk** | Low-medium — new prop type category with different visual semantics (openings vs. furniture) |
| **Expected files** | `scripts/maya/build_maya_room_scene.py` (procedural builders), `scripts/python/build_maya_room.py` (marker detection), tests, docs, template SVG update |
| **Tests** | New procedural builder tests, marker detection tests |
| **DCC needed** | Yes for final visual verification |

### E. 007M — SVG preflight checker in app

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Help artist detect room names, prop markers, unsupported elements, dry-run issues before running Maya |
| **Risk** | Low — reads SVG and reports findings; no Maya needed |
| **Expected files** | `scripts/python/artist_desktop_app.py` (preflight button/panel), possibly `scripts/python/svg_preflight.py` (extraction module), tests |
| **Tests** | Preflight parsing tests with existing test SVG fixtures |
| **DCC needed** | No |

### F. 005.3T — Procedural prop library v2

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Add more simple procedural props (e.g., lamp, rug, barrel, box variants, TV, monitor) |
| **Risk** | Low — extends existing procedural builder pattern |
| **Expected files** | `scripts/maya/build_maya_room_scene.py`, tests, docs, template SVG update |
| **Tests** | Builder mapping tests, alias tests |
| **DCC needed** | Yes for visual verification |

### G. 005.3U — Material/color tags from SVG names

| Aspect | Assessment |
|--------|-----------|
| **Goal** | Support `mat_wood`, `mat_metal`, `mat_green` tags in prop marker names |
| **Risk** | Medium — requires material assignment in Maya scene script; may need Lambert/Phong material library |
| **Expected files** | `scripts/maya/build_maya_room_scene.py`, `scripts/python/build_maya_room.py` (tag parsing), geometry JSON schema extension, tests, docs |
| **Tests** | Tag parsing tests, material assignment tests |
| **DCC needed** | Yes for visual verification |

### Explicitly Deferred / Out of Scope

| Item | Reason |
|------|--------|
| Local web UI | Dropped from near-term roadmap per owner decision |
| Paid AI image APIs (fal.ai, FLUX, etc.) | Cost concern; deferred until budget/policy ready |
| Feature 006 natural-language control | Deferred until pipeline/app workflow is stable |
| Automatic understanding of arbitrary freehand furniture line art | Research scope; current pipeline uses explicit markers |
| Full detailed final isometric art generation | Pipeline produces blockout; artist polishes manually |
| External 3D model download/import pipeline | Not planned; procedural blockout serves current needs |

---

## 6. Recommended Phase Order

The proposed order is **safe and well-sequenced**. My assessment agrees with the preferred direction with minor notes:

| Order | Phase | Rationale |
|-------|-------|-----------|
| 1 | **007J-F2** — De-emphasize paid AI preview | Docs-only, zero risk, removes confusion immediately |
| 2 | **007L** — One-click guided workflow | Highest artist-impact UX improvement; reduces clicks and cognitive load |
| 3 | **005.3R** — Prop orientation | Direct artist request; reduces manual Maya rotation work |
| 4 | **005.3S** — Door/window markers | Expands marker vocabulary for architectural elements |
| 5 | **007M** — SVG preflight checker | Catches errors before pipeline runs; best placed after marker vocabulary is stabilized |
| 6 | **005.3T** — Prop library v2 | More variety; lower priority than orientation/doors |
| 7 | **005.3U** — Material/color tags | Most complex; depends on stable prop library |

> **Note on 007M placement**: The preflight checker is more useful after 005.3R and 005.3S are done, because it can then report orientation tags and door/window markers. If placed earlier, it would need updating when those features land. The proposed order of 5th is correct.

---

## 7. One-Prompt-Per-Phase Definitions

### Phase 1: 007J-F2 — De-emphasize paid AI preview

| Item | Value |
|------|-------|
| **Goal** | Soften AI preview wording across docs; emphasize "không cần dùng ngay" |
| **Strict scope** | Docs/HTML guide wording only; no Python logic changes |
| **Files likely touched** | `docs/artist_workflow_cat_guide_vi.html`, `docs/desktop_app_mvp_vi.md`, `docs/HOW_TO_USE_FOR_ARTIST_VI.md` |
| **Tests required** | Existing tests must remain passing |
| **DCC verification** | Not required |
| **Stop conditions** | All AI mentions say "optional/deferred/reference-only"; no wording suggests the artist should set up fal.ai |
| **Must NOT change** | Python logic, Maya generation, SVG parser, AI provider code, Feature 006 |
| **Acceptance criteria** | Cat guide Step 4 clearly says "không cần dùng ngay"; fal setup instructions de-emphasized; all 86+ tests pass |
| **Final checklist** | Diff shows only doc/HTML changes; git status clean; tests pass |

### Phase 2: 007L — One-click guided workflow

| Item | Value |
|------|-------|
| **Goal** | Add one-click preset buttons for common workflows |
| **Strict scope** | Desktop app UI changes + helper functions + tests |
| **Files likely touched** | `scripts/python/artist_desktop_app.py`, `tests/test_artist_desktop_app.py`, `docs/desktop_app_mvp_vi.md`, `docs/HOW_TO_USE_FOR_ARTIST_VI.md`, `specs/007-artist-desktop-app-mvp/tasks.md` |
| **Tests required** | New command-building tests for each preset; existing tests pass |
| **DCC verification** | Recommended for `.exe` rebuild |
| **Stop conditions** | Preset buttons work; existing manual controls still available; AI section unchanged |
| **Must NOT change** | Maya generation logic, SVG parser, AI provider behavior, Feature 006 |
| **Acceptance criteria** | At least 3 preset buttons functional; dry-run default preserved; version bumped |
| **Final checklist** | Tests pass; diff shows only app/test/doc changes; no generated outputs |

### Phase 3: 005.3R — Prop orientation

| Item | Value |
|------|-------|
| **Goal** | Parse `_rot90`, `_rot180`, `_rot270` suffixes and apply rotation |
| **Strict scope** | Marker name parsing + Maya prop rotation + tests + docs |
| **Files likely touched** | `scripts/python/build_maya_room.py`, `scripts/maya/build_maya_room_scene.py`, tests, docs, template SVG |
| **Tests required** | Suffix parsing, rotation value extraction, Maya command verification |
| **DCC verification** | Required for visual rotation verification |
| **Stop conditions** | Rotated props appear correctly in dry-run plan and Maya scene |
| **Must NOT change** | Desktop app behavior, AI provider, Feature 006, SVG cleanup logic |
| **Acceptance criteria** | `prop_bed_rot90` creates bed rotated 90°; existing markers still work; tests pass |
| **Final checklist** | Tests pass; dry-run shows rotation; no generated outputs committed |

### Phase 4: 005.3S — Door/window markers

| Item | Value |
|------|-------|
| **Goal** | Add procedural builders for door, window, arch, opening |
| **Strict scope** | New procedural builders + marker detection + tests + docs |
| **Files likely touched** | `scripts/maya/build_maya_room_scene.py`, tests, docs, template SVG |
| **Tests required** | Builder mapping, marker detection, alias tests |
| **DCC verification** | Required |
| **Stop conditions** | Door/window markers detected and placed as blockout shapes |
| **Must NOT change** | Desktop app behavior, AI provider, Feature 006, existing prop builders |
| **Acceptance criteria** | `prop_door` and `prop_window` produce distinct blockout shapes; tests pass |
| **Final checklist** | Tests pass; template SVG updated; no generated outputs committed |

### Phase 5: 007M — SVG preflight checker

| Item | Value |
|------|-------|
| **Goal** | Add SVG analysis panel in desktop app |
| **Strict scope** | New preflight module + app UI integration + tests |
| **Files likely touched** | `scripts/python/svg_preflight.py` (new), `scripts/python/artist_desktop_app.py`, tests |
| **Tests required** | Preflight parsing tests with existing SVG fixtures |
| **DCC verification** | Not required |
| **Stop conditions** | Preflight reports rooms, markers, unsupported elements |
| **Must NOT change** | Maya generation, SVG parser behavior, AI provider, Feature 006 |
| **Acceptance criteria** | Preflight button shows analysis before pipeline run; tests pass |
| **Final checklist** | Tests pass; no Maya/AI logic changes; no generated outputs |

### Phase 6: 005.3T — Prop library v2

| Item | Value |
|------|-------|
| **Goal** | Add more procedural prop types |
| **Strict scope** | New builders + alias mapping + tests + docs |
| **Files likely touched** | `scripts/maya/build_maya_room_scene.py`, tests, docs, template SVG |
| **Tests required** | Builder mapping, alias normalization tests |
| **DCC verification** | Required |
| **Stop conditions** | New prop types produce blockout shapes; existing props unchanged |
| **Must NOT change** | Desktop app, AI provider, Feature 006 |
| **Acceptance criteria** | At least 5 new prop types; existing tests pass; template updated |
| **Final checklist** | Tests pass; no generated outputs committed |

### Phase 7: 005.3U — Material/color tags

| Item | Value |
|------|-------|
| **Goal** | Parse `mat_wood`, `mat_metal` tags and assign materials |
| **Strict scope** | Tag parsing + Maya material assignment + tests + docs |
| **Files likely touched** | `scripts/python/build_maya_room.py`, `scripts/maya/build_maya_room_scene.py`, tests, docs |
| **Tests required** | Tag parsing, material creation, fallback behavior |
| **DCC verification** | Required |
| **Stop conditions** | Tagged props get distinct materials; untagged props use default |
| **Must NOT change** | Desktop app, AI provider, Feature 006 |
| **Acceptance criteria** | `mat_wood` assigns warm brown Lambert; default remains gray; tests pass |
| **Final checklist** | Tests pass; no generated outputs committed |

---

## 8. SDD Spec Recommendation

| Phase | Spec action needed |
|-------|-------------------|
| **007J-F2** | Docs-only — add phase to `specs/007-artist-desktop-app-mvp/tasks.md` |
| **007L** | Add phase to `specs/007-artist-desktop-app-mvp/tasks.md`; no new spec folder needed |
| **005.3R** | Add phase to `specs/005-maya-bridge/tasks.md`; no new spec folder needed |
| **005.3S** | Add phase to `specs/005-maya-bridge/tasks.md`; no new spec folder needed |
| **007M** | Add phase to `specs/007-artist-desktop-app-mvp/tasks.md`; no new spec folder needed |
| **005.3T** | Add phase to `specs/005-maya-bridge/tasks.md`; no new spec folder needed |
| **005.3U** | Add phase to `specs/005-maya-bridge/tasks.md`; may warrant a mini plan section |

All phases extend existing features and can be tracked as new task phases in existing
spec folders. No new `specs/NNN-feature/` directories are needed.

---

## 9. Final Decision

### Is the proposed improvement sequence feasible?

**Yes.** Each phase has clear scope, well-defined acceptance criteria, and builds
on verified infrastructure. The dependency chain is logical: docs cleanup → UX
improvement → marker vocabulary → preflight → library expansion → materials.

### Is the current repo aligned enough to proceed?

**Mostly yes**, with the following caveats:

1. **AGENTS.md** and **`.cursor/rules/`** still frame Blender as default and Maya
   as optional. This is the most significant alignment gap because these files
   directly instruct AI agents. **Must be fixed before proceeding.**

2. **`docs/PIPELINE_OVERVIEW.md`** still says "Blender default, Maya optional" but
   the `MAYA_FIRST_WORKFLOW_AUDIT.md` already supersedes it. A brief note at the
   top of `PIPELINE_OVERVIEW.md` would prevent confusion.

3. Version references to `v0.7.8 (007J)` in several docs are cosmetically stale
   but not blocking.

### Safest immediate next phase

**Fix the stale agent instructions first** (AGENTS.md, cursor rules), then proceed
to **007J-F2** (de-emphasize AI preview in docs).

---

## 10. Alignment Fixes Applied in This Audit

The following files were updated in this same commit to resolve the most critical
alignment gaps identified above:

| File | Change |
|------|--------|
| `AGENTS.md` | Updated pipeline flow, tool roles, and research summary to reflect Maya-first direction |
| `.cursor/rules/00-project-context.mdc` | Updated pipeline summary and tool roles |
| `.cursor/rules/50-maya-pipeline.mdc` | Changed from "optional advanced branch" to "primary production DCC" |
| `.cursor/rules/40-blender-pipeline.mdc` | Added legacy/fallback note |
| `docs/PIPELINE_OVERVIEW.md` | Added superseded-by note at top |

Version-string updates (v0.7.8 → v0.7.9) in README, launcher docs, HOW_TO_USE, and
desktop_app_mvp are deferred to 007J-F2 as they are cosmetic and low-risk.
