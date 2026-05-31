"""Illustrator-oriented SVG transform, shape, unit, and CSS helpers (Feature 005.1).

This module hardens the shared Python SVG layer against realistic Adobe
Illustrator exports. It stays pure (no DCC, no network) and is intentionally
small and well-tested. It complements ``room_geometry`` (path math) and is used
by ``detect_rooms_from_svg`` to traverse nested groups, accumulate transforms,
read non-path shapes, and warn instead of crashing on unsupported content.

Conventions:
- A transform is a 6-tuple ``(a, b, c, d, e, f)`` describing the affine matrix::

      | a c e |
      | b d f |
      | 0 0 1 |

  applied to a point as ``x' = a*x + c*y + e``, ``y' = b*x + d*y + f``.
- Lengths are normalized to CSS "user units" (96 dpi) for reporting only; the
  downstream Maya scale is unchanged.
"""

from __future__ import annotations

import math
import re

Point2D = tuple[float, float]
Matrix = tuple[float, float, float, float, float, float]

IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
EPSILON = 1e-9

# Number token shared by path/points/length parsing.
_NUMBER = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
_NUMBER_RE = re.compile(_NUMBER)
_LENGTH_RE = re.compile(rf"^\s*({_NUMBER})\s*([a-z%]*)\s*$", re.IGNORECASE)
_TRANSFORM_RE = re.compile(r"([a-zA-Z]+)\s*\(([^)]*)\)")
_CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")

# CSS absolute units relative to user units (px) at 96 dpi.
_UNIT_TO_USER: dict[str, float] = {
    "": 1.0,
    "px": 1.0,
    "pt": 96.0 / 72.0,
    "pc": 16.0,
    "mm": 96.0 / 25.4,
    "cm": 96.0 / 2.54,
    "in": 96.0,
    "q": 96.0 / 101.6,
}

SUPPORTED_SHAPES = frozenset({"path", "rect", "polygon", "polyline"})
# Drawable elements we knowingly do not convert yet -> actionable warning.
UNSUPPORTED_DRAWABLE = frozenset(
    {"circle", "ellipse", "line", "text", "tspan", "image", "use"}
)
# Containers we recurse into while traversing.
CONTAINER_TAGS = frozenset({"svg", "g", "a", "switch"})
# Definition/metadata containers whose contents are not directly drawn geometry.
SKIP_SUBTREE_TAGS = frozenset(
    {
        "defs",
        "clippath",
        "mask",
        "symbol",
        "marker",
        "pattern",
        "metadata",
        "title",
        "desc",
        "style",
        "lineargradient",
        "radialgradient",
        "filter",
        "foreignobject",
    }
)


def parse_length(value: str | None) -> float | None:
    """Convert an SVG length such as ``10``, ``5mm``, or ``72pt`` to user units.

    Returns ``None`` for missing, percentage, or unparseable values so callers
    can warn instead of crashing.
    """

    if value is None:
        return None
    match = _LENGTH_RE.match(str(value).strip())
    if not match:
        return None
    number, unit = match.group(1), match.group(2).lower()
    if unit == "%":
        return None
    factor = _UNIT_TO_USER.get(unit)
    if factor is None:
        return None
    try:
        return float(number) * factor
    except ValueError:
        return None


def parse_viewbox(value: str | None) -> tuple[float, float, float, float] | None:
    """Parse a ``viewBox`` string into ``(min_x, min_y, width, height)``."""

    if not value:
        return None
    numbers = [float(token) for token in _NUMBER_RE.findall(value)]
    if len(numbers) != 4:
        return None
    return numbers[0], numbers[1], numbers[2], numbers[3]


def is_identity(matrix: Matrix, tolerance: float = 1e-6) -> bool:
    """Return whether a matrix is (numerically) the identity transform."""

    return all(abs(value - ref) <= tolerance for value, ref in zip(matrix, IDENTITY, strict=False))


def matrix_multiply(first: Matrix, second: Matrix) -> Matrix:
    """Return ``first`` followed by ``second`` (``first`` is the parent)."""

    a1, b1, c1, d1, e1, f1 = first
    a2, b2, c2, d2, e2, f2 = second
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def apply_matrix(matrix: Matrix, x: float, y: float) -> Point2D:
    """Apply an affine matrix to a single point."""

    a, b, c, d, e, f = matrix
    return (a * x + c * y + e, b * x + d * y + f)


def transform_points(matrix: Matrix, points: list[Point2D]) -> list[Point2D]:
    """Apply an affine matrix to every point in a list."""

    if is_identity(matrix):
        return list(points)
    return [apply_matrix(matrix, x, y) for x, y in points]


def _rotate_matrix(angle_degrees: float, cx: float = 0.0, cy: float = 0.0) -> Matrix:
    radians = math.radians(angle_degrees)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    rotation: Matrix = (cos_a, sin_a, -sin_a, cos_a, 0.0, 0.0)
    if cx == 0.0 and cy == 0.0:
        return rotation
    to_origin: Matrix = (1.0, 0.0, 0.0, 1.0, cx, cy)
    back: Matrix = (1.0, 0.0, 0.0, 1.0, -cx, -cy)
    return matrix_multiply(matrix_multiply(to_origin, rotation), back)


def parse_transform(transform: str | None) -> tuple[Matrix, list[str]]:
    """Parse an SVG ``transform`` attribute into one combined matrix.

    Supports ``translate``, ``scale``, ``matrix``, and ``rotate`` (optionally
    around a center). Unsupported operations (for example ``skewX``) are skipped
    with a Vietnamese warning so geometry parsing never crashes.
    """

    warnings: list[str] = []
    if not transform or not transform.strip():
        return IDENTITY, warnings

    result = IDENTITY
    matched_any = False
    for match in _TRANSFORM_RE.finditer(transform):
        name = match.group(1).lower()
        values = [float(token) for token in _NUMBER_RE.findall(match.group(2))]
        piece: Matrix | None = None
        if name == "translate" and 1 <= len(values) <= 2:
            tx = values[0]
            ty = values[1] if len(values) == 2 else 0.0
            piece = (1.0, 0.0, 0.0, 1.0, tx, ty)
        elif name == "scale" and 1 <= len(values) <= 2:
            sx = values[0]
            sy = values[1] if len(values) == 2 else sx
            piece = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        elif name == "matrix" and len(values) == 6:
            piece = (values[0], values[1], values[2], values[3], values[4], values[5])
        elif name == "rotate" and len(values) in {1, 3}:
            if len(values) == 1:
                piece = _rotate_matrix(values[0])
            else:
                piece = _rotate_matrix(values[0], values[1], values[2])
        else:
            warnings.append(
                f"Transform chưa hỗ trợ hoặc sai tham số: {name}(...). Bỏ qua phần này."
            )
            continue
        result = matrix_multiply(result, piece)
        matched_any = True

    if not matched_any and transform.strip():
        warnings.append(f"Không đọc được transform: {transform.strip()}. Bỏ qua.")
    return result, warnings


def points_attr_to_points(value: str | None) -> list[Point2D]:
    """Parse a ``points`` attribute (``x1,y1 x2,y2 ...``) into 2D points."""

    if not value:
        return []
    numbers = [float(token) for token in _NUMBER_RE.findall(value)]
    pairs = len(numbers) // 2
    return [(numbers[2 * i], numbers[2 * i + 1]) for i in range(pairs)]


def rect_to_points(element: object) -> tuple[list[Point2D], list[str]]:
    """Return the four corners of a ``<rect>`` plus any warnings.

    Rounded corners (``rx``/``ry``) are approximated as sharp corners because the
    blockout pipeline only needs the room footprint.
    """

    get = element.get  # type: ignore[attr-defined]
    x = parse_length(get("x")) or 0.0
    y = parse_length(get("y")) or 0.0
    width = parse_length(get("width"))
    height = parse_length(get("height"))
    warnings: list[str] = []
    if width is None or height is None or width <= 0.0 or height <= 0.0:
        warnings.append("Rect thiếu width/height hợp lệ; bỏ qua.")
        return [], warnings
    if get("rx") or get("ry"):
        warnings.append("Rect có bo góc (rx/ry); pipeline coi như góc vuông.")
    points = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
    ]
    return points, warnings


def parse_css_text(style_text: str | None) -> dict[str, dict[str, str]]:
    """Parse an internal ``<style>`` block into ``selector -> declarations``.

    Only flat rules (``.cls { ... }``, ``#id { ... }``, ``tag { ... }``) are
    handled. Declarations are lowercase key/value pairs. This is intentionally
    minimal: the pipeline only needs it to detect hidden elements; appearance
    (fill/stroke) does not affect extracted geometry.
    """

    rules: dict[str, dict[str, str]] = {}
    if not style_text:
        return rules
    for match in _CSS_RULE_RE.finditer(style_text):
        selectors = match.group(1)
        body = match.group(2)
        declarations: dict[str, str] = {}
        for item in body.split(";"):
            if ":" not in item:
                continue
            key, value = item.split(":", 1)
            declarations[key.strip().lower()] = value.strip().lower()
        if not declarations:
            continue
        for selector in selectors.split(","):
            selector = selector.strip()
            if selector:
                rules.setdefault(selector, {}).update(declarations)
    return rules


def declarations_hide_element(declarations: dict[str, str]) -> bool:
    """Return whether a CSS/style declaration set hides an element."""

    if declarations.get("display", "").strip() == "none":
        return True
    if declarations.get("visibility", "").strip() == "hidden":
        return True
    opacity = declarations.get("opacity", "").strip()
    return opacity in {"0", "0.0", "0.00"}

