# Hướng dẫn sử dụng cho họa sĩ - TuPhuongVoLo-ArtPipeline

## Tổng quan

Pipeline này giúp bạn tự động hóa một phần công việc lặp lại:

- Xuất SVG sạch từ Illustrator
- Đưa file vào đúng thư mục và đặt tên theo quy ước
- Làm sạch/kiểm tra SVG trước khi dựng 3D
- Tạo bản nháp phòng isometric trong Blender
- Render preview PNG để xem nhanh

Bạn vẫn là người quyết định cuối cùng. Pipeline chỉ tạo bản nháp/blockout để bạn mở ra chỉnh sửa tiếp.

## Quy trình cơ bản

```text
Vẽ trong Illustrator
  -> xuất SVG
  -> ingest/đặt tên asset
  -> làm sạch SVG
  -> tạo phòng isometric
  -> xem output trong outputs/
```

## Bước 1: Vẽ trong Illustrator

Khi vẽ bản vẽ mặt bằng:

- Đặt tên layer/group theo phòng, ví dụ `room_kho`, `room_sanh_chinh`.
- Mỗi phòng nên nằm trong một group/layer riêng.
- Boundary phòng nên là path đóng kín.
- Tránh để raster/reference image trong layer geometry.

## Bước 2: Xuất SVG

Cách khuyến nghị:

1. Mở file `.ai` trong Illustrator.
2. Chạy `scripts/illustrator/organize_layers.jsx` nếu muốn chuẩn hóa layer.
3. Chạy `scripts/illustrator/export_clean_svg.jsx`.
4. SVG raw sẽ nằm trong `assets/2d/svg_raw/`.

Nếu xuất thủ công, hãy lưu SVG vào `drops/`, rồi chạy bước ingest bên dưới.

## Bước 3: Ingest và đặt tên asset

Feature 003 copy file từ `drops/` vào thư mục đúng và cập nhật manifest.

1. Bỏ file cần xử lý vào `drops/`.
2. Nhấp đúp `launchers/06_ingest_assets.bat`.
3. File được copy sang thư mục phù hợp, ví dụ `assets/2d/svg_raw/`.
4. Manifest được cập nhật tại `outputs/manifest/asset_manifest.json`.

Launcher này không xóa file gốc trong `drops/`. Nếu chạy lại cùng asset, pipeline tạo phiên bản mới như `v002` thay vì ghi đè.

## Bước 4: Làm sạch SVG

1. Dùng file SVG raw trong `assets/2d/svg_raw/` hoặc kéo thả một file SVG vào launcher.
2. Nhấp đúp `launchers/02_clean_svg.bat`.
3. SVG sạch sẽ xuất hiện trong `assets/2d/svg_clean/`.

Launcher sẽ xóa phần tử ẩn, xóa path quá nhỏ, cảnh báo raster image, và kiểm tra clean SVG contract.

Nếu có lỗi:

- `Không tìm thấy file SVG nào`: kiểm tra lại `drops/` hoặc file bạn kéo thả.
- `Có embedded/linked raster image`: quay lại Illustrator và bỏ layer ảnh nếu đó không phải geometry.
- `Strict mode: còn transform`: thử Expand/Outline trong Illustrator hoặc báo developer kiểm tra file.

## Bước 5: Tạo phòng isometric

1. Nhấp đúp `launchers/03_build_isometric_room.bat`.
2. Nếu muốn chọn file cụ thể, kéo thả SVG sạch vào launcher này.
3. Nếu không kéo thả file, launcher sẽ tự lấy SVG mới nhất trong `assets/2d/svg_clean/`.

Kết quả:

- PNG preview: `outputs/preview/`
- File Blender chỉnh sửa được: `outputs/blender/`
- Manifest: `outputs/manifest/asset_manifest.json`

Nếu Blender chưa được cài hoặc không nằm trong PATH, launcher sẽ báo lỗi. Khi đó hãy cài Blender 4.x hoặc nhờ developer sửa `tool_paths.blender` trong `config/pipeline.yaml`.

Lưu ý: Đây là bản blockout/draft. Tường, sàn và props chỉ là hình khối đơn giản để kiểm tra bố cục, không phải final art.

## Bước 6: Batch render nhiều phòng / nhiều SVG

Khi có nhiều SVG sạch hoặc một SVG có nhiều phòng, dùng launcher:

```text
launchers/04_batch_isometric_render.bat
```

Mặc định launcher này chạy dry-run để lập kế hoạch an toàn. Dry-run không chạy Blender, không ghi manifest, không sửa file SVG nguồn, và vẫn dùng được khi máy chưa cài Blender.

Bạn có thể:

- Nhấp đúp launcher để quét `assets/2d/svg_clean/`.
- Kéo thả một file `.svg` vào launcher để lập kế hoạch cho một SVG.
- Kéo thả một thư mục vào launcher để lập kế hoạch cho nhiều SVG.

Kết quả batch:

- PNG preview khi render thật: `outputs/preview/`
- File Blender chỉnh sửa được khi render thật: `outputs/blender/`
- Báo cáo batch: `outputs/reports/batch_isometric_report.json`

Khi Blender đã được cài, developer có thể chạy actual batch render bằng script Python không dùng `--dry-run`. Đây vẫn là bản blockout/draft để kiểm tra bố cục, chưa phải final art.

## Bước 7: Xem kết quả

1. Nhấp đúp `launchers/05_open_outputs.bat`.
2. Hoặc mở trực tiếp thư mục `outputs/` trong Explorer.
3. Mở file `.blend` trong Blender nếu muốn chỉnh sửa cảnh.

## Thư mục quan trọng

| Thư mục | Mục đích | Bạn cần làm gì |
| --- | --- | --- |
| `drops/` | Bỏ file vào đây để xử lý | Bỏ SVG raw nếu xuất thủ công |
| `assets/2d/svg_raw/` | SVG raw từ Illustrator | Kiểm tra file export |
| `assets/2d/svg_clean/` | SVG sạch sau cleanup | Dùng cho bước isometric |
| `outputs/preview/` | Ảnh PNG xem nhanh | Xem render preview |
| `outputs/blender/` | File `.blend` chỉnh sửa được | Mở trong Blender |
| `outputs/manifest/` | Manifest kỹ thuật | Không cần sửa tay |
| `launchers/` | File `.bat` để chạy | Nhấp đúp hoặc kéo thả file |

## Lưu ý quan trọng

File gốc không bị thay đổi. Pipeline không xóa hoặc sửa file trong `drops/`, `assets/2d/ai_src/`, hoặc SVG nguồn.

Tên output luôn theo quy ước, ví dụ:

```text
tu_phuong_vo_lo_kho_main_iso_v001.blend
tu_phuong_vo_lo_kho_main_preview_v001.png
```

## Hiện tại

Feature 002 đã có xuất/làm sạch/kiểm tra SVG. Feature 003 đã có naming và manifest. Feature 001 hiện tạo được bản nháp phòng isometric qua Blender khi máy có Blender. Feature 004 đã có batch dry-run và báo cáo JSON; actual batch render cần Blender để kiểm chứng trên máy có Blender.
