# Checklist release/packaging desktop app Maya

Tài liệu này dùng cho developer khi chuẩn bị bản desktop app local cho họa sĩ.
Phase 007E chỉ thêm metadata phiên bản và checklist đóng gói; không thêm AI,
không gọi external API, không thay đổi parser SVG, Maya scene generation, render,
prop placement, hoặc manifest.

## Phiên bản hiện tại

- App: `TuPhuongVoLo Maya Artist App v0.7.5 (007E)`
- File source chính: `scripts/python/artist_desktop_app.py`
- Helper packaging: `scripts/python/package_artist_app.py`
- File `.exe` dự kiến nếu build local: `dist/TuPhuongVoLo_MayaArtistApp.exe`

Kiểm tra phiên bản:

```powershell
python scripts/python/artist_desktop_app.py --version
python scripts/python/package_artist_app.py --version
```

## Checklist trước khi đóng gói

- [ ] Đang ở branch `workflow/maya-first-artist-pipeline`.
- [ ] Worktree chỉ có thay đổi source/docs/tests dự kiến.
- [ ] Không có file sinh ra trong `build/`, `dist/`, hoặc `outputs/` được stage.
- [ ] `python scripts/python/artist_desktop_app.py --help` chạy được.
- [ ] `python scripts/python/artist_desktop_app.py --version` in đúng phiên bản.
- [ ] `python scripts/python/package_artist_app.py --dry-run` in phiên bản app và lệnh PyInstaller dự kiến.
- [ ] `pytest tests/ -v --ignore=tests/tmp` pass.

## Khi build `.exe`

PyInstaller là công cụ dev-only. Script không tự cài PyInstaller và `.exe` không
bundle Maya, `mayapy.exe`, hoặc toàn bộ repo.

```powershell
python scripts/python/package_artist_app.py --clean-output --build
```

Sau khi build, kiểm tra nhanh:

- [ ] `.exe` mở được trên máy artist/DCC.
- [ ] App title hoặc nhãn trên UI hiển thị `v0.7.5 (007E)`.
- [ ] Dry-run trả exit code 0.
- [ ] Actual Maya run chỉ chạy khi có `mayapy.exe` hợp lệ.
- [ ] File `.ma` và PNG preview nếu có chỉ nằm trong `outputs/`.

## Không commit

Không commit các artifact local sau:

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

## Cảnh báo phạm vi

Checklist này không cấp quyền thêm AI polish, fal.ai/FLUX, Feature 006
natural-language control, external API calls, `.env`, secrets, dependency mới,
hoặc Maya pipeline feature mới.
