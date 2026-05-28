---
name: floorplan-to-isometric
description: Convert a clean SVG floorplan room into an isometric 3D draft using Blender Python
---

# Skill: Floorplan to Isometric

## When to Use

Use this skill when the task involves:
- Converting a clean SVG floorplan into a 3D isometric room
- Setting up Blender scenes from SVG wall geometry
- Generating isometric PNG previews from floorplans
- Placing preset props in isometric room scenes

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Clean SVG file | `.svg` file | Yes | SVG that passes validation (from Feature 002) |
| Room name | string | No | Layer/group name to extract (default: first room found) |
| Style preset | string | No | Key from `config/style_presets.yaml` (default: `line_art_green_floor`) |
| Room preset | string | No | Key from `config/room_presets.yaml` (default: auto-detect) |

## Outputs

| Output | Type | Location | Description |
|--------|------|----------|-------------|
| PNG preview | image | `outputs/preview/` | Transparent PNG isometric render |
| Blender scene | `.blend` | `outputs/blender/` | Editable Blender scene file |
| Manifest entry | JSON | `outputs/manifest/` | Metadata record |

## Required Workflow

1. **Validate SVG** — Run `validate_svg_contract.py` on input
2. **Detect rooms** — Run `detect_rooms_from_svg.py` to list available rooms
3. **Build scene** — Run `build_isometric_room.py` in Blender headless mode
4. **Verify output** — Check PNG and .blend exist, manifest is updated
5. **Follow naming** — All outputs use naming convention

## Style & Safety Rules

- Never modify the source SVG
- Always output to `outputs/` directories
- Use orthographic camera (never perspective)
- Default isometric angle: 30° from horizontal
- PNG must have transparent background
- Blender scene must be saveable and reopenable

## Success Criteria

- [ ] PNG preview generated with correct style
- [ ] .blend file opens in Blender 4.x
- [ ] Manifest entry created with all required fields
- [ ] Output filename follows naming convention
- [ ] Room walls are correctly extruded from SVG paths

## Common Failure Cases

| Failure | Cause | Fix |
|---------|-------|-----|
| Empty render | Camera outside room bounds | Auto-fit camera to bounding box |
| No rooms found | SVG has no named groups | Ensure SVG has `<g id="room_...">` elements |
| Import fails | SVG has unsupported features | Run cleanup pipeline first |
| Props missing | Unknown room preset | Use empty room + warn |

## Future Implementation Notes

- Consider caching parsed SVG data for batch runs
- Props will start as basic geometry — future: use actual asset library
- Consider LOD (level of detail) for large rooms
