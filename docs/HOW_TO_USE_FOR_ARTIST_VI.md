# 🎨 Hướng dẫn sử dụng cho họa sĩ — TuPhuongVoLo-ArtPipeline

## Tổng quan

Pipeline này giúp bạn **tự động hóa** một phần công việc lặp lại:
- Xuất SVG sạch từ Illustrator
- Tạo phòng isometric 3D từ bản vẽ mặt bằng
- Render preview PNG tự động
- Đặt tên và quản lý file tự động

**Bạn vẫn là người quyết định cuối cùng** — pipeline chỉ tạo bản nháp để bạn chỉnh sửa.

---

## Quy trình cơ bản

```
Bạn vẽ trong Illustrator
    → Xuất SVG (dùng script JSX)
    → Bỏ SVG vào thư mục drops/
    → Chạy file .bat trong launchers/
    → Lấy kết quả từ outputs/
    → Chỉnh sửa thêm nếu cần
```

---

## Bước 1: Vẽ trong Illustrator

Khi vẽ bản vẽ mặt bằng, hãy:
- Đặt tên layer theo quy ước: `room_kho`, `room_sanh_chinh`, v.v.
- Mỗi phòng nên ở một layer riêng
- Dùng đường path đóng (closed path) cho tường

---

## Bước 2: Xuất SVG

**Cách 1: Dùng script JSX (khuyến nghị)**
1. Mở file `.ai` trong Illustrator.
2. Nếu muốn chuẩn hóa tên layer trước, chạy: File → Scripts → Other Script → chọn `scripts/illustrator/organize_layers.jsx`
3. Chạy export: File → Scripts → Other Script → chọn `scripts/illustrator/export_clean_svg.jsx`
4. File SVG raw sẽ xuất hiện trong `assets/2d/svg_raw/`.

Script export sẽ tự đặt tên dạng `_svgraw_v001.svg`. Nếu file đã tồn tại, script sẽ tạo phiên bản tiếp theo và không ghi đè file cũ.

**Cách 2: Xuất thủ công**
1. Trong Illustrator: File → Save As → SVG
2. Chọn SVG 1.1 nếu Illustrator hỏi tùy chọn
3. Lưu file vào thư mục `drops/`

Lưu ý: trước khi xuất, hãy tắt hoặc xóa khỏi bản xuất các layer raster/reference nếu không muốn pipeline báo lỗi raster image.

---

## Bước 3: Làm sạch SVG

1. Bỏ file SVG vào `drops/` hoặc dùng file đã xuất trong `assets/2d/svg_raw/`.
2. Nhấp đúp `launchers/02_clean_svg.bat`.
3. Nếu muốn xử lý một thư mục/file khác, có thể kéo thả file/thư mục SVG lên `02_clean_svg.bat`.
4. File SVG sạch sẽ xuất hiện trong `assets/2d/svg_clean/`.

Launcher sẽ:
- Xóa các phần tử bị ẩn (`display:none`, `visibility:hidden`, `opacity:0`)
- Xóa path quá nhỏ do lỗi export/vector hóa
- Cảnh báo nếu SVG còn ảnh raster nhúng
- Chạy kiểm tra clean SVG contract sau khi xử lý

Nếu cửa sổ báo lỗi:
- `Không tìm thấy file SVG nào`: hãy kiểm tra lại `drops/` hoặc đường dẫn bạn kéo thả.
- `Có embedded/linked raster image`: SVG còn ảnh PNG/JPG nhúng; hãy quay lại Illustrator và bỏ layer ảnh khỏi bản xuất nếu đó không phải geometry.
- `Strict mode: còn transform`: SVG còn transform chưa flatten; hãy thử Expand/Outline trong Illustrator hoặc báo developer kiểm tra file.

---

## Bước 4: Tạo phòng isometric

1. Nhấp đúp `launchers/03_build_isometric_room.bat`
2. Kết quả:
   - Ảnh preview PNG → `outputs/preview/`
   - File Blender → `outputs/blender/`

---

## Bước 5: Xem kết quả

1. Nhấp đúp `launchers/05_open_outputs.bat`
2. Hoặc mở trực tiếp thư mục `outputs/` trong Explorer

---

## Thư mục quan trọng

| Thư mục | Mục đích | Bạn cần làm gì |
|---------|----------|-----------------|
| `drops/` | Bỏ file vào đây để xử lý | Bỏ file SVG vào |
| `assets/2d/svg_raw/` | SVG raw xuất từ Illustrator | Kiểm tra file export |
| `assets/2d/svg_clean/` | SVG sạch sau cleanup | Dùng cho bước tiếp theo |
| `outputs/` | Kết quả các bước sau | Lấy file từ đây |
| `launchers/` | File .bat để chạy | Nhấp đúp để chạy |

---

## Lưu ý quan trọng

⚠️ **File gốc không bị thay đổi**: Pipeline không bao giờ xóa hoặc sửa file gốc của bạn.

⚠️ **SVG sạch là nguồn trung gian quan trọng**: Nếu bước kiểm tra SVG báo lỗi, hãy sửa file trong Illustrator rồi xuất lại.

⚠️ **Đặt tên tự động**: File kết quả được đặt tên theo quy ước, ví dụ:
`tu_phuong_vo_lo_kho_main_svgclean_v001.svg`

---

## Hiện tại (Trạng thái)

✅ Feature 002 đã có bước xuất SVG từ Illustrator, làm sạch SVG bằng launcher, và kiểm tra SVG sạch.

⚠️ Các bước tạo phòng isometric/render 3D thuộc feature sau, chưa phải phạm vi của Feature 002.
