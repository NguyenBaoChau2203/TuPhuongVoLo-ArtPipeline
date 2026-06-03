# Bàn giao desktop app Maya cho họa sĩ / dev operator

## 1. Mục tiêu bàn giao

Tài liệu này dùng để bàn giao MVP desktop app Maya-first cho họa sĩ hoặc dev
operator trên máy DCC. Mục tiêu là giúp người nhận có thể retest và sử dụng
workflow hiện tại một cách an toàn, không cần thêm feature mới.

MVP hiện tại cho phép:

- Mở desktop app từ launcher hoặc file `.exe` đã build.
- Chọn file SVG sạch đã xuất từ Illustrator.
- Bấm `Kiểm tra SVG` để chạy preflight read-only trước khi dựng Maya.
- Chạy `dry-run` trước để kiểm tra lệnh và output dự kiến.
- Chạy thật bằng Autodesk Maya thông qua `mayapy.exe`.
- Kiểm tra file `.ma` và ảnh PNG preview được tạo ra.
- Tạo AI polish preview tùy chọn từ một PNG preview đã có, bằng nút riêng trong app.
- Mở file `.ma` trong Maya để polish thủ công.
- Xem phiên bản app trong title/UI hoặc bằng `--version`: `v0.7.10 (007L)`.

Desktop app chỉ là wrapper local cho pipeline CLI đã kiểm chứng. App không thay
thế Maya, không tự parse SVG, không sửa SVG gốc. AI `fal` chỉ có thể gọi external
API khi người dùng tự chọn provider `fal`, tắt `AI dry-run`, và máy đã có cấu hình
`FAL_KEY`/`fal-client`; mặc định AI vẫn là dry-run/mock an toàn.

## 2. Yêu cầu máy chạy

- Windows 10/11.
- Python có trong `PATH`, hoặc đặt biến môi trường `TUPHUONGVOLO_PYTHON_EXE`.
- Repo local đã checkout trên máy DCC.
- Maya 2024 được cài trên máy nếu muốn chạy thật.
- Đường dẫn `mayapy.exe` đã kiểm chứng:

```text
C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
```

PyInstaller chỉ cần cho developer khi rebuild `.exe`. Nếu `.exe` đã được build
sẵn, họa sĩ không cần PyInstaller để dùng bình thường.

## 3. Cách cập nhật repo trên máy DCC

Chạy trong PowerShell:

```powershell
cd D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline
git fetch
git checkout workflow/maya-first-artist-pipeline
git pull
git log --oneline -10
```

Sau khi cập nhật, kiểm tra branch hiện tại:

```powershell
git branch --show-current
```

Kết quả phải là:

```text
workflow/maya-first-artist-pipeline
```

## 4. Cách mở app

Cách ưu tiên cho họa sĩ:

```powershell
launchers\09_artist_desktop_app.bat
```

Nếu dùng file `.exe` đã build:

```powershell
dist\TuPhuongVoLo_MayaArtistApp.exe
```

Nếu `.exe` được chạy từ nơi khác ngoài repo, đặt repo root trước:

```powershell
set TUPHUONGVOLO_REPO_ROOT=D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline
```

Nếu máy không nhận `python` trong `PATH`, đặt Python rõ ràng:

```powershell
set TUPHUONGVOLO_PYTHON_EXE=C:\Path\To\python.exe
```

## 5. Quy trình dùng an toàn

1. Mở app.
2. Chọn SVG sạch, ví dụ `tests\in\illustrator_prop_markers.svg` khi retest.
3. Nhập tên phòng, ví dụ `phong_kho`.
4. Bấm `Kiểm tra SVG` và đọc log preflight.
5. Bật `Render PNG preview` nếu muốn tạo ảnh kiểm tra nhanh.
6. Kiểm tra repo root và command preview trong app.
7. Bấm `Chạy dry-run` và đọc log.
8. Nếu dry-run trả exit code 0 và lệnh đúng, kiểm tra đường dẫn `mayapy.exe`.
9. Bấm `Chạy Maya thật` để tạo `.ma` và PNG preview.
10. Mở `outputs\maya\` và `outputs\preview\`.
11. Mở file `.ma` trong Maya để kiểm tra Outliner và polish thủ công.
12. Nếu cần ảnh AI reference, chọn PNG preview trong khu vực AI, giữ `AI dry-run`
    cho lần đầu, rồi bấm `Tạo AI polish preview`.

Preflight không sửa SVG. Dry-run không cần Maya và không tạo scene thật. Chạy
thật cần dry-run thành công cho đúng settings hiện tại và cần `mayapy.exe` hợp lệ.
AI preview không tự chạy sau Maya; đây là workflow riêng và output nằm trong
`outputs\ai_preview\`.

## 6. Checklist retest nhanh trên máy DCC

Dùng checklist này khi bàn giao hoặc xác nhận lại build `.exe`:

- [ ] Repo đang ở branch `workflow/maya-first-artist-pipeline`.
- [ ] App hoặc `.exe` mở được.
- [ ] App hiển thị phiên bản `v0.7.10 (007L)`.
- [ ] App hiển thị repo root.
- [ ] App hiển thị command preview.
- [ ] SVG input là file SVG sạch.
- [ ] Room name không trống, ví dụ `phong_kho`.
- [ ] Nút `Kiểm tra SVG` chạy preflight và ghi report/log.
- [ ] Dry-run chạy trước và trả exit code 0.
- [ ] App không cho chạy Maya thật nếu settings hiện tại chưa có dry-run thành công.
- [ ] Chạy thật dùng đúng `mayapy.exe`.
- [ ] Actual Maya run trả exit code 0.
- [ ] File `.ma` được tạo trong `outputs\maya\`.
- [ ] PNG preview được tạo trong `outputs\preview\` nếu bật preview.
- [ ] Khu vực AI có thể dry-run với provider `mock` từ một PNG preview có sẵn.
- [ ] Nút AI và nút Maya hoạt động độc lập; AI không tự chạy sau Maya.
- [ ] File `.ma` mở được trong Maya.
- [ ] Outliner có cấu trúc blockout mong đợi.

## 7. Outliner mong đợi khi retest `phong_kho`

Với input đã kiểm chứng `tests\in\illustrator_prop_markers.svg` và room
`phong_kho`, Maya Outliner nên có:

- `GRP_phong_kho_blockout`
- `walls`
- `wall_01`
- `wall_02`
- `wall_03`
- `wall_04`
- `props`
- `prop_shelf_unit_01`
- `prop_wooden_crate_01`
- `lights`
- `cam_phong_kho_iso1`
- `key_light`
- `ambient_light`
- `floor_blockout`

Các Maya default set như `defaultLightSet` hoặc `defaultObjectSet` có thể xuất
hiện thêm. Đây là mặc định bình thường của Maya, không phải lỗi pipeline.

## 8. Ghi chú đóng gói / release local

Developer có thể kiểm tra lệnh package bằng:

```powershell
python scripts\python\package_artist_app.py --dry-run
```

Dry-run sẽ in phiên bản app và lệnh PyInstaller dự kiến. Có thể kiểm tra riêng
phiên bản bằng:

```powershell
python scripts\python\artist_desktop_app.py --version
python scripts\python\package_artist_app.py --version
```

Hoặc dùng launcher:

```powershell
launchers\10_package_artist_app.bat
```

Nếu máy dev đã có PyInstaller và cần rebuild `.exe`:

```powershell
python scripts\python\package_artist_app.py --clean-output --build
```

File `.exe` dự kiến:

```text
dist\TuPhuongVoLo_MayaArtistApp.exe
```

`.exe` hiện tại vẫn là wrapper local. Nó không bundle toàn bộ repo, không bundle
Maya, không bundle `mayapy.exe`, và vẫn cần Python bên ngoài để gọi pipeline.

## 9. Không commit các file sinh ra

Không commit các artifact local sau:

- `build\`
- `dist\`
- `*.exe`
- `*.spec`
- `outputs\maya\*.ma`
- `outputs\preview\*.png`
- `outputs\ai_preview\*.png`
- `outputs\ai_preview\*.json`
- `outputs\tmp\*`
- `outputs\reports\*.json`

Nếu cần lưu output làm fixture/test case, phải làm riêng và có lý do rõ ràng.

## 10. Khi gặp lỗi thường gặp

| Vấn đề | Cách xử lý |
| --- | --- |
| App báo không tìm thấy repo root | Chạy app từ thư mục repo hoặc đặt `TUPHUONGVOLO_REPO_ROOT`. |
| `.exe` báo không tìm thấy Python | Cài Python vào `PATH` hoặc đặt `TUPHUONGVOLO_PYTHON_EXE`. |
| Preflight báo `FATAL` | Kiểm tra file có tồn tại, XML hợp lệ, root là `<svg>`, và export lại từ Illustrator nếu cần. |
| Dry-run chạy được nhưng chạy thật lỗi | Kiểm tra lại đường dẫn `mayapy.exe`. |
| Không có PNG preview | Kiểm tra đã bật `Render PNG preview` và đọc log Maya render. |
| File `.ma` mở được nhưng hình còn đơn giản | Đây là blockout kỹ thuật, chưa phải final art; họa sĩ polish tiếp trong Maya. |

## 11. Phạm vi chưa làm / giới hạn

Các phần sau chưa thuộc MVP bàn giao này hoặc vẫn là giới hạn an toàn:

- Feature 006 natural-language control.
- AI polish preview hiện đã có nút riêng trong desktop app ở phase 007G, nhưng vẫn là reference-only, không thay đổi Maya pipeline, và chỉ gọi fal.ai khi user tự chọn provider `fal` trong workflow AI.
- TencentDB-Agent-Memory integration.
- Thay đổi SVG parser.
- Thay đổi Maya scene generation.
- Tự động polish final art.

## 12. Tài liệu liên quan

- `docs\artist_svg_export_checklist_vi.md` — quy tắc marker `door_`/`window_`: preflight là nguồn kiểm tra; nếu preflight báo 0 marker thì Maya không tự tạo cửa.
- `docs\artist_workflow_cat_guide_vi.html` — sổ tay mèo con thân thiện cho họa sĩ (007H)
- `docs\desktop_app_mvp_vi.md`
- `docs\release_packaging_checklist_vi.md`
- `docs\HOW_TO_USE_FOR_ARTIST_VI.md`
- `docs\ai_polish_preview_evaluation_vi.md`
- `docs\ai_polish_preview_mock_vi.md`
- `docs\ai_polish_preview_fal_vi.md`
- `launchers\README_LAUNCHERS_VI.md`
- `docs\verification\007B_desktop_app_exe_verified.md`
- `docs\verification\007C_desktop_app_polish_verified.md`
- `docs\verification\007G_desktop_app_ai_preview_verified.md`
- `specs\007-artist-desktop-app-mvp\quickstart.md`
