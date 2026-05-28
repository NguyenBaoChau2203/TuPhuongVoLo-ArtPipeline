# Quickstart: Illustrator Export & Clean SVG

## Prerequisites

- [ ] Adobe Illustrator CC installed
- [ ] Python 3.11+ with vpype[all] 1.15.0 and svgpathtools 1.7.2 installed
- [ ] Virtual environment activated

## Quick Verification

### Step 1: Install JSX scripts

Copy `scripts/illustrator/*.jsx` to your Illustrator Scripts folder, or run them via File → Scripts → Other Script.

### Step 2: Export SVG from Illustrator

1. Open your `.ai` file in Illustrator
2. File → Scripts → Other Script → select `export_clean_svg.jsx`
3. Check `assets/2d/svg_raw/` for the exported SVG

### Step 3: Clean the SVG

```powershell
python scripts/python/clean_svg_paths.py --input assets/2d/svg_raw/my_file.svg --output assets/2d/svg_clean/
```

### Step 4: Validate

```powershell
python scripts/python/validate_svg_contract.py --input assets/2d/svg_clean/my_file_svgclean.svg
```

Expected: "✅ SVG passes all validation checks"

## Troubleshooting

| Issue | Solution |
|-------|----------|
| JSX script not found | Copy to Illustrator's Scripts folder |
| vpype not found | `pip install "vpype[all]==1.15.0"` |
| Validation fails | Check error messages for specific issues |
