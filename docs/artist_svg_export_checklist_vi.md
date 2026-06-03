# Checklist xuất SVG sạch từ Illustrator (dành cho Họa sĩ)

> **Loại tài liệu**: Hướng dẫn cho họa sĩ (tiếng Việt)
> **Giai đoạn**: Tài liệu nền cho Phase 005.1 (chưa đổi code parser)
> **Mục tiêu**: Giúp bạn xuất file SVG sạch để pipeline (Python -> Maya) đọc ổn định

Đây là checklist nhẹ, mang tính hướng dẫn. Phase 005.0A **chưa thay đổi** bất kỳ
code xử lý SVG nào. Tài liệu này chỉ giúp bạn chuẩn bị file SVG tốt hơn cho các
bước sau.

---

## Vì sao cần SVG sạch?

Pipeline lấy **SVG sạch làm nguồn chân lý** (source of truth). Python sẽ đọc SVG,
phát hiện phòng, tạo dữ liệu hình học, rồi chuyển cho Maya dựng cảnh `.ma`. Nếu SVG
gọn gàng, mọi bước sau sẽ chạy ổn định và ít lỗi hơn.

---

## Checklist trước khi xuất

- [ ] **Giữ layer/group gọn gàng.** Mỗi phòng nên nằm trong một group/layer riêng,
      tránh trộn lẫn nhiều phòng vào chung một nhóm.
- [ ] **Đặt tên layer/group có ý nghĩa.** Ví dụ: `kho`, `sanh_chinh`, `phong_ngu`.
      Tên rõ ràng giúp pipeline nhận diện phòng đúng. Tên tiếng Việt có dấu vẫn được
      vì pipeline sẽ tự chuẩn hóa (ví dụ `Sảnh Chính` -> `sanh_chinh`).
- [ ] **Tránh hiệu ứng phá hủy (destructive effects) khi không cần.** Hạn chế
      blend, mesh phức tạp, hoặc hiệu ứng làm rối đường path.
- [ ] **Expand / Outline appearance nếu hình phức tạp.** Nếu bạn dùng nhiều
      appearance/effect, hãy `Object > Expand Appearance` để đường nét trở thành
      path thật, dễ đọc hơn.
- [ ] **Đóng kín đường bao phòng (closed path).** Tường/đường bao phòng nên là một
      đường khép kín, không hở góc, để pipeline dựng được sàn và tường.
- [ ] **Ưu tiên đường thẳng cho tường.** Đường thẳng (line/polyline) dễ xử lý hơn
      đường cong phức tạp khi dựng blockout.

---

## Khi xuất SVG

- [ ] **Lưu/xuất một bản SVG sạch riêng.** Dùng `File > Export > Export As... > SVG`
      hoặc `Export for Screens`.
- [ ] **KHÔNG ghi đè file `.ai` gốc.** File `.ai` gốc của bạn phải được giữ nguyên,
      không bao giờ bị xóa hay sửa bởi pipeline.
- [ ] **Đặt file SVG vào thư mục xử lý** (ví dụ `drops/` hoặc `assets/2d/svg_clean/`),
      không để lẫn với file gốc.

---

## Trước khi dựng Maya thật

- [ ] **Kiểm tra môi trường nếu chưa chắc chắn.** Có thể chạy
      `launchers/00_maya_env_check.bat` để xem Python, PyYAML và `mayapy.exe` đã sẵn sàng chưa.
- [ ] **Chạy thử bằng dry-run trước.** Dry-run chỉ lập kế hoạch, **không** chạy Maya
      và **không** ghi manifest. Đây là cách an toàn để kiểm tra phòng và đường dẫn
      output trước khi tạo file thật.

```powershell
python scripts/python/build_maya_room.py --input drops/phong_cua_ban.svg --room kho --dry-run
```

- [ ] Khi dry-run hiển thị đúng phòng và đường dẫn `.ma` mong muốn, bạn mới chạy
      bản thật (cần Maya `mayapy.exe`).
- [ ] Sau khi chạy thật, kiểm tra output trong `outputs/maya/` và preview PNG trong
      `outputs/preview/` nếu bạn bật render preview. Geometry JSON tạm nằm trong `outputs/tmp/`;
      report batch nằm trong `outputs/reports/`.

---

## Đánh dấu prop blockout trong SVG

- [ ] Nếu muốn Maya tạo blockout đồ vật theo vị trí bạn đặt trong Illustrator, hãy mở template:
      `assets/2d/templates/illustrator_prop_marker_template.svg`.
- [ ] Copy group marker từ template, paste vào group phòng thật, rồi di chuyển/scale marker.
- [ ] Đọc hướng dẫn đặt tên/alias đầy đủ trong guide chính:
      `docs/artist_workflow_cat_guide_vi.html`.
- [ ] Prop blockout hiện hỗ trợ bảng keyword nhỏ dưới đây. Nếu tên prop không
      nằm trong bảng, Maya vẫn tạo khối cube generic để bạn không bị mất marker.

| Keyword | Blockout Maya |
|---------|---------------|
| `shelf_unit` | Kệ cao đơn giản |
| `wooden_crate` | Thùng gỗ placeholder |
| `table` | Bàn |
| `chair` | Ghế |
| `bed` | Giường |
| `cabinet` | Tủ |
| `barrel` | Thùng tròn placeholder dạng khối |
| `box` | Hộp nhỏ |

> Các prop này chỉ là kích thước placeholder, **chưa có model 3D thật, texture,
> hay material riêng**.
- [ ] Trong group prop, dùng hình marker đơn giản như `rect`, `polygon`, `polyline`, hoặc path thẳng đơn giản. Maya lấy tâm marker để đặt blockout.
- [ ] Nếu muốn xoay prop quanh trục đứng trong Maya, thêm hậu tố vào cuối tên marker:
      `_rot90`, `_rot180`, `_rot270`, `_rotation_90`, `_rotation_180`, hoặc `_rotation_270`.
      Ví dụ: `prop_shelf_unit_rot90`, `prop_wooden_crate_rot180`, `item_box_rotation_90`.
      Hãy chạy dry-run trước để kiểm tra tên prop và kế hoạch dựng Maya trước khi chạy thật.
- [ ] Đây chỉ là blockout để kiểm tra bố cục, **không phải model 3D cuối cùng**. Họa sĩ vẫn polish và thay asset thật trong Maya sau.

## Đánh dấu cửa và cửa sổ trong SVG

- [ ] Để Maya tạo marker vị trí cửa/cửa sổ, đặt tên group/layer bắt đầu bằng `door_` hoặc `window_`.
      Ví dụ: `door_main`, `door_left`, `window_small`, `window_back_01`.
- [ ] Phase 005.3S chỉ tạo khối marker đơn giản trong Maya để nhìn vị trí. Pipeline **chưa khoét tường**,
      chưa boolean, và chưa tạo lỗ cửa/cửa sổ thật.
- [ ] Sau khi build `.ma`, mở scene trong Maya và kiểm tra group `openings` để xem marker có đúng vị trí không.

> Checkpoint kỹ thuật: procedural prop blockout đã được kiểm chứng trong Maya ở `docs/verification/005_3P_procedural_prop_blockout_verified.md`. File test chỉ kiểm tra đúng kỹ thuật; preview có thể còn đơn giản và sẽ cần một phase polish visual riêng.

> Ghi chú visual sanity 005.3P-V1: `tests/in/illustrator_prop_markers.svg` là fixture kỹ thuật nhỏ nên ảnh preview có thể nhìn thưa hoặc chỉ nổi bật một vài prop cao. Khi muốn kiểm tra nhiều loại prop blockout rõ hơn, dùng `tests/in/illustrator_prop_showcase.svg` với phòng `phong_showcase`. Prop procedural vẫn là blockout để kiểm tra bố cục, không phải model cuối cùng.

> Checkpoint 005.3P-V1-R: `docs/verification/005_3P_V1_procedural_prop_preview_verified.md` ghi checklist Maya/DCC thật cho showcase fixture. Hiện checkpoint này vẫn pending cho đến khi operator chạy trên máy có `mayapy.exe`.

---

## Quy tắc an toàn (rất quan trọng)

- Pipeline **không bao giờ** sửa hay xóa file gốc `.ai`, SVG thô, ảnh tham khảo.
- Mọi kết quả sinh ra đều nằm trong `outputs/`.
- Manifest chỉ được cập nhật khi có file output thật.
- Nếu gặp lỗi, hãy đọc thông báo lỗi (có tiếng Việt) và thử lại bằng dry-run trước.

---

> Ghi chú kỹ thuật: Việc làm cho parser đọc tốt mọi kiểu SVG thật từ Illustrator là
> phạm vi của **Phase 005.1** và sẽ được làm sau. Hiện tại checklist này chỉ giúp
> bạn chuẩn bị file tốt hơn.
