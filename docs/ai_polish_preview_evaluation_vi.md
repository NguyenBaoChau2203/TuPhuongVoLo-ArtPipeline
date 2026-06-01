# Đánh giá AI polish preview 005.5A

> Trạng thái: Evaluation complete, implementation deferred.
> Phạm vi: Chỉ tài liệu và đánh giá kiến trúc. Không tích hợp API, không thêm dependency, không tạo output AI.

## 1. Mục tiêu

AI polish preview là một bước tùy chọn có thể xem xét trong tương lai. Ý tưởng là lấy ảnh PNG preview đã được Maya tạo ra từ scene blockout, rồi gửi ảnh đó vào một mô hình image-to-image để tạo ảnh concept/reference đẹp hơn cho họa sĩ tham khảo.

Bước này không được thay thế:

- File Illustrator nguồn.
- Clean SVG.
- Geometry JSON.
- File Maya `.ma`.
- Công đoạn polish thủ công của họa sĩ.

Mục tiêu của 005.5A chỉ là đánh giá lợi ích, rủi ro, chính sách an toàn và ranh giới kiến trúc trước khi quyết định có làm prototype hay không.

## 2. Vị trí trong pipeline tương lai

Pipeline đã kiểm chứng hiện tại:

```text
Illustrator
  -> clean SVG
  -> Python geometry JSON
  -> Maya .ma blockout
  -> PNG preview
  -> họa sĩ mở .ma trong Maya và polish thủ công
```

Bước tùy chọn có thể nghiên cứu sau:

```text
PNG preview
  -> AI polish preview image
  -> ảnh tham khảo cho họa sĩ
```

Ranh giới quan trọng:

- AI output chỉ là reference/concept.
- AI output không trở thành source of truth.
- File `.ma` vẫn là artifact production có thể chỉnh sửa.
- Clean SVG vẫn là source of truth 2D.
- Pipeline core không phụ thuộc vào AI polish preview.

## 3. Candidate providers / models để đánh giá sau

Các lựa chọn có thể đánh giá ở phase sau, chỉ ở mức high-level:

- FLUX.1 Kontext hoặc mô hình image-to-image tương tự cho style polish từ PNG preview.
- fal.ai như một hướng hosted API có thể thử nghiệm nếu được duyệt.
- Các provider image-to-image khác để so sánh về chất lượng, chi phí, quyền riêng tư và điều khoản sử dụng.

Tài liệu này không bao gồm API key, SDK provider, sample code chạy được, endpoint thật, hay bất kỳ lời gọi API nào.

## 4. Possible future input/output contract

Input tương lai đề xuất:

- `outputs/preview/*.png`
- Optional style prompt.
- Optional scene metadata.
- Optional room name.

Output tương lai đề xuất:

- `outputs/ai_preview/*.png`
- `outputs/reports/ai_polish_report.json`

Các path trên chỉ là đề xuất cho thiết kế sau. Phase 005.5A không tạo folder mới, không tạo ảnh AI, không tạo report AI, và không cập nhật manifest.

## 5. Safety and privacy policy

Nếu một phase sau thử nghiệm external AI service, chính sách tối thiểu phải là:

- Không commit API key vào repo.
- Không commit `.env`.
- Không ghi secrets trong prompt, log, hoặc report.
- Không upload file `.ai` gốc lên AI service.
- Không upload raw/private artist files nếu chưa có sự đồng ý rõ ràng.
- Chỉ cân nhắc upload PNG preview đã được pipeline tạo ra.
- User/operator phải approve rõ ràng trước mọi external API usage.
- Phải review chi phí và rate limit của external service trước khi dùng.
- Phải review licensing/usage terms của ảnh AI trước khi dùng trong production.

Repository docs vẫn là source of truth. Bất kỳ output AI nào cũng chỉ được xem là artifact tham khảo, không phải dữ liệu production bắt buộc.

## 6. Artifact policy

Nếu AI polish được làm ở phase sau, output mặc định nên bị ignore:

- `outputs/ai_preview/`
- AI reports nếu không được chủ động thêm làm fixture.
- Logs có chứa prompt hoặc API metadata.

Repo hiện đã ignore rộng `outputs/reports/*`, nên report như `outputs/reports/ai_polish_*.json` mặc định không nên bị commit. `.gitignore` chỉ cần bổ sung path AI preview nếu chưa có ignore rule phù hợp.

Không commit generated image, prompt log, API response raw, token usage report, secret, `.env`, hoặc provider cache.

## 7. Risk analysis

Rủi ro chính:

- AI result có thể hallucinate geometry hoặc thêm chi tiết không có trong scene.
- AI result có thể không khớp với Maya scene có thể chỉnh sửa.
- AI result có thể làm họa sĩ hiểu nhầm nếu bị xem như final.
- External API có thể làm lộ private art nếu dùng không cẩn thận.
- Chi phí có thể tăng nhanh khi generate nhiều lần.
- Provider/model behavior có thể thay đổi theo thời gian.
- Prompt logs có thể vô tình chứa thông tin nhạy cảm.
- AI polish có thể làm lệch trọng tâm khỏi Maya-first workflow đã ổn định.

## 8. Recommended guardrails

Nếu tiếp tục nghiên cứu, guardrails nên là:

- Disabled by default.
- Opt-in only.
- Tách khỏi core pipeline.
- Có dry-run/planning mode trước.
- UI/docs phải cảnh báo rõ đây chỉ là reference.
- Không bao giờ overwrite `.ma` hoặc PNG preview gốc.
- Không bao giờ sửa source SVG hoặc artist files.
- Chỉ lưu output vào folder riêng.
- Chỉ record prompt/model/settings khi an toàn.
- Hỗ trợ xóa local AI outputs.
- Không tự động update manifest trừ khi phase thiết kế tương lai quyết định rõ.

## 9. Proposed future phases

Các phase tương lai có thể là:

- 005.5B: local mock interface, không external API.
- 005.5C: provider comparison matrix, cost/privacy review.
- 005.5D: optional API proof-of-concept sau explicit env flag.
- 005.5E: optional button trong desktop app chỉ sau safety review.

Feature 006 natural-language control vẫn deferred và tách biệt. Không trộn AI polish preview với natural-language control, agent memory, hoặc workflow automation nâng cao.

## 10. Decision

Khuyến nghị hiện tại: không tích hợp AI polish vào production pipeline.

Trạng thái đề xuất:

- Evaluation complete.
- Implementation deferred.
- Core Maya-first pipeline remains source of truth.

Maya `.ma`, clean SVG, geometry JSON và thao tác polish thủ công của họa sĩ vẫn là workflow production chính. AI polish preview chỉ nên quay lại khi có nhu cầu rõ ràng, review an toàn/quyền riêng tư/chi phí đầy đủ, và phase riêng được approve.
