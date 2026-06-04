# Feature Specification: Artist Prompt Control Loop MVP

**Feature Branch**: `workflow/maya-first-artist-pipeline`

**Created**: 2026-06-04

**Status**: Approved for documentation and workflow reset

**Input**: User request for Feature 015A: document the true product direction as a prompt-driven Illustrator + Maya art assistant loop for a Vietnamese-speaking artist/operator.

## Product Direction

This feature resets the project direction for future models and operators. The project is no longer only:

```text
SVG -> Maya blockout
```

The target workflow is:

```text
Artist prompt
-> AI controls Illustrator sandbox when MCP is healthy
-> SVG export
-> App/CLI builds Maya
-> Visual Fidelity pass
-> Maya sandbox
-> Artist prompt
-> Codex controls Maya polish
-> Artist review / rollback loop
```

This is a prompt-control workflow feature, not a full autonomous art generator. Illustrator and Maya remain the production tools. AI agents are technical operators that work only inside sandboxed copies, with mandatory artist review after every meaningful change. Manual SVG export remains the safe fallback while the Illustrator MCP EOF blocker is unresolved.

## User Scenarios & Testing

### User Story 1 - Daily Prompt-Control Handoff (Priority: P1)

The artist/operator can follow one Vietnamese daily workflow for tomorrow's stable path: manual Illustrator SVG export, app/CLI Maya build, Visual Fidelity pass, Maya sandbox, Codex prompt polish, review, and rollback.

**Why this priority**: The artist needs a safe, concrete workflow now, without waiting for Illustrator MCP repair.

**Independent Test**: Open `docs/artist_daily_workflow_vi.md` and verify it answers what to open, what to export, what app/CLI step to run, what Maya file to open, what prompt to paste, how to review, how to rollback, and what remains beta.

**Acceptance Scenarios**:

1. **Given** Illustrator MCP is unavailable or returns EOF, **When** the artist needs to continue production, **Then** the workflow directs them to manually export SVG and continue through the existing Maya pipeline.
2. **Given** the Visual Fidelity sandbox path is available, **When** the operator prepares a prompt polish session, **Then** the workflow identifies the sandbox working `.ma` and restore script to use.

---

### User Story 2 - Maya Prompt Loop Template (Priority: P1)

The artist/operator can copy a prompt template that tells Codex exactly which Maya sandbox scene is allowed, what Vietnamese art request to perform, what edit style is allowed, what edits are forbidden, what agent group name is required, how the artist should review, and where rollback lives.

**Why this priority**: Maya prompt polish is the nearer stable target because Codex + Maya sandbox inspect/edit/save/rollback have already passed controlled tests.

**Independent Test**: Open `docs/templates/maya_artist_prompt_template_vi.md` and verify it contains placeholders for scene path, sandbox path, artist request in Vietnamese, allowed edit style, forbidden edits, required group name, review instructions, and rollback path.

**Acceptance Scenarios**:

1. **Given** a sandbox working `.ma`, **When** the operator fills the template, **Then** the prompt requires a scene path guard before any edit/save.
2. **Given** Codex makes polish changes, **When** the artist reviews the scene, **Then** changes are isolated under a named agent group and rollback instructions are visible.

---

### User Story 3 - Illustrator Prompt Loop Template (Priority: P2)

The artist/operator can copy a prompt template for Antigravity to control only an Illustrator sandbox `.ai` after MCP health is repaired and a path-guard smoke test passes.

**Why this priority**: Illustrator prompt control is part of the real product, but it is beta/blocked until the Antigravity Illustrator MCP EOF issue is repaired.

**Independent Test**: Open `docs/templates/illustrator_artist_prompt_template_vi.md` and verify it contains placeholders for original AI path, sandbox AI path, artist request in Vietnamese, active document guard, allowed edits, forbidden edits, export policy, and stop conditions.

**Acceptance Scenarios**:

1. **Given** the Illustrator MCP server returns EOF on inspect/help calls, **When** the operator reads the template, **Then** it states to stop and use manual SVG export.
2. **Given** MCP health is confirmed, **When** Antigravity edits Illustrator, **Then** it must verify the active document path is the sandbox `.ai` before edit/save/export.

---

### User Story 4 - Future Model Routing and Safety Reset (Priority: P2)

Future agents can read one concise feature spec and Vietnamese docs that route models by task complexity and preserve safety constraints for Illustrator and Maya prompt loops.

**Why this priority**: The repo needs a clear handoff so later models do not regress to treating the pipeline as only SVG-to-blockout automation.

**Independent Test**: Inspect `specs/015-artist-prompt-control-loop/`, `docs/artist_prompt_control_loop_vi.md`, and README links; verify the two loops, model routing, safety checklist, and beta/stable status are explicit.

**Acceptance Scenarios**:

1. **Given** a future model starts from README or current specs, **When** it searches for Feature 015, **Then** it finds the prompt-control product goal and daily workflow.
2. **Given** a prompt-control task is requested, **When** the model selects an operating mode, **Then** it follows the documented model routing and sandbox safety status.

## Edge Cases

- Illustrator MCP may return EOF on `view`, `help`, or `get_system_prompt`; the workflow must stop and use manual export.
- The artist may accidentally provide an original `.ai`, `.svg`, or `.ma`; prompts must require sandbox path guards and no-original-file edits.
- Maya may have a different scene open; Codex must verify the current scene path before any edit/save.
- Visual Fidelity may be optional; the workflow must still explain how to proceed from a plain blockout sandbox.
- The artist may want destructive cleanup; the MVP only allows additive or guarded polish under agent-owned groups.
- Rollback scripts live outside the repo; docs may reference them but this phase must not touch those files.

## Requirements

### Functional Requirements

- **FR-001**: The SDD artifacts MUST state that Feature 015A is a prompt-control workflow reset, not a full autonomous art generator.
- **FR-002**: The SDD artifacts MUST state that Illustrator and Maya remain the production tools and AI agents are sandboxed technical operators.
- **FR-003**: The workflow MUST require artist review after AI-operated Illustrator or Maya changes.
- **FR-004**: The workflow MUST preserve manual SVG export as the safe fallback while the Illustrator MCP EOF blocker is unresolved.
- **FR-005**: The documentation MUST define an Illustrator Prompt Loop with status Beta/blocked until an MCP EOF repair smoke test passes.
- **FR-006**: The documentation MUST define a Maya Prompt Loop with status MVP-ready after Visual Fidelity pass and Maya sandbox creation.
- **FR-007**: The daily workflow MUST cover manual SVG export, app/CLI preflight/dry-run/Maya build, Visual Fidelity pass, Maya sandbox, Codex prompt polish, review, and rollback.
- **FR-008**: The Maya prompt template MUST include placeholders for scene path, sandbox path, artist request in Vietnamese, allowed edit style, forbidden edits, required group name, review instructions, and rollback path.
- **FR-009**: The Illustrator prompt template MUST include placeholders for original AI path, sandbox AI path, artist request in Vietnamese, active document guard, allowed edits, forbidden edits, export policy, and stop conditions.
- **FR-010**: The safety checklist MUST include no original file edits, sandbox-only working files, active document/scene path guard, no overwrite, agent groups, hash checks where appropriate, rollback procedure, known MCP EOF blocker, and manual export fallback.
- **FR-011**: The model routing guidance MUST include Codex GPT-5.5 medium/high/xhigh, Antigravity Claude Sonnet 4.6, Antigravity Claude Opus 4.6, and Gemini light inspect/report usage.
- **FR-012**: Feature 015A MUST NOT implement a new app, use Illustrator MCP, use Maya commandPort, run Maya edits, touch external sandbox files, or modify generated outputs.

### Key Entities

- **Artist Prompt Control Loop**: The end-to-end workflow where Vietnamese art-direction prompts are translated into guarded Illustrator or Maya sandbox operations.
- **Illustrator Prompt Loop**: Beta loop for Antigravity-controlled Illustrator sandbox editing/export after MCP health is restored.
- **Maya Prompt Loop**: MVP-ready loop for Codex-controlled guarded polish on a Maya sandbox working scene.
- **Sandbox Working File**: The only file an agent may inspect/edit/save during a prompt loop.
- **Agent Group**: A named Maya group containing all additive prompt-polish changes for review and rollback.
- **Rollback Script**: The sandbox restore script used to return a working file to its pre-agent state.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All four SDD files exist under `specs/015-artist-prompt-control-loop/`.
- **SC-002**: Both prompt templates exist under `docs/templates/` and contain all required placeholders.
- **SC-003**: `docs/artist_daily_workflow_vi.md` gives a complete tomorrow workflow in Vietnamese.
- **SC-004**: README and the desktop handoff doc link to the daily workflow and prompt-control loop docs.
- **SC-005**: Documentation validation or full pytest completes without failures, or any unrelated failure is clearly documented and no commit is made.
- **SC-006**: No external sandbox files, generated `.ma`, `.svg`, `.json`, `.png`, `.zip`, MCP sessions, Maya sessions, or pushes are used in 015A.

## Assumptions

- The current branch is `workflow/maya-first-artist-pipeline`.
- Feature 014A Visual Fidelity MVP is implemented and available.
- The 014C Visual Fidelity sandbox exists outside the repo for artist review:
  `D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\working\scene_agent_work.ma`
- The matching restore script exists outside the repo:
  `D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\restore_agent_backup.ps1`
- Illustrator MCP daily prompt control remains beta/blocked until EOF repair and path-guard smoke tests pass.
- Maya prompt polish should be validated next in Feature 015B using the 014C Visual Fidelity sandbox.
