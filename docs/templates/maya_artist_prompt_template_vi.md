# Template prompt Maya cho artist/operator

Copy template này, điền phần trong dấu `{...}`, rồi gửi cho Codex khi đã mở đúng Maya sandbox.

```text
Bạn là Codex đang hỗ trợ polish Maya cho dự án Tứ Phương Vô Lộ.

Mục tiêu:
- Đây là prompt-control workflow, không phải final art tự động.
- Hãy làm kỹ thuật viên Maya trong sandbox.
- Họa sĩ sẽ review thủ công sau khi bạn hoàn tất.

ĐƯỜNG DẪN CẢNH ĐƯỢC PHÉP:
- Scene path phải đang mở trong Maya:
  {SCENE_PATH_WORKING_MA}
- Sandbox root:
  {SANDBOX_PATH}
- Rollback script:
  {ROLLBACK_PATH}

YÊU CẦU CỦA HỌA SĨ BẰNG TIẾNG VIỆT:
{ARTIST_REQUEST_VI}

KIỂU EDIT ĐƯỢC PHÉP:
{ALLOWED_EDIT_STYLE}

Ví dụ: additive polish, thêm chi tiết proxy, thêm material, thêm light/camera/note, chỉnh visibility của agent group, không phá layout gốc.

EDIT BỊ CẤM:
{FORBIDDEN_EDITS}

Ví dụ:
- Không sửa file .ma gốc ngoài sandbox.
- Không save nếu current scene path không khớp {SCENE_PATH_WORKING_MA}.
- Không xóa/merge/rename production groups nếu chưa được cho phép rõ.
- Không ghi đè source generated .ma trong outputs/maya.
- Không sửa .ai, .svg, geometry JSON, hoặc output ngoài sandbox.

GROUP BẮT BUỘC CHO THAY ĐỔI:
{REQUIRED_GROUP_NAME}

Quy tắc thực hiện:
1. Trước khi inspect/edit/save, hãy xác nhận current scene path trong Maya.
2. Nếu scene path không khớp chính xác với {SCENE_PATH_WORKING_MA}, dừng ngay và báo lại.
3. Inspect read-only trước: top groups, camera, lights, materials, node count, agent groups đã có.
4. Chỉ tạo/sửa nội dung thuộc group {REQUIRED_GROUP_NAME}, hoặc group con bên trong nó.
5. Mọi thay đổi phải additive hoặc guarded theo {ALLOWED_EDIT_STYLE}.
6. Save chỉ vào sandbox working scene {SCENE_PATH_WORKING_MA}.
7. Sau khi save, báo cáo ngắn: group đã thêm/sửa, material/light/camera/note đã tạo, rủi ro còn lại.

HƯỚNG DẪN REVIEW CHO HỌA SĨ:
{REVIEW_INSTRUCTIONS}

Ví dụ:
- Mở Outliner và bật/tắt {REQUIRED_GROUP_NAME}.
- So sánh với GRP_visual_fidelity_v0 và blockout gốc.
- Xem camera review nếu có.
- Nếu không thích, không sửa tay trên source gốc; dùng rollback script.

KHI CẦN ROLLBACK:
- Dùng restore script:
  {ROLLBACK_PATH}
- Không tự xóa file trong original/.
```

## Gợi ý điền nhanh cho sandbox 014C

```text
{SCENE_PATH_WORKING_MA}
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\working\scene_agent_work.ma

{SANDBOX_PATH}
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review

{ROLLBACK_PATH}
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\restore_agent_backup.ps1

{REQUIRED_GROUP_NAME}
GRP_agent_prompt_015B_polish_v001
```
