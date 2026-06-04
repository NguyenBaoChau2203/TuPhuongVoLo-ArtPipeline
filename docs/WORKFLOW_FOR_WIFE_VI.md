# Quy trình hằng ngày cho vợ/họa sĩ

Tài liệu này là đường chính. Không cần đọc hết phase cũ.

## Mục tiêu

Vợ không cần vẽ mọi thứ từ trang trắng. Mỗi cảnh đi theo vòng:

```text
Ảnh mẫu + mô tả tiếng Việt
-> Codex tạo JSX draft
-> mở trong Illustrator, chỉnh theo mắt
-> export SVG
-> app tạo Maya .ma
-> sandbox Maya
-> Codex tạo script polish
-> bật/tắt group để review, giữ hoặc rollback
```

## 1. Gửi ảnh mẫu cho Codex

Gửi ảnh mẫu và mô tả ngắn:

```text
Đây là cảnh phòng kho nhìn top-down.
Hãy tạo JSX draft cho Illustrator.
Cần ranh phòng, cửa, cửa sổ, vị trí đồ lớn, flow đi lại, vài shape chính.
Ưu tiên đúng pipeline để export SVG sang Maya.
```

Codex sẽ tạo JSX dựa trên template:

```text
scripts\illustrator\templates\reference_to_layout_draft.jsx
```

JSX nên tạo sẵn group/layer kiểu:

```text
room_phong_kho
door_main
window_back_01
prop_shelf_01
prop_wooden_crate_01
flow_main_path
```

## 2. Chạy JSX trong Illustrator

Trong Illustrator:

```text
File -> Scripts -> Other Script...
```

Chọn file `.jsx` Codex tạo.

Sau khi chạy:

- nhìn bố cục tổng thể
- kéo/sửa shape nếu cần
- đổi style theo mắt
- giữ tên group/marker do JSX tạo

JSX chỉ tạo bản nháp có thể chỉnh, không thay mắt thẩm mỹ của vợ.

## 3. Export SVG

Khi thấy ổn:

```text
File -> Export -> Export As... -> SVG
```

Gợi ý:

- đặt SVG vào `drops\`
- không ghi đè file `.ai` gốc
- giữ Object IDs theo layer/group nếu Illustrator hỏi
- nếu chưa chắc, export thêm bản mới thay vì ghi đè

## 4. Mở app pipeline

Chạy:

```powershell
launchers\09_artist_desktop_app.bat
```

Trong app:

1. chọn SVG vừa export
2. nhập room name, ví dụ `phong_kho`
3. bấm `Kiểm tra SVG`
4. bấm `Chạy thử an toàn`
5. chỉ khi dry-run ổn mới bấm `Dựng Maya thật`
6. bấm `Tự tìm output mới nhất` để app điền `.ma` và geometry JSON cho các bước sau

Nếu không dùng app, dùng CLI:

```powershell
python scripts\python\svg_preflight_check.py --input "drops\scene_export.svg"

python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --dry-run
```

Chạy Maya thật:

```powershell
python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --render-preview
```

## 5. Kiểm tra output

Sau khi chạy thật:

```text
outputs\maya\       file .ma
outputs\preview\    ảnh PNG preview nếu bật render
outputs\tmp\        geometry JSON
```

Mở `.ma` trong Maya để xem bố cục.

Nếu ranh phòng/cửa/đồ lớn sai nhiều, quay lại Illustrator sửa SVG rồi chạy lại app.

Nếu layout ổn, qua bước polish.

## 6. Chạy Visual Fidelity nếu cần

Visual Fidelity thêm một lớp phụ trợ để scene dễ đọc hơn.

Cách dễ nhất trong app:

1. bấm `Tự tìm output mới nhất`
2. giữ `Visual Fidelity dry-run trước`
3. bấm `Tạo Visual Fidelity`
4. nếu dry-run ổn và muốn tạo `.ma` thật, bỏ dry-run rồi bấm lại

Nếu không dùng app, dùng CLI:

```powershell
python scripts\python\maya_visual_fidelity_pass.py `
  --input-scene "outputs\maya\scene.ma" `
  --geometry-json "outputs\tmp\scene.json" `
  --output-scene "outputs\maya\scene_visual_fidelity.ma" `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

Luôn để `--output-scene` khác `--input-scene`.

## 7. Tạo sandbox Maya trước khi nhờ Codex polish

Không cho Codex/AI sửa file `.ma` gốc. Cách dễ nhất trong app:

1. bấm `Tự tìm output mới nhất`
2. bấm `Tạo Maya Sandbox`
3. bấm `Mở working/scene_agent_work.ma`

Nếu không dùng app, double-click:

```powershell
launchers\08_create_maya_sandbox.bat
```

Hoặc dùng CLI:

```powershell
python scripts\python\maya_agent_sandbox.py `
  --maya-scene "outputs\maya\scene.ma" `
  --room phong_kho `
  --backup-root "D:\TuPhuongVoLo_AgentBackups"
```

Sau đó chỉ mở file:

```text
D:\TuPhuongVoLo_AgentBackups\...\working\scene_agent_work.ma
```

## 8. Nhờ Codex tạo script Maya polish

Gửi cho Codex:

```text
Scene đang mở là sandbox working:
D:\TuPhuongVoLo_AgentBackups\...\working\scene_agent_work.ma

Hãy tạo Maya Python script để làm phòng kho cũ hơn:
- thêm 2 kệ gỗ bên phải
- thêm vài thùng gỗ giữa phòng
- ánh sáng vàng nhẹ
- không đổi tường/cửa/layout gốc
- mọi thứ mới nằm trong GRP_agent_polish_v001
```

Codex sẽ tạo script dựa trên:

```text
scripts\maya\agent_polish_templates\agent_polish_additive_template.py
```

## 9. Chạy script trong Maya

Trong Maya:

```text
Windows -> General Editors -> Script Editor
```

Chọn tab Python, paste script Codex tạo, rồi Run.

Script phải tạo group riêng, ví dụ:

```text
GRP_agent_polish_v001
```

## 10. Review và rollback

Trong Maya Outliner:

- bật/tắt `GRP_agent_polish_v001`
- bật/tắt `GRP_visual_fidelity_v0` nếu có
- nếu đẹp thì giữ và save bản sandbox/result mới
- nếu không đẹp thì xóa group, tắt group, hoặc rollback

Rollback bằng script trong thư mục sandbox:

```text
restore_agent_backup.ps1
```

## Không làm

- Không sửa file `.ai` gốc bằng AI.
- Không để AI sửa file `.ma` trong `outputs\maya\`.
- Không commit output sinh ra.
- Không dùng Illustrator MCP nếu nó còn lỗi EOF.
- Không cần AI preview/fal/API key cho workflow hằng ngày.

## Checklist 1 ngày làm việc

- [ ] Có ảnh mẫu và mô tả.
- [ ] Codex tạo JSX draft.
- [ ] Vợ mở JSX trong Illustrator và chỉnh.
- [ ] Export SVG vào `drops\`.
- [ ] App preflight pass hoặc warning chấp nhận được.
- [ ] Dry-run đúng room/output.
- [ ] Tạo `.ma` thật bằng `mayapy`.
- [ ] Mở `.ma` trong Maya.
- [ ] Tạo sandbox trước khi polish bằng script.
- [ ] Codex tạo Maya Python script.
- [ ] Vợ bật/tắt group review.
- [ ] Giữ, sửa tiếp, hoặc rollback.
