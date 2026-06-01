# AI polish preview fal 005.5C

> Trạng thái: provider thật tùy chọn.
> Provider: `fal`
> Model mặc định: `fal-ai/flux-pro/kontext`
> Output: `outputs/ai_preview/`
> Checkpoint: `docs/verification/005_5C_ai_polish_fal_verified.md`

## Mục tiêu

Phase 005.5C thêm provider `fal` cho `scripts/python/ai_polish_preview.py`.
Đây là bước tham khảo sau khi đã có PNG preview từ Maya. Ảnh AI chỉ giúp họa
sĩ xem mood, ánh sáng, chất liệu và không thay thế SVG sạch, geometry JSON,
file Maya `.ma`, PNG preview gốc, manifest, hay polish thủ công trong Maya.

Pipeline Maya-first vẫn chạy bình thường khi không có AI, không có `FAL_KEY`,
không cài `fal-client`, hoặc không có internet.

## Cài đặt tùy chọn

Chỉ cài khi thật sự muốn gọi fal.ai:

```powershell
python -m pip install fal-client
```

Không thêm `fal-client` vào dependency bắt buộc của repo. Test và pipeline Maya
không cần package này.

## API key

Provider `fal` chỉ đọc key từ biến môi trường `FAL_KEY`.

Ví dụ trong PowerShell của máy cá nhân:

```powershell
$env:FAL_KEY = "your-fal-key"
```

Không ghi key vào code, docs, `.env`, commit, screenshot, hoặc report JSON.

## Chạy dry-run trước

Dry-run không tạo output và không gọi API:

```powershell
python scripts/python/ai_polish_preview.py `
  --dry-run `
  --provider fal `
  --input tests/in/sample_preview.png `
  --model fal-ai/flux-pro/kontext
```

## Chạy provider fal

Sau khi đã có `FAL_KEY` và đã cài `fal-client`, chạy:

```powershell
python scripts/python/ai_polish_preview.py `
  --provider fal `
  --input outputs/preview/ten_preview.png `
  --prompt-preset tropical-island-room
```

Có thể override model:

```powershell
python scripts/python/ai_polish_preview.py `
  --provider fal `
  --input outputs/preview/ten_preview.png `
  --model fal-ai/flux-pro/kontext `
  --timeout-seconds 120 `
  --prompt "Cải thiện ánh sáng ẩm, đèn lồng cũ, mood đảo nhiệt đới bí ẩn"
```

## Khi thiếu cấu hình

Nếu thiếu `FAL_KEY`, có thể cho script bỏ qua AI mà không làm fail workflow:

```powershell
python scripts/python/ai_polish_preview.py `
  --provider fal `
  --input tests/in/sample_preview.png `
  --skip-on-missing-config
```

Lúc này script exit `0`, ghi rõ bằng tiếng Việt rằng AI polish đã bị bỏ qua, và
pipeline Maya vẫn hợp lệ.

Nếu có `FAL_KEY` nhưng thiếu `fal-client`, script báo lỗi rõ ràng và hướng dẫn:

```text
python -m pip install fal-client
```

## Output

Ảnh AI reference nằm trong:

```text
outputs/ai_preview/
```

Tên file PNG:

```text
<ten_input>_v001_fal_ai_preview.png
```

Report JSON:

```text
<ten_input>_v001_fal_ai_preview_report.json
```

Nếu `v001` đã tồn tại, script tự chọn `v002`, `v003`, ...

Report JSON ghi provider, model, input/output path, prompt, preset, trạng thái,
`external_api_called`, `skipped`, và `error_type` nếu có lỗi hoặc bị bỏ qua.
Report không ghi API key hay secret.

## Prompt preset

Preset `tropical-island-room` hướng model theo phong cách:

- Phiêu lưu sinh tồn ở quần đảo nhiệt đới bí ẩn.
- Concept preview môi trường game indie stylized.
- Giữ layout isometric và các object chính.
- Cải thiện ánh sáng, mood, vật liệu và không khí.
- Không thêm text, watermark, UI, logo, hoặc nhân vật nếu ảnh gốc không có.

## Ranh giới an toàn

Provider `fal` không sửa:

- SVG.
- Geometry JSON.
- Maya `.ma`.
- Manifest.
- Render logic.
- Prop placement.
- Source assets trong `assets/` hoặc `drops/`.

Feature 006 natural-language control vẫn deferred và tách biệt. Phase này không
thêm agent command, MCP server, hay natural-language automation.

## Ghi chú kỹ thuật

Code dùng lazy import để `import ai_polish_preview` không lỗi khi chưa cài
`fal-client`. Dry-run và test không gọi external API. API thật chỉ chạy khi
người dùng chọn `--provider fal`, không dùng `--dry-run`, có `FAL_KEY`, và có
`fal-client`.

Tài liệu fal tham khảo:

- `https://fal.ai/docs/clients/python`
- `https://fal.ai/docs/model-api-reference/image-generation-api/flux-pro-kontext`
