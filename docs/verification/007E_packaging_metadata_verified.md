# Phase 007E-R: Kiểm chứng metadata packaging desktop app

## Phạm vi

Checkpoint này chỉ kiểm chứng metadata phiên bản và dry-run packaging của Phase
007E. Không thêm logic production, không thêm AI integration, không gọi external
API, và không thay đổi SVG parser, Maya scene generation, render, prop placement,
hoặc manifest.

## Branch và commit

- Branch: `workflow/maya-first-artist-pipeline`
- Commit được kiểm chứng: `63c59bb` chore: polish desktop app packaging metadata
- App version: `v0.7.5 (007E)`

## Kết quả validation

Chạy từ repo root:

```powershell
git status
```

Kết quả: worktree clean trước khi tạo checkpoint; branch đang ahead origin 1
commit do `63c59bb` chưa push.

```powershell
git log --oneline -5
```

Kết quả: `63c59bb` xuất hiện ở HEAD, theo sau là `911c929`, `2a892f8`,
`9b6e40c`, và `3d278b8`.

```powershell
python scripts/python/artist_desktop_app.py --version
```

Kết quả:

```text
TuPhuongVoLo Maya Artist App v0.7.5 (007E)
```

```powershell
python scripts/python/package_artist_app.py --dry-run
```

Kết quả: exit code 0; dry-run in app version, lệnh PyInstaller dự kiến, output
dự kiến `dist/TuPhuongVoLo_MayaArtistApp.exe`, và ghi chú `.exe` vẫn cần
repo/pipeline local, không bundle Maya hoặc `mayapy.exe`.

```powershell
pytest tests/ -v --ignore=tests/tmp
```

Kết quả: `175 passed`. Có cảnh báo pytest cache do không ghi được
`.pytest_cache`; cảnh báo này không ảnh hưởng kết quả test.

## Ghi chú packaging

Packaging vẫn là workflow local/dev-only. PyInstaller không phải dependency
runtime của họa sĩ, script không tự cài PyInstaller, và file `.exe` nếu build
ra vẫn là wrapper local cho repo/pipeline hiện có.

Không commit các artifact sinh ra:

- `build/`
- `dist/`
- `*.exe`
- `*.spec`
- `*.zip`
- `outputs/tmp/`
- `outputs/maya/`
- `outputs/preview/`
- `outputs/reports/`
- `outputs/ai_preview/`
- file `.ma` sinh ra
- file `.png` sinh ra

## Phạm vi vẫn deferred

- Feature 006 natural-language control vẫn deferred.
- AI polish implementation vẫn deferred.
- Không thêm fal.ai, FLUX, external API, `.env`, secrets, hoặc dependency mới.
