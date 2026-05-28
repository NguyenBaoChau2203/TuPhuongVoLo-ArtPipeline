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
| `04_batch_render.bat` | Render hàng loạt | Khi muốn render tất cả phòng |
| `05_open_outputs.bat` | Mở thư mục kết quả | Khi muốn xem file đã tạo |

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

### Bước 4: Tạo phòng isometric
1. Nhấp đúp `03_build_isometric_room.bat`
2. Ảnh preview PNG + file Blender sẽ xuất hiện trong `outputs/`

### Bước 5: Xem kết quả
1. Nhấp đúp `05_open_outputs.bat`
2. Thư mục `outputs/` sẽ mở ra trong Explorer

---

## Gặp lỗi?

- Xem thông báo lỗi trên màn hình (bằng tiếng Việt)
- Đọc file `docs/TROUBLESHOOTING_VI.md` để biết cách xử lý
- Nếu cửa sổ đóng quá nhanh, giữ phím bất kỳ khi thấy "Press any key..."

---

## Lưu ý

⚠️ **Hiện tại**: Các launcher đang ở trạng thái **placeholder** (chưa hoạt động thật).
Chúng sẽ được kích hoạt khi các feature tương ứng được triển khai.
