"""Tests for Feature 005.1 Illustrator-style SVG compatibility in detection."""

from __future__ import annotations

from pathlib import Path

import pytest

from detect_rooms_from_svg import (
    detect_rooms,
    normalize_opening_marker_label,
    normalize_prop_marker_label,
    normalize_prop_marker_label_with_hints,
    normalize_prop_marker_type,
    normalize_surface_material_label,
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
    ("label", "expected_type", "expected_material", "expected_color"),
    [
        ("prop_wooden_crate_01_mat_wood", "wooden_crate", "wood", None),
        ("prop_table_material_metal", "table", "metal", None),
        ("prop_box_color_red", "box", None, "red"),
        ("prop_chair_mat_mystery", "chair", "mystery", None),
    ],
)
def test_prop_marker_material_color_suffix_normalization(
    label: str,
    expected_type: str,
    expected_material: str | None,
    expected_color: str | None,
) -> None:
    prop_type, rotation, material_hint, color_hint = normalize_prop_marker_label_with_hints(label)

    assert prop_type == expected_type
    assert rotation == 0
    assert material_hint == expected_material
    assert color_hint == expected_color


def test_surface_material_color_suffix_normalization() -> None:
    assert normalize_surface_material_label("wall_mat_stone") == ("wall", "stone", None)
    assert normalize_surface_material_label("floor_material_wood") == ("floor", "wood", None)
    assert normalize_surface_material_label("wall_color_gray") == ("wall", None, "gray")
    assert normalize_surface_material_label("room_kho_mat_wood")[0] is None


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


def test_detected_prop_marker_material_color_hints(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "material_tags.svg",
        '<g id="room_kho">'
        '<path d="M0 0 L100 0 L100 100 L0 100 Z"/>'
        '<g id="prop_wooden_crate_01_mat_wood"><rect x="20" y="30" width="10" height="8"/></g>'
        '<g id="prop_table_material_metal"><rect x="40" y="30" width="10" height="8"/></g>'
        '<g id="prop_box_color_red"><rect x="60" y="30" width="10" height="8"/></g>'
        '<g id="prop_chair_mat_mystery"><rect x="80" y="30" width="10" height="8"/></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "kho")
    markers = {marker.prop_type: marker for marker in kho.prop_markers}

    assert markers["wooden_crate"].material_hint == "wood"
    assert markers["table"].material_hint == "metal"
    assert markers["box"].color_hint == "red"
    assert markers["chair"].material_hint == "mystery"


def test_detected_floor_and_wall_material_hints(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "surface_tags.svg",
        '<g id="room_kho">'
        '<g id="floor_material_wood"><path d="M0 0 L100 0 L100 100 L0 100 Z"/></g>'
        '<g id="wall_color_gray"></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "kho")

    assert kho.has_usable_boundary
    assert kho.floor_material_hint == "wood"
    assert kho.wall_color_hint == "gray"


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


def test_real_illustrator_sibling_prop_groups_attach_to_parent_room() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_real_grouped_room_props.svg")
    kho = _room(reports, "phong_kho")

    assert kho.has_usable_boundary
    assert kho.original_label == "phong_kho"
    assert kho.group_path == ["Layer_1", "phong_kho"]
    assert kho.boundary is not None
    assert kho.boundary.bbox == (20.0, 20.0, 190.0, 140.0)

    original_labels = {marker.original_label for marker in kho.prop_markers}
    assert {
        "prop_shelf_unit_01",
        "prop_wooden_crate_01",
        "prop_barrel_01",
        "prop_electrical_cabinet_01_mat_metal",
        "prop_floor_grate_01_mat_metal",
    } <= original_labels
    assert len(kho.prop_markers) == 5
    assert [(marker.marker_type, marker.marker_name) for marker in kho.opening_markers] == [
        ("door", "main")
    ]


def test_real_illustrator_sibling_prop_groups_keep_material_suffixes() -> None:
    reports = detect_rooms(FIXTURE_DIR / "illustrator_real_grouped_room_props.svg")
    kho = _room(reports, "phong_kho")
    markers = {marker.original_label: marker for marker in kho.prop_markers}

    assert markers["prop_electrical_cabinet_01_mat_metal"].prop_type == "electrical_cabinet"
    assert markers["prop_electrical_cabinet_01_mat_metal"].material_hint == "metal"
    assert markers["prop_floor_grate_01_mat_metal"].prop_type == "floor_grate"
    assert markers["prop_floor_grate_01_mat_metal"].material_hint == "metal"


@pytest.mark.parametrize(
    "boundary_label",
    ["room_boundary", "room_phong_kho", "boundary_phong_kho"],
)
def test_supported_boundary_group_names_use_parent_room_name(
    tmp_path: Path,
    boundary_label: str,
) -> None:
    svg = write_svg(
        tmp_path / f"{boundary_label}.svg",
        '<g id="phong_kho">'
        f'<g id="{boundary_label}"><path d="M0 0 L100 0 L100 80 L0 80 Z"/></g>'
        '<g id="prop_shelf_unit_01"><rect x="20" y="20" width="20" height="8"/></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "phong_kho")

    assert kho.original_label == "phong_kho"
    assert kho.has_usable_boundary
    assert [marker.original_label for marker in kho.prop_markers] == ["prop_shelf_unit_01"]


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


# --- Feature 008B: Root-level Illustrator SVG room wrappers ---


def test_root_svg_room_fixture_detects_room_props_and_openings() -> None:
    """Fixture <svg id="phong_kho"> should detect room with props and openings."""
    reports = detect_rooms(FIXTURE_DIR / "illustrator_root_level_room.svg")
    kho = _room(reports, "phong_kho")

    assert kho.has_usable_boundary
    assert kho.original_label == "phong_kho"
    assert "phong_kho" in kho.group_path
    assert kho.boundary is not None
    assert kho.boundary.bbox == (20.0, 20.0, 190.0, 140.0)

    prop_types = [marker.prop_type for marker in kho.prop_markers]
    assert "shelf_unit" in prop_types
    assert "wooden_crate" in prop_types
    assert len(kho.prop_markers) == 2

    assert [(m.marker_type, m.marker_name) for m in kho.opening_markers] == [
        ("door", "main")
    ]


def test_root_svg_room_inline_detects_room_with_boundary(tmp_path: Path) -> None:
    """Inline <svg id="phong_kho"> with room_phong_kho child boundary."""
    svg = tmp_path / "root_room.svg"
    svg.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="100" height="100">\n'
        '  <g id="room_phong_kho"><path d="M0 0 L100 0 L100 80 L0 80 Z"/></g>\n'
        '  <g id="prop_shelf_unit_01"><rect x="20" y="20" width="20" height="8"/></g>\n'
        '  <g id="prop_wooden_crate_01"><rect x="60" y="50" width="15" height="12"/></g>\n'
        '  <g id="door_main"><rect x="40" y="72" width="20" height="4"/></g>\n'
        "</svg>\n",
        encoding="utf-8",
    )

    kho = _room(detect_rooms(svg), "phong_kho")

    assert kho.has_usable_boundary
    assert kho.original_label == "phong_kho"
    assert "phong_kho" in kho.group_path
    assert len(kho.prop_markers) == 2
    prop_types = {marker.prop_type for marker in kho.prop_markers}
    assert {"shelf_unit", "wooden_crate"} <= prop_types
    assert len(kho.opening_markers) == 1
    assert kho.opening_markers[0].marker_type == "door"
    assert kho.opening_markers[0].marker_name == "main"


def test_root_svg_room_with_boundary_prefix_variant(tmp_path: Path) -> None:
    """Root <svg id="phong_kho"> with boundary_phong_kho child."""
    svg = tmp_path / "boundary_variant.svg"
    svg.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="100" height="100">\n'
        '  <g id="boundary_phong_kho"><polygon points="0,0 100,0 100,80 0,80"/></g>\n'
        '  <g id="prop_barrel_01"><rect x="30" y="30" width="12" height="14"/></g>\n'
        "</svg>\n",
        encoding="utf-8",
    )

    kho = _room(detect_rooms(svg), "phong_kho")

    assert kho.has_usable_boundary
    assert kho.original_label == "phong_kho"
    assert len(kho.prop_markers) == 1
    assert kho.prop_markers[0].prop_type == "barrel"


def test_curved_illustrator_prop_path_uses_marker_bbox_fallback(tmp_path: Path) -> None:
    """Curved prop marker paths should emit a safe approximate bbox."""

    svg = tmp_path / "curved_barrel.svg"
    svg.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="240" height="460">\n'
        '  <g id="room_phong_kho"><polygon points="0,0 220,0 220,440 0,440"/></g>\n'
        '  <g id="prop_barrel_01">\n'
        '    <path d="M183.44,406.93c-16,0-28.9,2.43-28.9,5.44s12.94,5.45,28.9,5.45"/>\n'
        "  </g>\n"
        "</svg>\n",
        encoding="utf-8",
    )

    kho = _room(detect_rooms(svg), "phong_kho")
    barrel = _prop(kho, "barrel")

    assert barrel.original_label == "prop_barrel_01"
    assert barrel.group_path == ["phong_kho", "prop_barrel_01"]
    assert barrel.source_kind == "path_bbox_fallback"
    assert barrel.bbox_svg
    assert barrel.center_svg
    assert barrel.bbox_svg[0] < barrel.bbox_svg[2]
    assert barrel.bbox_svg[1] < barrel.bbox_svg[3]
    assert any("fallback approximate path bbox" in warning for warning in barrel.warnings)


def test_curved_opening_path_uses_marker_bbox_fallback(tmp_path: Path) -> None:
    """Opening markers share marker-only fallback without loosening room boundaries."""

    svg = write_svg(
        tmp_path / "curved_window.svg",
        '<g id="room_kho">'
        '<path d="M0 0 L120 0 L120 80 L0 80 Z"/>'
        '<g id="window_round_01"><path d="M20,10 A8,4 0 0,1 36,10"/></g>'
        "</g>",
    )

    kho = _room(detect_rooms(svg), "kho")
    window = _opening(kho, "window", "round_01")

    assert window.center_svg
    assert window.bbox_svg[0] < window.bbox_svg[2]
    assert any("fallback approximate path bbox" in warning for warning in window.warnings)


def test_root_svg_room_with_room_boundary_label(tmp_path: Path) -> None:
    """Root <svg id="phong_kho"> with generic room_boundary child."""
    svg = tmp_path / "room_boundary.svg"
    svg.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="100" height="100">\n'
        '  <g id="room_boundary"><path d="M5 5 L95 5 L95 75 L5 75 Z"/></g>\n'
        '  <g id="prop_shelf_unit_01"><rect x="20" y="20" width="20" height="8"/></g>\n'
        '  <g id="window_back"><rect x="70" y="5" width="16" height="4"/></g>\n'
        "</svg>\n",
        encoding="utf-8",
    )

    kho = _room(detect_rooms(svg), "phong_kho")

    assert kho.has_usable_boundary
    assert len(kho.prop_markers) == 1
    assert len(kho.opening_markers) == 1
    assert kho.opening_markers[0].marker_type == "window"


def test_root_svg_generic_id_does_not_become_room(tmp_path: Path) -> None:
    """Generic <svg id="Layer_1"> should NOT be treated as a room name."""
    svg = write_svg(
        tmp_path / "generic_root.svg",
        '<g id="room_kho"><path d="M0 0 L100 0 L100 80 L0 80 Z"/></g>',
        root_attrs='id="Layer_1" width="100" height="100"',
    )

    reports = detect_rooms(svg)

    kho = _room(reports, "kho")
    assert kho.has_usable_boundary
    assert kho.original_label == "room_kho"


def test_root_svg_no_id_uses_stem_fallback(tmp_path: Path) -> None:
    """SVG without root id should use file stem as before."""
    svg = write_svg(
        tmp_path / "my_room.svg",
        '<g id="room_kho"><path d="M0 0 L100 0 L100 80 L0 80 Z"/></g>',
    )

    reports = detect_rooms(svg)

    kho = _room(reports, "kho")
    assert kho.has_usable_boundary


def test_existing_nested_group_room_detection_unaffected_by_root_fix() -> None:
    """Existing <g id="phong_kho"> inside a Layer_1 wrapper still works."""
    reports = detect_rooms(FIXTURE_DIR / "illustrator_real_grouped_room_props.svg")
    kho = _room(reports, "phong_kho")

    assert kho.has_usable_boundary
    assert kho.original_label == "phong_kho"
    assert len(kho.prop_markers) == 5
    assert len(kho.opening_markers) == 1
