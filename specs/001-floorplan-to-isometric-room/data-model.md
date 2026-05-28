# Data Model: Floorplan to Isometric Room

## Entities

### Room
Extracted from a clean SVG file. Represents a single room in a floorplan.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Room identifier from SVG layer/group name |
| `walls` | list[WallSegment] | Ordered list of wall segments forming the boundary |
| `floor_polygon` | list[Point2D] | Closed polygon for floor plane |
| `layer_id` | string | SVG layer/group ID |
| `source_file` | Path | Path to the source SVG |
| `bounding_box` | BBox2D | Axis-aligned bounding box |

### WallSegment
A single straight wall segment (curves simplified to line segments).

| Field | Type | Description |
|-------|------|-------------|
| `start` | Point2D | Start point (x, y) in SVG units |
| `end` | Point2D | End point (x, y) in SVG units |
| `height` | float | Wall height from preset (meters) |
| `thickness` | float | Wall thickness (default 0.15m) |

### Point2D
| Field | Type | Description |
|-------|------|-------------|
| `x` | float | X coordinate |
| `y` | float | Y coordinate |

### RoomPreset
Loaded from `config/room_presets.yaml`.

| Field | Type | Description |
|-------|------|-------------|
| `preset_name` | string | Key in room_presets.yaml |
| `display_name` | string | Human-readable name |
| `display_name_vi` | string | Vietnamese name |
| `floor_material` | string | Material identifier for floor |
| `wall_height` | float | Default wall height in meters |
| `props` | list[PropDef] | Props to place in the room |

### PropDef
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Prop identifier |
| `count` | int | Number to place |
| `placement` | string | Placement strategy (along_wall, center, corner, etc.) |

### StylePreset
Loaded from `config/style_presets.yaml`.

| Field | Type | Description |
|-------|------|-------------|
| `preset_name` | string | Key in style_presets.yaml |
| `background` | string | Background color or "transparent" |
| `floor_color` | string | Hex color for floor |
| `wall_color` | string | Hex color for walls |
| `line_color` | string | Hex color for outlines |
| `line_weight` | float | Outline weight in pixels |
| `ambient_light` | float | Ambient light intensity (0–1) |
| `use_shadows` | bool | Whether to render shadows |
| `render_engine` | string | "EEVEE" or "CYCLES" |

### ManifestEntry
Written to `outputs/manifest/asset_manifest.json`.

| Field | Type | Description |
|-------|------|-------------|
| `asset_name` | string | Asset identifier |
| `variant` | string | Variant (main, alt, etc.) |
| `stage` | string | Pipeline stage |
| `version` | string | Version number (e.g., "001") |
| `source_file` | string | Input SVG path |
| `output_path` | string | Generated output path |
| `timestamp` | string | ISO 8601 timestamp |
| `checksum` | string | SHA-256 hash |
| `pipeline_step` | string | Feature/script that generated this |

## Relationships

```
SVG File → contains → Room(s)
Room → has → WallSegment(s)
Room → uses → RoomPreset (for props)
Room → uses → StylePreset (for visuals)
Build Run → produces → ManifestEntry(s)
```
