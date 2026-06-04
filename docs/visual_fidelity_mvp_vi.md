# Visual Fidelity MVP 014A - hướng dẫn vận hành

Tài liệu này dành cho artist/operator dùng pipeline Illustrator -> Maya của
**Tứ Phương Vô Lộ**.

## Tính năng này làm gì?

`maya_visual_fidelity_pass.py` là bước chạy sau khi đã có scene Maya blockout.
Công cụ đọc geometry JSON đã sinh từ SVG, rồi thêm một lớp trình bày dễ nhìn hơn
vào scene Maya mới:

- thùng gỗ có thân hộp, viền tối và band mặt trước
- thùng barrel dạng cylinder, có vòng trên/dưới và band tối
- kệ có trụ đứng, ván ngang và vài filler nhỏ
- floor grate có khung và các thanh slat tối
- tủ điện có thân tủ, panel, tay nắm và chi tiết cảnh báo
- camera review, đèn review, floor tint nhẹ và note cho artist

Tất cả phần thêm mới nằm trong group top-level:

```text
GRP_visual_fidelity_v0
```

## Tính năng này không làm gì?

- Không sửa file `.ai`, SVG gốc, hoặc geometry JSON gốc.
- Không ghi đè scene Maya đầu vào.
- Không biến blockout thành final art.
- Không làm Maya khớp SVG 100%.
- Không dùng Illustrator MCP.
- Không dùng Maya commandPort.
- Không thay đổi camera, light, material sản xuất sẵn trong scene.

## Vì sao Maya chưa giống SVG 100%?

SVG concept là hình 2D có màu, curve, layer và chi tiết minh họa. Geometry JSON
hiện tại chủ yếu chứa boundary phòng và marker prop để dựng blockout. Một số
prop như barrel dùng curve/arc trong SVG nên bbox chỉ là ước lượng. Vì vậy 014A
chọn hướng an toàn: tạo proxy 3D dễ nhận diện, đặt đúng vị trí tương đối, nhưng
không cố sao chép từng nét SVG.

## Workflow khuyến nghị cho ngày mai

1. Dùng workflow hiện tại để tạo `.ma` blockout và geometry JSON.
2. Chạy dry-run visual fidelity để xem kế hoạch.
3. Chỉ khi dry-run ổn, chạy actual apply bằng `mayapy.exe`.
4. Mở output `.ma` mới trong Maya.
5. Bật/tắt `GRP_visual_fidelity_v0` để so sánh với blockout gốc.
6. Artist polish trực tiếp trong Maya sau khi đã chọn scene phù hợp.

## Lệnh dry-run

Dry-run không cần Maya và không tạo `.ma`.

```powershell
python scripts/python/maya_visual_fidelity_pass.py `
  --geometry-json "D:\duong_dan\blockout.json" `
  --preset warehouse_v0 `
  --dry-run `
  --report-json "D:\duong_dan\visual_fidelity_report_014A.json"
```

Report JSON sẽ có:

- tên phòng
- số lượng prop theo loại
- danh sách phần sẽ thêm
- cảnh báo
- output scene nếu có truyền `--output-scene`
- trạng thái an toàn

## Lệnh chạy thật

Luôn ghi output ra file `.ma` khác input.

```powershell
python scripts/python/maya_visual_fidelity_pass.py `
  --input-scene "D:\duong_dan\source_scene.ma" `
  --geometry-json "D:\duong_dan\blockout.json" `
  --output-scene "D:\duong_dan\tu_phuong_vo_lo_phong_kho_main_maya_visual_fidelity_v018.ma" `
  --preset warehouse_v0 `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --verbose
```

Nếu `--output-scene` trùng `--input-scene`, tool sẽ dừng trước khi mở Maya.

## Cách mở kết quả trong Maya

1. Mở Maya.
2. File -> Open Scene.
3. Chọn file output từ `--output-scene`.
4. Trong Outliner, tìm `GRP_visual_fidelity_v0`.
5. Mở group để xem `vf_props`, `vf_presentation`, và `vf_artist_notes`.

## Cách bật/tắt visual fidelity group

Trong Outliner:

1. Chọn `GRP_visual_fidelity_v0`.
2. Tắt biểu tượng visibility nếu muốn xem blockout gốc.
3. Bật lại visibility để xem bản có visual fidelity.

Vì group này là additive, việc hide group không ảnh hưởng production groups.

## Rollback an toàn

Có hai cách rollback:

- Mở lại source scene `.ma` ban đầu.
- Hoặc trong output scene, hide/delete `GRP_visual_fidelity_v0`.

Nếu đang làm trong sandbox, có thể dùng lại source scene hoặc restore script của
sandbox để quay về trạng thái trước agent.

## Quy tắc an toàn

- Không dùng output path trùng input path.
- Không chạy trực tiếp lên file source gốc ngoài sandbox.
- Không commit `.ma`, `.svg`, `.png`, `.zip` sinh ra.
- Với smoke test ngoài repo, đặt output vào folder backup/sandbox ngoài repo.
- Dry-run trước actual run.

## Ghi chú giới hạn MVP

`warehouse_v0` là preset duy nhất ở 014A. Các prop khác ngoài wooden crate,
barrel, shelf unit, floor grate, electrical cabinet sẽ được ghi warning và bỏ
qua, không làm hỏng lệnh.
