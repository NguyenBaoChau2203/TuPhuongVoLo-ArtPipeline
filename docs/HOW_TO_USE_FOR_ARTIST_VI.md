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

### Cách dễ nhất: desktop app MVP

1. Nhấp đúp `launchers/09_artist_desktop_app.bat`.
2. Chọn file SVG sạch.
3. Nhập tên phòng/layer, ví dụ `phong_kho`.
4. Giữ `Dry-run` cho lần đầu để kiểm tra an toàn.
5. Bật `Render PNG preview` nếu cần ảnh xem nhanh.
6. Khi dry-run đúng, bỏ chọn `Dry-run`, kiểm tra đường dẫn `mayapy.exe`, rồi chạy thật.

Phase 007C giúp app kiểm tra lỗi trước khi chạy: thiếu SVG, SVG không tồn tại,
tên phòng trống, output trống, thiếu repo root, thiếu `build_maya_room.py`,
hoặc chạy thật nhưng `mayapy.exe` không hợp lệ. App cũng hiển thị trạng thái,
lệnh đang chuẩn bị chạy, exit code cuối cùng, nút xóa log, nút copy lệnh, và các
nút mở nhanh `outputs/maya`, `outputs/preview`, `outputs/reports`.

Desktop app chỉ bọc pipeline CLI đã kiểm chứng. App không sửa SVG gốc, không
thay thế Maya, và output sinh ra vẫn nằm trong `outputs/maya/`,
`outputs/preview/`, `outputs/reports/`.

Ghi chú 005.5: repo đã có tài liệu đánh giá, mock local, và provider `fal` tùy
chọn cho AI polish preview:

- `docs/ai_polish_preview_evaluation_vi.md`
- `docs/ai_polish_preview_mock_vi.md`
- `docs/ai_polish_preview_fal_vi.md`

AI polish preview hiện là CLI tùy chọn, chưa có nút AI trong desktop app. API
thật chỉ chạy khi user tự gọi `scripts/python/ai_polish_preview.py --provider
fal`, không dùng `--dry-run`, có `FAL_KEY`, và đã cài `fal-client`. Ảnh AI chỉ
là reference/concept. File `.ma` và clean SVG vẫn là source of truth.

### Đóng gói desktop app thành .exe

Developer có thể tạo `.exe` local bằng PyInstaller qua launcher:

```powershell
launchers/10_package_artist_app.bat
```

Launcher này mặc định chỉ dry-run và in lệnh package. Nếu máy dev đã cài
PyInstaller, có thể build thật bằng:

```powershell
python scripts/python/package_artist_app.py --build
```

PyInstaller là công cụ dev-only, không phải dependency runtime của pipeline. File
`.exe` sinh ra nằm trong `dist/TuPhuongVoLo_MayaArtistApp.exe`, vẫn cần repo và
pipeline local để chạy, và không được commit cùng `build/`, `dist/`, hoặc file
`.spec` sinh tự động.

File `.exe` vẫn là wrapper local: nó cần repo files, Python bên ngoài, Maya và
`mayapy.exe` trên máy đang chạy. Trước khi chạy thật, hãy dry-run trước; khi chạy
thật phải dùng đường dẫn `mayapy.exe` hợp lệ, ví dụ
`C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`.

Checkpoint 007C-R đã kiểm chứng bản `.exe` sau polish trên máy artist/DCC:
app mở được, hiển thị repo root và lệnh dự kiến, dry-run trả exit code 0,
chạy thật Maya trả exit code 0, sinh PNG preview, và file `.ma` mở được
trong Maya với Outliner đúng. Chi tiết nằm trong
`docs/verification/007C_desktop_app_polish_verified.md`.

### Cách cũ: launcher CLI một phòng

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
3. Ưu tiên chạy `launchers/09_artist_desktop_app.bat` và giữ dry-run trước.
4. Nếu muốn dùng launcher CLI cũ, chạy `launchers/07_build_maya_room.bat` và chọn dry-run trước.
5. Đọc kết quả dry-run: kiểm tra tên phòng được chọn, prop marker phát hiện được, đường dẫn `.ma` và PNG preview dự kiến.
6. Khi dry-run đúng, chạy lại và chọn không dry-run để tạo `.ma` thật bằng `mayapy.exe`.
7. Nếu cần ảnh kiểm tra nhanh, bật lựa chọn PNG preview.
8. Mở file `.ma` trong Maya, kiểm tra Outliner và polish thủ công.

Launcher `07_build_maya_room.bat` dùng cho một SVG/một phòng. Launcher `08_batch_maya_room.bat` dùng cho nhiều SVG hoặc nhiều phòng và luôn in đường dẫn report JSON để kiểm tra.

## Prop marker trong Illustrator

Nếu muốn Maya đặt blockout đồ vật theo bố cục đã vẽ, tạo group/layer con bên trong group phòng và đặt tên theo mẫu:

- `prop_bed`
- `prop_table`
- `prop_chair`
- `prop_sofa`
- `prop_fridge`
- `prop_sink`
- `prop_kitchen_counter`
- `prop_cabinet`
- `prop_locker`
- `prop_plant`
- `prop_shelf_unit`
- `prop_wooden_crate`

Pipeline bỏ prefix `prop_`, `item_`, hoặc `object_` và dùng phần còn lại làm loại prop. Một số alias an toàn cũng được hỗ trợ: `desk` -> `table`, `couch` -> `sofa`, `refrigerator` -> `fridge`, `counter` -> `kitchen_counter`, `cupboard` -> `cabinet`, `potted_plant` -> `plant`, `shelf`/`shelving` -> `shelf_unit`, `crate`/`box` -> `wooden_crate`.

Trong group prop, giữ marker thật đơn giản: `rect`, `polygon`, `polyline`, hoặc path thẳng. Các prop được hỗ trợ sẽ tạo blockout nhiều khối dễ nhận ra hơn, nhưng vẫn là draft editable để kiểm tra bố cục. Nếu tên prop chưa được hỗ trợ, Maya vẫn tạo cube placeholder đơn giản thay vì dừng pipeline. Họa sĩ vẫn polish/thay model thật trong Maya sau.

Checkpoint DCC cho procedural prop blockout đã được ghi lại tại `docs/verification/005_3P_procedural_prop_blockout_verified.md`: file `.ma` mở được trong Maya, `prop_shelf_unit_01` và `prop_wooden_crate_01` là multi-piece, tên child node an toàn cho Maya, và PNG preview đã generate.

## Không nên commit

Các file sinh ra sau đây không nên commit trừ khi developer cố ý cần một fixture hoặc report mẫu:

- `outputs/maya/*.ma`
- `outputs/preview/*.png`
- `outputs/tmp/*`
- `outputs/reports/*.json`
- `build/`, `dist/`, file `.exe`, file `.spec`
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

005.5C có provider `fal` tùy chọn cho AI polish preview reference-only qua CLI;
pipeline Maya vẫn hoạt động bình thường nếu không có AI, `FAL_KEY`,
`fal-client`, hoặc internet.
Feature 006 natural-language control vẫn deferred.
