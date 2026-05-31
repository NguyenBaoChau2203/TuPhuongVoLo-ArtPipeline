"""Tests for Feature 005.1 Illustrator-style SVG compatibility in detection."""

from __future__ import annotations

from pathlib import Path

from detect_rooms_from_svg import detect_rooms

FIXTURE_DIR = Path(__file__).parent / "in"


def write_svg(path: Path, body: str, root_attrs: str = 'width="100" height="100"') -> Path:
    """Write a minimal SVG test file."""

    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     {root_attrs}>
{body}
</svg>
""",
        encoding="utf-8",
    )
    return path


def _room(reports, name):
    for report in reports:
        if report.room_name == name:
            return report
    raise AssertionError(f"Room {name} not found in {[r.room_name for r in reports]}")


def test_nested_groups_fixture_detects_both_rooms() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_nested_groups.svg")

    names = {report.room_name for report in reports}
    assert {"phong_kho", "sanh_chinh"} <= names
    kho = _room(reports, "phong_kho")
    assert kho.has_usable_boundary
    assert kho.transform_applied
    # translate(50 30) + translate(10 10) accumulate to (60, 40) origin.
    assert kho.boundary is not None
    assert kho.boundary.bbox == (60.0, 40.0, 180.0, 120.0)


def test_nested_group_records_group_path() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_nested_groups.svg")
    kho = _room(reports, "phong_kho")

    assert kho.group_path[-1] == "Phòng Kho"
    assert "Layer 1" in kho.group_path[0]


def test_transform_fixture_supports_rect_polygon_polyline() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_transforms_shapes.svg")

    rect_room = _room(reports, "phong_ngu")
    assert "rect" in rect_room.shape_kinds
    assert rect_room.transform_applied
    # rect 40x30 scaled by 2 then translated -> bbox (10,10)-(90,70).
    assert rect_room.boundary is not None
    assert rect_room.boundary.bbox == (10.0, 10.0, 90.0, 70.0)

    polygon_room = _room(reports, "ban_cong")
    assert "polygon" in polygon_room.shape_kinds
    assert polygon_room.has_usable_boundary

    polyline_room = _room(reports, "hanh_lang")
    assert "polyline" in polyline_room.shape_kinds
    assert polyline_room.has_usable_boundary


def test_style_class_fixture_warns_on_unsupported_and_skips_hidden() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_style_class.svg")

    names = {report.room_name for report in reports}
    # CSS .guide{display:none} and inline display:none layers are excluded.
    assert "guides" not in names
    assert "hidden_helper" not in names

    bep = _room(reports, "bep")
    assert bep.has_usable_boundary
    assert any("circle" in item for item in bep.unsupported_elements)
    assert any("chưa hỗ trợ" in warning for warning in bep.warnings)


def test_rect_boundary_inline(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "rect.svg",
        '<g id="room_kho"><rect x="0" y="0" width="10" height="8"/></g>',
    )

    reports = detect_rooms(svg)

    assert reports[0].room_name == "kho"
    assert reports[0].has_usable_boundary
    assert reports[0].boundary.bbox == (0.0, 0.0, 10.0, 8.0)


def test_polygon_boundary_inline(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "poly.svg",
        '<g id="room_kho"><polygon points="0,0 10,0 10,10 0,10"/></g>',
    )

    reports = detect_rooms(svg)

    assert reports[0].has_usable_boundary
    assert reports[0].closed_path_count == 1


def test_translate_transform_offsets_boundary(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "shift.svg",
        '<g id="room_kho" transform="translate(100 50)">'
        '<path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>',
    )

    reports = detect_rooms(svg)

    assert reports[0].boundary.bbox == (100.0, 50.0, 110.0, 60.0)


def test_h_v_path_in_nested_group_with_scale(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "hv.svg",
        '<g id="outer" transform="scale(2)">'
        '<g id="room_kho"><path d="M0 0 H10 V10 H0 Z"/></g></g>',
    )

    reports = detect_rooms(svg)
    kho = _room(reports, "kho")

    assert kho.transform_applied
    assert kho.boundary.bbox == (0.0, 0.0, 20.0, 20.0)


def test_unsupported_element_does_not_crash(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "mixed.svg",
        '<g id="room_kho">'
        '<text x="0" y="0">nhãn</text>'
        '<path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>',
    )

    reports = detect_rooms(svg)
    kho = _room(reports, "kho")

    assert kho.has_usable_boundary
    assert any("text" in item for item in kho.unsupported_elements)


def test_existing_simple_fixture_still_works() -> None:
    reports = detect_rooms(FIXTURE_DIR / "feature001_kho.svg")

    assert len(reports) == 1
    assert reports[0].room_name == "kho"
    assert reports[0].has_usable_boundary
