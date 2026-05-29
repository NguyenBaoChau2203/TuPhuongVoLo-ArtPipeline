# Quickstart: Asset Naming & Manifest

## Prerequisites

- Python 3.11+ installed
- Virtual environment activated
- Dependencies installed from `requirements.txt`

## Quick Verification

### Step 1: Create a temporary SVG in drops/

```powershell
@'
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <path id="wall" d="M0 0 L10 0 L10 10 Z"/>
</svg>
'@ | Set-Content -Encoding UTF8 drops\sanh_chinh.svg
```

### Step 2: Ingest the file

```powershell
python scripts/python/asset_agent.py ingest --input drops --stage raw --variant main
```

Expected output includes:

```text
Tóm tắt ingest:
  Đã xử lý: 1 file
```

Expected file:

```text
assets/2d/svg_raw/tu_phuong_vo_lo_sanh_chinh_main_raw_v001.svg
```

If `v001` already exists, the next version is used, such as `v002`.

### Step 3: Query the manifest

```powershell
python scripts/python/manifest.py query --stage raw
python scripts/python/asset_agent.py query --asset-name sanh_chinh
```

Expected output includes a matching manifest row:

```text
- sanh_chinh | main | raw | v001 | assets/2d/svg_raw/tu_phuong_vo_lo_sanh_chinh_main_raw_v001.svg
```

### Step 4: Validate the manifest

```powershell
python scripts/python/manifest.py validate
python scripts/python/asset_agent.py validate-manifest
```

Expected output:

```text
PASS: Manifest hợp lệ.
```

### Step 5: CLI help checks

```powershell
python scripts/python/manifest.py --help
python scripts/python/asset_agent.py --help
```

Both commands should print usage information and exit successfully.

## Artist Launcher

The artist can double-click:

```text
launchers/06_ingest_assets.bat
```

The launcher processes `drops/` in copy mode by default. It does not delete artist files.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Không tìm thấy input` | Put files in `drops/` or pass a valid `--input` path |
| `định dạng chưa hỗ trợ` | Use `.svg`, `.png`, `.jpg`, `.jpeg`, or `.webp` |
| `Manifest JSON đang bị lỗi` | Back up and repair `outputs/manifest/asset_manifest.json`; the tool will not overwrite corrupted data |
