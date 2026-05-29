"""Pure-Python room geometry helpers for Feature 001.

The MVP intentionally supports simple Illustrator-cleaned floor boundaries:
straight SVG path commands (M/L/H/V/Z), closed polygons, bounding boxes, and
wall segments. Curves are reported as unsupported so the artist can clean or
simplify the SVG before sending it to Blender.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any

Point2D = tuple[float, float]
WallSegment = tuple[Point2D, Point2D]
BBox = tuple[float, float, float, float]

COMMAND_RE = re.compile(
    r"[MmLlHhVvZzCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?",
)
COMMAND_TOKEN_RE = re.compile(r"^[A-Za-z]$")
SUPPORTED_COMMANDS = {"M", "m", "L", "l", "H", "h", "V", "v", "Z", "z"}
UNSUPPORTED_COMMANDS = {"C", "c", "S", "s", "Q", "q", "T", "t", "A", "a"}
EPSILON = 1e-6


@dataclass(frozen=True)
class RoomBoundary:
    """Closed 2D room boundary selected from SVG path data."""

    points: list[Point2D]
    bbox: BBox
    area: float
    source_path_index: int
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""

        data = asdict(self)
        data["points"] = [[x, y] for x, y in self.points]
        data["bbox"] = list(self.bbox)
        return data


def _is_command(token: str) -> bool:
    return bool(COMMAND_TOKEN_RE.match(token))


def _read_number(tokens: list[str], index: int) -> tuple[float | None, int]:
    if index >= len(tokens) or _is_command(tokens[index]):
        return None, index
    return float(tokens[index]), index + 1


def _dedupe_closing_point(points: list[Point2D]) -> list[Point2D]:
    if len(points) > 1 and points_close(points[0], points[-1]):
        return points[:-1]
    return points


def points_close(first: Point2D, second: Point2D, tolerance: float = EPSILON) -> bool:
    """Return whether two points are equal within tolerance."""

    return math.dist(first, second) <= tolerance


def parse_svg_path_points(path_data: str) -> tuple[list[Point2D], bool, list[str]]:
    """Parse simple SVG path data into absolute 2D points.

    Supports M, L, H, V, and Z commands. Relative lowercase variants are
    accepted because Illustrator can still produce them after light cleanup.
    Unsupported curves/arcs return no points plus a Vietnamese warning.
    """

    tokens = COMMAND_RE.findall(path_data or "")
    warnings: list[str] = []
    if not tokens:
        return [], False, ["Path rỗng hoặc không có dữ liệu geometry."]

    unsupported = sorted({token for token in tokens if token in UNSUPPORTED_COMMANDS})
    if unsupported:
        return [], False, [f"Path có lệnh curve/arc chưa hỗ trợ: {', '.join(unsupported)}."]

    points: list[Point2D] = []
    index = 0
    command = ""
    current: Point2D = (0.0, 0.0)
    subpath_start: Point2D | None = None
    closed = False

    while index < len(tokens):
        token = tokens[index]
        if _is_command(token):
            command = token
            index += 1
        if command and command not in SUPPORTED_COMMANDS:
            return [], False, [f"Path có lệnh chưa hỗ trợ: {command}."]

        if command in {"M", "m", "L", "l"}:
            first_pair = True
            while index < len(tokens) and not _is_command(tokens[index]):
                x_value, index = _read_number(tokens, index)
                y_value, index = _read_number(tokens, index)
                if x_value is None or y_value is None:
                    warnings.append("Path thiếu cặp tọa độ x/y.")
                    break
                if command.islower():
                    x_value += current[0]
                    y_value += current[1]
                current = (x_value, y_value)
                if command in {"M", "m"} and first_pair:
                    subpath_start = current
                points.append(current)
                first_pair = False
            if command in {"M", "m"}:
                command = "l" if command.islower() else "L"
            continue

        if command in {"H", "h"}:
            while index < len(tokens) and not _is_command(tokens[index]):
                x_value, index = _read_number(tokens, index)
                if x_value is None:
                    break
                if command.islower():
                    x_value += current[0]
                current = (x_value, current[1])
                points.append(current)
            continue

        if command in {"V", "v"}:
            while index < len(tokens) and not _is_command(tokens[index]):
                y_value, index = _read_number(tokens, index)
                if y_value is None:
                    break
                if command.islower():
                    y_value += current[1]
                current = (current[0], y_value)
                points.append(current)
            continue

        if command in {"Z", "z"}:
            closed = True
            if subpath_start is not None:
                current = subpath_start
                if points and not points_close(points[-1], subpath_start):
                    points.append(subpath_start)
            command = ""
            continue

        warnings.append("Path không bắt đầu bằng lệnh SVG hợp lệ.")
        break

    if len(points) > 2 and points_close(points[0], points[-1]):
        closed = True
    return _dedupe_closing_point(points), closed, warnings


def is_closed_path(points: list[Point2D], explicitly_closed: bool = False) -> bool:
    """Return whether a point list forms a closed polygon."""

    if explicitly_closed and len(points) >= 3:
        return True
    return len(points) >= 4 and points_close(points[0], points[-1])


def calculate_bbox(points: list[Point2D]) -> BBox:
    """Calculate an axis-aligned bbox as (min_x, min_y, max_x, max_y)."""

    if not points:
        raise ValueError("Không thể tính bbox vì path không có điểm.")
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def polygon_area(points: list[Point2D]) -> float:
    """Return absolute polygon area using the shoelace formula."""

    clean_points = _dedupe_closing_point(points)
    if len(clean_points) < 3:
        return 0.0
    total = 0.0
    for first, second in zip(clean_points, clean_points[1:] + clean_points[:1], strict=False):
        total += first[0] * second[1] - second[0] * first[1]
    return abs(total) / 2.0


def normalize_points_to_origin(points: list[Point2D]) -> list[Point2D]:
    """Move points so the bbox minimum sits at local origin."""

    min_x, min_y, _, _ = calculate_bbox(points)
    return [(x - min_x, y - min_y) for x, y in points]


def scale_points_to_blender(
    points: list[Point2D],
    scale: float = 0.01,
    invert_y: bool = True,
) -> list[Point2D]:
    """Scale SVG units to Blender units, optionally flipping SVG's Y axis."""

    y_multiplier = -1.0 if invert_y else 1.0
    return [(x * scale, y * scale * y_multiplier) for x, y in points]


def create_wall_segments(points: list[Point2D]) -> list[WallSegment]:
    """Create ordered wall segments from a closed boundary."""

    clean_points = _dedupe_closing_point(points)
    if len(clean_points) < 3:
        raise ValueError("Cần ít nhất 3 điểm để tạo tường phòng.")
    return list(zip(clean_points, clean_points[1:] + clean_points[:1], strict=False))


def choose_largest_closed_boundary(path_data_items: list[str]) -> RoomBoundary | None:
    """Choose the largest closed path as the room floor boundary."""

    best: RoomBoundary | None = None
    collected_warnings: list[str] = []
    for index, path_data in enumerate(path_data_items):
        points, closed, warnings = parse_svg_path_points(path_data)
        collected_warnings.extend(f"path {index}: {warning}" for warning in warnings)
        if not closed or len(points) < 3:
            if points:
                collected_warnings.append(f"path {index}: path chưa đóng kín, bỏ qua.")
            continue
        area = polygon_area(points)
        if area <= EPSILON:
            collected_warnings.append(f"path {index}: diện tích quá nhỏ, bỏ qua.")
            continue
        boundary = RoomBoundary(
            points=points,
            bbox=calculate_bbox(points),
            area=area,
            source_path_index=index,
            warnings=list(warnings),
        )
        if best is None or boundary.area > best.area:
            best = boundary

    if best is not None:
        merged_warnings = [*collected_warnings, *best.warnings]
        return RoomBoundary(
            points=best.points,
            bbox=best.bbox,
            area=best.area,
            source_path_index=best.source_path_index,
            warnings=list(dict.fromkeys(merged_warnings)),
        )
    return None
