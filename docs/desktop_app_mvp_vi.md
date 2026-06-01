# Desktop App MVP cho họa sĩ

## Mục đích

Desktop app MVP là cửa sổ local nhỏ để chạy pipeline Maya-first đã được kiểm
chứng. App giúp họa sĩ chọn SVG, nhập tên phòng, chọn dry-run hoặc chạy thật,
bật/tắt PNG preview, nhập đường dẫn `mayapy.exe`, xem log, và mở nhanh các thư
mục output.

App chỉ bọc script CLI hiện có:

```powershell
python scripts/python/build_maya_room.py
```

App không thay thế Maya, không parse SVG trực tiếp, không tạo geometry riêng, và
không sửa file SVG nguồn. Pipeline CLI vẫn là source of truth.

## Cách chạy từ source

```powershell
python scripts/python/artist_desktop_app.py
```

## Cách chạy bằng launcher

```powershell
launchers/09_artist_desktop_app.bat
```

## Quy trình khuyến nghị

1. Chọn file SVG sạch.
2. Nhập tên phòng, ví dụ `phong_kho`.
3. Giữ `Dry-run` cho lần đầu.
4. Bật `Render PNG preview` nếu cần ảnh kiểm tra nhanh.
5. Bấm `Chạy pipeline` và đọc log trong app.
6. Nếu dry-run đúng, bỏ chọn `Dry-run`, kiểm tra đường dẫn `mayapy.exe`, rồi chạy thật.

## Thư mục có thể mở từ app

- `outputs/maya/`
- `outputs/preview/`
- `outputs/reports/`
- Thư mục repo

## Đóng gói .exe cho máy dev

Phase 007B thêm workflow đóng gói local bằng PyInstaller. PyInstaller là công cụ
dev-only, không phải dependency runtime của artist pipeline và không được cài tự
động.

Chạy dry-run để xem lệnh package:

```powershell
python scripts/python/package_artist_app.py --dry-run
```

Hoặc dùng launcher:

```powershell
launchers/10_package_artist_app.bat
```

Nếu máy dev đã cài PyInstaller, có thể build thật:

```powershell
python scripts/python/package_artist_app.py --build
```

Output dự kiến:

```text
dist/TuPhuongVoLo_MayaArtistApp.exe
```

Lưu ý: `.exe` MVP này vẫn là wrapper local cho repo/pipeline hiện có. Nó không
bundle toàn bộ repo, không bundle Maya, và không bundle `mayapy.exe`. Không commit
`build/`, `dist/`, file `.spec` sinh tự động, hoặc file `.exe`.
