# Quy trình Illustrator MCP edit/export có kiểm soát

> **Giai đoạn**: 011B-D kết quả thật + 011B-E hardening  
> **Mục tiêu**: Cho phép agent chỉnh sửa/export SVG trong sandbox Illustrator mà không làm hỏng file gốc, đồng thời giữ UX phòng `phong_kho` cho pipeline Python/Maya.

> **Closeout 012E**: Luồng Illustrator sandbox -> Maya MCP sandbox đã được ghi lại tại `docs/maya_mcp_sandbox_workflow_closeout_vi.md`.

## Tóm tắt 011B-D

Smoke test Illustrator MCP đã PASS trên bản sao sandbox:

- Agent chỉ chỉnh sửa file `working/scene_agent_work.ai`.
- Export SVG mới nằm trong sandbox `working/`.
- Maya dry-run PASS khi trỏ vào SVG export mới.
- Actual Maya generation trên máy hiện tại bị chặn bởi `ERR_MAYA_NOT_FOUND`.

`ERR_MAYA_NOT_FOUND` nghĩa là máy đang thiếu Maya hoặc `mayapy.exe`, không tự động nghĩa là SVG sai. Dry-run vẫn là bước kiểm tra hợp lệ vì dry-run không cần Maya và không ghi manifest.

## Ghi chú 011B-F / 011B-G: actual Maya sandbox an toàn

Ở 011B-F, máy DCC đã xác nhận có Maya 2024:

- `C:\Program Files\Autodesk\Maya2024\bin\maya.exe`
- `C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe`

Dry-run với SVG export từ Illustrator và room thân thiện `phong_kho` đã PASS, nhưng actual run bị dừng trước khi chạy vì CLI mặc định sẽ cập nhật repo manifest tại `outputs/manifest/asset_manifest.json`. Với smoke test output nằm ngoài repo, side-effect này làm repo bị dirty nên không phù hợp cho sandbox verification.

Từ 011B-G, smoke test actual Maya ngoài repo dùng thêm:

```powershell
python scripts/python/build_maya_room.py `
  --input "D:\TuPhuongVoLo_IllustratorAgentBackups\20260604_134449_phong_kho\working\scene_agent_work_011B_D_export.svg" `
  --room phong_kho `
  --output-dir "D:\TuPhuongVoLo_IllustratorAgentBackups\20260604_134449_phong_kho\outputs\011B_F_actual_maya_generation" `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --skip-manifest-update `
  --verbose
```

Chế độ này vẫn tạo `.ma` và geometry JSON ở output folder ngoài repo, nhưng bỏ qua cập nhật repo manifest theo yêu cầu. File `.ma`/`.json` sinh ra là artifact kiểm chứng bên ngoài, không commit vào repo.

## Quy tắc sandbox

- Không mở/chỉnh sửa file `.ai` gốc của họa sĩ.
- Không sửa SVG gốc hoặc file trong `D:\TuPhuongVoLo_ArtistTests`.
- MCP/agent chỉ làm việc trong `D:\TuPhuongVoLo_IllustratorAgentBackups\<session>\working`.
- SVG export từ agent cũng chỉ ghi vào thư mục `working/` của sandbox.
- Không commit `.ai`, `.svg`, `.ma`, `.json`, `.png`, `.zip`, report, hoặc backup sinh ra từ sandbox.
- Sau khi export, họa sĩ hoặc operator review file sandbox trước khi đưa vào production.

## Illustrator mã hóa dấu gạch dưới

Illustrator 2020 có thể export dấu `_` trong XML ID thành token `x5F` hoặc `x5f`.

Ví dụ:

```text
phong_kho -> phong_x5F_kho
room_phong_kho -> room_x5F_phong_x5F_kho
prop_wooden_crate_01 -> prop_x5F_wooden_x5F_crate_x5F_01
```

Từ 011B-E, pipeline Python giải mã token này cho tên phòng/marker. Họa sĩ và app vẫn nên dùng tên thân thiện:

```powershell
python scripts/python/build_maya_room.py --input path\to\scene_agent_work_export.svg --room phong_kho --dry-run
```

Pipeline vẫn có thể hiểu dạng cũ đã lộ ra trước đó như `x5f_phong_x5f_kho`, nhưng UX ưu tiên là `phong_kho`.

## Marker smoke/test của agent

Các group/layer dùng để smoke test agent không phải phòng production. Pipeline 011B-E bỏ qua các tên hẹp sau khi phát hiện room candidate:

- `agent_test_*`
- `agent_smoke_marker_*`
- `*_smoke_marker_*`

Không dùng các mẫu tên này cho phòng thật. Nếu cần ghi chú test trong Illustrator, để trong sandbox và xóa trước khi production.

## Cảnh báo active document sau export

`doc.exportFile()` trong Illustrator có thể làm active document chuyển sang SVG vừa export. Script MCP không được giả định `activeDocument` vẫn là file `.ai`.

Sau mỗi bước export, script phải:

1. Lưu lại reference tới document `.ai` trước khi export.
2. Export SVG vào sandbox `working/`.
3. Re-activate document `.ai` trước mọi thao tác edit/save tiếp theo.
4. Kiểm tra tên/đường dẫn active document trước khi ghi tiếp.

Quy tắc này giúp tránh trường hợp agent vô tình sửa hoặc save nhầm SVG export thay vì file AI sandbox.

## Dry-run và actual Maya

- `--dry-run`: đọc SVG, phát hiện phòng/prop/door/window, lập kế hoạch output; không cần Maya, không tạo `.ma`, không ghi manifest.
- Actual run: cần Autodesk Maya và `mayapy.exe`; sau khi Maya tạo `.ma` thành công mới cập nhật manifest.
- Actual run sandbox ngoài repo: thêm `--skip-manifest-update` và `--output-dir` ngoài repo để tạo artifact kiểm chứng mà không làm repo dirty.
- `ERR_MAYA_NOT_FOUND`: cần kiểm tra cài đặt Maya, `tool_paths.mayapy` trong `config/pipeline.yaml`, hoặc tham số `--maya-path`.

Luôn chạy dry-run trước actual run, đặc biệt sau export từ Illustrator MCP.

## Liên kết closeout 012E

Tài liệu `docs/maya_mcp_sandbox_workflow_closeout_vi.md` ghi lại chuỗi đã PASS sau 012D, gồm x5F SVG parsing, `--skip-manifest-update`, Maya sandbox, commandPort `127.0.0.1:50007`, restore bằng `restore_agent_backup.ps1`, và checklist không commit artifact sinh ra.
