# Closeout 012E - Quy trình Illustrator-to-Maya MCP sandbox

> **Trạng thái**: PASS sau 012D  
> **Mục tiêu**: Ghi lại luồng đã kiểm chứng từ Illustrator sandbox tới Maya MCP sandbox, các quy tắc an toàn, và các phát hiện cần nhớ trước khi bàn giao cho họa sĩ.

Tài liệu này không yêu cầu mở Illustrator, Maya, MCP server, hay sửa bất kỳ file sandbox bên ngoài repo. Đây là tài liệu đóng pha cho workflow 011B/012.

## 1. Luồng đã kiểm chứng

Luồng end-to-end đã PASS:

```text
Illustrator sandbox
-> Illustrator MCP inspect-only
-> Illustrator MCP edit/export SVG trong sandbox
-> SVG parser hỗ trợ ID x5F
-> build_maya_room.py actual run không làm dirty manifest repo
-> Maya agent sandbox
-> Maya commandPort inspect/edit/restore/polish trên working .ma
-> artist review thủ công
```

Các checkpoint liên quan:

- 011B-C: Illustrator MCP inspect-only PASS.
- 011B-D: Illustrator MCP controlled write/export PASS.
- 011B-E: hỗ trợ Illustrator `x5F` SVG ID, commit `f03eb1e`.
- 011B-G: actual Maya generation an toàn manifest, commit `481abe8`.
- 012A-R1: Maya commandPort inspect-only PASS sau khi mở có kiểm soát scene sandbox.
- 012B: controlled harmless edit/save PASS trên sandbox working scene.
- 012C: restore/rollback PASS, working `.ma` khôi phục về hash source/original.
- 012D: fresh sandbox polish micro-task PASS.

## 2. Quy trình vận hành chuẩn

1. Tạo Illustrator sandbox bằng workflow backup Illustrator. Chỉ mở/chỉnh file `.ai` trong `working/`.
2. Dùng Illustrator MCP inspect-only trước, không ghi file trong lần kiểm tra đầu.
3. Khi cần sửa/export, chỉ export SVG vào `working/` của Illustrator sandbox.
4. Sau export, kiểm tra lại active document trong Illustrator; `doc.exportFile()` có thể chuyển active document sang SVG vừa export.
5. Chạy dry-run Maya bằng SVG sandbox, ví dụ `--room phong_kho`. Từ 011B-E, room name thân thiện vẫn hoạt động khi Illustrator export ID dạng `room_x5F_phong_x5F_kho`.
6. Khi smoke test actual Maya generation ngoài repo, dùng `--output-dir` ngoài repo và `--skip-manifest-update`.
7. Nếu máy không tự tìm thấy Maya, truyền rõ:

```powershell
python scripts/python/build_maya_room.py `
  --input "D:\TuPhuongVoLo_IllustratorAgentBackups\20260604_134449_phong_kho\working\scene_agent_work_011B_D_export.svg" `
  --room phong_kho `
  --output-dir "D:\TuPhuongVoLo_IllustratorAgentBackups\20260604_134449_phong_kho\outputs\011B_F_actual_maya_generation" `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --skip-manifest-update `
  --verbose
```

8. Tạo Maya sandbox từ `.ma` đã sinh ra bằng `scripts/python/maya_agent_sandbox.py`.
9. Trong Maya, chỉ mở file `working\scene_agent_work.ma` của session sandbox. Không mở trực tiếp source generated `.ma`.
10. Bật/kiểm tra commandPort trên `127.0.0.1:50007` bằng `scripts/maya/enable_maya_mcp_command_port.py`.
11. Trước mọi inspect/edit, agent phải kiểm tra scene path hiện tại trong Maya và xác nhận nó chính là sandbox working `.ma` được phép.
12. Inspect scene read-only trước: camera, layers, group hierarchy, node count, và scene path.
13. Nếu cần edit, chỉ edit/save sandbox working `.ma`. Không save nếu scene path không khớp allowlist.
14. Khi cần rollback, dùng `restore_agent_backup.ps1` để copy từ `original\scene_before_agent.ma` sang target rõ ràng.
15. Với polish task mới, tạo fresh sandbox mới thay vì reuse sandbox đã rollback.
16. Artist review trong Maya luôn là bước bắt buộc trước khi đưa thay đổi vào production.

## 3. Dữ liệu 012D đã ghi nhận

012D fresh sandbox:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_164546_phong_kho_v017_012D_maya_polish_microtask
```

012D working `.ma`:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_164546_phong_kho_v017_012D_maya_polish_microtask\working\scene_agent_work.ma
```

012D original copy:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_164546_phong_kho_v017_012D_maya_polish_microtask\original\scene_before_agent.ma
```

012D restore script:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_164546_phong_kho_v017_012D_maya_polish_microtask\restore_agent_backup.ps1
```

Polish nodes trong sandbox:

- `agent_polish_012D`
- `agent_fill_light_012D`
- `agent_polish_note_012D`

012D saved sandbox working hash:

```text
7F04231FA8E06229A3E33922CB55D02A382AB0FF14960D3895ECCA13E4823CA2
```

Source generated `.ma` chỉ đọc:

```text
D:\TuPhuongVoLo_IllustratorAgentBackups\20260604_134449_phong_kho\outputs\011B_F_actual_maya_generation\maya\tu_phuong_vo_lo_phong_kho_main_maya_v017.ma
```

Source generated JSON chỉ đọc:

```text
D:\TuPhuongVoLo_IllustratorAgentBackups\20260604_134449_phong_kho\outputs\011B_F_actual_maya_generation\tmp\tu_phuong_vo_lo_phong_kho_main_blockout_v017.json
```

Known source hashes:

```text
Source .ma:
5978B85CF623E08455C90B3913B15C18FF4A5042C8AEA8285B127AFF6D89EA1D

Source JSON:
B4CFA647F9121BBC75D83C0695ECF2746570BAE595CED3B218441A67BAD4E329
```

## 4. Checklist an toàn bắt buộc

Trước khi dùng agent/MCP:

- [ ] Repo đang ở branch dự kiến và `git status` sạch.
- [ ] Nếu branch đang ahead of origin, chỉ push sau khi user/operator đồng ý rõ ràng.
- [ ] Không mở/chỉnh source `.ai` hoặc SVG gốc của họa sĩ.
- [ ] Không mở/chỉnh generated source `.ma` hoặc geometry JSON sinh ra từ pipeline.
- [ ] Illustrator/Maya chỉ mở file trong sandbox `working\`.
- [ ] Đã ghi lại path sandbox working file được phép trước khi inspect/edit.
- [ ] Đã ghi hash/source path trước khi bắt đầu nếu cần rollback verification.
- [ ] commandPort chỉ là localhost `127.0.0.1:50007`.

Trong khi agent chạy:

- [ ] Agent phải verify current scene path trước mỗi lệnh Maya có khả năng sửa scene.
- [ ] Không save nếu current scene path không khớp đúng sandbox `working\scene_agent_work.ma`.
- [ ] Với commandPort trả về chế độ MEL, dùng wrapper an toàn `python("...")` cho probe Python.
- [ ] Không cấp quyền filesystem rộng cho toàn bộ `D:\` hoặc source artist folders.
- [ ] Không tạo output vào `assets\`, `drops\`, hoặc source folders.

Sau khi agent kết thúc:

- [ ] So sánh hash hoặc kiểm tra file trước/sau theo mục tiêu của session.
- [ ] Nếu rollback, chạy `restore_agent_backup.ps1` với restore target rõ ràng, ưu tiên target kiểm tra riêng.
- [ ] Trên Windows, nếu cần, dùng process-scoped `-ExecutionPolicy Bypass` sau khi đã inspect nội dung script restore.
- [ ] Artist mở Maya kiểm tra thủ công trước khi chấp nhận polish.
- [ ] Không commit generated `.ai`, `.svg`, `.ma`, `.json`, `.png`, `.zip`, reports, backup folders, hoặc outputs sandbox.
- [ ] External outputs/backups ở `D:\TuPhuongVoLo_AgentBackups`, `D:\TuPhuongVoLo_IllustratorAgentBackups`, `D:\TuPhuongVoLo_ArtistTests` vẫn nằm ngoài repo.

## 5. Known findings

- Illustrator export có thể encode `_` thành `x5F` hoặc `x5f` trong SVG ID. Pipeline hiện giải mã các ID này cho room/marker.
- `--room phong_kho` hoạt động với SVG Illustrator-exported x5F sau 011B-E.
- Illustrator `doc.exportFile()` có thể chuyển active document sang SVG vừa export; script MCP phải re-activate `.ai` sandbox trước khi edit/save tiếp.
- Agent smoke markers có thể bị xem là room candidates nếu không filter. Pipeline hiện bỏ qua `agent_test_*`, `agent_smoke_marker_*`, và `*_smoke_marker_*`.
- Actual Maya generation dùng cho external smoke test có thể truyền `--skip-manifest-update` để không cập nhật repo manifest.
- Actual Maya generation cần Autodesk Maya/mayapy. Máy DCC đã kiểm chứng path `C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`.
- Maya commandPort đang dùng `127.0.0.1:50007`.
- Maya commandPort hoặc MCP adapter có thể diễn giải command như MEL; probe Python an toàn có thể cần dạng MEL `python("...")`.
- Maya launch/open phải guarded: luôn verify current scene path trước inspect/edit.
- Restore script do sandbox workflow sinh ra tên là `restore_agent_backup.ps1`.
- Restore script trên Windows có thể cần `powershell -ExecutionPolicy Bypass -File ...` ở phạm vi process, chỉ sau khi đã đọc script.
- Một lần sandbox CLI bị abort do lỗi encoding/charmap đã tạo folder ngoài repo dạng `20260604_164504...`. Không xóa folder ngoài repo trong closeout này; chỉ ghi nhận để operator biết.

## 6. Tài liệu liên quan

- `docs/illustrator_agent_backup_workflow_vi.md`
- `docs/illustrator_mcp_edit_export_workflow_vi.md`
- `docs/maya_agent_antigravity_backup_workflow_vi.md`
- `docs/antigravity_maya_mcp_sandbox_vi.md`
- `docs/maya_render_preview_vi.md`
- `docs/artist_handoff_desktop_app_vi.md`
- `docs/release_packaging_checklist_vi.md`
- `specs/010-maya-agent-sandbox-backup-workflow/quickstart.md`
