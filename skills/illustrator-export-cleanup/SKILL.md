---
name: illustrator-export-cleanup
description: Export clean SVG from Adobe Illustrator and process through cleanup/validation pipeline
---

# Skill: Illustrator Export & Cleanup

## When to Use

Use this skill when the task involves:
- Exporting SVG from Adobe Illustrator with layer names preserved
- Cleaning up raw SVG (simplify paths, flatten transforms, remove hidden elements)
- Validating SVG against the clean SVG contract
- Organizing Illustrator layers with naming conventions

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Illustrator file | `.ai` | For export | Source art file (export only) |
| Raw SVG | `.svg` | For cleanup | SVG from Illustrator export |

## Outputs

| Output | Type | Location | Description |
|--------|------|----------|-------------|
| Raw SVG | `.svg` | `assets/2d/svg_raw/` | Exported from Illustrator |
| Clean SVG | `.svg` | `assets/2d/svg_clean/` | After cleanup pipeline |
| Validation report | text | stdout | Pass/fail with details |

## Required Workflow

1. **Export** — Run `export_clean_svg.jsx` in Illustrator
2. **Clean** — Run `clean_svg_paths.py` on raw SVG
3. **Validate** — Run `validate_svg_contract.py` on cleaned SVG
4. **Name** — Ensure output follows naming convention

## Style & Safety Rules

- NEVER modify the source `.ai` file
- Export to `assets/2d/svg_raw/` only
- Clean SVG goes to `assets/2d/svg_clean/`
- Preserve layer names as SVG group IDs
- Remove hidden/invisible elements during cleanup
- Flatten all transforms

## Success Criteria

- [ ] SVG exported with correct layer names
- [ ] Cleanup removes unnecessary elements
- [ ] Validation passes all checks
- [ ] Output follows naming convention

## Common Failure Cases

| Failure | Cause | Fix |
|---------|-------|-----|
| Layer names lost | Wrong SVG export settings | Use JSX script, not manual export |
| Embedded rasters | Illustrator file has linked images | Remove raster layers before export |
| Invalid paths | Complex Illustrator effects | Expand appearances before export |

## Future Implementation Notes

- Consider Illustrator Actions for batch export
- vpype may need special installation on some Windows setups
- Watch for Illustrator version-specific SVG export differences
