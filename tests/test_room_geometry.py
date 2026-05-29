"""Tests for Feature 001 pure Python room geometry."""

from __future__ import annotations

from room_geometry import (
    calculate_bbox,
    choose_largest_closed_boundary,
    create_wall_segments,
    normalize_points_to_origin,
    parse_svg_path_points,
    scale_points_to_blender,
)


def test_parse_simple_closed_rectangle_path() -> None:
    points, closed, warnings = parse_svg_path_points("M0 0 L10 0 L10 5 L0 5 Z")

    assert closed
    assert warnings == []
    assert points == [(0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)]


def test_parse_horizontal_vertical_path_commands() -> None:
    points, closed, warnings = parse_svg_path_points("M0 0 H10 V5 H0 Z")

    assert closed
    assert warnings == []
    assert points == [(0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)]


def test_detect_closed_path_from_repeated_endpoint() -> None:
    points, closed, _warnings = parse_svg_path_points("M0 0 L10 0 L10 5 L0 0")

    assert closed
    assert points == [(0.0, 0.0), (10.0, 0.0), (10.0, 5.0)]


def test_bbox_calculation() -> None:
    assert calculate_bbox([(2.0, 3.0), (8.0, 1.0), (5.0, 9.0)]) == (2.0, 1.0, 8.0, 9.0)


def test_normalize_points_to_local_origin() -> None:
    points = normalize_points_to_origin([(10.0, 20.0), (15.0, 20.0), (15.0, 30.0)])

    assert points == [(0.0, 0.0), (5.0, 0.0), (5.0, 10.0)]


def test_scale_svg_units_to_blender_units() -> None:
    assert scale_points_to_blender([(100.0, 50.0)], scale=0.01) == [(1.0, -0.5)]


def test_wall_segment_generation_from_closed_boundary() -> None:
    segments = create_wall_segments([(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)])

    assert len(segments) == 4
    assert segments[-1] == ((0.0, 1.0), (0.0, 0.0))


def test_unsupported_curve_path_produces_warning() -> None:
    points, closed, warnings = parse_svg_path_points("M0 0 C1 1 2 2 3 3 Z")

    assert points == []
    assert not closed
    assert any("chưa hỗ trợ" in warning for warning in warnings)


def test_choose_largest_closed_path() -> None:
    boundary = choose_largest_closed_boundary(
        [
            "M0 0 L1 0 L1 1 L0 1 Z",
            "M0 0 L4 0 L4 3 L0 3 Z",
        ]
    )

    assert boundary is not None
    assert boundary.area == 12.0
    assert boundary.source_path_index == 1
