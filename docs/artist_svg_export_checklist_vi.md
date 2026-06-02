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

- [ ] Nếu muốn Maya tạo blockout đồ vật theo vị trí bạn đặt trong Illustrator, hãy tạo group/layer con bên trong group phòng và đặt tên theo mẫu đơn giản:
      `prop_bed`, `prop_table`, `prop_chair`, `prop_sofa`, `prop_fridge`, `prop_sink`,
      `prop_kitchen_counter`, `prop_cabinet`, `prop_locker`, `prop_plant`,
      `prop_shelf_unit`, `prop_wooden_crate`.
- [ ] Pipeline sẽ bỏ phần prefix `prop_`, `item_`, hoặc `object_` và hiểu loại prop. Một số tên tương đương cũng dùng được, ví dụ `desk` -> `table`, `couch` -> `sofa`, `refrigerator` -> `fridge`, `counter` -> `kitchen_counter`, `cupboard` -> `cabinet`, `potted_plant` -> `plant`, `shelf`/`shelving` -> `shelf_unit`, `crate`/`box` -> `wooden_crate`.
- [ ] Trong group prop, dùng một hình marker đơn giản như `rect`, `polygon`, `polyline`, hoặc path thẳng đơn giản. Maya sẽ lấy tâm của marker để đặt blockout, và dùng kích thước marker một cách an toàn nếu đọc được.
- [ ] Các prop được hỗ trợ sẽ hiện thành hình khối dễ nhận ra hơn cube trống, ví dụ giường có gối, bàn có chân, ghế có lưng, sofa có tay, tủ lạnh/tủ/locker có vệt cửa, sink có basin, shelf/crate có các khối phụ.
- [ ] Nếu tên prop chưa được hỗ trợ, Maya vẫn tạo cube placeholder đơn giản thay vì báo lỗi.
- [ ] Đây chỉ là blockout để kiểm tra bố cục, **không phải model 3D cuối cùng**. Họa sĩ vẫn polish và thay asset thật trong Maya sau.

> Checkpoint kỹ thuật: procedural prop blockout đã được kiểm chứng trong Maya ở `docs/verification/005_3P_procedural_prop_blockout_verified.md`. File test chỉ kiểm tra đúng kỹ thuật; preview có thể còn đơn giản và sẽ cần một phase polish visual riêng.

> Ghi chú visual sanity 005.3P-V1: `tests/in/illustrator_prop_markers.svg` là fixture kỹ thuật nhỏ nên ảnh preview có thể nhìn thưa hoặc chỉ nổi bật một vài prop cao. Khi muốn kiểm tra nhiều loại prop blockout rõ hơn, dùng `tests/in/illustrator_prop_showcase.svg` với phòng `phong_showcase`. Prop procedural vẫn là blockout để kiểm tra bố cục, không phải model cuối cùng.

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
