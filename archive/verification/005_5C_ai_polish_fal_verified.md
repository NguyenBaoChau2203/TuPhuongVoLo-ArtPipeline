# Xác minh 005.5C-R - AI polish preview fal

> Phase: 005.5C-R
> Base commit: `8b05d10 feat: add optional fal AI polish preview provider`
> Ngày xác minh: 2026-06-02
> Nhánh: `workflow/maya-first-artist-pipeline`

## Kết luận

Phase 005.5C optional fal provider đã được xác minh ở chế độ an toàn. CLI `ai_polish_preview.py` hỗ trợ provider `mock` và provider `fal`; provider `fal` vẫn là bước tham khảo tùy chọn, không phải dependency của Maya-first pipeline.

Không có external API call nào được thực hiện trong lần xác minh này. `fal-client` không được cài thêm và không trở thành dependency bắt buộc. Không có secret, `.env`, generated PNG/report, Feature 006, SVG parser, Maya generation, render logic, prop placement, hoặc manifest logic nào được thêm/sửa trong checkpoint này.

Maya-first pipeline vẫn là source of truth:

```text
Illustrator -> clean SVG -> geometry JSON -> Maya .ma -> PNG preview -> artist polish
```

AI polish preview chỉ là reference/concept tùy chọn sau PNG preview.

## Trạng thái git trước xác minh

`git status --short`:

```text
<clean>
```

`git log --oneline -5`:

```text
8b05d10 feat: add optional fal AI polish preview provider
a92df0b docs: add AI polish mock verification checkpoint
8401056 feat: add mock AI polish preview workflow
09ee446 docs: add packaging metadata verification checkpoint
63c59bb chore: polish desktop app packaging metadata
```

## Lệnh validation đã chạy

```powershell
python scripts/python/ai_polish_preview.py --help
python scripts/python/ai_polish_preview.py --version
python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png
python scripts/python/ai_polish_preview.py --dry-run --provider fal --input tests/in/sample_preview.png --model fal-ai/flux-pro/kontext
python scripts/python/ai_polish_preview.py --provider fal --input tests/in/sample_preview.png --skip-on-missing-config
python -m compileall scripts/python/ai_polish_preview.py
pytest tests/ -v --ignore=tests/tmp
```

## Kết quả CLI

`python scripts/python/ai_polish_preview.py --help` chạy thành công, exit code 0. Help hiển thị các option chính:

- `--provider {mock,fal}`
- `--model MODEL`
- `--timeout-seconds TIMEOUT_SECONDS`
- `--skip-on-missing-config`
- `--prompt`
- `--prompt-preset {tropical-island-room}`
- `--dry-run`
- `--version`

`python scripts/python/ai_polish_preview.py --version` chạy thành công, exit code 0:

```text
ai_polish_preview 0.5.5C
```

Mock dry-run chạy thành công, exit code 0:

```powershell
python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png
```

Kết quả chính:

```text
Provider: mock
Input PNG: D:\TuPhuongVoLo-ArtPipeline\tests\in\sample_preview.png
Output PNG dự kiến: D:\TuPhuongVoLo-ArtPipeline\outputs\ai_preview\sample_preview_v001_mock_ai_preview.png
Report JSON dự kiến: D:\TuPhuongVoLo-ArtPipeline\outputs\ai_preview\sample_preview_v001_mock_ai_preview_report.json
Mock-only local preview. No external API was called; no API key, secret, or internet access was used.
```

fal dry-run chạy thành công, exit code 0:

```powershell
python scripts/python/ai_polish_preview.py --dry-run --provider fal --input tests/in/sample_preview.png --model fal-ai/flux-pro/kontext
```

Kết quả chính:

```text
Provider: fal
Model: fal-ai/flux-pro/kontext
Timeout giây: 120
Output PNG dự kiến: D:\TuPhuongVoLo-ArtPipeline\outputs\ai_preview\sample_preview_v001_fal_ai_preview.png
Report JSON dự kiến: D:\TuPhuongVoLo-ArtPipeline\outputs\ai_preview\sample_preview_v001_fal_ai_preview_report.json
```

Dry-run không tạo PNG/report và không gọi API.

## Hành vi thiếu FAL_KEY

Lệnh sau được chạy trong process đã remove `FAL_KEY`:

```powershell
Remove-Item Env:FAL_KEY -ErrorAction SilentlyContinue
python scripts/python/ai_polish_preview.py --provider fal --input tests/in/sample_preview.png --skip-on-missing-config
```

Kết quả: exit code 0 và in thông báo tiếng Việt:

```text
Bỏ qua AI polish preview fal: chưa có biến môi trường FAL_KEY. Output Maya pipeline hiện tại vẫn hợp lệ.
```

Lệnh này tạo một JSON report skipped trong `outputs/ai_preview/`; report được xóa sau validation và không được commit.

Hành vi đã xác nhận:

- Có `--skip-on-missing-config`: thiếu `FAL_KEY` được safe skip, exit 0.
- Không có `--skip-on-missing-config`: thiếu `FAL_KEY` là lỗi rõ ràng bằng tiếng Việt, exit non-zero. Hành vi này được cover bởi `tests/test_ai_polish_preview.py`.

## Provider/model direction

Provider thật tùy chọn:

```text
provider: fal
default model: fal-ai/flux-pro/kontext
```

`fal-client` chỉ là optional install khi user thật sự muốn gọi fal.ai:

```powershell
python -m pip install fal-client
```

Checkpoint này không cài `fal-client`, không thêm package này vào `requirements.txt`, và không biến nó thành dependency bắt buộc.

## Kết quả compile/test

`python -m compileall scripts/python/ai_polish_preview.py` chạy thành công, exit code 0.

`pytest tests/ -v --ignore=tests/tmp`:

```text
185 passed, 1 warning in 4.18s
```

Warning duy nhất là `PytestCacheWarning` vì không tạo được cache path trong `.pytest_cache`; warning này không liên quan tới fal provider và không làm test fail.

## Kiểm tra artifact

`outputs/ai_preview/` vẫn là output folder ignored. Generated AI preview PNG/report artifacts không được commit.

Checkpoint này chỉ thêm/cập nhật tài liệu. Không có output sinh ra từ validation được commit.

## Ranh giới an toàn đã xác nhận

- Không gọi fal.ai hoặc external API trong validation/tests.
- Không thêm API key hoặc secret.
- Không thêm `.env`.
- Không cài dependency mới.
- Không thêm required dependency cho `fal-client`.
- Không thêm generated PNG/report output.
- Không implement Feature 006 natural-language control.
- Không thêm UI/desktop app integration.
- Không sửa SVG parser.
- Không sửa Maya scene generation.
- Không sửa render logic.
- Không sửa prop placement.
- Không sửa manifest logic.

## Trạng thái sau xác minh

005.5C-R xác nhận provider `fal` đã sẵn sàng ở mức CLI tùy chọn và an toàn: mock vẫn hoạt động, fal dry-run không gọi API, thiếu cấu hình có safe-skip path, và Maya-first pipeline vẫn chạy bình thường khi không có AI, `FAL_KEY`, `fal-client`, hoặc internet.
