# Desktop App MVP cho họa sĩ

> **Phiên bản hiện tại**: `v0.7.10 (007L)`
> **Giao diện hiện tại**: Desktop App (Tkinter) chạy local. Dự án đã bỏ kế hoạch phát triển local web UI trong ngắn hạn để tập trung hoàn toàn vào ứng dụng desktop.
> **Quy trình sản xuất chính (Maya-first)**: Illustrator SVG -> dry-run -> Dựng Maya .ma thật -> Họa sĩ polish thủ công trong Maya. Quy trình này hoạt động hoàn toàn local, ngoại tuyến và **không yêu cầu bất kỳ API AI trả phí nào (không cần API Key, không cần fal.ai, OpenAI, Gemini hay ComfyUI)**. Tính năng AI Preview chỉ là ảnh tham khảo tùy chọn, không thay thế file `.ma` và hiện đang tạm hoãn vì chi phí API.

## Mục đích

Desktop app MVP là cửa sổ local nhỏ để chạy pipeline Maya-first đã được kiểm
chứng. App giúp họa sĩ chọn SVG, kiểm tra SVG preflight, nhập tên phòng, chạy
dry-run trước, chỉ chạy Maya thật sau khi dry-run đúng, bật/tắt PNG preview,
nhập đường dẫn `mayapy.exe`, xem log, và mở nhanh các thư mục output.

App chỉ bọc script CLI hiện có:

```powershell
python scripts/python/build_maya_room.py
```

App không thay thế Maya, không parse SVG trực tiếp, không tạo geometry riêng, và
không sửa file SVG nguồn. Pipeline CLI vẫn là source of truth.

## Cập nhật 007L: luồng hướng dẫn một nút theo từng bước

Phase 007L làm rõ luồng an toàn cho họa sĩ không rành command line:

1. `Kiểm tra SVG`: gọi `scripts/python/svg_preflight_check.py` để kiểm tra file SVG read-only.
2. `Chạy dry-run`: ép app chạy `build_maya_room.py --dry-run` để xem kế hoạch trước.
3. `Chạy Maya thật`: chỉ nên dùng sau khi dry-run thành công cho đúng SVG, phòng, output và render settings hiện tại.
4. Mở `outputs/maya`, `outputs/preview`, và `outputs/reports` để kiểm tra `.ma`, PNG preview, và report.

App ghi nhớ dry-run thành công theo SVG/phòng/output/render hiện tại. Nếu đổi
settings, app sẽ yêu cầu chạy dry-run lại trước khi chạy Maya thật. Các checkbox
và nút manual `Chạy pipeline` vẫn còn cho người dùng nâng cao, nhưng luồng
khuyến nghị trong UI là `Kiểm tra SVG -> Chạy dry-run -> Chạy Maya thật`.

## Cập nhật 007C: kiểm tra và trạng thái rõ hơn

Phase 007C polish thêm kiểm tra trước khi chạy để họa sĩ thấy lỗi dễ hiểu hơn:

- Chưa chọn SVG, SVG không tồn tại, tên phòng trống, hoặc output trống.
- Không tìm thấy repo root hoặc `scripts/python/build_maya_room.py`.
- Chạy thật nhưng chưa có `mayapy.exe` hợp lệ.
- File `.exe` đóng gói không tìm thấy Python bên ngoài để gọi pipeline.

App hiển thị repo root đang dùng, lệnh dự kiến, trạng thái `Sẵn sàng`,
`Đang chạy...`, `Hoàn tất: mã 0`, hoặc `Lỗi: mã <code>`, và luôn ghi exit code
vào log. Nút `Chạy pipeline` bị khóa trong lúc subprocess đang chạy và được mở
lại sau khi kết thúc.

Các nút tiện ích gồm `Xóa log`, `Copy lệnh`, mở repo, mở `outputs/maya`,
`outputs/preview`, và `outputs/reports`. Các thư mục output này có thể được tạo
an toàn khi bấm mở; app không tạo hoặc sửa thư mục source asset.

## Cập nhật 007E: phiên bản app và checklist packaging

Phase 007E thêm metadata phiên bản nhỏ cho app desktop:

- App title và nhãn trong UI hiển thị `TuPhuongVoLo Maya Artist App v0.7.7 (007I)`.
- CLI hỗ trợ kiểm tra phiên bản:

```powershell
python scripts/python/artist_desktop_app.py --version
```

- Packaging helper in phiên bản app trong dry-run và cũng hỗ trợ:

```powershell
python scripts/python/package_artist_app.py --version
```

Checklist release/packaging tiếng Việt nằm ở:

```text
docs/release_packaging_checklist_vi.md
```

Checkpoint kiểm chứng 007E-R nằm ở:

```text
docs/verification/007E_packaging_metadata_verified.md
```

## Cập nhật 007G: AI polish preview tùy chọn trong desktop app

Phase 007G thêm một khu vực riêng trong app để tạo AI polish preview từ một ảnh PNG
preview đã có, thường là ảnh trong `outputs/preview/`. AI không tự chạy sau khi bấm
`Chạy pipeline`; người dùng phải tự chọn PNG và bấm `Tạo AI polish preview`.

Các trường chính trong khu vực AI:

- `PNG preview`: ảnh `.png` đầu vào.
- `Provider`: `mock` hoặc `fal`.
- `Model`: mặc định `fal-ai/flux-pro/kontext`.
- `Prompt preset`: mặc định `tropical-island-room`.
- `Prompt thêm`: nội dung tùy chọn, chỉ gửi khi có nhập.
- `Bỏ qua nếu thiếu cấu hình AI`: mặc định bật, giúp provider `fal` skip an toàn khi thiếu `FAL_KEY`.
- `AI dry-run`: mặc định bật để chỉ in kế hoạch, không tạo output và không gọi API.

Provider `mock` dùng được local, không cần API key, không cần internet, không cần
`fal-client`. Provider `fal` chỉ là tùy chọn; nếu muốn chạy thật thì máy cần cài
`fal-client` và đặt biến môi trường `FAL_KEY`. Desktop app không import `fal-client`
và không đọc/cất API key; app chỉ gọi CLI:

```powershell
python scripts/python/ai_polish_preview.py
```

Output AI nằm trong:

```text
outputs/ai_preview/
```

Ảnh AI chỉ là reference để họa sĩ xem mood, ánh sáng, vật liệu. File Maya `.ma` vẫn
là nguồn chính để polish cuối cùng. Phase này không sửa SVG, geometry JSON, Maya
scene generation, render logic, manifest, source assets, hay Feature 006
natural-language control.

Checkpoint kiểm chứng 007G-R nằm ở:

```text
docs/verification/007G_desktop_app_ai_preview_verified.md
```

Phase 007H thêm hướng dẫn web thân thiện cho họa sĩ (sổ tay mèo con). Xem:

```text
docs/artist_workflow_cat_guide_vi.html
```

## Cập nhật 007I: nút hướng dẫn và template marker

Phase 007I gom layout desktop app thành các khung rõ bước hơn:

- `Step 1: Chọn SVG và phòng`
- `Step 2: Maya output / render preview`
- `Step 3: Hướng dẫn & template`
- `Step 4: AI polish preview tùy chọn`
- `Log / trạng thái`

Khu vực `Step 3` có các nút mở nhanh:

- `Mở hướng dẫn` mở `docs/artist_workflow_cat_guide_vi.html`.
- `Mở SVG mẫu marker` mở `assets/2d/templates/illustrator_prop_marker_template.svg`.
- `Mở thư mục template` mở `assets/2d/templates/`.
- `Copy đường dẫn SVG mẫu` copy đường dẫn template vào clipboard.

Guide HTML là nguồn hướng dẫn chính cho prop marker; Markdown chỉ nên link tới guide và template, không lặp lại toàn bộ taxonomy.

## Cập nhật 007J: giao diện mèo thân thiện

Phase 007J đánh bóng giao diện desktop app bằng bảng màu pastel ấm và phong
cách mèo con, chỉ dùng `ttk.Style` có sẵn trong Tkinter — **không thêm thư
viện, font, CDN, ảnh nhị phân, hay web UI**.

Thay đổi giao diện:

- Bảng màu ấm: nền kem/đào nhạt, text nâu đậm, accent cam/terracotta, nút phụ
  hồng phấn, nhãn gợi ý màu xanh sage muted.
- Header mèo ở đầu app: `🐱 Tứ Phương Vô Lộ — Maya Artist App` cùng subtitle
  và gợi ý quy trình.
- Tiêu đề section thân thiện hơn:
  - `🐾 Step 1: Chọn bản vẽ SVG`
  - `🏠 Step 2: Dựng Maya blockout`
  - `📖 Step 3: Hướng dẫn & SVG mẫu`
  - `✨ Step 4: AI polish preview tùy chọn`
  - `📋 Log / trạng thái`
- Nhãn gợi ý nhỏ dưới mỗi step nhắc nhở họa sĩ.
- Nút `Chạy pipeline` và `Tạo AI polish preview` nổi bật hơn (`Primary.TButton`).
- Nút `Mở hướng dẫn` và `Mở SVG mẫu marker` dùng `Accent.TButton`.
- Nút tiện ích còn lại dùng `Secondary.TButton`.
- Phiên bản sau 007L: `TuPhuongVoLo Maya Artist App v0.7.10 (007L)`.

HTML guide vẫn là nguồn hướng dẫn chính cho họa sĩ. App không thay đổi pipeline
Maya, SVG parser, AI provider, Feature 006, local web UI, hay manifest.

## Cách chạy từ source

```powershell
python scripts/python/artist_desktop_app.py
```

## Cách chạy bằng launcher

```powershell
launchers/09_artist_desktop_app.bat
```

## Quy trình khuyến nghị

1. Chọn file SVG sạch.
2. Bấm `Kiểm tra SVG` và đọc kết quả preflight trong log.
3. Nhập tên phòng, ví dụ `phong_kho`.
4. Bật `Render PNG preview` nếu cần ảnh kiểm tra nhanh.
5. Bấm `Chạy dry-run` và đọc log trong app.
6. Nếu dry-run đúng, kiểm tra đường dẫn `mayapy.exe`, rồi bấm `Chạy Maya thật`.
7. Mở `outputs/maya` và `outputs/preview` để kiểm tra `.ma` và PNG preview.
8. Nếu cần AI reference, chọn PNG preview đã có trong khu vực AI, giữ `AI dry-run` cho lần đầu, rồi bấm `Tạo AI polish preview`.

## Thư mục có thể mở từ app

- `outputs/maya/`
- `outputs/preview/`
- `outputs/reports/`
- `outputs/ai_preview/`
- `assets/2d/templates/`
- Thư mục repo

## Đóng gói .exe cho máy dev

Phase 007B thêm workflow đóng gói local bằng PyInstaller. PyInstaller là công cụ
dev-only, không phải dependency runtime của artist pipeline và không được cài tự
động.

Chạy dry-run để xem lệnh package:

```powershell
python scripts/python/package_artist_app.py --dry-run
```

Dry-run sẽ in phiên bản app hiện tại và lệnh PyInstaller dự kiến. Nếu chưa cài
PyInstaller, dry-run vẫn có thể dùng để kiểm tra metadata/lệnh dự kiến; chỉ
`--build` mới cần PyInstaller thật.

Hoặc dùng launcher:

```powershell
launchers/10_package_artist_app.bat
```

Nếu máy dev đã cài PyInstaller, có thể build thật:

```powershell
python scripts/python/package_artist_app.py --build
```

Output dự kiến:

```text
dist/TuPhuongVoLo_MayaArtistApp.exe
```

## Kiểm chứng 007B-R trên máy artist/DCC

File `.exe` đóng gói `dist/TuPhuongVoLo_MayaArtistApp.exe` đã được kiểm chứng
trên máy artist/DCC với Maya 2024. Kết quả: app mở được, dry-run trả exit code
0, chạy thật Maya trả exit code 0, sinh file `.ma` trong `outputs/maya/`, sinh
PNG preview trong `outputs/preview/`, và file `.ma` mở được trong Maya.

Chi tiết checkpoint nằm ở:

```text
docs/verification/007B_desktop_app_exe_verified.md
```

## Kiểm chứng 007C-R sau polish UX/reliability

Sau polish 007C, file `.exe` đã được build lại và kiểm chứng trên máy
artist/DCC. App hiển thị repo root, hiển thị lệnh dự kiến, dry-run trả exit
code 0, chạy thật Maya trả exit code 0, sinh PNG preview, và file `.ma` mở
được trong Maya với Outliner đúng cấu trúc blockout.

Chi tiết checkpoint nằm ở:

```text
docs/verification/007C_desktop_app_polish_verified.md
```

Checklist bàn giao/retest cho họa sĩ và dev operator nằm ở:

```text
docs/artist_handoff_desktop_app_vi.md
```

Khi chạy file `.exe`, app vẫn cần tìm thấy repo local để gọi script pipeline:

```powershell
scripts/python/build_maya_room.py
```

Nên chạy `.exe` từ thư mục repo hoặc đặt biến môi trường nếu cần chạy từ nơi khác:

```powershell
set TUPHUONGVOLO_REPO_ROOT=D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline
```

File `.exe` không tự bundle Python pipeline. Máy chạy `.exe` cần có Python trong `PATH`,
hoặc đặt rõ Python bằng biến môi trường:

```powershell
set TUPHUONGVOLO_PYTHON_EXE=C:\Path\To\python.exe
```

Lưu ý: `.exe` MVP này vẫn là wrapper local cho repo/pipeline hiện có. Nó không
bundle toàn bộ repo, không bundle Maya, và không bundle `mayapy.exe`. Không commit
`build/`, `dist/`, file `.spec` sinh tự động, file `.exe`, hoặc output sinh ra
trong `outputs/maya/`, `outputs/preview/`, `outputs/tmp/`, `outputs/reports/`.
