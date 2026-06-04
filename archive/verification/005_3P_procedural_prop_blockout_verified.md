# Xac minh 005.3P-R - Procedural prop blockout Maya

> Phase: `005.3P-R`
> Ngay xac minh: 2026-06-02
> Nhanh: `workflow/maya-first-artist-pipeline`

## Commits duoc xac minh

- `107a2fc feat: add procedural Maya prop blockout library`
- `187375d fix: use Maya-safe procedural prop part names`

## Muc tieu

Checkpoint nay xac minh rang SVG prop markers co the tao procedural Maya blockout props, thay vi chi tao generic cube placeholder cho cac prop type da biet. Output van la geometry blockout don gian, editable trong Maya, de artist kiem tra bo cuc va polish/replace thu cong.

## Supported prop blockouts

- `bed`
- `table`
- `chair`
- `sofa`
- `fridge`
- `sink`
- `kitchen_counter`
- `cabinet`
- `locker`
- `plant`
- `shelf_unit`
- `wooden_crate`

## Alias examples

- `desk` -> `table`
- `couch` -> `sofa`
- `refrigerator` -> `fridge`
- `counter` -> `kitchen_counter`
- `cupboard` -> `cabinet`
- `potted_plant` -> `plant`
- `shelf` / `shelving` -> `shelf_unit`
- `crate` / `box` -> `wooden_crate`

## Ket qua DCC verification

Real Maya/DCC verification da duoc thuc hien sau Phase 005.3P-F1.

- File `.ma` mo duoc trong Maya.
- Outliner co hierarchy mong doi:

```text
GRP_phong_kho_blockout
  walls
  props
  lights
  floor_blockout
```

- Trong `props`, `prop_shelf_unit_01` la multi-piece procedural blockout:

```text
prop_shelf_unit_01
  prop_shelf_unit_01_side_left
  prop_shelf_unit_01_side_right
  prop_shelf_unit_01_shelf_1
  prop_shelf_unit_01_shelf_2
  prop_shelf_unit_01_shelf_3
```

- Trong `props`, `prop_wooden_crate_01` la multi-piece procedural blockout:

```text
prop_wooden_crate_01
  prop_wooden_crate_01_body
  prop_wooden_crate_01_top_seam
  prop_wooden_crate_01_side_seam
```

- Prop child names da duoc xac minh la Maya-safe trong Outliner, khong dung raw signed suffix nhu `leg_-1_-1`, `arm_-1`, hoac `side_-1`.
- Camera ton tai trong scene: `cam_phong_kho_iso1`.
- Artist/operator co the xem qua camera bang:
  - `Panels -> Perspective -> cam_phong_kho_iso1`
  - hoac chon `cam_phong_kho_iso1` roi dung `Panels -> Look Through Selected`.
- PNG preview da duoc generate.

## Ghi chu ve visual quality

Fixture `tests/in/illustrator_prop_markers.svg` dung de kiem tra technical correctness, khong phai final visual quality. Preview co the trong sparse/odd vi fixture chi co hai marker don gian: `prop_shelf_unit` va `prop_wooden_crate`.

Phase `005.3P-V1` da xu ly visual sanity polish nho:

- Camera framing tinh them explicit SVG prop marker centers va footprint uoc luong, nen phong + prop duoc frame on dinh hon.
- Chieu cao prop procedural duoc tinh vao framing khi can, giup prop cao nhu shelf/fridge/locker an toan hon trong crop doc.
- San co preview-friendly fallback neu preset floor color qua nhat tren nen render trang.
- Fixture `tests/in/illustrator_prop_showcase.svg` duoc them de smoke test nhieu prop hon trong mot phong rong.

Dung `tests/in/illustrator_prop_showcase.svg` voi room `phong_showcase` khi can kiem tra visual/DCC prop variety. Procedural props van la blockout, khong phai final model.

Pending DCC follow-up:

```text
Real Maya/DCC render verification for illustrator_prop_showcase.svg remains pending on a machine with mayapy.exe.
```

## Safety confirmation

- Khong sua file goc cua artist.
- Khong commit generated outputs.
- Khong implement Feature 006 natural-language control.
- Khong thay doi AI behavior.
- Khong goi external API.
- Khong them secret hoac `.env`.
- Khong them dependency moi.
- Khong them binary asset, image, `.ma`, `.png`, build/dist file, hoac generated report.
- Khong sua SVG parser.
- Khong sua desktop app logic.

## Validation da tham chieu

Validation sau 005.3P-F1:

```powershell
python scripts/python/build_maya_room.py --help
python scripts/python/build_maya_room.py --input tests/in/illustrator_prop_markers.svg --room phong_kho --dry-run
python -m compileall scripts/maya/build_maya_room_scene.py tests/test_build_maya_room.py
python -m pytest tests/test_build_maya_room.py -v
pytest tests/ -v --ignore=tests/tmp
```

Ket qua:

```text
python scripts/python/build_maya_room.py --help: passed
python scripts/python/build_maya_room.py --input tests/in/illustrator_prop_markers.svg --room phong_kho --dry-run: passed
python -m compileall scripts/maya/build_maya_room_scene.py tests/test_build_maya_room.py: passed
python -m pytest tests/test_build_maya_room.py -v: 40 passed
pytest tests/ -v --ignore=tests/tmp: 197 passed
```
