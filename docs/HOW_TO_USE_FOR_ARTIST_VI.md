# Hướng dẫn sử dụng cho họa sĩ - TuPhuongVoLo-ArtPipeline

## Tổng quan

Pipeline này giúp tự động hóa một phần công việc lặp lại trong quy trình vẽ game:

- Vẽ và xuất SVG từ Adobe Illustrator
- Làm sạch/kiểm tra SVG trước khi đưa sang 3D
- Tạo geometry JSON bằng Python
- Tạo bản blockout `.ma` trong Autodesk Maya để họa sĩ mở ra chỉnh tiếp
- Ghi manifest khi có output thật

Illustrator là công cụ vẽ chính. Maya là công cụ 3D/chỉnh sửa chính cho production. Blender vẫn còn trong repo như backend MVP cũ hoặc fallback tùy chọn, nhưng không bắt buộc cho quy trình Maya.

## Quy trình chính

```text
Vẽ trong Illustrator
  -> xuất SVG sạch
  -> Python phát hiện phòng/boundary
  -> Python tạo geometry JSON
  -> Maya tạo .ma blockout
  -> họa sĩ mở .ma trong Maya và polish
```

## Bước 1: Vẽ trong Illustrator

- Đặt tên layer/group theo phòng, ví dụ `room_kho`, `room_sanh_chinh`.
- Mỗi phòng nên nằm trong một group/layer riêng.
- Boundary phòng nên là path đóng kín.
- Không để raster/reference image trong layer geometry.

## Bước 2: Xuất và làm sạch SVG

1. Mở file `.ai` trong Illustrator.
2. Chạy `scripts/illustrator/export_clean_svg.jsx` hoặc dùng launcher cleanup hiện có.
3. SVG sạch nên nằm trong `assets/2d/svg_clean/`.

Nếu cleanup báo lỗi path chưa đóng kín hoặc còn transform, hãy quay lại Illustrator để sửa boundary/layer trước khi dựng Maya.

## Tạo phòng Maya từ SVG sạch

1. Nhấp đúp `launchers/07_build_maya_room.bat`.
2. Có thể kéo-thả một file `.svg` sạch vào launcher.
3. Nếu không kéo-thả file, launcher sẽ lấy SVG mới nhất trong `assets/2d/svg_clean/`.

Launcher mặc định chạy dry-run để lập kế hoạch an toàn:

- Không chạy Maya
- Không ghi manifest
- Không sửa file SVG nguồn
- In đường dẫn `.ma` dự kiến trong `outputs/maya/`

Khi developer cấu hình `mayapy.exe` trong `config/pipeline.yaml` hoặc chạy script với `--maya-path`, output thật sẽ là:

```text
outputs/maya/tu_phuong_vo_lo_{ten_phong}_main_maya_v001.ma
```

Đây là blockout/draft, chưa phải final art. Họa sĩ mở file `.ma` trong Maya để chỉnh hình khối, vật liệu, props, ánh sáng và camera.

Lưu ý kỹ thuật: MVP hiện chỉ hỗ trợ chạy thật qua `mayapy.exe`. `maya.exe` và `mayabatch.exe` sẽ được hỗ trợ sau nếu cần.

## Batch Maya nhiều phòng / nhiều SVG

1. Nhấp đúp `launchers/08_batch_maya_room.bat`.
2. Có thể kéo-thả một file `.svg` hoặc một thư mục chứa nhiều SVG sạch.
3. Nếu không kéo-thả gì, launcher sẽ quét `assets/2d/svg_clean/`.

Batch launcher cũng chạy dry-run mặc định. Báo cáo nằm tại:

```text
outputs/reports/batch_maya_report.json
```

Báo cáo cho biết file nào đã quét, phòng nào phát hiện được, output `.ma` dự kiến, job nào lỗi, và job nào bị bỏ qua.

## Backend Blender cũ

Các launcher Blender cũ vẫn còn để kiểm tra/fallback:

- `launchers/03_build_isometric_room.bat`
- `launchers/04_batch_isometric_render.bat`

Blender không bắt buộc để dùng Feature 005 Maya Bridge.

## Thư mục quan trọng

| Thư mục | Mục đích |
| --- | --- |
| `drops/` | Nơi bỏ file đầu vào thủ công; pipeline không xóa file ở đây |
| `assets/2d/svg_raw/` | SVG raw từ Illustrator |
| `assets/2d/svg_clean/` | SVG sạch làm đầu vào cho Maya |
| `outputs/tmp/` | Geometry JSON handoff tạm thời |
| `outputs/maya/` | File `.ma` editable cho Maya |
| `outputs/preview/` | Preview nếu backend tạo được |
| `outputs/reports/` | Báo cáo batch JSON |
| `outputs/manifest/` | Manifest kỹ thuật |
| `launchers/` | File `.bat` để chạy nhanh |

## Lưu ý quan trọng

File gốc không bị thay đổi. Pipeline không xóa hoặc sửa file trong `drops/`, `assets/2d/ai_src/`, hoặc SVG nguồn.

Dry-run chỉ lập kế hoạch. Manifest chỉ được cập nhật sau khi Maya chạy thật thành công và file `.ma` tồn tại.

Tên output luôn theo quy ước, ví dụ:

```text
tu_phuong_vo_lo_kho_main_maya_v001.ma
tu_phuong_vo_lo_kho_main_preview_v001.png
```

## Quy trình khuyến nghị cho họa sĩ

1. Vẽ và export SVG sạch từ Illustrator.
2. Đặt SVG vào `assets/2d/svg_clean/` hoặc `drops/`.
3. Chạy `launchers/07_build_maya_room.bat` và chọn dry-run trước.
4. Đọc kết quả dry-run: kiểm tra tên phòng được chọn, prop marker phát hiện được, đường dẫn `.ma` và PNG preview dự kiến.
5. Khi dry-run đúng, chạy lại launcher và chọn không dry-run để tạo `.ma` thật bằng `mayapy.exe`.
6. Nếu cần ảnh kiểm tra nhanh, bật lựa chọn PNG preview.
7. Mở file `.ma` trong Maya, kiểm tra Outliner và polish thủ công.

Launcher `07_build_maya_room.bat` dùng cho một SVG/một phòng. Launcher `08_batch_maya_room.bat` dùng cho nhiều SVG hoặc nhiều phòng và luôn in đường dẫn report JSON để kiểm tra.

## Prop marker trong Illustrator

Nếu muốn Maya đặt khối placeholder theo bố cục đã vẽ, tạo group/layer con bên trong group phòng và đặt tên theo mẫu:

- `prop_shelf_unit`
- `prop_wooden_crate`
- `item_cardboard_box`
- `object_console_desk`

Pipeline bỏ prefix `prop_`, `item_`, hoặc `object_` và dùng phần còn lại làm loại prop. Đây chỉ là blockout để kiểm tra bố cục, không phải model cuối.

## Không nên commit

Các file sinh ra sau đây không nên commit trừ khi developer cố ý cần một fixture hoặc report mẫu:

- `outputs/maya/*.ma`
- `outputs/preview/*.png`
- `outputs/tmp/*`
- `outputs/reports/*.json`
- File `.ma` hoặc `.png` sinh từ Maya launcher

## Xử lý sự cố nhanh

| Vấn đề | Cách xử lý |
| --- | --- |
| `No module named yaml` | Kích hoạt virtual environment hoặc chạy `pip install -r requirements.txt`. |
| Không tìm thấy `mayapy` | Chạy `launchers/00_maya_env_check.bat`, kiểm tra đường dẫn Maya, hoặc đặt `tool_paths.mayapy` trong `config/pipeline.yaml`. |
| Dry-run chạy được nhưng chạy thật lỗi | Kiểm tra lại đường dẫn `mayapy.exe`; dry-run không cần Maya nên có thể vẫn thành công. |
| PNG preview lỗi | Đọc log render phía trên; kiểm tra Maya có render được scene `.ma` hay không. |
| Output nhìn còn đơn giản | Đây là blockout preview kỹ thuật, chưa phải final art. Họa sĩ vẫn polish trong Maya. |

## Hiện tại

Feature 002 đã có xuất/làm sạch/kiểm tra SVG. Feature 003 đã có naming và manifest. Feature 001/004 là Blender MVP và batch dry-run/report cũ. Feature 005 bổ sung Maya Bridge làm backend DCC production chính; quy trình launcher 005.4 đã được kiểm chứng trên máy DCC có Autodesk Maya 2024 và `mayapy.exe`.
