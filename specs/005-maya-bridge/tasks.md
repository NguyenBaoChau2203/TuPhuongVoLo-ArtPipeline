# Tasks: Maya Bridge

**Input**: Design documents from `/specs/005-maya-bridge/`

**Correction applied**: Feature 005 treats Maya as the primary production DCC backend for the Illustrator + Maya artist workflow. Blender remains optional/fallback legacy MVP code and is not required for Feature 005 tests.

## Phase 1: Maya-First Build Wrapper

- [X] T001 Implement `scripts/python/build_maya_room.py` CLI wrapper
- [X] T002 Reuse existing Python SVG detection and room geometry logic
- [X] T003 Select room by normalized Vietnamese/ASCII room name
- [X] T004 Load style and room presets from config
- [X] T005 Create geometry JSON handoff for Maya
- [X] T006 Resolve Maya/mayapy executable from CLI, config, or PATH
- [X] T007 Support dry-run planning without Maya
- [X] T008 Name `.ma` outputs using `tu_phuong_vo_lo_{asset_name}_{variant}_maya_v{version}`
- [X] T009 Update manifest only after verified successful Maya `.ma` generation

## Phase 2: Maya Scene Script

- [X] T010 Implement `scripts/maya/build_maya_room_scene.py`
- [X] T011 Initialize Maya standalone safely when running under mayapy
- [X] T012 Read geometry JSON instead of parsing SVG directly in Maya
- [X] T013 Create floor mesh, wall blocks, simple placeholder props, materials, lights, and isometric camera
- [X] T014 Save editable Maya ASCII `.ma` scene
- [X] T015 Verify actual Maya execution on a machine with Autodesk Maya/mayapy installed

## Phase 3: Batch Maya Wrapper

- [X] T016 Implement `scripts/python/batch_maya_room.py`
- [X] T017 Support `--input-dir`, `--input-file`, and `--job-file`
- [X] T018 Support `--all-rooms`, `--room`, `--stop-on-error`, and dry-run mode
- [X] T019 Write JSON report to `outputs/reports/batch_maya_report.json`
- [X] T020 Continue past corrupt SVGs by default

## Phase 4: Artist Launchers and Docs

- [X] T021 Add `launchers/07_build_maya_room.bat`
- [X] T022 Add `launchers/08_batch_maya_room.bat`
- [X] T023 Update `docs/HOW_TO_USE_FOR_ARTIST_VI.md`
- [X] T024 Update `README.md` to document Maya as primary DCC backend
- [X] T025 Update `specs/005-maya-bridge/quickstart.md`

## Phase 5: Tests and Validation

- [X] T026 Add `tests/test_build_maya_room.py`
- [X] T027 Add `tests/test_batch_maya_room.py`
- [X] T028 Unit tests do not require Maya
- [X] T029 Dry-run does not update manifest
- [X] T030 Existing Feature 001/002/003/004 tests remain supported

## Phase 6: SVG Prop Marker Placement (005.3)

- [X] T031 Define `prop_`, `item_`, and `object_` marker naming convention
- [X] T032 Detect nested SVG prop marker geometry in the Python SVG layer
- [X] T033 Include `prop_markers` with SVG/local/Maya centers in geometry JSON
- [X] T034 Create deterministic Maya placeholder cubes from `prop_markers`
- [X] T035 Prefer explicit SVG markers over room-preset auto props
- [X] T036 Add `tests/in/illustrator_prop_markers.svg` fixture and non-Maya tests
- [X] T037 Update Vietnamese artist checklist with prop marker guidance

## Notes

Verified manually on artist/DCC machine with Autodesk Maya 2024 mayapy.exe. .ma output generated and opened successfully in Maya. Scene contained floor, walls, props, camera, and lights.

## Phase 7: AI Polish Preview Evaluation (005.5A)

- [X] T038 Create Vietnamese evaluation document for optional future AI polish preview
- [X] T039 Document that AI polish preview is reference-only and must not replace clean SVG, geometry JSON, Maya `.ma`, or manual artist polish
- [X] T040 Document safety/privacy policy for any future external AI API usage
- [X] T041 Confirm no external API integration, provider SDK, dependency, `.env`, generated image, or Feature 006 implementation is added

## Phase 8: AI Polish Preview Local Mock Architecture (005.5B)

- [X] T042 Add `scripts/python/ai_polish_preview.py` local mock CLI
- [X] T043 Support `--input`, `--output-dir`, `--provider mock`, optional prompt/preset, `--dry-run`, and `--version`
- [X] T044 Validate PNG input and return clear Vietnamese errors for missing or non-PNG files
- [X] T045 Create only local mock PNG copies and JSON reports under AI preview output folders
- [X] T046 Add non-Maya, non-network tests for dry-run, mock output/report, validation errors, and version
- [X] T047 Add Vietnamese mock workflow documentation
- [X] T048 Confirm no external API calls, secrets, Feature 006, SVG/Maya/render/manifest changes, or generated outputs are added

## Phase 9: AI Polish Preview Mock Verification Checkpoint (005.5B-R)

- [X] T049 Run 005.5B CLI and pytest validation checkpoint
- [X] T050 Add `docs/verification/005_5B_ai_polish_mock_verified.md`
- [X] T051 Confirm dry-run creates no output and AI preview artifacts remain ignored/uncommitted
- [X] T052 Confirm no external API calls, secrets, `.env`, provider SDKs, Feature 006, SVG/Maya/render/manifest changes, or generated artifacts are added

## Phase 10: Real Optional fal Provider Integration (005.5C)

- [X] T053 Extend `scripts/python/ai_polish_preview.py` with `--provider mock|fal`, `--model`, `--timeout-seconds`, and `--skip-on-missing-config`
- [X] T054 Keep provider `mock` behavior unchanged for dry-run, PNG copy output, and local JSON report
- [X] T055 Read fal API configuration only from `FAL_KEY`, lazy-import optional `fal-client`, and keep `fal-client` out of required dependencies
- [X] T056 Implement fal upload/subscribe/download path for `fal-ai/flux-pro/kontext` with versioned `_fal_ai_preview` PNG/report outputs
- [X] T057 Write safe fal report JSON with provider, model, prompt, prompt preset, status, external API call flag, skipped flag, and error type without secrets
- [X] T058 Add non-network pytest coverage for fal dry-run, missing key skip/fail, missing optional dependency, fake successful provider result, report safety, and model override
- [X] T059 Add Vietnamese fal provider documentation and update README/quickstart
- [X] T060 Confirm generated `outputs/ai_preview/` PNG/report artifacts remain ignored
- [X] T061 Confirm no Feature 006, SVG, geometry JSON, Maya scene, render, prop placement, manifest, required dependency, `.env`, secret, or generated output changes are added

## Phase 11: fal Provider Verification Checkpoint (005.5C-R)

- [X] T062 Run 005.5C CLI, compileall, and pytest validation checkpoint
- [X] T063 Add `docs/verification/005_5C_ai_polish_fal_verified.md`
- [X] T064 Confirm `fal-client` remains optional-only and no external API calls are made during validation
- [X] T065 Confirm generated AI preview artifacts remain ignored/uncommitted
- [X] T066 Confirm no secrets, `.env`, Feature 006, UI/app integration, SVG/Maya/render/manifest changes, or generated outputs are added

## Phase 12: Procedural Prop Blockout Library (005.3P)

- [X] T067 Add procedural Maya prop blockout builders for bed, table, chair, sofa, fridge, sink, kitchen counter, cabinet, locker, plant, shelf, and crate
- [X] T068 Support safe prop aliases such as `desk`, `couch`, `refrigerator`, `counter`, `cupboard`, `potted_plant`, `shelf`, `shelving`, `crate`, and `box`
- [X] T069 Keep explicit SVG marker placement centered on marker centers, use marker bbox only as a conservative footprint hint, and keep generic cube fallback for unknown prop names
- [X] T070 Add non-Maya tests for procedural builder mapping, alias normalization, marker creation, and unknown fallback behavior
- [X] T071 Update Vietnamese artist docs with supported prop marker examples and blockout/fallback guidance
- [X] T072 Confirm no Feature 006, AI provider changes, external API calls, SVG parser refactor, manifest safety changes, generated outputs, binary assets, or external 3D assets are added

## Phase 13: Procedural Prop Blockout DCC Verification Checkpoint (005.3P-R)

- [X] T073 Add `docs/verification/005_3P_procedural_prop_blockout_verified.md`
- [X] T074 Record real Maya/DCC verification for `.ma` open, Outliner hierarchy, multi-piece shelf/crate props, Maya-safe child names, camera, and generated PNG preview
- [X] T075 Document that `tests/in/illustrator_prop_markers.svg` validates technical correctness, not final visual quality, and recommend `005.3P-V1` for preview visual sanity polish
- [X] T076 Confirm checkpoint is documentation-only with no Python/Maya logic, SVG parser, AI provider, desktop app, Feature 006, external API, secret, dependency, binary asset, generated output, build/dist, or generated report changes

## Phase 14: Procedural Prop Preview Visual Sanity Polish (005.3P-V1)

- [X] T077 Expand Maya isometric camera framing to include explicit SVG prop marker centers, safe marker footprints, and relevant procedural prop height
- [X] T078 Add preview-friendly floor color fallback when a style preset would make the floor too pale on a white render background
- [X] T079 Add `tests/in/illustrator_prop_showcase.svg` visual sanity fixture with supported procedural prop marker variety
- [X] T080 Add non-Maya tests for prop-aware scene bounds, malformed marker safety, showcase dry-run marker detection, dry-run manifest safety, and render preview planning
- [X] T081 Update Vietnamese artist docs, quickstart, README, and verification notes with marker/showcase guidance
- [X] T082 Confirm no Feature 006, AI provider changes, desktop app AI behavior changes, external APIs, secrets, dependencies, binary assets, SVG parser refactor, manifest safety changes, or generated output commits are added

## Phase 15: Procedural Prop Preview DCC Verification Checkpoint (005.3P-V1-R)

- [X] T083 Create `docs/verification/005_3P_V1_procedural_prop_preview_verified.md`
- [X] T084 Record DCC verification status as pending real Maya/DCC verification until operator results are provided
- [X] T085 Document preview visual sanity improvements from 005.3P-V1
- [X] T086 Add next-improvement audit with prioritized future phases
- [X] T087 Confirm documentation/checkpoint/audit only: no generated outputs, no Feature 006, no AI changes, no Python/Maya/parser/desktop app logic changes, no external APIs, secrets, dependencies, binary assets, build/dist, exe/spec/zip, or reports

## Phase 16: Illustrator Prop Marker Template and Naming Guide (005.3Q)

- [X] T088 Add Illustrator prop marker SVG template
- [X] T089 Integrate prop marker taxonomy into cat-themed HTML guide
- [X] T090 Link template/guide from relevant docs
- [X] T091 Add non-Maya validation that template is readable and detects supported markers
- [X] T092 Confirm no Maya logic, SVG parser refactor, Feature 006, AI changes, external API, secrets, dependencies, binary assets, or generated outputs

## Note on Production Direction (005.5-F2)

- [X] T093 Note that AI image/API work is deferred and Maya-first blockout remains the production path

## Phase 17: Prop Orientation Markers MVP (005.3R)

- [X] T094 Support `_rot90`, `_rot180`, `_rot270`, `_rotation_90`, `_rotation_180`, and `_rotation_270` suffixes on existing SVG prop markers
- [X] T095 Strip orientation suffixes from normalized prop marker type/name while storing `rotation_y_degrees`
- [X] T096 Apply `rotation_y_degrees` around Maya vertical/Y axis for explicit SVG prop placeholders
- [X] T097 Add non-Maya tests for unrotated markers, supported rotation suffixes, JSON handoff metadata, and Maya transform application
- [X] T098 Update Vietnamese artist SVG checklist and quickstart with supported suffixes and dry-run recommendation
- [X] T099 Confirm no AI API, web UI, Feature 006, new dependencies, generated output commits, door/window logic, material/color logic, broad SVG parser refactor, or scaling/dimension changes are added

## Phase 18: Door/Window Markers MVP (005.3S)

- [X] T100 Detect SVG group/layer names starting with `door_` or `window_` as opening markers
- [X] T101 Add `opening_markers` geometry JSON handoff entries with SVG/local/Maya centers and SVG bbox
- [X] T102 Create a deterministic Maya `openings` group only when opening markers exist
- [X] T103 Create simple door/window placeholder cubes with deterministic sanitized names
- [X] T104 Add non-Maya tests for door/window detection, JSON handoff, Maya placeholder names, no-marker compatibility, and unchanged prop markers
- [X] T105 Update Vietnamese artist docs and quickstart with marker naming and marker-only guidance
- [X] T106 Confirm no AI API, web UI, Feature 006, new dependencies, generated output commits, wall cutting, boolean operations, material changes, prop library changes, or unrelated parser/Maya refactor are added

## Phase 19: Prop Library v2 MVP (005.3T)

- [X] T107 Add a small internal prop definition table for deterministic placeholder dimensions
- [X] T108 Support `shelf_unit`, `wooden_crate`, `table`, `chair`, `bed`, `cabinet`, `barrel`, and `box` keyword dimensions without external asset files
- [X] T109 Keep existing prop marker compatibility and generic cube fallback for unknown props
- [X] T110 Add non-Maya tests for known dimensions, `prop_type`/`name` lookup, unknown fallback, existing fixtures, and deterministic Maya placeholder output
- [X] T111 Update Vietnamese artist docs and quickstart with supported keywords, fallback behavior, and no-real-assets guidance
- [X] T112 Confirm no AI API, web UI, Feature 006, new dependencies, generated output commits, textures, materials, real 3D assets, new marker types, or SVG parsing rule changes are added

## Phase 20: Material/Color Tags MVP (005.3U)

- [X] T113 Parse `_mat_<name>`, `_material_<name>`, and `_color_<name>` suffixes from supported SVG group/layer labels
- [X] T114 Store optional material/color hints in prop marker and room-level Maya geometry JSON where available
- [X] T115 Create deterministic Maya materials for supported hints using names such as `mat_tpv_wood` and `mat_tpv_red`
- [X] T116 Keep unknown hints safe, untagged SVG behavior unchanged, and existing prop orientation plus door/window marker tests passing
- [X] T117 Update Vietnamese artist docs and quickstart with supported tags, examples, fallback behavior, and no-texture guidance
- [X] T118 Confirm no AI API, web UI, Feature 006, new dependencies, generated output commits, texture files, real asset materials, renderer changes, lighting/camera/render preview changes, or advanced CSS/style parsing are added
