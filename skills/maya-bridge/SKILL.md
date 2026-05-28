---
name: maya-bridge
description: Optional Maya integration for advanced isometric rendering and USD interchange
---

# Skill: Maya Bridge

## When to Use

Use this skill when the task involves:
- Setting up isometric cameras in Maya matching the Blender pipeline
- Importing SVG geometry into Maya (via USD bridge or custom parser)
- Rendering isometric previews via mayapy
- USD interchange between Blender and Maya

> ⚠️ This is an OPTIONAL ADVANCED skill. The primary pipeline uses Blender.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Clean SVG or USD | file | Yes | Geometry source |
| Style preset | string | No | From `config/style_presets.yaml` |

## Outputs

| Output | Type | Location | Description |
|--------|------|----------|-------------|
| Maya scene | `.ma` | `outputs/maya/` | Maya scene file |
| PNG render | image | `outputs/maya/` | Isometric preview |

## Required Workflow

1. **Check Maya** — Verify mayapy is available (graceful failure if not)
2. **Import** — Import geometry via chosen method
3. **Camera** — Setup isometric camera matching Blender parameters
4. **Render** — Execute headless render via mayapy
5. **Output** — Save to `outputs/maya/`

## Style & Safety Rules

- Maya features MUST NOT block Blender pipeline
- Always check Maya availability before running
- Fail gracefully with helpful message if Maya is absent
- Match Blender camera parameters for consistency
- Use mayapy for headless execution

## Success Criteria

- [ ] Scripts work via mayapy (headless)
- [ ] Camera matches Blender isometric setup
- [ ] Graceful failure when Maya is not installed
- [ ] Output follows naming convention

## Common Failure Cases

| Failure | Cause | Fix |
|---------|-------|-----|
| mayapy not found | Maya not installed | Use Blender pipeline instead |
| SVG import fails | Maya lacks native SVG support | Use USD bridge or custom parser |
| License error | Maya license expired | Check license manager |

## Future Implementation Notes

- USD may become the primary interchange format
- Consider Alembic as alternative interchange
- Maya Bifrost could offer advanced procedural features
