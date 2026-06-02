"""Tests for Feature 005.1 Illustrator-style SVG compatibility in detection."""

from __future__ import annotations

from pathlib import Path

import pytest

from detect_rooms_from_svg import (
    detect_rooms,
    normalize_opening_marker_label,
    normalize_prop_marker_label,
    normalize_prop_marker_type,
)

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


def _prop(report, prop_type):
    for marker in report.prop_markers:
        if marker.prop_type == prop_type:
            return marker
    raise AssertionError(f"Prop {prop_type} not found in {[m.prop_type for m in report.prop_markers]}")


def _opening(report, marker_type, marker_name):
    for marker in report.opening_markers:
        if marker.marker_type == marker_type and marker.marker_name == marker_name:
            return marker
    found = [(m.marker_type, m.marker_name) for m in report.opening_markers]
    raise AssertionError(f"Opening {marker_type}:{marker_name} not found in {found}")


def test_prop_marker_name_normalization() -> None:
    assert normalize_prop_marker_type("prop_shelf_unit") == "shelf_unit"
    assert normalize_prop_marker_type("item_cardboard_box") == "cardboard_box"
    assert normalize_prop_marker_type("object_console_desk") == "console_desk"
    assert normalize_prop_marker_type("room_kho") is None
    assert normalize_prop_marker_label("prop_shelf_unit") == ("shelf_unit", 0)


def test_opening_marker_name_normalization() -> None:
    assert normalize_opening_marker_label("door_main") == ("door", "main")
    assert normalize_opening_marker_label("door_left") == ("door", "left")
    assert normalize_opening_marker_label("window_back_01") == ("window", "back_01")
    assert normalize_opening_marker_label("prop_shelf_unit") == (None, None)
    assert normalize_opening_marker_label("door") == (None, None)


@pytest.mark.parametrize(
    ("label", "expected_type", "expected_rotation"),
    [
        ("prop_shelf_unit_rot90", "shelf_unit", 90),
        ("prop_wooden_crate_rot180", "wooden_crate", 180),
        ("prop_table_rot270", "table", 270),
        ("item_box_rotation_90", "box", 90),
        ("object_barrel_rotation_270", "barrel", 270),
    ],
)
def test_prop_marker_rotation_suffix_normalization(
    label: str,
    expected_type: str,
    expected_rotation: int,
) -> None:
    assert normalize_prop_marker_label(label) == (expected_type, expected_rotation)
    assert normalize_prop_marker_type(label) == expected_type


@pytest.mark.parametrize(
    ("label", "expected_type", "expected_rotation"),
    [
        ("prop_shelf_unit", "shelf_unit", 0),
        ("prop_shelf_unit_rot90", "shelf_unit", 90),
        ("prop_wooden_crate_rot180", "wooden_crate", 180),
        ("prop_table_rot270", "table", 270),
        ("item_box_rotation_90", "box", 90),
    ],
)
def test_detected_prop_marker_rotation_metadata(
    tmp_path: Path,
    label: str,
    expected_type: str,
    expected_rotation: int,
) -> None:
    svg = write_svg(
        tmp_path / f"{label}.svg",
        '<g id="room_kho">'
        '<path d="M0 0 L100 0 L100 100 L0 100 Z"/>'
        f'<g id="{label}"><rect x="20" y="30" width="10" height="8"/></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "kho")

    assert len(kho.prop_markers) == 1
    assert kho.prop_markers[0].prop_type == expected_type
    assert kho.prop_markers[0].rotation_y_degrees == expected_rotation


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
    assert reports[0].opening_markers == []


def test_detect_door_and_window_opening_markers(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "openings.svg",
        '<g id="room_kho">'
        '<path d="M0 0 L120 0 L120 80 L0 80 Z"/>'
        '<g id="door_main"><rect x="8" y="72" width="16" height="4"/></g>'
        '<g id="window_back_01"><rect x="80" y="0" width="20" height="4"/></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "kho")
    door = _opening(kho, "door", "main")
    window = _opening(kho, "window", "back_01")

    assert door.source_name == "door_main"
    assert door.group_path == ["room_kho", "door_main"]
    assert door.center_svg == (16.0, 74.0)
    assert door.bbox_svg == (8.0, 72.0, 24.0, 76.0)
    assert window.source_name == "window_back_01"
    assert window.center_svg == (90.0, 2.0)


def test_nested_prop_markers_fixture_detects_room_markers() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_prop_markers.svg")
    kho = _room(reports, "phong_kho")

    assert kho.has_usable_boundary
    assert kho.boundary is not None
    assert kho.boundary.bbox == (15.0, 25.0, 135.0, 105.0)
    assert [marker.prop_type for marker in kho.prop_markers] == [
        "shelf_unit",
        "wooden_crate",
    ]
    assert [marker.rotation_y_degrees for marker in kho.prop_markers] == [0, 0]
    assert "hidden_box" not in {marker.prop_type for marker in kho.prop_markers}
    assert kho.group_path == ["Layer 1", "Phòng Kho"]


def test_prop_markers_preserve_group_path_and_transform_centers() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_prop_markers.svg")
    kho = _room(reports, "phong_kho")
    shelf = _prop(kho, "shelf_unit")
    crate = _prop(kho, "wooden_crate")

    assert shelf.group_path == ["Layer 1", "Phòng Kho", "prop_shelf_unit"]
    assert shelf.source_kind == "rect"
    assert shelf.bbox_svg == (35.0, 35.0, 55.0, 43.0)
    assert shelf.center_svg == (45.0, 39.0)
    assert crate.source_kind == "polygon"
    assert crate.center_svg == (80.0, 60.0)
    assert any("prop_decorative_text" in warning for warning in kho.warnings)


def test_opening_markers_do_not_change_prop_marker_detection(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "openings_and_props.svg",
        '<g id="room_kho">'
        '<path d="M0 0 L120 0 L120 80 L0 80 Z"/>'
        '<g id="door_main"><rect x="8" y="72" width="16" height="4"/></g>'
        '<g id="prop_shelf_unit"><rect x="40" y="30" width="20" height="8"/></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "kho")

    assert [_marker.prop_type for _marker in kho.prop_markers] == ["shelf_unit"]
    assert [(marker.marker_type, marker.marker_name) for marker in kho.opening_markers] == [
        ("door", "main")
    ]
