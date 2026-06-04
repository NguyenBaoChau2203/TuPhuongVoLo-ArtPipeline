# 005.3P-V1-R — Procedural Prop Preview DCC Verification

> Date: 2026-06-02
> Branch: `workflow/maya-first-artist-pipeline`

## Commits Covered

- `107a2fc feat: add procedural Maya prop blockout library`
- `187375d fix: use Maya-safe procedural prop part names`
- `1f2f7f6 fix: improve procedural prop preview framing`

## What Changed

- Added a procedural prop blockout library for common SVG markers: bed, table, chair, sofa, fridge, sink, kitchen counter, cabinet, locker, plant, shelf unit, and wooden crate.
- Updated procedural prop child node names to be Maya-safe and stable in the Outliner.
- Improved Maya preview framing so the isometric camera considers explicit prop marker extents and relevant prop height.
- Added a preview-friendly floor color fallback when a preset floor color would be too pale against a white render background.
- Added the visual sanity showcase fixture: `tests/in/illustrator_prop_showcase.svg`.
- Updated dry-run output so it reports prop marker count and type list.

## DCC Verification Command

Run this on the artist/DCC machine with Autodesk Maya 2024 `mayapy.exe`:

```powershell
python scripts/python/build_maya_room.py --input tests/in/illustrator_prop_showcase.svg --room phong_showcase --output-dir outputs --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" --render-preview
```

## DCC Verification Result

Status: **Pending real Maya/DCC verification**

No real operator-confirmed DCC result for `tests/in/illustrator_prop_showcase.svg` was provided during this checkpoint. Do not treat this phase as fully DCC-verified until the command above has been run on a Maya machine and the generated files have been opened/inspected.

Pending checklist:

- [ ] Command exits with code `0`.
- [ ] `.ma` is generated under `outputs/maya/`.
- [ ] PNG preview is generated under `outputs/preview/`.
- [ ] `.ma` opens successfully in Maya.
- [ ] Outliner contains `GRP_phong_showcase_blockout`, `walls`, `props`, `lights`, and `floor_blockout`.
- [ ] `props` contains the expected procedural prop parents listed below.
- [ ] Camera `cam_phong_showcase_iso1` exists.
- [ ] Viewport can switch through `Panels -> Perspective -> cam_phong_showcase_iso1`.
- [ ] PNG preview is clearer than the old sparse marker fixture because camera framing accounts for explicit prop extents and the floor is more visible.
- [ ] Any visual limitation is recorded before marking the checkpoint verified.

Expected output paths after a first successful run:

```text
outputs/maya/tu_phuong_vo_lo_phong_showcase_main_maya_v001.ma
outputs/preview/tu_phuong_vo_lo_phong_showcase_main_preview_v001.png
```

## Expected Outliner

```text
GRP_phong_showcase_blockout
  walls
  props
    prop_bed_01
    prop_table_01
    prop_chair_01
    prop_sofa_01
    prop_fridge_01
    prop_sink_01
    prop_kitchen_counter_01
    prop_cabinet_01
    prop_locker_01
    prop_plant_01
    prop_shelf_unit_01
    prop_wooden_crate_01
  lights
    cam_phong_showcase_iso1
    key_light
    ambient_light
  floor_blockout
```

Note: Maya may append numeric suffixes if a scene already contains similarly named nodes. For a clean generated scene, the names above are expected.

## Known Validation Before DCC

These validations were confirmed after `005.3P-V1`:

```text
python scripts/python/build_maya_room.py --help: passed
python scripts/python/build_maya_room.py --input tests/in/illustrator_prop_markers.svg --room phong_kho --dry-run: passed
python scripts/python/build_maya_room.py --input tests/in/illustrator_prop_showcase.svg --room phong_showcase --render-preview --dry-run: passed
python -m compileall scripts/python scripts/maya tests: passed
python -m pytest tests/test_build_maya_room.py -v: 46 passed
pytest tests/ -v --ignore=tests/tmp: 203 passed
```

## Safety Confirmations

- Dry-run still does not update manifest.
- Manifest updates only after real outputs exist.
- Unknown prop names still fall back to a generic cube placeholder.
- No original artist files are modified.
- No generated outputs are committed.
- No Feature 006 implementation was added.
- No AI behavior changes were added.
- No external API calls were added.
- No secrets or `.env` files were added.
- No external 3D assets, textures, or dependencies were added.

## Còn gì có thể cải thiện/nâng cấp tiếp?

This section is analysis-only. No item below is implemented in this checkpoint.

### Priority A — Recommended Next Small Improvements

| Item | Why it helps the wife/artist workflow | Risk | Touches | Recommended phase |
| --- | --- | --- | --- | --- |
| Prop orientation support from SVG marker rotation or naming suffix, such as `prop_bed_rot90` or group transform | Lets the artist control bed/table/sofa direction in Illustrator instead of fixing orientation manually in Maya | Medium | Code + tests + docs | `005.3R` |
| Artist-friendly prop marker template SVG for Illustrator | Gives the artist a copyable starter sheet with correctly named groups, reducing naming mistakes | Low | Docs + SVG fixture/template | `005.3Q` |
| Desktop app shortcut/link to open the artist guide HTML | Makes the existing guide easier to reach from the local app during handoff | Low | Desktop app code + docs | `007I` |
| Better DCC smoke-test checklist for operator | Makes real Maya verification repeatable and less dependent on developer memory | Low | Docs only | `005.3P-V1-R2` |
| Optional screenshot/preview comparison note | Helps the operator compare old sparse fixture versus showcase preview without adding generated images to git | Low | Docs only | `005.3P-V1-R2` |

### Priority B — Later Improvements

| Item | Why it helps the wife/artist workflow | Risk | Touches | Recommended phase |
| --- | --- | --- | --- | --- |
| More procedural prop shapes | Covers more room types and makes blockouts easier to read before manual polish | Medium | Maya code + tests + docs | `005.3S` |
| Door/window markers | Lets Illustrator communicate openings and architectural intent | Medium | Parser/geometry/Maya code + tests + docs | `005.4D` |
| Wall opening support | Makes rooms more accurate for production blockout scenes | High | Geometry + Maya scene generation + tests | `005.4E` |
| Room scale calibration guide | Helps the artist choose SVG sizes that produce sensible Maya units | Low | Docs only | `005.3T` |
| Material/color tags from SVG layer names | Allows simple visual labels from Illustrator without editing Maya materials manually | Medium | Parser + Maya code + docs | `005.4C` |
| Prop category docs with Vietnamese examples | Makes supported names and aliases easier to remember | Low | Docs only | `005.3Q` |

### Priority C — Defer

| Item | Why defer | Risk | Touches | Recommended phase |
| --- | --- | --- | --- | --- |
| Automatic understanding of arbitrary freehand furniture line art | Hard to make deterministic and may confuse artist-authored intent | High | Parser + geometry + heuristics | Deferred |
| Full detailed final isometric art generation | Outside the current blockout-first workflow; final art still needs artist polish | High | Broad pipeline + art direction | Deferred |
| Feature 006 natural-language control | Current work should stabilize handoff and markers before adding agent control | High | New feature area | `006` deferred |
| Any real external AI API workflow unless explicitly requested | Needs explicit approval, privacy review, and separate validation | High | Provider/API/docs | Deferred |

## Recommended Next Phase

Recommended next phase: **005.3Q — Illustrator prop marker template and naming taxonomy**

Why this is the safest next step: it directly helps the artist create correct prop marker SVGs, is low risk, can be mostly docs/template work, and does not require changing Maya logic, AI behavior, or Feature 006. A guide button in the desktop app (`007I`) is also useful, but it touches app code; the marker template improves the source artwork workflow first.
