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
1. Trong Illustrator: File → Scripts → Other Script
2. Chọn `scripts/illustrator/export_clean_svg.jsx`
3. File SVG sẽ xuất hiện trong `assets/2d/svg_raw/`

**Cách 2: Xuất thủ công**
1. File → Save As → SVG
2. Chọn SVG 1.1
3. Lưu vào thư mục `drops/`

---

## Bước 3: Làm sạch SVG

1. Nhấp đúp `launchers/02_clean_svg.bat`
2. File SVG sạch sẽ xuất hiện trong `assets/2d/svg_clean/`

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
| `outputs/` | Kết quả xuất hiện ở đây | Lấy file từ đây |
| `assets/` | File nguồn đã tổ chức | Không cần đụng vào |
| `launchers/` | File .bat để chạy | Nhấp đúp để chạy |

---

## Lưu ý quan trọng

⚠️ **File gốc không bị thay đổi**: Pipeline không bao giờ xóa hoặc sửa file gốc của bạn.

⚠️ **Kết quả là bản nháp**: Ảnh render và file 3D là bản nháp — bạn vẫn cần chỉnh sửa cuối cùng.

⚠️ **Đặt tên tự động**: File kết quả được đặt tên theo quy ước, ví dụ:
`tu_phuong_vo_lo_kho_main_iso_v001.png`

---

## Hiện tại (Trạng thái)

⚠️ Pipeline đang ở giai đoạn **chuẩn bị**. Các script chưa hoạt động thật.
Chúng sẽ được triển khai trong các bước tiếp theo.
