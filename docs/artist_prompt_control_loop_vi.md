# Artist Prompt Control Loop 015A - hướng dẫn định hướng

Tài liệu này là điểm neo mới cho workflow thật của **Tứ Phương Vô Lộ**.
Mục tiêu không còn chỉ là:

```text
SVG -> Maya blockout
```

Mục tiêu sản phẩm là:

```text
Artist prompt
-> AI điều khiển Illustrator sandbox khi MCP khỏe
-> export SVG
-> App/CLI dựng Maya
-> Visual Fidelity pass
-> Maya sandbox
-> Artist prompt
-> Codex polish trong Maya
-> artist review / rollback
```

Đây là workflow điều khiển bằng prompt, không phải máy tự sinh final art. Illustrator và Maya vẫn là công cụ sản xuất chính. AI agent chỉ là người vận hành kỹ thuật trong sandbox, phải kiểm tra đường dẫn trước khi sửa/lưu, và họa sĩ luôn review trước khi chấp nhận kết quả.

## Trạng thái hiện tại

| Vòng lặp | Trạng thái | Ghi chú |
| --- | --- | --- |
| Illustrator Prompt Loop | Beta / đang bị chặn | Antigravity Illustrator MCP `illustrator-sandbox` vừa trả EOF khi gọi `view`, `help`, hoặc `get_system_prompt`. Dùng export SVG thủ công cho workflow hằng ngày. |
| Maya Prompt Loop | MVP-ready cho smoke test tiếp theo | Visual Fidelity 014A đã có, sandbox Maya 014C đã inspect thành công. Bước kế tiếp là 015B smoke test prompt polish trên sandbox. |

## Vòng lặp Illustrator Prompt Loop

Luồng mục tiêu sau khi MCP được sửa:

```text
Artist prompt tiếng Việt
-> Antigravity
-> Illustrator sandbox .ai
-> kiểm tra active document path
-> inspect/edit/export an toàn
-> không sửa file gốc
-> SVG sandbox
-> app/CLI Maya pipeline
```

Quy tắc:

- Chỉ mở/chỉnh `working\scene_agent_work.ai` trong sandbox.
- Không sửa file `.ai` gốc, SVG gốc, hoặc file trong thư mục nguồn của họa sĩ.
- Trước mọi edit/save/export, agent phải xác nhận active document chính là sandbox `.ai` được phép.
- Sau `doc.exportFile()`, phải kiểm tra lại active document vì Illustrator có thể chuyển sang SVG vừa export.
- Chỉ export SVG vào thư mục sandbox/export hoặc `working\`, và chỉ khi prompt cho phép rõ.
- Nếu MCP trả EOF hoặc không trả lời lệnh inspect, dừng ngay và dùng manual SVG export.

Template prompt:

```text
docs/templates/illustrator_artist_prompt_template_vi.md
```

## Vòng lặp Maya Prompt Loop

Luồng gần ổn định hơn:

```text
Artist prompt tiếng Việt
-> Codex
-> Maya sandbox working .ma
-> kiểm tra scene path
-> polish additive/guarded dưới agent group
-> save sandbox working only
-> artist review
-> rollback nếu cần
```

Quy tắc:

- Họa sĩ/operator chỉ mở `working\scene_agent_work.ma` của sandbox.
- Codex phải verify current scene path trước mọi edit/save.
- Nếu scene path không khớp allowlist, dừng và báo operator.
- Mọi thay đổi phải nằm dưới group agent được đặt tên rõ, ví dụ `GRP_agent_prompt_015B_polish_v001`.
- Ưu tiên thêm vật thể, material, light, note, camera phụ. Không xóa/merge production mesh nếu chưa được cho phép rõ.
- Chỉ save sandbox working `.ma`, không save source generated `.ma` trong `outputs\maya\`.
- Artist review bằng cách bật/tắt agent group, xem camera review, và so sánh với blockout/Visual Fidelity group.
- Rollback bằng restore script của sandbox.

Template prompt:

```text
docs/templates/maya_artist_prompt_template_vi.md
```

## Workflow ổn định cho ngày mai

1. Họa sĩ vẽ hoặc chỉnh layout trong Illustrator.
2. Nếu Illustrator MCP chưa khỏe, export SVG thủ công từ Illustrator.
3. Chạy preflight SVG bằng desktop app hoặc CLI.
4. Chạy dry-run Maya.
5. Khi dry-run ổn, chạy actual Maya build bằng `mayapy.exe`.
6. Chạy Visual Fidelity pass nếu cần scene dễ đọc hơn.
7. Tạo hoặc dùng Maya sandbox từ file `.ma` Visual Fidelity.
8. Mở sandbox `working\scene_agent_work.ma` trong Maya.
9. Dán prompt Maya đã điền cho Codex.
10. Codex kiểm tra scene path, tạo polish additive/guarded dưới agent group, rồi lưu sandbox working.
11. Họa sĩ review trong Maya.
12. Nếu không đạt, rollback bằng restore script rồi lặp lại bằng prompt mới.

Xem bản handoff ngắn tại:

```text
docs/artist_daily_workflow_vi.md
```

## Model routing khuyến nghị

| Việc cần làm | Model khuyến nghị |
| --- | --- |
| Inspect, kiểm chứng, đọc log, kiểm tra path/hash | Codex GPT-5.5 medium |
| Maya polish/write có guard trong sandbox | Codex GPT-5.5 high |
| SDD, refactor lớn, audit an toàn, kiểm tra nhiều tài liệu | Codex GPT-5.5 xhigh |
| Illustrator MCP edit/export sau khi smoke test EOF pass | Antigravity Claude Sonnet 4.6 |
| Kiến trúc hoặc audit an toàn Illustrator MCP | Antigravity Claude Opus 4.6 |
| Inspect/report nhẹ nếu muốn | Gemini models |

## Checklist an toàn bắt buộc

- Không sửa file `.ai`, `.svg`, `.ma` gốc.
- Luôn làm việc trên sandbox `working\`.
- Luôn verify active document path trong Illustrator trước edit/save/export.
- Luôn verify current scene path trong Maya trước edit/save.
- Không ghi đè input bằng output.
- Mọi thay đổi Maya phải nằm dưới agent group rõ ràng.
- Khi cần, ghi hash trước/sau cho file sandbox hoặc source snapshot để kiểm chứng rollback.
- Không commit `.ai`, `.svg`, `.ma`, `.json`, `.png`, `.zip`, report, backup, hoặc output sinh ra.
- Rollback bằng restore script của sandbox, không tự xóa/sửa file original.
- Nếu Illustrator MCP trả EOF, dừng loop Illustrator và quay về export SVG thủ công.
- Manual SVG export là fallback chính thức cho daily workflow cho tới khi MCP được repair.

## Giới hạn 015A

015A chỉ tạo spec, plan, tasks, quickstart, tài liệu, và prompt templates. Phase này không dùng Illustrator MCP, không dùng Maya commandPort, không mở Illustrator/Maya, không sửa sandbox ngoài repo, và không implement app điều phối prompt mới.
