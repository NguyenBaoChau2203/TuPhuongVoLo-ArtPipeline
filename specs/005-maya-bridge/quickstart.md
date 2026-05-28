# Quickstart: Maya Bridge

## Prerequisites

- [ ] Autodesk Maya 2024+ installed (optional — this is an advanced branch)
- [ ] mayapy accessible from PATH or configured in `config/pipeline.yaml`
- [ ] Feature 001 Blender pipeline functional (for reference)

## Quick Verification

### Step 1: Check Maya availability

```powershell
mayapy --version
```

If this fails, Maya is not installed. The Maya bridge is optional.

### Step 2: Setup isometric camera

```powershell
mayapy scripts/maya/setup_iso_camera.py
```

### Step 3: Import SVG walls

```powershell
mayapy scripts/maya/import_svg_walls.py --input assets/2d/svg_clean/example.svg --room kho
```

### Step 4: Batch render

```powershell
mayapy scripts/maya/batch_render.py --scene outputs/maya/scene.ma --output outputs/maya/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "mayapy not found" | Maya is optional. Use Blender pipeline instead. |
| "Maya license error" | Ensure Maya license is activated |
