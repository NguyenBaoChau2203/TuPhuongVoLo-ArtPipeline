# Feature Specification: Artist-Focused Repo Cleanup

**Feature Branch**: `codex/016-artist-focused-repo-cleanup`

**Created**: 2026-06-05

**Status**: Draft

**Input**: User description: "Dọn repo thành một workflow chính duy nhất cho vợ: ảnh mẫu + mô tả -> Codex tạo JSX draft -> chỉnh Illustrator/export SVG -> app kiểm SVG/dry-run/tạo Maya .ma -> Visual Fidelity nếu cần -> Maya sandbox -> Codex tạo Maya Python polish script -> vợ review/rollback. Đưa phần cũ/optional vào archive hoặc ẩn khỏi README, thêm docs/prompt/template cần thiết, sửa README ngắn gọn và chuyên nghiệp."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily Artist Workflow Is Obvious (Priority: P1)

The artist and operator can open the repository and immediately understand the one supported daily workflow without reading old phase history, optional AI preview experiments, Blender fallback notes, or research docs.

**Why this priority**: The current repo feels like many experiments at once. The artist needs one calming workflow that starts from a reference image and ends with a Maya scene review.

**Independent Test**: Open `README.md` and `docs/WORKFLOW_FOR_WIFE_VI.md`; verify they explain the daily path, commands/app entry points, outputs, and next action after Maya generation in Vietnamese or simple operator English without branch confusion.

**Acceptance Scenarios**:

1. **Given** a clean checkout on `master`, **When** the artist reads the README, **Then** the primary path is reference image -> JSX draft -> SVG -> Maya .ma -> sandbox polish -> review/rollback.
2. **Given** old optional features exist, **When** the artist follows the README, **Then** they are not routed into AI preview, Blender, batch, or natural-language roadmap docs.

---

### User Story 2 - Prompt Templates Reduce Blank-Page Work (Priority: P1)

The operator can copy ready prompts for Codex to create an Illustrator JSX draft from a reference image and to create an additive Maya polish script after the `.ma` exists.

**Why this priority**: The biggest pain is the artist drawing from a blank Illustrator page. The cleanup must add practical prompts and templates, not just remove clutter.

**Independent Test**: Open `docs/CODEX_PROMPTS_VI.md`, `scripts/illustrator/templates/reference_to_layout_draft.jsx`, and `scripts/maya/agent_polish_templates/agent_polish_additive_template.py`; verify each contains placeholders, naming guidance, and sandbox/group safety rules.

**Acceptance Scenarios**:

1. **Given** the artist sends a reference image and Vietnamese description, **When** the operator uses the prompt doc, **Then** Codex can produce a JSX draft with pipeline-friendly groups such as `room_*`, `door_*`, `window_*`, and `prop_*`.
2. **Given** a Maya sandbox working scene exists, **When** the operator uses the Maya polish prompt, **Then** Codex is instructed to add changes under an agent-owned group and avoid changing source walls/doors.

---

### User Story 3 - Legacy Work Is Preserved But Out Of The Way (Priority: P2)

Legacy or optional work remains available for developers, but the daily artist surface no longer presents it as the main path.

**Why this priority**: The repo must look professional without destroying prior tested work or violating the constitution's fallback requirements.

**Independent Test**: Inspect `archive/README.md`, `launchers/README_LAUNCHERS_VI.md`, and README; verify archived/legacy surfaces are documented separately and daily launchers are limited to environment check, one-room Maya build, and desktop app.

**Acceptance Scenarios**:

1. **Given** legacy Blender code still has tests, **When** cleanup completes, **Then** it remains discoverable as legacy/fallback but is not highlighted in the daily workflow.
2. **Given** AI polish preview and research documents are not part of the daily path, **When** cleanup completes, **Then** they are archived or clearly marked optional outside the main README.

---

### User Story 4 - Verification Stays Trustworthy (Priority: P2)

The cleanup does not break the core SVG/Maya/app/sandbox tools and leaves a clear quickstart for validation.

**Why this priority**: The repo is useful only if the simplified surface still runs the existing pipeline.

**Independent Test**: Run targeted tests for SVG preflight, Maya build dry-run, desktop app command construction, Visual Fidelity, and Maya sandbox; run the quickstart smoke commands without requiring Maya for dry-run paths.

**Acceptance Scenarios**:

1. **Given** Maya is not installed or `mayapy` is not in PATH, **When** the core dry-run commands execute, **Then** they still pass without requiring actual Maya.
2. **Given** the test suite has local temp permission issues, **When** tests are reported, **Then** the known `tests/tmp` ignore workaround is documented honestly.

### Edge Cases

- Archived files must not include generated `.ma`, `.svg`, `.json`, `.png`, `.zip`, secrets, or external sandbox outputs.
- Cleanup must not delete or overwrite artist source files in `assets/`, `drops/`, or external backup folders.
- References to deleted remote branch `workflow/maya-first-artist-pipeline` must be replaced for daily docs.
- Optional features with tests should not be broken merely because they are hidden from the artist workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: README MUST present one primary workflow: reference image and Vietnamese description -> Codex JSX draft -> Illustrator edit/export SVG -> desktop app or CLI builds Maya `.ma` -> optional Visual Fidelity -> Maya sandbox -> Codex Maya Python polish -> artist review/rollback.
- **FR-002**: README MUST provide the shortest reliable way to open the artist app and the fallback CLI commands for SVG preflight, Maya dry-run, actual Maya build, Visual Fidelity, and sandbox creation.
- **FR-003**: Artist-facing daily instructions MUST live in `docs/WORKFLOW_FOR_WIFE_VI.md` and be written in Vietnamese.
- **FR-004**: Prompt templates MUST live in `docs/CODEX_PROMPTS_VI.md` and cover both reference-image-to-JSX and Maya sandbox polish.
- **FR-005**: The repo MUST include an Illustrator JSX draft template under `scripts/illustrator/templates/` with pipeline group naming examples.
- **FR-006**: The repo MUST include a Maya Python polish template under `scripts/maya/agent_polish_templates/` with additive group isolation and no-source-layout-change rules.
- **FR-007**: Legacy/optional surfaces MUST be archived or hidden from daily README flow, including AI polish preview docs, long research docs, old verification docs, natural-language roadmap, Blender/isometric daily links, and batch/package launchers not needed by the artist day-to-day.
- **FR-008**: Cleanup MUST preserve core production files and tests for SVG preflight, Maya build, desktop app, Visual Fidelity, and Maya sandbox.
- **FR-009**: Daily docs MUST no longer tell users to checkout the deleted `workflow/maya-first-artist-pipeline` branch.
- **FR-010**: No cleanup step may overwrite, delete, or move source artwork or generated outputs into source folders.
- **FR-011**: `AGENTS.md` MUST point to the current Feature 016 plan while this cleanup is active.
- **FR-012**: The quickstart MUST define verification commands and expected output locations.
- **FR-013**: The artist desktop app MUST expose clear post-build controls for Visual Fidelity, Maya sandbox creation, and opening the latest sandbox working scene, without requiring the artist to type terminal commands.
- **FR-014**: The daily launcher set MUST include a Windows `.bat` launcher for creating a Maya sandbox from an existing `.ma` scene.

### Key Entities

- **Daily Workflow Surface**: README plus Vietnamese docs that the artist/operator reads first.
- **Archived Surface**: Documents or launchers retained for reference but removed from the daily path.
- **Illustrator Draft Template**: A JSX starter that Codex can customize from a reference image.
- **Maya Polish Template**: A Maya Python starter that Codex can customize for sandbox-only additive edits.
- **Core Pipeline Tools**: Existing scripts and launchers required for SVG validation, Maya scene generation, Visual Fidelity, and sandbox/rollback.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can identify the daily workflow and first launcher from the README in under two minutes.
- **SC-002**: The daily workflow doc contains no branch checkout instruction for deleted feature branches.
- **SC-003**: The prompt doc contains at least one copyable JSX prompt and one copyable Maya polish prompt.
- **SC-004**: The repository contains at least one JSX draft template and one Maya polish template.
- **SC-005**: Core targeted tests for preflight, Maya build, desktop app, Visual Fidelity, and Maya sandbox pass, or any environment-only limitation is explicitly documented.
- **SC-006**: `git status` shows only intentional cleanup/spec/template/doc changes and no generated output files.

## Assumptions

- The primary daily user is a Vietnamese-speaking artist working on Windows with Illustrator and Maya.
- Existing code for SVG parsing, Maya `.ma` generation, Visual Fidelity, and sandbox backup remains the technical backbone.
- Blender and earlier isometric code are retained as legacy/fallback per constitution but are not presented as the daily production path.
- AI polish preview remains optional/reference-only and is not part of the simplified daily workflow.
- Codex will generate customized JSX or Maya Python per reference image/prompt during normal use; Feature 016 provides templates and instructions rather than a fully automated image-to-JSX service.
