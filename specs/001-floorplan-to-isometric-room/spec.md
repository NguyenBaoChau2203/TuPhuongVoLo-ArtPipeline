# Feature Specification: Floorplan to Isometric Room

**Feature Branch**: `001-floorplan-to-isometric-room`

**Created**: 2026-05-29

**Status**: Draft

**Input**: Artist-exported clean SVG floorplan → isometric room draft

## User Scenarios & Testing

### User Story 1 — Single Room Isometric Draft (Priority: P1)

The artist has a clean SVG floorplan exported from Illustrator. They want to pick a room (by name or layer) and generate an isometric 3D draft of that room with basic props from a preset.

**Why this priority**: This is the core value proposition — transforming flat floorplans into visual isometric drafts that the artist can review and polish.

**Independent Test**: Drop a test SVG into `drops/`, run the build script, verify a PNG preview + Blender scene appear in `outputs/`.

**Acceptance Scenarios**:

1. **Given** a clean SVG with room layers, **When** the artist runs `03_build_isometric_room.bat` with a room name, **Then** a PNG preview + `.blend` file are generated in `outputs/`.
2. **Given** a valid room name and style preset, **When** the script runs, **Then** the room has correct wall extrusion, floor plane, and preset props placed.
3. **Given** an SVG with no matching room layer, **When** the script runs, **Then** a clear error message in Vietnamese is shown.

---

### User Story 2 — Style Preset Selection (Priority: P2)

The artist can choose a visual style preset (line art, blockout, review render) that changes colors, lighting, and render quality.

**Why this priority**: Different stages of art review need different visual styles.

**Independent Test**: Run the same room with two different presets and verify the output colors/lighting differ.

**Acceptance Scenarios**:

1. **Given** a valid room and `line_art_green_floor` preset, **When** rendered, **Then** floor is green-tinted, walls are off-white, lines are dark.
2. **Given** a valid room and `grayscale_blockout` preset, **When** rendered, **Then** output is grayscale with no shadows.

---

### User Story 3 — Room Preset Props (Priority: P2)

Based on the room type (kho, phòng điều khiển, etc.), basic placeholder props are placed in the scene from `config/room_presets.yaml`.

**Why this priority**: Props make the isometric draft useful for visual review without requiring the artist to furnish every room manually.

**Independent Test**: Generate a "kho" room and verify shelves + crates appear.

**Acceptance Scenarios**:

1. **Given** a room preset `kho`, **When** the room is built, **Then** shelf_unit, wooden_crate, and cardboard_box props appear.
2. **Given** an unknown room preset, **When** the script runs, **Then** the room is built with empty floor and a warning is logged.

---

### User Story 4 — Manifest Entry (Priority: P3)

Every generated output (PNG, .blend, SVG) is recorded in the asset manifest with name, version, timestamp, and checksum.

**Why this priority**: Traceability and version management for generated assets.

**Independent Test**: Run a build, check `outputs/manifest/asset_manifest.json` for the new entry.

**Acceptance Scenarios**:

1. **Given** a successful build, **When** output is written, **Then** a manifest entry with all required fields is appended.

---

### Edge Cases

- What happens when the SVG has overlapping room boundaries?
- How does the system handle SVG with no valid paths (empty/corrupt file)?
- What if the room name contains Vietnamese diacritics?
- What if Blender is not installed?

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a clean SVG file path as input
- **FR-002**: System MUST accept an optional room name/layer identifier
- **FR-003**: System MUST accept a style preset name (default: `line_art_green_floor`)
- **FR-004**: System MUST accept a room preset name for prop placement
- **FR-005**: System MUST parse SVG paths to extract room boundaries (walls)
- **FR-006**: System MUST generate a Blender scene with extruded walls on a floor plane
- **FR-007**: System MUST set up an orthographic isometric camera (30° angle)
- **FR-008**: System MUST render a PNG preview with transparent background
- **FR-009**: System MUST save the `.blend` scene file for artist editing
- **FR-010**: System MUST generate output filenames following naming convention
- **FR-011**: System MUST write a manifest entry for each output
- **FR-012**: System MUST show Vietnamese error messages for artist-facing errors

### Key Entities

- **Room**: Extracted from SVG — has walls (paths), floor area, name/layer ID
- **RoomPreset**: YAML config defining props and materials for a room type
- **StylePreset**: YAML config defining colors, lighting, and render settings
- **ManifestEntry**: JSON record of generated output with metadata

## Success Criteria

### Measurable Outcomes

- **SC-001**: A clean SVG floorplan with labeled room layers can produce an isometric PNG preview in under 60 seconds
- **SC-002**: Generated `.blend` files can be opened and edited in Blender 4.x
- **SC-003**: Output filenames follow naming convention 100% of the time
- **SC-004**: Manifest is updated for every generated output
- **SC-005**: Artist can run the full workflow via `.bat` launcher without using terminal

## Assumptions

- Artist exports SVG with rooms on separate named layers
- SVG has been cleaned via Feature 002 pipeline before reaching this feature
- Blender 4.x is installed on the artist's Windows machine
- Room boundaries are closed paths (not open strokes)
- Props are placeholder geometry — not final game assets

## Out of Scope

- Perfect OCR from screenshots
- Final polished game art
- Full natural language control
- Complex procedural furniture generation
- Multi-floor buildings
- Curved walls
