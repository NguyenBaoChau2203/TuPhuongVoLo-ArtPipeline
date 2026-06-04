# Daily workflow cho artist/operator - 015A

Tài liệu này là checklist ngắn cho workflow ổn định ngày mai. Hiện tại Illustrator MCP đang beta/bị chặn bởi lỗi EOF, nên đường an toàn là **manual SVG export -> app/CLI Maya -> Visual Fidelity -> Maya sandbox -> Codex prompt polish -> review/rollback**.

## 1. Tôi mở gì?

Mở:

- Adobe Illustrator để vẽ/chỉnh layout.
- Repo local:

```text
D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline
```

- Desktop app nếu muốn dùng UI:

```powershell
launchers\09_artist_desktop_app.bat
```

- Maya để mở sandbox review/polish.

Không mở file gốc để cho agent sửa. Agent chỉ được làm trên sandbox working file.

## 2. Tôi export gì?

Nếu Illustrator MCP chưa được repair, họa sĩ export SVG thủ công từ Illustrator.

Quy tắc:

- Không ghi đè SVG gốc.
- Export ra sandbox hoặc thư mục output/drop đã thống nhất.
- Giữ tên room/marker thân thiện, ví dụ `phong_kho`, `prop_wooden_crate_01`.
- Nếu file export từ Illustrator có ID dạng `x5F`, pipeline hiện đã hỗ trợ decode cho room/marker.

## 3. Tôi chạy app/CLI bước nào?

Ưu tiên dùng desktop app:

1. Chọn SVG sạch.
2. Nhập room, ví dụ `phong_kho`.
3. Bấm `Kiểm tra SVG`.
4. Bấm `Chạy dry-run`.
5. Chỉ khi dry-run pass, bấm `Chạy Maya thật`.

CLI tương đương:

```powershell
python scripts/python/svg_preflight_check.py --input "D:\path\to\scene_export.svg"
python scripts/python/build_maya_room.py --input "D:\path\to\scene_export.svg" --room phong_kho --dry-run
python scripts/python/build_maya_room.py --input "D:\path\to\scene_export.svg" --room phong_kho --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

Nếu đang chạy smoke test ngoài repo, dùng output folder sandbox ngoài repo và `--skip-manifest-update` theo tài liệu closeout 012E.

## 4. Tôi chạy Visual Fidelity như thế nào?

Sau khi có `.ma` blockout và geometry JSON, chạy Visual Fidelity nếu muốn scene dễ đọc hơn.

Dry-run:

```powershell
python scripts/python/maya_visual_fidelity_pass.py `
  --geometry-json "D:\path\to\blockout.json" `
  --preset warehouse_v0 `
  --dry-run `
  --report-json "D:\path\to\visual_fidelity_report_015A.json"
```

Actual:

```powershell
python scripts/python/maya_visual_fidelity_pass.py `
  --input-scene "D:\path\to\source_scene.ma" `
  --geometry-json "D:\path\to\blockout.json" `
  --output-scene "D:\path\to\tu_phuong_vo_lo_phong_kho_main_maya_visual_fidelity_v018.ma" `
  --preset warehouse_v0 `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --verbose
```

Luôn để `--output-scene` khác `--input-scene`.

## 5. Tôi mở file Maya nào?

Cho review hiện tại từ 014C, mở file sandbox working:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\working\scene_agent_work.ma
```

Không mở source generated `.ma` trong `outputs\maya\` để agent sửa. Không mở `original\scene_before_agent.ma` để edit.

## 6. Tôi paste prompt nào?

Dùng template:

```text
docs/templates/maya_artist_prompt_template_vi.md
```

Điền ít nhất:

- scene path
- sandbox path
- yêu cầu của họa sĩ bằng tiếng Việt
- allowed edit style
- forbidden edits
- required group name
- review instructions
- rollback path

Gợi ý cho 015B:

```text
Scene path:
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\working\scene_agent_work.ma

Sandbox:
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review

Required group:
GRP_agent_prompt_015B_polish_v001

Rollback:
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\restore_agent_backup.ps1
```

Ví dụ yêu cầu tiếng Việt:

```text
Hãy thêm một lớp polish nhẹ cho phòng kho: làm thùng gỗ dễ đọc hơn, thêm vài mép tối và note review, không đổi layout tường/cửa, không xóa mesh gốc.
```

## 7. Tôi review như thế nào?

Trong Maya:

1. Mở Outliner.
2. Tìm `GRP_visual_fidelity_v0` để xem lớp Visual Fidelity.
3. Tìm group agent, ví dụ `GRP_agent_prompt_015B_polish_v001`.
4. Bật/tắt visibility group agent để so sánh trước/sau.
5. Kiểm tra camera review nếu agent tạo thêm.
6. Kiểm tra object mới có tên dễ hiểu và nằm trong group agent.
7. Nếu không đạt, ghi prompt sửa tiếp hoặc rollback.

Không cần chấp nhận thay đổi nếu nhìn chưa đúng. Artist review là bước bắt buộc.

## 8. Tôi rollback như thế nào?

Rollback sandbox 014C:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\restore_agent_backup.ps1
```

Quy tắc:

- Đọc/kiểm tra restore script trước nếu cần.
- Chỉ restore sandbox working file.
- Không xóa thư mục `original\`.
- Sau rollback, mở lại `working\scene_agent_work.ma` và kiểm tra trong Maya.

## 9. Cái gì vẫn beta?

- Illustrator prompt control qua Antigravity MCP vẫn beta/bị chặn do `illustrator-sandbox` trả EOF ở lần thử mới nhất.
- Agent chưa được phép sửa `.ai` gốc.
- Agent chỉ được sửa Illustrator sandbox sau khi MCP repair smoke test pass.
- Prompt orchestration app mới chưa được implement trong 015A.
- Maya prompt polish cần phase 015B để smoke test một task additive thật trên sandbox 014C.

## 10. Nhắc an toàn cuối

- Không sửa original `.ai`, `.svg`, `.ma`.
- Không commit generated `.ma`, `.svg`, `.json`, `.png`, `.zip`, report, backup.
- Không dùng Illustrator MCP khi còn EOF.
- Không dùng Maya commandPort trong 015A.
- Manual SVG export là fallback chính thức.
