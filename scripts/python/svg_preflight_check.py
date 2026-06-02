"""Read-only SVG preflight checker for real Illustrator SVG tests.

Phase 007M adds a soft safety check before the Maya build step. Unlike the
clean SVG contract validator, this checker reports warnings without failing the
run; only fatal input problems return a non-zero exit code.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_VERSION = "0.7.10"
APP_PHASE = "007M"

CANONICAL_TAG_NAMES = {
    "clippath": "clipPath",
}
SUPPORTED_ELEMENTS = frozenset({"rect", "polygon", "polyline", "path", "g"})
VISIBLE_SHAPE_ELEMENTS = frozenset({"rect", "polygon", "polyline", "path"})
RISKY_ELEMENTS = frozenset(
    {
        "image",
        "use",
        "symbol",
        "clippath",
        "mask",
        "pattern",
        "text",
        "circle",
        "ellipse",
        "line",
    }
)
PROP_MARKERS = ("prop_", "item_", "object_")
ORIENTATION_MARKERS = (
    "rot90",
    "rot180",
    "rot270",
    "rotation_90",
    "rotation_180",
    "rotation_270",
)
DOOR_WINDOW_MARKERS = ("door_", "window_")
MATERIAL_MARKERS = ("mat_", "material_", "color_")


@dataclass
class MarkerCandidate:
    """Small marker hit that can help the artist debug naming in Illustrator."""

    tag: str
    value: str


@dataclass
class PreflightReport:
    """Summary for one SVG preflight run."""

    input_path: str
    status: str
    checks: dict[str, bool] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    supported_elements: dict[str, int] = field(default_factory=dict)
    risky_elements: dict[str, int] = field(default_factory=dict)
    hidden_elements: list[str] = field(default_factory=list)
    prop_marker_candidates: list[MarkerCandidate] = field(default_factory=list)
    orientation_marker_candidates: list[MarkerCandidate] = field(default_factory=list)
    door_window_marker_candidates: list[MarkerCandidate] = field(default_factory=list)
    material_color_candidates: list[MarkerCandidate] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fatal_errors: list[str] = field(default_factory=list)


def configure_stdio() -> None:
    """Make Vietnamese CLI text safe on Windows shells with legacy code pages."""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def local_name(tag: str) -> str:
    """Return an XML tag name without namespace."""

    if "}" in tag:
        return tag.rsplit("}", 1)[1].lower()
    return tag.lower()


def canonical_tag_name(tag: str) -> str:
    """Return the SVG spelling used in reports."""

    normalized = local_name(tag)
    return CANONICAL_TAG_NAMES.get(normalized, normalized)


def parse_style(style: str | None) -> dict[str, str]:
    """Parse a small inline CSS declaration string."""

    declarations: dict[str, str] = {}
    if not style:
        return declarations
    for part in style.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        declarations[key.strip().lower()] = value.strip().lower()
    return declarations


def element_label(element: ET.Element) -> str:
    """Return a compact label for reports."""

    tag = local_name(element.tag)
    element_id = element.get("id")
    if element_id:
        return f"{tag}#{element_id}"
    return tag


def element_is_hidden(element: ET.Element) -> bool:
    """Return whether an element is visibly hidden by common SVG attributes."""

    style = parse_style(element.get("style"))
    display = (element.get("display") or style.get("display") or "").strip().lower()
    visibility = (element.get("visibility") or style.get("visibility") or "").strip().lower()
    opacity = (element.get("opacity") or style.get("opacity") or "").strip().lower()
    return display == "none" or visibility == "hidden" or opacity in {"0", "0.0", "0.00"}


def marker_text(element: ET.Element) -> str:
    """Collect useful naming attributes into one searchable marker string."""

    values: list[str] = []
    for raw_key, raw_value in element.attrib.items():
        key = local_name(raw_key)
        if key in {"id", "class", "label", "name"} or key.startswith("data-"):
            values.append(str(raw_value))
    return " ".join(values).strip()


def add_marker_hit(
    target: list[MarkerCandidate],
    element: ET.Element,
    text: str,
    markers: tuple[str, ...],
) -> None:
    """Append one marker hit if the element naming text contains a marker."""

    normalized = text.lower()
    if any(marker in normalized for marker in markers):
        target.append(MarkerCandidate(local_name(element.tag), text))


def walk_svg(
    element: ET.Element,
    report: PreflightReport,
    inherited_hidden: bool = False,
) -> None:
    """Traverse the SVG tree and collect read-only preflight facts."""

    tag = local_name(element.tag)
    is_hidden = inherited_hidden or element_is_hidden(element)

    report_tag = canonical_tag_name(element.tag)
    if tag in SUPPORTED_ELEMENTS:
        report.supported_elements[report_tag] = report.supported_elements.get(report_tag, 0) + 1
    if tag in RISKY_ELEMENTS:
        report.risky_elements[report_tag] = report.risky_elements.get(report_tag, 0) + 1
    if is_hidden:
        report.hidden_elements.append(element_label(element))
    if tag in VISIBLE_SHAPE_ELEMENTS and not is_hidden:
        report.counts["visible_shape_candidates"] = report.counts.get("visible_shape_candidates", 0) + 1

    text = marker_text(element)
    if text:
        add_marker_hit(report.prop_marker_candidates, element, text, PROP_MARKERS)
        add_marker_hit(report.orientation_marker_candidates, element, text, ORIENTATION_MARKERS)
        add_marker_hit(report.door_window_marker_candidates, element, text, DOOR_WINDOW_MARKERS)
        add_marker_hit(report.material_color_candidates, element, text, MATERIAL_MARKERS)

    for child in list(element):
        walk_svg(child, report, inherited_hidden=is_hidden)


def fatal_report(input_path: Path, message: str, checks: dict[str, bool] | None = None) -> PreflightReport:
    """Create a report for an unrecoverable preflight error."""

    report = PreflightReport(str(input_path), status="FATAL")
    report.checks.update(checks or {})
    report.fatal_errors.append(message)
    return report


def check_svg(svg_path: Path) -> PreflightReport:
    """Run a read-only preflight check on one SVG path."""

    resolved = svg_path.resolve()
    checks = {
        "file_exists": resolved.exists(),
        "extension_is_svg": resolved.suffix.lower() == ".svg",
        "xml_parseable": False,
        "root_is_svg": False,
        "has_width": False,
        "has_height": False,
        "has_viewBox": False,
    }
    if not checks["file_exists"]:
        return fatal_report(resolved, "Không tìm thấy file SVG.", checks)

    try:
        tree = ET.parse(resolved)
    except ET.ParseError as exc:
        return fatal_report(resolved, f"XML không hợp lệ: {exc}", checks)
    except OSError as exc:
        return fatal_report(resolved, f"Không đọc được file: {exc}", checks)

    checks["xml_parseable"] = True
    root = tree.getroot()
    checks["root_is_svg"] = local_name(root.tag) == "svg"
    if not checks["root_is_svg"]:
        return fatal_report(resolved, "Root element không phải <svg>.", checks)

    checks["has_width"] = bool(root.get("width"))
    checks["has_height"] = bool(root.get("height"))
    checks["has_viewBox"] = bool(root.get("viewBox"))

    report = PreflightReport(str(resolved), status="OK", checks=checks)
    walk_svg(root, report)
    report.counts["hidden_elements"] = len(report.hidden_elements)
    report.counts["prop_marker_candidates"] = len(report.prop_marker_candidates)
    report.counts["orientation_marker_candidates"] = len(report.orientation_marker_candidates)
    report.counts["door_window_marker_candidates"] = len(report.door_window_marker_candidates)
    report.counts["material_color_candidates"] = len(report.material_color_candidates)

    if not checks["extension_is_svg"]:
        report.warnings.append("Đuôi file không phải .svg; hãy kiểm tra lại file export.")
    if not checks["has_width"]:
        report.warnings.append("Thiếu thuộc tính width trên root <svg>.")
    if not checks["has_height"]:
        report.warnings.append("Thiếu thuộc tính height trên root <svg>.")
    if not checks["has_viewBox"]:
        report.warnings.append("Thiếu viewBox; Maya dry-run có thể khó suy luận kích thước.")
    if report.counts.get("visible_shape_candidates", 0) == 0:
        report.warnings.append("Không thấy shape ứng viên đang hiển thị: rect/polygon/polyline/path.")
    if report.risky_elements:
        risky = ", ".join(f"{name}={count}" for name, count in sorted(report.risky_elements.items()))
        report.warnings.append(f"Có element rủi ro/cần xem tay: {risky}.")
    if report.hidden_elements:
        report.warnings.append("Có element ẩn; preflight chỉ báo cáo, không xóa.")

    if report.warnings:
        report.status = "WARNING"
    return report


def report_to_json_data(report: PreflightReport) -> dict[str, object]:
    """Convert nested dataclasses into JSON-friendly data."""

    return asdict(report)


def write_json_report(report: PreflightReport, output_path: Path) -> None:
    """Write the optional JSON report."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report_to_json_data(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_console_summary(report: PreflightReport) -> None:
    """Print a friendly Vietnamese console summary."""

    print("TuPhuongVoLo-ArtPipeline - SVG preflight checker")
    print(f"File: {report.input_path}")
    if report.status == "FATAL":
        print("Kết quả: FATAL - cần sửa input trước khi chạy dry-run Maya.")
    elif report.status == "WARNING":
        print("Kết quả: WARNING - có thể chạy tiếp, nhưng nên xem các cảnh báo.")
    else:
        print("Kết quả: OK - SVG sẵn sàng để thử Maya dry-run.")

    print("")
    print("Kiểm tra chính:")
    labels = {
        "file_exists": "File tồn tại",
        "extension_is_svg": "Đuôi .svg",
        "xml_parseable": "XML đọc được",
        "root_is_svg": "Root là <svg>",
        "has_width": "Có width",
        "has_height": "Có height",
        "has_viewBox": "Có viewBox",
    }
    for key, label in labels.items():
        if key in report.checks:
            print(f"  {'OK' if report.checks[key] else 'WARN'}  {label}")

    if report.status != "FATAL":
        print("")
        print("Tóm tắt nội dung:")
        print(f"  Shape đang hiển thị: {report.counts.get('visible_shape_candidates', 0)}")
        print(f"  Element được hỗ trợ: {report.supported_elements or {}}")
        print(f"  Element rủi ro: {report.risky_elements or {}}")
        print(f"  Element ẩn phát hiện được: {len(report.hidden_elements)}")
        print(f"  Prop/item/object marker: {len(report.prop_marker_candidates)}")
        print(f"  Rotation marker: {len(report.orientation_marker_candidates)}")
        print(f"  Door/window marker: {len(report.door_window_marker_candidates)}")
        print(f"  Material/color tag: {len(report.material_color_candidates)}")

    for warning in report.warnings:
        print(f"Cảnh báo: {warning}")
    for error in report.fatal_errors:
        print(f"Lỗi: {error}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Kiểm tra read-only SVG thật từ Illustrator trước khi chạy Maya dry-run.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Đường dẫn tới file SVG cần kiểm tra.")
    parser.add_argument("--json-output", type=Path, help="Ghi báo cáo JSON tùy chọn.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"svg-preflight-check {APP_VERSION} ({APP_PHASE})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the SVG preflight CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    report = check_svg(args.input)
    print_console_summary(report)
    if args.json_output:
        write_json_report(report, args.json_output)
        print(f"Đã ghi JSON report: {args.json_output}")
    if report.status == "FATAL":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
