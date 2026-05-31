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

## Giới hạn hiện tại

- Đây là render preview kỹ thuật, dùng renderer offline mặc định của Maya
  (`mayaSoftware`); chưa tinh chỉnh ánh sáng/vật liệu cho art cuối.
- Chưa đặt prop theo tên layer/group SVG (đó là Phase 005.3).
- Không gọi AI ngoài, không FLUX/fal.ai.
- Camera dùng camera iso do scene builder tạo (`cam_<phòng>_iso`).
