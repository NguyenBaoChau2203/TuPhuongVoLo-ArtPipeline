# Data Model: Artist-Focused Repo Cleanup

## Daily Workflow Surface

**Represents**: The files an artist/operator should read or run every day.

**Fields**:

- `entry_doc`: `README.md`
- `artist_doc`: `docs/WORKFLOW_FOR_WIFE_VI.md`
- `prompt_doc`: `docs/CODEX_PROMPTS_VI.md`
- `launchers`: `00_maya_env_check.bat`, `07_build_maya_room.bat`, `09_artist_desktop_app.bat`
- `core_scripts`: SVG preflight, Maya build, Visual Fidelity, Maya sandbox

**Validation Rules**:

- Must not require old feature branch checkout.
- Must not route the artist into optional AI preview, Blender, or roadmap docs as the main path.
- Must state output folders and next review action.

## Archived Surface

**Represents**: Optional, legacy, research, or historical content retained but removed from the daily path.

**Fields**:

- `archive_index`: `archive/README.md`
- `legacy_code_paths`: retained in original locations when moving would break tests or constitution
- `archived_doc_paths`: optional docs moved under `archive/` where safe
- `hidden_docs`: docs that remain in place because app/tests reference them, but are no longer linked from the daily path

**Validation Rules**:

- Must preserve provenance and explain why content is not daily workflow.
- Must not include generated outputs or secrets.

## Illustrator Draft Template

**Represents**: A starter JSX file Codex can copy and customize from a reference image.

**Fields**:

- `canvas_setup`
- `pipeline_layers`
- `room_group_names`
- `door_window_marker_names`
- `prop_marker_names`
- `flow_path_names`
- `artist_notes`

**Validation Rules**:

- Must use pipeline-friendly prefixes: `room_`, `door_`, `window_`, `prop_`, `flow_`.
- Must create editable Illustrator objects, not raster-only placeholders.
- Must avoid automatic SVG export by default for artist review.

## Maya Polish Template

**Represents**: A starter Maya Python file Codex can copy and customize for sandbox-only polish.

**Fields**:

- `required_scene_guard`
- `agent_group_name`
- `allowed_operations`
- `forbidden_operations`
- `materials`
- `lights`
- `review_camera`
- `artist_note`

**Validation Rules**:

- Must add or edit only agent-owned objects unless explicitly instructed otherwise.
- Must keep new objects under `GRP_agent_*`.
- Must tell the operator to run it only on `working/scene_agent_work.ma`.
