"""Detect room candidates from a clean SVG file.

Feature 001 uses this module as the pure-Python SVG inspection layer before
handing selected geometry to Blender. It never modifies the source SVG.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from clean_svg_paths import (
    configure_stdio,
    is_hidden_element,
    load_svg_tree,
    local_name,
)
from manifest import normalize_asset_name
from room_geometry import (
    RoomBoundary,
    ShapeCandidate,
    calculate_bbox,
    choose_largest_closed_boundary_from_candidates,
    is_closed_path,
    parse_svg_path_points,
)
from svg_shapes import (
    CONTAINER_TAGS,
    SKIP_SUBTREE_TAGS,
    SUPPORTED_SHAPES,
    UNSUPPORTED_DRAWABLE,
    Matrix,
    Point2D,
    declarations_hide_element,
    is_identity,
    matrix_multiply,
    parse_css_text,
    parse_transform,
    points_attr_to_points,
    rect_to_points,
    transform_points,
)

INKSCAPE_LABEL_ATTR = "{http://www.inkscape.org/namespaces/inkscape}label"
PROP_MARKER_PREFIXES = ("prop_", "item_", "object_")
OPENING_MARKER_PREFIXES = ("door_", "window_")
PROP_ROTATION_SUFFIX_RE = re.compile(
    r"_(?:rot(?P<short>90|180|270)|rotation_(?P<long>90|180|270))$"
)


@dataclass(frozen=True)
class PropMarker:
    """Artist-authored placeholder prop marker from a named SVG group/layer."""

    prop_type: str
    original_label: str
    group_path: list[str]
    center_svg: Point2D
    bbox_svg: tuple[float, float, float, float]
    source_kind: str
    rotation_y_degrees: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""

        return {
            "prop_type": self.prop_type,
            "original_label": self.original_label,
            "group_path": list(self.group_path),
            "center_svg": [self.center_svg[0], self.center_svg[1]],
            "bbox_svg": list(self.bbox_svg),
            "source_kind": self.source_kind,
            "rotation_y_degrees": self.rotation_y_degrees,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class OpeningMarker:
    """Artist-authored door/window marker from a named SVG group/layer."""

    marker_type: str
    marker_name: str
    source_name: str
    group_path: list[str]
    center_svg: Point2D
    bbox_svg: tuple[float, float, float, float]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""

        return {
            "marker_type": self.marker_type,
            "marker_name": self.marker_name,
            "source_name": self.source_name,
            "group_path": list(self.group_path),
            "center_svg": [self.center_svg[0], self.center_svg[1]],
            "bbox_svg": list(self.bbox_svg),
        }


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
    shape_kinds: dict[str, int] = field(default_factory=dict)
    unsupported_elements: list[str] = field(default_factory=list)
    transform_applied: bool = False
    group_path: list[str] = field(default_factory=list)
    prop_markers: list[PropMarker] = field(default_factory=list)
    opening_markers: list[OpeningMarker] = field(default_factory=list)

    @property
    def has_usable_boundary(self) -> bool:
        """Return whether the room can be sent to Blender."""

        return self.boundary is not None

    def to_dict(self, include_boundary: bool = False) -> dict[str, Any]:
        """Return a JSON-friendly representation."""

        data = asdict(self)
        data["bbox"] = list(self.bbox) if self.bbox else None
        data["prop_markers"] = [marker.to_dict() for marker in self.prop_markers]
        data["opening_markers"] = [marker.to_dict() for marker in self.opening_markers]
        if include_boundary and self.boundary is not None:
            data["boundary"] = self.boundary.to_dict()
        else:
            data.pop("boundary", None)
        return data


def normalize_room_name(label: str) -> str:
    """Normalize a group/layer label into the shared asset-name convention.

    Only structural scaffolding prefixes (``room_``, ``room-``, ``room ``,
    ``layer_``) are stripped. The Vietnamese word ``phong`` ("phòng"/room) is
    kept because it is meaningful content: a real label like ``Phòng Ngủ``
    normalizes to ``phong_ngu``, which the naming convention treats as the final
    room name. Stripping it would make the function non-idempotent and break the
    round-trip between detection output and ``--room`` selection.
    """

    clean = label.strip()
    lowered = clean.lower()
    for prefix in ("room_", "room-", "room ", "layer_"):
        if lowered.startswith(prefix):
            clean = clean[len(prefix) :]
            break
    return normalize_asset_name(clean)


def normalize_prop_marker_type(label: str) -> str | None:
    """Return the normalized prop type for prop/item/object marker labels."""

    normalized, _rotation = normalize_prop_marker_label(label)
    return normalized


def normalize_prop_marker_label(label: str) -> tuple[str | None, int]:
    """Return normalized prop type and optional Y-axis rotation for a marker label."""

    normalized = normalize_asset_name(label.strip())
    for prefix in PROP_MARKER_PREFIXES:
        if normalized.startswith(prefix) and len(normalized) > len(prefix):
            prop_type = normalized[len(prefix) :]
            rotation = 0
            suffix_match = PROP_ROTATION_SUFFIX_RE.search(prop_type)
            if suffix_match:
                rotation = int(suffix_match.group("short") or suffix_match.group("long"))
                prop_type = prop_type[: suffix_match.start()]
            return prop_type, rotation
    return None, 0


def normalize_opening_marker_label(label: str) -> tuple[str | None, str | None]:
    """Return marker type/name for door/window marker labels."""

    normalized = normalize_asset_name(label.strip())
    for prefix in OPENING_MARKER_PREFIXES:
        if normalized.startswith(prefix) and len(normalized) > len(prefix):
            return prefix[:-1], normalized[len(prefix) :]
    return None, None


def _element_label(element: object) -> str:
    get = element.get  # type: ignore[attr-defined]
    return (
        get(INKSCAPE_LABEL_ATTR)
        or get("inkscape:label")
        or get("data-name")
        or get("id")
        or ""
    ).strip()


def _element_classes(element: object) -> list[str]:
    raw = element.get("class") or ""  # type: ignore[attr-defined]
    return [token for token in raw.split() if token]


def _element_hidden(element: object, css_rules: dict[str, dict[str, str]]) -> bool:
    """Return whether an element is hidden via attribute, style, or CSS class."""

    if is_hidden_element(element):
        return True
    element_id = element.get("id")  # type: ignore[attr-defined]
    if element_id and declarations_hide_element(css_rules.get(f"#{element_id}", {})):
        return True
    for class_name in _element_classes(element):
        if declarations_hide_element(css_rules.get(f".{class_name}", {})):
            return True
    return False


def _shape_points(
    element: object,
    matrix: Matrix,
) -> tuple[list[Point2D], bool, str, list[str]]:
    """Extract absolute, transform-applied points for one supported shape."""

    tag = local_name(element.tag).lower()  # type: ignore[attr-defined]
    warnings: list[str] = []
    if tag == "path":
        points, closed, warnings = parse_svg_path_points(element.get("d") or "")  # type: ignore[attr-defined]
    elif tag == "rect":
        points, warnings = rect_to_points(element)
        closed = bool(points)
    elif tag == "polygon":
        points = points_attr_to_points(element.get("points"))  # type: ignore[attr-defined]
        closed = len(points) >= 3
    elif tag == "polyline":
        points = points_attr_to_points(element.get("points"))  # type: ignore[attr-defined]
        closed = is_closed_path(points)
    else:  # pragma: no cover - guarded by SUPPORTED_SHAPES upstream
        return [], False, tag, []
    return transform_points(matrix, points), closed, tag, warnings


@dataclass
class _RoomBucket:
    """Mutable accumulator for one named room (or the top-level fallback)."""

    label: str
    group_path: list[str]
    candidates: list[ShapeCandidate] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    transform_warnings: list[str] = field(default_factory=list)
    prop_warnings: list[str] = field(default_factory=list)
    opening_warnings: list[str] = field(default_factory=list)
    prop_markers: list[PropMarker] = field(default_factory=list)
    opening_markers: list[OpeningMarker] = field(default_factory=list)
    transform_applied: bool = False


@dataclass
class _PropMarkerBucket:
    """Mutable accumulator for one prop marker group/layer."""

    prop_type: str
    rotation_y_degrees: int
    original_label: str
    group_path: list[str]
    candidates: list[ShapeCandidate] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    transform_applied: bool = False


@dataclass
class _OpeningMarkerBucket:
    """Mutable accumulator for one door/window marker group/layer."""

    marker_type: str
    marker_name: str
    source_name: str
    group_path: list[str]
    candidates: list[ShapeCandidate] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    transform_applied: bool = False


def _collect_prop_marker_shapes(
    element: object,
    matrix: Matrix,
    css_rules: dict[str, dict[str, str]],
    marker: _PropMarkerBucket,
) -> None:
    """Collect supported marker geometry inside one prop marker group."""

    for child in list(element):  # type: ignore[call-overload]
        tag_raw = getattr(child, "tag", None)
        if not isinstance(tag_raw, str):
            continue
        tag = local_name(tag_raw).lower()
        if tag in SKIP_SUBTREE_TAGS:
            continue
        if _element_hidden(child, css_rules):
            continue

        child_matrix, transform_warnings = matrix, []
        own_transform = child.get("transform")  # type: ignore[attr-defined]
        if own_transform:
            own_matrix, transform_warnings = parse_transform(own_transform)
            child_matrix = matrix_multiply(matrix, own_matrix)
            marker.warnings.extend(transform_warnings)

        if tag in CONTAINER_TAGS:
            _collect_prop_marker_shapes(child, child_matrix, css_rules, marker)
            continue

        if tag in SUPPORTED_SHAPES:
            points, closed, kind, warnings = _shape_points(child, child_matrix)
            if not is_identity(child_matrix):
                marker.transform_applied = True
            marker.candidates.append(
                ShapeCandidate(
                    points=points,
                    closed=closed,
                    source_index=len(marker.candidates),
                    source_kind=kind,
                    warnings=warnings,
                )
            )
            continue

        if tag in UNSUPPORTED_DRAWABLE:
            element_id = child.get("id") or ""  # type: ignore[attr-defined]
            label = f"<{tag}>" + (f" id={element_id}" if element_id else "")
            marker.unsupported.append(label)
            continue

        marker.unsupported.append(f"<{tag}>")


def _collect_opening_marker_shapes(
    element: object,
    matrix: Matrix,
    css_rules: dict[str, dict[str, str]],
    marker: _OpeningMarkerBucket,
) -> None:
    """Collect supported marker geometry inside one door/window marker group."""

    for child in list(element):  # type: ignore[call-overload]
        tag_raw = getattr(child, "tag", None)
        if not isinstance(tag_raw, str):
            continue
        tag = local_name(tag_raw).lower()
        if tag in SKIP_SUBTREE_TAGS:
            continue
        if _element_hidden(child, css_rules):
            continue

        child_matrix, transform_warnings = matrix, []
        own_transform = child.get("transform")  # type: ignore[attr-defined]
        if own_transform:
            own_matrix, transform_warnings = parse_transform(own_transform)
            child_matrix = matrix_multiply(matrix, own_matrix)
            marker.warnings.extend(transform_warnings)

        if tag in CONTAINER_TAGS:
            _collect_opening_marker_shapes(child, child_matrix, css_rules, marker)
            continue

        if tag in SUPPORTED_SHAPES:
            points, closed, kind, warnings = _shape_points(child, child_matrix)
            if not is_identity(child_matrix):
                marker.transform_applied = True
            marker.candidates.append(
                ShapeCandidate(
                    points=points,
                    closed=closed,
                    source_index=len(marker.candidates),
                    source_kind=kind,
                    warnings=warnings,
                )
            )
            continue

        if tag in UNSUPPORTED_DRAWABLE:
            element_id = child.get("id") or ""  # type: ignore[attr-defined]
            label = f"<{tag}>" + (f" id={element_id}" if element_id else "")
            marker.unsupported.append(label)
            continue

        marker.unsupported.append(f"<{tag}>")


def _make_prop_marker(marker: _PropMarkerBucket) -> tuple[PropMarker | None, list[str]]:
    """Create a prop marker from collected geometry, or return skip warnings."""

    warnings: list[str] = list(marker.warnings)
    all_points: list[Point2D] = []
    source_kinds: list[str] = []
    for candidate in marker.candidates:
        warnings.extend(
            f"shape {candidate.source_index} ({candidate.source_kind}): {warning}"
            for warning in candidate.warnings
        )
        if candidate.points:
            all_points.extend(candidate.points)
            source_kinds.append(candidate.source_kind)

    if marker.unsupported:
        unique_unsupported = list(dict.fromkeys(marker.unsupported))
        warnings.append(
            f"Prop marker '{marker.original_label}' có phần tử chưa hỗ trợ, đã bỏ qua: "
            + ", ".join(unique_unsupported)
            + "."
        )

    if not all_points:
        warnings.append(
            f"Prop marker '{marker.original_label}' không có rect/path/polygon/polyline hợp lệ; bỏ qua."
        )
        return None, list(dict.fromkeys(warnings))

    bbox = calculate_bbox(all_points)
    min_x, min_y, max_x, max_y = bbox
    unique_kinds = list(dict.fromkeys(source_kinds))
    source_kind = unique_kinds[0] if len(unique_kinds) == 1 else "mixed"
    return (
        PropMarker(
            prop_type=marker.prop_type,
            original_label=marker.original_label,
            group_path=list(marker.group_path),
            center_svg=((min_x + max_x) / 2.0, (min_y + max_y) / 2.0),
            bbox_svg=bbox,
            source_kind=source_kind,
            rotation_y_degrees=marker.rotation_y_degrees,
            warnings=list(dict.fromkeys(warnings)),
        ),
        [],
    )


def _make_opening_marker(
    marker: _OpeningMarkerBucket,
) -> tuple[OpeningMarker | None, list[str]]:
    """Create a door/window marker from collected geometry, or return skip warnings."""

    warnings: list[str] = list(marker.warnings)
    all_points: list[Point2D] = []
    for candidate in marker.candidates:
        warnings.extend(
            f"shape {candidate.source_index} ({candidate.source_kind}): {warning}"
            for warning in candidate.warnings
        )
        if candidate.points:
            all_points.extend(candidate.points)

    if marker.unsupported:
        unique_unsupported = list(dict.fromkeys(marker.unsupported))
        warnings.append(
            f"Opening marker '{marker.source_name}' chưa hỗ trợ một số phần tử, đã bỏ qua: "
            + ", ".join(unique_unsupported)
            + "."
        )

    if not all_points:
        warnings.append(
            f"Opening marker '{marker.source_name}' không có rect/path/polygon/polyline hợp lệ; bỏ qua."
        )
        return None, list(dict.fromkeys(warnings))

    bbox = calculate_bbox(all_points)
    min_x, min_y, max_x, max_y = bbox
    return (
        OpeningMarker(
            marker_type=marker.marker_type,
            marker_name=marker.marker_name,
            source_name=marker.source_name,
            group_path=list(marker.group_path),
            center_svg=((min_x + max_x) / 2.0, (min_y + max_y) / 2.0),
            bbox_svg=bbox,
        ),
        [],
    )


def _collect_shapes(
    element: object,
    matrix: Matrix,
    css_rules: dict[str, dict[str, str]],
    current: _RoomBucket,
    buckets: "list[_RoomBucket]",
    group_path: list[str],
) -> None:
    """Recursively traverse a container, attributing shapes to nearest named room."""

    for child in list(element):  # type: ignore[call-overload]
        tag_raw = getattr(child, "tag", None)
        if not isinstance(tag_raw, str):
            continue
        tag = local_name(tag_raw).lower()
        if tag in SKIP_SUBTREE_TAGS:
            continue
        if _element_hidden(child, css_rules):
            continue

        child_matrix, transform_warnings = matrix, []
        own_transform = child.get("transform")  # type: ignore[attr-defined]
        if own_transform:
            own_matrix, transform_warnings = parse_transform(own_transform)
            child_matrix = matrix_multiply(matrix, own_matrix)

        if tag in CONTAINER_TAGS:
            label = _element_label(child)
            if label:
                marker_type, marker_name = normalize_opening_marker_label(label)
                if marker_type and marker_name:
                    marker_bucket = _OpeningMarkerBucket(
                        marker_type=marker_type,
                        marker_name=marker_name,
                        source_name=label,
                        group_path=[*group_path, label],
                        warnings=list(transform_warnings),
                    )
                    _collect_opening_marker_shapes(
                        child,
                        child_matrix,
                        css_rules,
                        marker_bucket,
                    )
                    opening_marker, opening_warnings = _make_opening_marker(marker_bucket)
                    if opening_marker is not None:
                        current.opening_markers.append(opening_marker)
                    current.opening_warnings.extend(opening_warnings)
                    if marker_bucket.transform_applied:
                        current.transform_applied = True
                    continue

                prop_type, rotation_y_degrees = normalize_prop_marker_label(label)
                if prop_type:
                    marker_bucket = _PropMarkerBucket(
                        prop_type=prop_type,
                        rotation_y_degrees=rotation_y_degrees,
                        original_label=label,
                        group_path=[*group_path, label],
                        warnings=list(transform_warnings),
                    )
                    _collect_prop_marker_shapes(child, child_matrix, css_rules, marker_bucket)
                    prop_marker, prop_warnings = _make_prop_marker(marker_bucket)
                    if prop_marker is not None:
                        current.prop_markers.append(prop_marker)
                    current.prop_warnings.extend(prop_warnings)
                    if marker_bucket.transform_applied:
                        current.transform_applied = True
                    continue

                current.transform_warnings.extend(transform_warnings)
                bucket = _RoomBucket(label=label, group_path=[*group_path, label])
                buckets.append(bucket)
                _collect_shapes(child, child_matrix, css_rules, bucket, buckets, bucket.group_path)
            else:
                current.transform_warnings.extend(transform_warnings)
                _collect_shapes(child, child_matrix, css_rules, current, buckets, group_path)
            continue

        if tag in SUPPORTED_SHAPES:
            current.transform_warnings.extend(transform_warnings)
            points, closed, kind, warnings = _shape_points(child, child_matrix)
            if not is_identity(child_matrix):
                current.transform_applied = True
            current.candidates.append(
                ShapeCandidate(
                    points=points,
                    closed=closed,
                    source_index=len(current.candidates),
                    source_kind=kind,
                    warnings=warnings,
                )
            )
            continue

        if tag in UNSUPPORTED_DRAWABLE:
            current.transform_warnings.extend(transform_warnings)
            element_id = child.get("id") or ""  # type: ignore[attr-defined]
            label = f"<{tag}>" + (f" id={element_id}" if element_id else "")
            current.unsupported.append(label)
            continue

        # Unknown/decorative element: warn but keep going.
        current.transform_warnings.extend(transform_warnings)
        current.unsupported.append(f"<{tag}>")


def _make_room_report_from_bucket(label: str, bucket: _RoomBucket) -> RoomReport:
    room_name = normalize_room_name(label)
    warnings: list[str] = [
        *bucket.transform_warnings,
        *bucket.prop_warnings,
        *bucket.opening_warnings,
    ]
    boundary = choose_largest_closed_boundary_from_candidates(bucket.candidates)
    closed_count = sum(
        1
        for candidate in bucket.candidates
        if (candidate.closed or is_closed_path(candidate.points)) and len(candidate.points) >= 3
    )
    shape_kinds: dict[str, int] = {}
    for candidate in bucket.candidates:
        shape_kinds[candidate.source_kind] = shape_kinds.get(candidate.source_kind, 0) + 1

    bbox = boundary.bbox if boundary else None
    if not bucket.candidates:
        warnings.append("Không tìm thấy hình (path/rect/polygon/polyline) trong group/layer này.")
    if bucket.candidates and closed_count == 0:
        warnings.append(
            "Không có path đóng kín để làm boundary phòng. "
            "Hãy kiểm tra path/rect/polygon có khép kín không."
        )
        all_points = [point for candidate in bucket.candidates for point in candidate.points]
        if all_points:
            bbox = calculate_bbox(all_points)
    if bucket.unsupported:
        unique_unsupported = list(dict.fromkeys(bucket.unsupported))
        warnings.append(
            "SVG có phần tử chưa hỗ trợ, pipeline đã bỏ qua: "
            + ", ".join(unique_unsupported)
            + "."
        )
    if boundary and boundary.warnings:
        warnings.extend(boundary.warnings)

    return RoomReport(
        room_name=room_name,
        original_label=label,
        path_count=len(bucket.candidates),
        closed_path_count=closed_count,
        bbox=bbox,
        warnings=list(dict.fromkeys(warnings)),
        boundary=boundary,
        shape_kinds=shape_kinds,
        unsupported_elements=list(dict.fromkeys(bucket.unsupported)),
        transform_applied=bucket.transform_applied,
        group_path=list(bucket.group_path),
        prop_markers=list(bucket.prop_markers),
        opening_markers=list(bucket.opening_markers),
    )


def _collect_css_rules(root: object) -> dict[str, dict[str, str]]:
    rules: dict[str, dict[str, str]] = {}
    for element in root.iter():  # type: ignore[attr-defined]
        tag = getattr(element, "tag", "")
        if isinstance(tag, str) and local_name(tag).lower() == "style":
            css_text = "".join(element.itertext()) if hasattr(element, "itertext") else (
                getattr(element, "text", "") or ""
            )
            for selector, declarations in parse_css_text(css_text).items():
                rules.setdefault(selector, {}).update(declarations)
    return rules


def detect_rooms(svg_path: Path) -> list[RoomReport]:
    """Detect named room groups/layers from a clean SVG file.

    Handles nested groups, parent transform accumulation, multiple shape types
    (path/rect/polygon/polyline), CSS classes for hidden elements, and warns on
    unsupported elements instead of crashing.
    """

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

    css_rules = _collect_css_rules(root)
    root_matrix, _ = parse_transform(root.get("transform"))  # type: ignore[attr-defined]
    top_level = _RoomBucket(label=svg_path.stem, group_path=[])
    buckets: list[_RoomBucket] = []
    _collect_shapes(root, root_matrix, css_rules, top_level, buckets, [])

    named_with_shapes = [bucket for bucket in buckets if bucket.candidates]
    reports = [
        _make_room_report_from_bucket(bucket.label, bucket) for bucket in named_with_shapes
    ]

    if not reports and top_level.candidates:
        reports.append(_make_room_report_from_bucket(svg_path.stem, top_level))

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
    if report.group_path:
        print(f"  Đường dẫn group: {' > '.join(report.group_path)}")
    print(f"  Số hình: {report.path_count}; đường bao đóng kín: {report.closed_path_count}")
    if report.shape_kinds:
        kinds = ", ".join(f"{kind}={count}" for kind, count in sorted(report.shape_kinds.items()))
        print(f"  Loại hình: {kinds}")
    if report.transform_applied:
        print("  Transform: đã áp dụng transform từ group/shape vào tọa độ.")
    if report.bbox:
        min_x, min_y, max_x, max_y = report.bbox
        print(f"  BBox: ({min_x:.3f}, {min_y:.3f}) - ({max_x:.3f}, {max_y:.3f})")
    if report.unsupported_elements:
        print(f"  Phần tử bỏ qua: {', '.join(report.unsupported_elements)}")
    if report.prop_markers:
        props = ", ".join(marker.prop_type for marker in report.prop_markers)
        print(f"  Prop marker: {props}")
        for marker in report.prop_markers:
            for warning in marker.warnings:
                print(f"  Cảnh báo prop {marker.original_label}: {warning}")
    if report.opening_markers:
        openings = ", ".join(
            f"{marker.marker_type}:{marker.marker_name}" for marker in report.opening_markers
        )
        print(f"  Opening marker: {openings}")
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
