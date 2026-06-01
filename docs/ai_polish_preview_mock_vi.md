# AI polish preview mock 005.5B

> Trạng thái: local mock-only.
> Phạm vi: tạo bản sao PNG preview và report JSON trong `outputs/ai_preview/`.
> Không gọi API, không cần internet, không cần API key.

## Mục tiêu

Phase 005.5B thêm một workflow thử kiến trúc cho AI polish preview, nhưng chưa tích hợp AI thật. Mục tiêu là kiểm tra contract local trước: input là PNG preview, output là một PNG mock và một JSON report để họa sĩ/developer thấy luồng dự kiến.

Workflow Maya-first hiện tại vẫn hoạt động bình thường khi không có AI, không có API key và không có internet.

## Cách chạy dry-run

```powershell
python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png
```

Dry-run chỉ in kế hoạch:

- Input PNG.
- Output PNG dự kiến.
- Report JSON dự kiến.
- Provider `mock`.
- Prompt hoặc preset nếu có.

Dry-run không tạo file và không gọi API.

## Cách tạo mock preview local

```powershell
python scripts/python/ai_polish_preview.py --provider mock --input outputs/preview/ten_preview.png --prompt-preset tropical-island-room
```

Kết quả mặc định nằm trong:

```text
outputs/ai_preview/
```

File PNG mock có dạng:

```text
<ten_input>_v001_mock_ai_preview.png
```

Report JSON nằm cạnh PNG:

```text
<ten_input>_v001_mock_ai_preview_report.json
```

Nếu tên `v001` đã tồn tại, script tự chọn phiên bản kế tiếp như `v002`.

## Ý nghĩa của mock

Trong 005.5B, provider `mock` chỉ copy input PNG sang `outputs/ai_preview/`. Đây là output giả lập để kiểm tra kiến trúc, không phải ảnh AI thật.

Report JSON luôn ghi rõ:

- Input path.
- Output path.
- Provider.
- Prompt.
- Prompt preset.
- Status.
- Ghi chú rằng đây là mock-only và không có API nào được gọi.

## Ranh giới an toàn

Script không sửa input PNG.

Script không sửa:

- File `.ma`.
- SVG.
- Geometry JSON.
- Manifest.
- Render logic.
- Prop placement.
- Feature 006 natural-language control.

Script không thêm:

- API key.
- `.env`.
- Provider SDK.
- Network call.

Output mock là artifact local và không nên commit.

## Quan hệ với pipeline Maya

AI polish preview chỉ là bước tham khảo tùy chọn sau khi đã có PNG preview. Source of truth vẫn là Illustrator/SVG sạch và file Maya `.ma` có thể chỉnh sửa.

Pipeline chính:

```text
Illustrator -> clean SVG -> geometry JSON -> Maya .ma -> PNG preview -> artist polish
```

Mock AI preview tùy chọn:

```text
PNG preview -> local mock copy trong outputs/ai_preview/
```

Nếu không chạy script này, pipeline Maya vẫn chạy như cũ.
