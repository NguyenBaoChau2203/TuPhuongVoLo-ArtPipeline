# Quickstart: Asset Naming & Manifest

## Prerequisites

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] PyYAML installed

## Quick Verification

### Step 1: Drop a test file

```powershell
Copy-Item examples/motel_room/placeholder_input.svg drops/test_room.svg
```

### Step 2: Run the asset agent

```powershell
python scripts/python/asset_agent.py --input drops/ --config config/naming_convention.yaml
```

### Step 3: Verify naming

```powershell
Get-ChildItem assets/2d/svg_raw/ -Filter "*test_room*"
```

Expected: `tu_phuong_vo_lo_test_room_main_raw_v001.svg`

### Step 4: Check manifest

```powershell
Get-Content outputs/manifest/asset_manifest.json
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No files in drops/" | Place files in the `drops/` folder first |
| "naming_convention.yaml not found" | Check `config/` directory |
