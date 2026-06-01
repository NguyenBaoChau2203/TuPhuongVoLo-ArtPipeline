# 007G-R - Kiểm chứng desktop app AI polish preview

## Thông tin checkpoint

- Phase: `007G-R`
- Base commit: `fc036c0 feat: add desktop app AI polish preview controls`
- Branch: `workflow/maya-first-artist-pipeline`
- Desktop app version: `TuPhuongVoLo Maya Artist App v0.7.6 (007G)`
- AI CLI: `scripts/python/ai_polish_preview.py`
- Ngày kiểm chứng: 2026-06-02

## Kết quả kiểm chứng

| Lệnh | Kết quả |
| --- | --- |
| `git status` | Worktree sạch trước khi checkpoint; `outputs/ai_preview/` chỉ xuất hiện dưới dạng ignored output sau validation. |
| `git log --oneline -5` | HEAD là `fc036c0`, trước đó là `31b9610`, `8b05d10`, `a92df0b`, `8401056`. |
| `python scripts/python/artist_desktop_app.py --help` | Exit code `0`; CLI help mở được. |
| `python scripts/python/artist_desktop_app.py --version` | Exit code `0`; in `TuPhuongVoLo Maya Artist App v0.7.6 (007G)`. |
| `python scripts/python/ai_polish_preview.py --help` | Exit code `0`; CLI help mở được, có provider `mock` và `fal`. |
| `python scripts/python/ai_polish_preview.py --version` | Exit code `0`; in `ai_polish_preview 0.5.5C`. |
| `python scripts/python/ai_polish_preview.py --dry-run --provider mock --input tests/in/sample_preview.png` | Exit code `0`; chỉ lập kế hoạch, không tạo output và không gọi API. |
| `python scripts/python/ai_polish_preview.py --dry-run --provider fal --input tests/in/sample_preview.png --model fal-ai/flux-pro/kontext` | Exit code `0`; chỉ lập kế hoạch provider `fal`, không gọi API. |
| `python scripts/python/ai_polish_preview.py --provider fal --input tests/in/sample_preview.png --skip-on-missing-config` với `FAL_KEY` unset | Exit code `0`; bỏ qua an toàn vì thiếu `FAL_KEY`, ghi report ignored trong `outputs/ai_preview/`. |
| `python -m compileall scripts/python/artist_desktop_app.py scripts/python/ai_polish_preview.py` | Exit code `0`; compile thành công. |
| `pytest tests/ -v --ignore=tests/tmp` | `192 passed`; có cảnh báo pytest cache permission của Windows, không ảnh hưởng kết quả test. |

## Xác nhận an toàn

- AI preview UI là tùy chọn và nằm riêng với workflow chạy Maya.
- AI không tự chạy sau khi Maya generation kết thúc.
- Provider `mock` hoạt động không cần API key, không cần internet, không cần `fal-client`.
- Provider `fal` vẫn dùng optional `fal-client` và biến môi trường `FAL_KEY` khi chạy thật.
- Thiếu `FAL_KEY` với `--skip-on-missing-config` là safe skip, exit `0`.
- Không có external API call nào được thực hiện trong validation checkpoint này.
- Không cài `fal-client`; dependency này vẫn chỉ được document là optional.
- Không thêm secrets, `.env`, API key, hoặc generated output vào commit.
- `outputs/ai_preview/` vẫn ignored/uncommitted.
- Maya pipeline vẫn là source of truth và chạy được không cần AI.
- Workflow Maya và workflow AI preview vẫn độc lập.
- Không thay đổi SVG parser, Maya scene generation, render logic, prop placement, hoặc manifest logic.
- Feature 006 natural-language control vẫn deferred.
