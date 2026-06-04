# Maya — Render ảnh preview isometric (Phase 005.2)

> Tài liệu cho artist + developer. Tiếng Việt.
> Phase 005.2 — Maya isometric base render PNG.

## Tóm tắt

Sau khi pipeline dựng scene Maya `.ma` từ SVG sạch, bạn có thể **render thêm
một ảnh PNG preview** theo góc isometric trực tiếp từ Maya (qua `mayapy`).

Luồng đầy đủ:

```
Illustrator clean SVG
→ Python kiểm tra SVG / xuất geometry JSON
→ Maya .ma blockout            (outputs/maya/*.ma)
→ Maya isometric PNG preview   (outputs/preview/*.png)   ← phần mới ở 005.2
→ artist chỉnh sửa trong Maya
```

Ảnh PNG này là **preview kỹ thuật**, không phải art cuối cùng. Nó giúp xem nhanh
khối phòng (floor, walls, props placeholder) dưới góc isometric mà không cần mở
Maya thủ công.

## `--render-preview` làm gì?

Khi thêm cờ `--render-preview`, pipeline sẽ:

1. Vẫn tạo scene `.ma` editable như trước.
2. Mở scene `.ma` đó (chỉ để render, **không ghi đè / không đổi tên** — file
   `.ma` vẫn nguyên vẹn và chỉnh sửa được).
3. Render một ảnh PNG isometric qua camera iso của scene.
4. Lưu PNG vào `outputs/preview/` theo đúng quy ước đặt tên.

## Lệnh ví dụ

Dry-run (an toàn, không cần Maya, không tạo file, không ghi manifest):

```powershell
python scripts/python/build_maya_room.py `
  --input assets/2d/svg_clean/floorplan.svg `
  --room kho `
  --render-preview `
  --dry-run
```

Chạy thật (cần `mayapy`):

```powershell
python scripts/python/build_maya_room.py `
  --input assets/2d/svg_clean/floorplan.svg `
  --room kho `
  --render-preview `
  --maya-path "C:/Program Files/Autodesk/Maya2025/bin/mayapy.exe"
```

Smoke test actual run vào thư mục ngoài repo, không cập nhật repo manifest:

```powershell
python scripts/python/build_maya_room.py `
  --input "D:/duong_dan_sandbox/working/scene_agent_work_export.svg" `
  --room phong_kho `
  --output-dir "D:/duong_dan_sandbox/outputs/actual_maya_generation" `
  --maya-path "C:/Program Files/Autodesk/Maya2024/bin/mayapy.exe" `
  --skip-manifest-update
```

Batch có render preview:

```powershell
python scripts/python/batch_maya_room.py `
  --input-dir assets/2d/svg_clean `
  --all-rooms `
  --render-preview `
  --dry-run
```

## Các cờ CLI mới

| Cờ | Mặc định | Ý nghĩa |
|----|----------|---------|
| `--render-preview` | tắt | Bật render ảnh PNG isometric preview. |
| `--render-output` | (theo quy ước) | Đường dẫn PNG tùy chọn; nếu bỏ trống dùng tên chuẩn. |
| `--render-width` | `1280` | Chiều rộng ảnh render. |
| `--render-height` | `720` | Chiều cao ảnh render. |
| `--skip-manifest-update` | tắt | Chạy actual Maya nhưng bỏ qua cập nhật repo manifest; chỉ dùng cho smoke test output ngoài repo. |

Batch hỗ trợ `--render-preview`, `--render-width`, `--render-height`.

## Đầu ra và đặt tên

- Scene editable: `outputs/maya/tu_phuong_vo_lo_{ten}_{variant}_maya_v{NNN}.ma`
- Ảnh preview: `outputs/preview/tu_phuong_vo_lo_{ten}_{variant}_preview_v{NNN}.png`

Ví dụ:

- `tu_phuong_vo_lo_kho_main_maya_v001.ma`
- `tu_phuong_vo_lo_kho_main_preview_v001.png`

Stage `preview` đã có sẵn trong `config/naming_convention.yaml`, nên manifest
theo dõi ảnh PNG theo đúng quy tắc như file `.ma`.

## Hành vi dry-run (an toàn)

Trong chế độ `--dry-run`:

- Chỉ **in** đường dẫn PNG dự kiến và kích thước render.
- **Không** chạy Maya.
- **Không** tạo file PNG.
- **Không** ghi/cập nhật manifest.
- File gốc (`.ai`, SVG, ảnh tham chiếu) không bị thay đổi.

## Hành vi khi chạy thật

- Tạo `.ma` trước, xác minh `.ma` tồn tại → ghi manifest entry stage `maya`.
- Nếu bật `--render-preview`: render PNG, xác minh PNG tồn tại → ghi manifest
  entry stage `preview`.
- Nếu thêm `--skip-manifest-update`: vẫn tạo `.ma`, geometry JSON và PNG preview nếu bật, nhưng bỏ qua entry manifest cho các artifact đó.
- Nếu yêu cầu render nhưng PNG không xuất hiện → báo lỗi `ERR_RENDER_MISSING`
  và **không** ghi manifest cho PNG.
- Nếu Maya render trả mã lỗi → báo `ERR_RENDER_FAILED`.

## Yêu cầu `mayapy`

- Chạy thật cần `mayapy.exe` (Autodesk Maya).
- MVP **chỉ** hỗ trợ `mayapy.exe`. `maya.exe` / `mayabatch.exe` chưa được hỗ trợ.
- Có thể truyền `--maya-path` hoặc đặt `tool_paths.mayapy` trong
  `config/pipeline.yaml`.
- Dry-run **không** cần Maya.

## An toàn manifest

- Dry-run không bao giờ động vào manifest.
- Manifest chỉ được cập nhật **sau khi** file thật (`.ma`, sau đó `.png`) đã tồn
  tại và được xác minh.
- Production actual run mặc định vẫn cập nhật `outputs/manifest/asset_manifest.json`; đây là hành vi chủ ý để theo dõi output thật.
- Smoke test ngoài repo nên dùng `--output-dir` ngoài repo kèm `--skip-manifest-update` để repo luôn clean.

## Giới hạn hiện tại

- Đây là render preview kỹ thuật, dùng renderer offline mặc định của Maya
  (`mayaSoftware`); chưa tinh chỉnh ánh sáng/vật liệu cho art cuối.
- Prop marker theo tên layer/group SVG đã được hỗ trợ ở Phase 005.3, nhưng vẫn chỉ
  tạo cube placeholder để kiểm tra bố cục.
- Không gọi AI ngoài, không FLUX/fal.ai.
- Camera dùng camera iso do scene builder tạo (`cam_<phòng>_iso`).

## Gợi ý dùng launcher ở Phase 005.4

- Chạy `launchers/00_maya_env_check.bat` nếu không chắc Python, PyYAML hoặc `mayapy.exe` đã sẵn sàng.
- Chạy `launchers/07_build_maya_room.bat` cho một SVG/một phòng và bật dry-run trước.
- Chạy `launchers/08_batch_maya_room.bat` cho nhiều SVG hoặc nhiều phòng; report JSON nằm mặc định ở `outputs/reports/batch_maya_report.json`.
- Khi dry-run đã đúng, chạy actual run và bật PNG preview nếu muốn kiểm tra nhanh hình isometric.
