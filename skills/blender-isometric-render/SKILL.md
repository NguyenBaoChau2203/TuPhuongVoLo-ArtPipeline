---
name: blender-isometric-render
description: Configure and execute isometric renders in Blender headless mode
---

# Skill: Blender Isometric Render

## When to Use

Use this skill when the task involves:
- Setting up an isometric camera in Blender
- Rendering scenes with orthographic projection
- Batch rendering multiple rooms/scenes
- Configuring render settings from style presets

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Blender scene | `.blend` or script | Yes | Scene to render |
| Style preset | string | No | Key from `config/style_presets.yaml` |
| Resolution | tuple | No | Width x Height (default: 1920x1080) |

## Outputs

| Output | Type | Location | Description |
|--------|------|----------|-------------|
| PNG render | image | `outputs/preview/` | Transparent isometric PNG |
| Blender scene | `.blend` | `outputs/blender/` | Scene with camera/lights |

## Required Workflow

1. **Setup** — Verify Blender is accessible
2. **Configure** — Apply style preset to materials and render settings
3. **Camera** — Set up orthographic isometric camera
4. **Render** — Execute headless render
5. **Save** — Save .blend scene and PNG output
6. **Manifest** — Update manifest

## Style & Safety Rules

- Always use `blender --background` (headless)
- Orthographic camera only (no perspective)
- Transparent background by default
- EEVEE for speed, CYCLES only for review_render preset
- Never render to source directories

## Success Criteria

- [ ] Render completes without GUI
- [ ] PNG has transparent background
- [ ] Camera shows complete room with padding
- [ ] .blend file is saveable and reopenable
- [ ] Render matches style preset colors

## Common Failure Cases

| Failure | Cause | Fix |
|---------|-------|-----|
| Blender not found | Not in PATH | Set `tool_paths.blender` in pipeline.yaml |
| Black render | No lights | Ensure lighting setup runs before render |
| Cropped render | Camera too close | Auto-fit camera to scene bounding box |
| Crash on large scene | Insufficient memory | Reduce resolution or simplify geometry |
