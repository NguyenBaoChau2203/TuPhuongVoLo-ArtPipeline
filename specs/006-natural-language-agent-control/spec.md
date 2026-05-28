# Feature Specification: Natural Language Agent Control

**Feature Branch**: `006-natural-language-agent-control`

**Created**: 2026-05-29

**Status**: Draft — Future Feature

> ⚠️ **IMPORTANT**: This feature MUST NOT be implemented before Features 001–004 are functional. It is a future intelligence layer that wraps existing pipeline scripts.

## User Scenarios & Testing

### User Story 1 — Natural Language Command Execution (Priority: P1)

The artist or developer issues natural language commands like "Render all rooms from building_a.svg in grayscale blockout style" and the system translates this to the correct pipeline commands.

**Why this priority**: Natural language is the ultimate usability improvement for a non-programmer artist.

**Independent Test**: Issue a natural language command, verify the correct pipeline script is invoked with correct arguments.

**Acceptance Scenarios**:

1. **Given** "Render kho room from floorplan.svg", **When** processed, **Then** the system invokes `build_isometric_room.py` with `--room kho --input floorplan.svg`.
2. **Given** "Clean all SVGs in drops/", **When** processed, **Then** the system invokes `clean_svg_paths.py` on each SVG in `drops/`.

---

### User Story 2 — MCP Server Integration (Priority: P2)

An MCP (Model Context Protocol) server exposes pipeline tools to AI assistants, enabling tool-use-based automation.

**Acceptance Scenarios**:

1. **Given** an MCP-compatible client, **When** it lists tools, **Then** pipeline tools are available (clean_svg, build_room, batch_render, etc.).

---

### User Story 3 — Safety Guardrails (Priority: P1)

Natural language commands must be validated before execution — no destructive operations, no source file modification, no operations outside the pipeline scope.

**Acceptance Scenarios**:

1. **Given** "Delete all files in assets/", **When** processed, **Then** the command is rejected with explanation.
2. **Given** any command, **When** processed, **Then** the system shows what it will do and asks for confirmation before executing.

---

### Edge Cases

- What if the natural language is ambiguous?
- What if the requested file doesn't exist?
- What if multiple interpretations are equally valid?

## Requirements

- **FR-001**: System MUST parse natural language commands related to the art pipeline
- **FR-002**: System MUST map commands to existing pipeline scripts
- **FR-003**: System MUST show the translated command before execution
- **FR-004**: System MUST require confirmation for any file operations
- **FR-005**: System MUST reject destructive operations
- **FR-006**: System MAY expose tools via MCP server

## Success Criteria

- **SC-001**: Common pipeline commands (clean, render, batch) are correctly interpreted
- **SC-002**: No destructive operation can be triggered via NLC
- **SC-003**: Artist can operate basic pipeline without knowing script names

## Assumptions

- Features 001–004 are implemented and functional
- Local LLM or API access is available (not guaranteed)
- This is a v2+ feature — not needed for initial pipeline operation

## Dependencies

- Feature 001: Floorplan to Isometric Room (scripts to wrap)
- Feature 002: Illustrator Export & Clean SVG (scripts to wrap)
- Feature 003: Asset Naming & Manifest (scripts to wrap)
- Feature 004: Batch Isometric Render (scripts to wrap)
