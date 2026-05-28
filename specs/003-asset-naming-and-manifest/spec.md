# Feature Specification: Asset Naming & Manifest

**Feature Branch**: `003-asset-naming-and-manifest`

**Created**: 2026-05-29

**Status**: Draft

## User Scenarios & Testing

### User Story 1 — Drop & Auto-Name (Priority: P1)

The artist drops files into `drops/`. A Python agent ingests them, creates versioned names following the naming convention, moves assets to correct folders, and writes a manifest entry.

**Why this priority**: Consistent naming is required by all other features.

**Independent Test**: Drop a test file into `drops/`, run the agent, verify it appears in the correct folder with the correct name.

**Acceptance Scenarios**:

1. **Given** a file `room_sketch.svg` in `drops/`, **When** the agent runs, **Then** it is moved to `assets/2d/svg_raw/tu_phuong_vo_lo_room_sketch_main_raw_v001.svg`.
2. **Given** a file that already has a versioned name, **When** the agent runs, **Then** it increments the version number.
3. **Given** a manifest already exists, **When** the agent runs, **Then** the new entry is appended (not overwritten).

---

### User Story 2 — Manifest Query (Priority: P2)

A developer or script can query the manifest to find assets by name, stage, or version.

**Acceptance Scenarios**:

1. **Given** a populated manifest, **When** queried for `stage=svgclean`, **Then** all clean SVGs are returned.

---

### Edge Cases

- What if the dropped file has no extension?
- What if two files have identical names?
- What if the manifest JSON is corrupted?

## Requirements

- **FR-001**: System MUST watch/process `drops/` folder
- **FR-002**: System MUST apply naming convention from `config/naming_convention.yaml`
- **FR-003**: System MUST auto-increment version numbers
- **FR-004**: System MUST write manifest entries in JSON format
- **FR-005**: System MUST compute SHA-256 checksums

## Success Criteria

- **SC-001**: Every processed file has a name matching the naming pattern
- **SC-002**: Manifest contains entries for all processed assets
- **SC-003**: No files are lost or overwritten during processing

## Assumptions

- Artist drops files manually or via Illustrator export
- One file at a time is sufficient for v1 (batch is a stretch goal)
