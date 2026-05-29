"""Detect room candidates from a clean SVG file.

Feature 001 uses this module as the pure-Python SVG inspection layer before
handing selected geometry to Blender. It never modifies the source SVG.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from clean_svg_paths import configure_stdio, iter_elements, load_svg_tree, local_name
from manifest import normalize_asset_name
from room_geometry import (
    RoomBoundary,
    calculate_bbox,
    choose_largest_closed_boundary,
    parse_svg_path_points,
)

INKSCAPE_LABEL_ATTR = "{http://www.inkscape.org/namespaces/inkscape}label"


@dataclass
class RoomReport:
    """Room detection summary for one SVG group or fallback path set."""

    room_name: str
    original_label: str
    path_count: int
    closed_path_count: int
    bbox: tuple[float, float, float, float] | None
    warnings: list[str] = field(default_factory=list)
    boundary: RoomBoundary | None = None

    @property
    def has_usable_boundary(self) -> bool:
        """Return whether the room can be sent to Blender."""

        return self.boundary is not None

    def to_dict(self, include_boundary: bool = False) -> dict[str, Any]:
        """Return a JSON-friendly representation."""

        data = asdict(self)
        data["bbox"] = list(self.bbox) if self.bbox else None
        if include_boundary and self.boundary is not None:
            data["boundary"] = self.boundary.to_dict()
        else:
            data.pop("boundary", None)
        return data


def normalize_room_name(label: str) -> str:
    """Normalize a group/layer label into the shared asset-name convention."""

    clean = label.strip()
    lowered = clean.lower()
    for prefix in ("room_", "room-", "room ", "phong_", "phong-", "layer_"):
        if lowered.startswith(prefix):
            clean = clean[len(prefix) :]
            break
    return normalize_asset_name(clean)


def _element_label(element: object) -> str:
    get = element.get  # type: ignore[attr-defined]
    return (
        get(INKSCAPE_LABEL_ATTR)
        or get("inkscape:label")
        or get("data-name")
        or get("id")
        or ""
    ).strip()


def _path_data_under(element: object) -> list[str]:
    path_data: list[str] = []
    for child in iter_elements(element):
        if local_name(child.tag) == "path":  # type: ignore[attr-defined]
            data = (child.get("d") or "").strip()  # type: ignore[attr-defined]
            if data:
                path_data.append(data)
    return path_data


def _closed_path_count(path_data_items: list[str]) -> int:
    count = 0
    for path_data in path_data_items:
        points, closed, _ = parse_svg_path_points(path_data)
        if closed and len(points) >= 3:
            count += 1
    return count


def _make_room_report(label: str, path_data_items: list[str]) -> RoomReport:
    room_name = normalize_room_name(label)
    warnings: list[str] = []
    boundary = choose_largest_closed_boundary(path_data_items)
    closed_count = _closed_path_count(path_data_items)
    bbox = boundary.bbox if boundary else None

    if not path_data_items:
        warnings.append("Không tìm thấy path nào trong group/layer này.")
    if path_data_items and closed_count == 0:
        warnings.append("Không có path đóng kín để làm boundary phòng.")
        point_sets = [
            points
            for path_data in path_data_items
            for points, _closed, _warnings in [parse_svg_path_points(path_data)]
            if points
        ]
        if point_sets:
            all_points = [point for points in point_sets for point in points]
            bbox = calculate_bbox(all_points)
    if boundary and boundary.warnings:
        warnings.extend(boundary.warnings)

    return RoomReport(
        room_name=room_name,
        original_label=label,
        path_count=len(path_data_items),
        closed_path_count=closed_count,
        bbox=bbox,
        warnings=list(dict.fromkeys(warnings)),
        boundary=boundary,
    )


def _candidate_groups(root: object) -> list[object]:
    groups: list[object] = []
    for element in iter_elements(root):
        if local_name(element.tag) != "g":  # type: ignore[attr-defined]
            continue
        label = _element_label(element)
        if not label:
            continue
        if _path_data_under(element):
            groups.append(element)
    return groups


def detect_rooms(svg_path: Path) -> list[RoomReport]:
    """Detect named room groups/layers from a clean SVG file."""

    svg_path = svg_path.resolve()
    if not svg_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file SVG: {svg_path}")
    if svg_path.suffix.lower() != ".svg":
        raise ValueError("Input phải là file .svg.")

    try:
        _tree, root = load_svg_tree(svg_path)
    except Exception as exc:
        raise ValueError(f"SVG không hợp lệ hoặc bị lỗi XML: {exc}") from exc

    if local_name(root.tag).lower() != "svg":  # type: ignore[attr-defined]
        raise ValueError("File không phải SVG hợp lệ.")

    reports: list[RoomReport] = []
    groups = _candidate_groups(root)
    for group in groups:
        label = _element_label(group)
        reports.append(_make_room_report(label, _path_data_under(group)))

    if not reports:
        top_level_paths = [
            (element.get("d") or "").strip()  # type: ignore[attr-defined]
            for element in iter_elements(root)
            if local_name(element.tag) == "path" and (element.get("d") or "").strip()  # type: ignore[attr-defined]
        ]
        if top_level_paths:
            reports.append(_make_room_report(svg_path.stem, top_level_paths))

    return reports


def write_json_report(reports: list[RoomReport], json_report: Path) -> None:
    """Write room detection results to JSON."""

    json_report.parent.mkdir(parents=True, exist_ok=True)
    payload = [report.to_dict(include_boundary=True) for report in reports]
    json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def print_room_report(report: RoomReport) -> None:
    """Print one room report in Vietnamese."""

    status = "OK" if report.has_usable_boundary else "CHƯA DÙNG ĐƯỢC"
    print(f"- {report.room_name} ({status})")
    print(f"  Nhãn gốc: {report.original_label}")
    print(f"  Số path: {report.path_count}; path đóng kín: {report.closed_path_count}")
    if report.bbox:
        min_x, min_y, max_x, max_y = report.bbox
        print(f"  BBox: ({min_x:.3f}, {min_y:.3f}) - ({max_x:.3f}, {max_y:.3f})")
    for warning in report.warnings:
        print(f"  Cảnh báo: {warning}")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Phát hiện phòng/layer từ SVG sạch cho pipeline isometric.",
    )
    parser.add_argument("--input", required=True, type=Path, help="File SVG sạch.")
    parser.add_argument("--json-report", type=Path, help="Ghi báo cáo JSON tùy chọn.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the room detection CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        reports = detect_rooms(args.input)
    except (OSError, ValueError) as exc:
        print(f"ERR_SVG_INVALID: Không thể đọc SVG. Chi tiết: {exc}", file=sys.stderr)
        return 2

    print("TuPhuongVoLo-ArtPipeline - Phát hiện phòng từ SVG")
    if not reports:
        print(
            "ERR_ROOM_NOT_FOUND: Không tìm thấy group hoặc path phòng trong SVG.",
            file=sys.stderr,
        )
        return 1

    for report in reports:
        print_room_report(report)

    if args.json_report:
        write_json_report(reports, args.json_report)
        print(f"Đã ghi JSON report: {args.json_report}")

    if not any(report.has_usable_boundary for report in reports):
        print(
            "ERR_ROOM_BOUNDARY: Không tìm thấy boundary phòng đóng kín để dựng Blender.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
