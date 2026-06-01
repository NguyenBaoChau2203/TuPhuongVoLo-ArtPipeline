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

## Đóng gói .exe

Phase 007A ưu tiên app local chạy được từ source và launcher. Đóng gói `.exe`
có thể làm ở bước tiếp theo bằng PyInstaller, nhưng hiện chưa thêm dependency
PyInstaller và chưa commit `build/`, `dist/`, file `.spec`, hay `.exe`.

