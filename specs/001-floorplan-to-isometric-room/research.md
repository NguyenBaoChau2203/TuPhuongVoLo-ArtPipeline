# Research: Floorplan to Isometric Room

## SVG to 3D Isometric — Approach Research

### Recommended Pipeline

1. **SVG Parsing**: Use `svgpathtools 1.7.2` to parse SVG paths. Each room should be on a named layer/group in the SVG. Extract `<path>`, `<rect>`, `<polygon>` elements that define walls. Use svgpathtools capabilities: read/write SVG, get bbox, compute path length, compute area of closed paths, split continuous subpaths, detect intersections.

2. **Room Detection**: Rooms are identified by:
   - Named SVG groups (`<g id="room_kho">`)
   - Named layers (Illustrator layers export as named `<g>` elements)
   - Closed paths representing room boundaries
   - Filtering: discard paths shorter than `MIN_LENGTH` (8px) or with bbox smaller than `MIN_BBOX_SIDE` (2px) — these are tracing artifacts

3. **Blender Import**: Two approaches:
   - **Direct SVG import** (recommended): `bpy.ops.import_curve.svg(filepath=...)` converts paths to curves. Set `dimensions='2D'`, `fill_mode='BOTH'`, assign `extrude` value for wall height, then `scale = (0.01, 0.01, 0.01)` to normalize SVG px to scene units.
   - **Programmatic curve creation**: Parse SVG with svgpathtools, sample path segments at configurable `SAMPLES_PER_SEGMENT`, deduplicate points, create Blender curves from coordinates. More control but more code.
   - Start with Blender's native SVG import for simplicity. Fall back to programmatic if control is insufficient.

4. **Isometric Camera**: Standard isometric uses:
   - Orthographic projection (`cam_data.type = 'ORTHO'`)
   - Camera position: `(10, -10, 10)` looking at scene center
   - Rotation: `X = 54.7356°` (tilt), `Y = 0°`, `Z = 45°` — this is the strict isometric angle where `arctan(1/√2) ≈ 35.264°` from horizontal
   - Alternative: **2:1 dimetric** game look if closer to game aesthetic than technical isometric
   - `ortho_scale` auto-calculated from room bounding box + padding
   - Camera named `IsometricCamera`

5. **Wall Extrusion**: Convert 2D path to 3D wall:
   - Import SVG curves via `import_curve.svg`
   - Set curve data: `dimensions='2D'`, `fill_mode='BOTH'`, `extrude=0.28` (scene units)
   - Or convert to mesh and extrude faces for more control
   - Apply wall material from `config/style_presets.yaml`

6. **Lighting & Render**:
   - Default engine: EEVEE (fast preview)
   - Sun light at `rotation_euler = (45°, 0°, 35°)`
   - `film_transparent = True` for PNG alpha background
   - Resolution: `2048×2048` for production, configurable
   - Output format: PNG with RGBA

### Existing Tools & GitHub Repositories

| Repository | Purpose | License | Risk Level |
|-----------|---------|---------|------------|
| `grebtsew/FloorplanToBlender3d` | Auto-detect wall lines from floor plan images (PNG/PDF) using OpenCV → extruded 3D rooms in Blender | GPL-3.0 | Medium — deep dependencies, requires Docker on Windows |
| `mpbrucker/illustrator-isometric-transforms` | Automates SSR transforms in Illustrator via popup GUI — maps 2D art to isometric planes | MIT | Low — stable, unmaintained but fully operational on modern Illustrator CC |
| `creold/illustrator-scripts` (Osokin) | ExportSequence, SortLayerItems, TrimMasks, SplitPath — daily Illustrator automation | MIT | Low — highly active, verified on CC 2019–2026 |
| `sky-chaser-high/adobe-illustrator-scripts` | alignInCenterOfSpace, stepAndRepeat — grid alignment and asset scattering | MIT | Low — highly active |

### FloorplanToBlender3d Assessment

`FloorplanToBlender3d` (GPL-3.0) auto-detects wall lines from flat floor plan images using OpenCV and constructs extruded 3D room geometries inside Blender. Supports Python ≥3.8 and Blender >2.93.

**Why we don't use it directly**: It is image-based (PNG/PDF input), not SVG-based. Our pipeline uses clean SVG as the source of truth. However, its approach to wall detection and extrusion is a useful reference for our own `build_isometric_room.py` implementation.

### Isometric Transform Math (Illustrator SSR)

For mapping flat 2D Illustrator assets onto isometric planes, the standard SSR parameters are:

| Face | Scale Vertical | Shear | Rotate |
|------|---------------|-------|--------|
| Left wall | 86.602% | −30° | −30° |
| Right wall | 86.602% | +30° | +30° |
| Top face (Option A) | 86.602% | +30° | −30° |

These transforms are automated by `mpbrucker/illustrator-isometric-transforms` (MIT, stable). The `IsometricTransform.jsx` script provides a pop-up GUI for selecting the face. Can be mapped to hotkeys via Illustrator Actions (e.g., F2).

### Key Libraries

| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| svgpathtools | 1.7.2 | SVG path parsing, bbox, area, length, intersection | Pure Python, Python ≥3.8 |
| vpype | 1.15.0 | SVG cleanup/simplification batch pipeline | Python ≥3.11,<3.14 |
| bpy | (Blender built-in) | Blender Python API | Only available inside Blender |
| lxml | (latest) | SVG/XML parsing | Fallback for structure parsing |
| Potrace | 1.16 | B&W line art to SVG tracing | Binary, deterministic, includes mkbitmap |
| Vectorizer.AI | Web/API | Color/transparency-aware tracing | Web app $9.99/mo, API usage-based |

### Maya SVG Import — Research Finding

> **Critical**: No first-party SVG import for Maya was confirmed in official Autodesk product help documentation. The English research mentions "Maya SVG Import (Built-in)" as "Create > SVG" tool, but the Vietnamese research explicitly contradicts this after deeper investigation and recommends against relying on it.

**Safe Maya paths**:
1. **Python parser**: Use `svgpathtools` to parse SVG, sample path segments, then create Maya polygons via `cmds.polyCreateFacet(p=pts3d)` and `cmds.polyExtrudeFacet` for wall height. This is the research-recommended approach.
2. **Blender → USD → Maya**: Export from Blender as USD, import in Maya via `Autodesk/maya-usd` plugin (supports Maya 2023–2027, MIT-like license, 16,842 commits).

### Risks & Mitigations

| Risk | Source | Mitigation |
|------|--------|------------|
| SVG paths may not form clean closed loops | Tracing artifacts | Validation step in Feature 002; svgpathtools area/length filtering |
| Blender's SVG importer may struggle with complex Illustrator exports | Dense Illustrator output | Always run vpype cleanup before import |
| Props are placeholder geometry | Scope limitation | Artist must understand these are drafts, not final |
| Poor 3D mesh topology from auto-extrude | Research: triangulated/messy meshes | Keep blockout as non-rendering reference; final art built manually |
| Camera misalignment | Isometric math precision | Unit test: place a cube and verify three axes have equal foreshortening |
| Closed paths with holes/self-intersection | Complex room geometry | Tách outer/inner contours first in Illustrator or svgpathtools, or use Blender boolean |

### Mandatory Test Cases

1. **Motel room** — Interior, walls closed, minimal furniture, orthographic render with clear layer separation. Pass if: extrude doesn't flip faces; furniture silhouettes don't overlap incorrectly; alpha is clean.
2. **Island map** — Complex coastline, small islands, path cleanup must keep main silhouette but remove tracing dust. Pass if: no runt paths remain; main contour intact; isometric camera produces readable height map.

### References

- Blender Python API: https://docs.blender.org/api/current/
- svgpathtools: https://github.com/mathandy/svgpathtools (MIT, 358 commits, PyPI 1.7.2)
- vpype: https://github.com/abey79/vpype (MIT, 519 commits, PyPI 1.15.0)
- Potrace: https://potrace.sourceforge.net/ (GPL-2.0, v1.16)
- Isometric projection math: https://en.wikipedia.org/wiki/Isometric_projection
- FloorplanToBlender3d: https://github.com/grebtsew/FloorplanToBlender3d (GPL-3.0)
- IsometricTransform.jsx: https://github.com/mpbrucker/illustrator-isometric-transforms (MIT)
- Autodesk Maya USD: https://github.com/Autodesk/maya-usd (supports Maya 2023–2027)
- Illustrator MCP (jinkeda): https://github.com/jinkeda/Illustrator_MCP (MIT)
- Illustrator MCP (krVatsal): https://github.com/krVatsal/illustrator-mcp (MIT)

## Research Incorporated

This document was substantially expanded on 2026-05-29 with findings from:
- `docs/research/Indie Game Art Workflow Automation Research.md` — GitHub repo registry, FloorplanToBlender3d assessment, SSR isometric transform parameters, MCP server references.
- `docs/research/Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ.md` — Blender curve import specifics (`dimensions='2D'`, `fill_mode='BOTH'`, `extrude`), camera math, Maya SVG import limitation, svgpathtools code samples, mandatory test cases.
