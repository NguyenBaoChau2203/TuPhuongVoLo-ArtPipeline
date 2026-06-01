# 🚀 Hướng dẫn sử dụng Launchers (File .bat)

## Launcher là gì?

Launcher là các file `.bat` (batch) giúp bạn chạy các công cụ pipeline mà **không cần mở terminal hay biết lệnh**.

Chỉ cần **nhấp đúp** (double-click) vào file `.bat` để chạy.

---

## Danh sách Launcher

| File | Chức năng | Khi nào dùng |
|------|-----------|-------------|
| `01_install_tools.bat` | Kiểm tra và cài đặt công cụ | Chạy một lần khi bắt đầu |
| `02_clean_svg.bat` | Làm sạch file SVG | Sau khi xuất SVG từ Illustrator |
| `03_build_isometric_room.bat` | Tạo phòng isometric 3D | Khi muốn xem preview phòng |
| `04_batch_isometric_render.bat` | Lập kế hoạch batch render | Khi muốn xử lý nhiều phòng/nhiều SVG |
| `04_batch_render.bat` | Wrapper tương thích | Gọi lại launcher batch mới |
| `05_open_outputs.bat` | Mở thư mục kết quả | Khi muốn xem file đã tạo |
| `00_maya_env_check.bat` | Kiểm tra Python/PyYAML/mayapy | Khi chuẩn bị chạy Maya thật |
| `07_build_maya_room.bat` | Dựng một phòng Maya từ SVG sạch | Chạy dry-run trước, sau đó tạo `.ma` nếu cần |
| `08_batch_maya_room.bat` | Batch Maya nhiều SVG/phòng | Tạo report dry-run hoặc chạy nhiều job Maya |
| `09_artist_desktop_app.bat` | Mở desktop app Maya MVP | Cách thân thiện nhất để chạy một SVG/một phòng |
| `10_package_artist_app.bat` | Dry-run lệnh package desktop app | Dành cho developer muốn tạo `.exe` local bằng PyInstaller |

---

## Quy trình sử dụng

### Bước 1: Cài đặt (chỉ cần 1 lần)
1. Nhấp đúp `01_install_tools.bat`
2. Kiểm tra Python đã cài chưa
3. Nếu thiếu, cài đặt theo hướng dẫn trên màn hình

### Bước 2: Chuẩn bị file
1. Xuất SVG từ Illustrator (dùng script JSX hoặc File → Save As → SVG)
2. Bỏ file SVG vào thư mục `drops/`

### Bước 3: Làm sạch SVG
1. Nhấp đúp `02_clean_svg.bat`
2. File SVG sạch sẽ xuất hiện trong `assets/2d/svg_clean/`

### Bước 4: Tạo phòng isometric bằng Blender cũ/fallback
1. Nhấp đúp `03_build_isometric_room.bat`
2. Ảnh preview PNG + file Blender sẽ xuất hiện trong `outputs/` nếu dùng backend Blender cũ

### Bước 5: Batch render nhiều phòng / nhiều SVG
1. Nhấp đúp `04_batch_isometric_render.bat`
2. Mặc định launcher chạy dry-run an toàn, không sửa file nguồn
3. Báo cáo JSON nằm trong `outputs/reports/batch_isometric_report.json`

### Bước 6: Xem kết quả
1. Nhấp đúp `05_open_outputs.bat`
2. Thư mục `outputs/` sẽ mở ra trong Explorer

### Bước 7: Dựng Maya blockout
1. Chạy `00_maya_env_check.bat` nếu chưa chắc máy đã có Python/PyYAML/mayapy.
2. Ưu tiên chạy `09_artist_desktop_app.bat` để mở app thân thiện cho một file SVG/một phòng.
3. Trong app, chọn SVG, nhập phòng, giữ dry-run trước, và đọc log.
4. Khi dry-run đúng, bỏ dry-run và cung cấp `mayapy.exe` để tạo `.ma` thật.
5. Nếu muốn dùng CLI launcher cũ, chạy `07_build_maya_room.bat` cho một file SVG/phòng.
6. Chạy `08_batch_maya_room.bat` nếu cần xử lý nhiều SVG hoặc nhiều phòng. Report JSON mặc định nằm trong `outputs/reports/batch_maya_report.json`.

### Bước 8: Package desktop app thành .exe (developer-only)
1. Chạy `10_package_artist_app.bat` để in lệnh package dry-run.
2. PyInstaller là công cụ dev-only; launcher này không tự cài PyInstaller.
3. Nếu máy dev đã cài PyInstaller, chạy `python scripts/python/package_artist_app.py --build`.
4. File `.exe` dự kiến nằm trong `dist/TuPhuongVoLo_MayaArtistApp.exe` và không được commit.
5. `.exe` là wrapper local: hãy chạy từ thư mục repo hoặc đặt `TUPHUONGVOLO_REPO_ROOT`.
6. `.exe` vẫn cần Python bên ngoài để chạy pipeline; nếu Python không nằm trong `PATH`, đặt `TUPHUONGVOLO_PYTHON_EXE`.
7. `.exe` không bundle Autodesk Maya hoặc `mayapy.exe`; chạy thật vẫn cần đường dẫn `mayapy.exe` hợp lệ.

---

## Gặp lỗi?

- Xem thông báo lỗi trên màn hình (bằng tiếng Việt)
- Đọc file `docs/TROUBLESHOOTING_VI.md` để biết cách xử lý
- Nếu cửa sổ đóng quá nhanh, giữ phím bất kỳ khi thấy "Press any key..."

---

## Lưu ý

⚠️ **Blender cũ/fallback**: Batch launcher Blender chạy dry-run mặc định để an toàn khi máy chưa có Blender. Render thật cần Blender 4.x và nên do developer chạy/kiểm chứng.

Với Maya launcher, dry-run cũng là mặc định. Chạy thật cần Autodesk Maya `mayapy.exe`; quy trình launcher Maya 005.4 đã được kiểm chứng trên máy DCC. File sinh ra nằm trong `outputs/maya/`, ảnh preview trong `outputs/preview/`, file tạm trong `outputs/tmp/`, và report trong `outputs/reports/`.
