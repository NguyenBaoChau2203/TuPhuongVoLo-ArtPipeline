"""Tests for Feature 005.1 Illustrator SVG transform/shape/unit helpers."""

from __future__ import annotations

import math

from svg_shapes import (
    IDENTITY,
    apply_matrix,
    declarations_hide_element,
    is_identity,
    matrix_multiply,
    parse_css_text,
    parse_length,
    parse_transform,
    parse_viewbox,
    points_attr_to_points,
    rect_to_points,
    transform_points,
)


class _FakeElement:
    """Minimal element exposing only ``.get`` like an XML node."""

    def __init__(self, attrib: dict[str, str]) -> None:
        self._attrib = attrib

    def get(self, key: str, default=None):
        return self._attrib.get(key, default)


def test_parse_translate_scale_combines_in_order() -> None:
    matrix, warnings = parse_transform("translate(10 20) scale(2)")

    assert warnings == []
    # A point (1, 1) is first scaled to (2, 2) then translated to (12, 22).
    assert apply_matrix(matrix, 1.0, 1.0) == (12.0, 22.0)


def test_parse_matrix_transform() -> None:
    matrix, warnings = parse_transform("matrix(1 0 0 1 100 50)")

    assert warnings == []
    assert apply_matrix(matrix, 5.0, 5.0) == (105.0, 55.0)


def test_parse_rotate_90_degrees() -> None:
    matrix, warnings = parse_transform("rotate(90)")

    assert warnings == []
    x, y = apply_matrix(matrix, 1.0, 0.0)
    assert math.isclose(x, 0.0, abs_tol=1e-9)
    assert math.isclose(y, 1.0, abs_tol=1e-9)


def test_parse_rotate_around_center() -> None:
    matrix, warnings = parse_transform("rotate(90 10 10)")

    assert warnings == []
    x, y = apply_matrix(matrix, 10.0, 0.0)
    assert math.isclose(x, 20.0, abs_tol=1e-9)
    assert math.isclose(y, 10.0, abs_tol=1e-9)


def test_unsupported_transform_warns_but_does_not_crash() -> None:
    matrix, warnings = parse_transform("skewX(20)")

    assert is_identity(matrix)
    assert any("chưa hỗ trợ" in warning for warning in warnings)


def test_empty_transform_is_identity() -> None:
    matrix, warnings = parse_transform(None)

    assert matrix == IDENTITY
    assert warnings == []


def test_matrix_multiply_is_associative_compose() -> None:
    translate = (1.0, 0.0, 0.0, 1.0, 5.0, 0.0)
    scale = (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)
    combined = matrix_multiply(translate, scale)

    # translate-then-scale: (1,1) -> (2,2) -> (7,2)
    assert apply_matrix(combined, 1.0, 1.0) == (7.0, 2.0)


def test_transform_points_identity_returns_copy() -> None:
    points = [(1.0, 2.0), (3.0, 4.0)]
    result = transform_points(IDENTITY, points)

    assert result == points
    assert result is not points


def test_parse_length_units() -> None:
    assert parse_length("10") == 10.0
    assert parse_length("10px") == 10.0
    assert math.isclose(parse_length("25.4mm"), 96.0)
    assert math.isclose(parse_length("1in"), 96.0)
    assert math.isclose(parse_length("72pt"), 96.0)


def test_parse_length_rejects_percent_and_garbage() -> None:
    assert parse_length("50%") is None
    assert parse_length("abc") is None
    assert parse_length(None) is None


def test_parse_viewbox() -> None:
    assert parse_viewbox("0 0 100 50") == (0.0, 0.0, 100.0, 50.0)
    assert parse_viewbox("bad") is None


def test_points_attr_parsing() -> None:
    points = points_attr_to_points("0,0 10,0 10,10")

    assert points == [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]


def test_rect_to_points_basic() -> None:
    element = _FakeElement({"x": "5", "y": "5", "width": "10", "height": "4"})
    points, warnings = rect_to_points(element)

    assert points == [(5.0, 5.0), (15.0, 5.0), (15.0, 9.0), (5.0, 9.0)]
    assert warnings == []


def test_rect_to_points_missing_size_warns() -> None:
    element = _FakeElement({"x": "5", "y": "5"})
    points, warnings = rect_to_points(element)

    assert points == []
    assert warnings


def test_rect_rounded_corners_warns_but_returns_box() -> None:
    element = _FakeElement({"width": "10", "height": "10", "rx": "2"})
    points, warnings = rect_to_points(element)

    assert len(points) == 4
    assert any("bo góc" in warning for warning in warnings)


def test_parse_css_text_and_hidden_detection() -> None:
    rules = parse_css_text(".guide { display: none; } .wall { stroke: #000; }")

    assert declarations_hide_element(rules[".guide"]) is True
    assert declarations_hide_element(rules[".wall"]) is False
