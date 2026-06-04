# Bàn giao desktop app Maya cho họa sĩ / dev operator

Tài liệu này chỉ nói về app hằng ngày. Các phase cũ, AI preview tùy chọn, batch, packaging và research đã được đưa ra khỏi luồng chính.

## 1. App dùng để làm gì?

App mở bằng:

```powershell
launchers\09_artist_desktop_app.bat
```

App giúp:

- chọn SVG sạch đã export từ Illustrator
- chạy `Kiểm tra SVG`
- chạy `Chạy dry-run`
- chỉ cho chạy Maya thật sau khi dry-run đúng settings đã pass
- gọi `mayapy.exe` để tạo file `.ma`
- mở nhanh thư mục output

App không sửa file `.ai`, không sửa SVG gốc, không thay thế Maya.

## 2. Cập nhật repo trên máy DCC

Repo chính hiện dùng `master`.

```powershell
cd D:\TuPhuongVoLo-ArtPipeline
git fetch
git checkout master
git pull --ff-only
git branch --show-current
```

Kết quả mong đợi:

```text
master
```

## 3. Yêu cầu máy

- Windows 10/11.
- Python có trong `PATH`, hoặc đặt `TUPHUONGVOLO_PYTHON_EXE`.
- Maya 2024+ nếu muốn chạy thật.
- Đường dẫn `mayapy.exe` thường dùng:

```text
C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
```

## 4. Quy trình app

1. Mở app.
2. Chọn SVG vợ export.
3. Nhập room name, ví dụ `phong_kho`.
4. Bấm `Kiểm tra SVG`.
5. Bấm `Chạy dry-run`.
6. Nếu dry-run đúng, nhập/kiểm tra `mayapy.exe`.
7. Bấm `Chạy Maya thật`.
8. Mở `outputs\maya\` và `outputs\preview\`.
9. Mở `.ma` trong Maya để review.

Nếu cần workflow đầy đủ từ ảnh mẫu đến Maya sandbox, đọc:

```text
docs\WORKFLOW_FOR_WIFE_VI.md
docs\CODEX_PROMPTS_VI.md
```

## 5. Checklist retest nhanh

- [ ] Repo đang ở `master`.
- [ ] App mở được bằng launcher.
- [ ] App hiển thị repo root.
- [ ] App hiển thị command preview.
- [ ] SVG input tồn tại và là `.svg`.
- [ ] `Kiểm tra SVG` chạy và ghi log.
- [ ] Dry-run trả exit code 0.
- [ ] App chặn chạy thật nếu chưa dry-run thành công với settings hiện tại.
- [ ] Chạy thật dùng đúng `mayapy.exe`.
- [ ] File `.ma` được tạo trong `outputs\maya\`.
- [ ] PNG preview được tạo trong `outputs\preview\` nếu bật render.
- [ ] File `.ma` mở được trong Maya.

## 6. Sau khi app tạo `.ma`

Nếu layout sai: quay lại Illustrator sửa SVG và chạy lại app.

Nếu layout ổn:

1. tạo Maya sandbox bằng `scripts\python\maya_agent_sandbox.py`
2. chỉ mở `working\scene_agent_work.ma`
3. nhờ Codex tạo Maya Python polish script
4. chạy script trong Maya Script Editor
5. bật/tắt `GRP_agent_*` để review
6. giữ, sửa tiếp, hoặc rollback bằng `restore_agent_backup.ps1`

## 7. Không commit

Không commit:

- `outputs\maya\*.ma`
- `outputs\preview\*.png`
- `outputs\tmp\*`
- `outputs\reports\*.json`
- `dist\*.exe`
- sandbox từ `D:\TuPhuongVoLo_AgentBackups`

## 8. Tài liệu liên quan

- `docs\WORKFLOW_FOR_WIFE_VI.md`
- `docs\CODEX_PROMPTS_VI.md`
- `docs\artist_svg_export_checklist_vi.md`
- `docs\visual_fidelity_mvp_vi.md`
- `docs\maya_mcp_sandbox_workflow_closeout_vi.md`
- `launchers\README_LAUNCHERS_VI.md`
