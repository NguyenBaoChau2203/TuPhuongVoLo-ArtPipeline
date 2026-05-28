"""Validate clean SVG files for the TuPhuongVoLo art pipeline.

This module implements Feature 002 task T012. It checks the structural SVG
contract before downstream Blender/Maya features consume the file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from clean_svg_paths import (
    configure_stdio,
    detect_raster_images,
    find_svg_inputs,
    inspect_path_data,
    is_hidden_element,
    is_tiny_path,
    iter_elements,
    load_svg_tree,
    local_name,
)


@dataclass
class ValidationReport:
    """Validation result for one SVG file."""

    input_path: Path
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def is_meaningful_group_id(group_id: str | None) -> bool:
    """Return whether a group/layer id looks artist-authored enough."""

    if not group_id:
        return False
    normalized = group_id.strip().lower()
    if normalized in {"layer", "group", "path"}:
        return False
    return re.match(r"^(layer|group|g)[_\-\s]?\d+$", normalized) is None


def validate_svg_file(
    svg_path: Path,
    strict: bool = False,
    min_path_length: float = 1.0,
    min_bbox_side: float = 1.0,
) -> ValidationReport:
    """Validate one SVG file against the clean SVG contract."""

    errors: list[str] = []
    warnings: list[str] = []
    svg_path = svg_path.resolve()

    if not svg_path.exists():
        return ValidationReport(svg_path, passed=False, errors=["Không tìm thấy file SVG."])
    if svg_path.suffix.lower() != ".svg":
        return ValidationReport(svg_path, passed=False, errors=["Input không phải file .svg."])

    try:
        svg_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ValidationReport(
            svg_path,
            passed=False,
            errors=["File không đọc được bằng UTF-8."],
        )
    except OSError as exc:
        return ValidationReport(
            svg_path,
            passed=False,
            errors=[f"Không đọc được file: {exc}"],
        )

    try:
        _, root = load_svg_tree(svg_path)
    except Exception as exc:
        return ValidationReport(
            svg_path,
            passed=False,
            errors=[f"XML/SVG không hợp lệ: {exc}"],
        )

    if local_name(root.tag).lower() != "svg":  # type: ignore[attr-defined]
        errors.append("Root element không phải <svg>.")

    raster_images = detect_raster_images(root)
    if raster_images:
        errors.append("Có embedded/linked raster image trong SVG.")
        for raster in raster_images:
            warnings.append(f"Raster image: {raster}")

    for element in iter_elements(root):
        element_id = element.get("id") or local_name(element.tag)  # type: ignore[attr-defined]
        if is_hidden_element(element):
            errors.append(f"Còn phần tử hidden/invisible: {element_id}.")
        if strict and element.get("transform"):  # type: ignore[attr-defined]
            errors.append(f"Strict mode: còn transform chưa flatten tại {element_id}.")
        elif element.get("transform"):  # type: ignore[attr-defined]
            warnings.append(f"Còn transform tại {element_id}; strict mode sẽ fail.")

        if local_name(element.tag) == "path":
            path_data = element.get("d") or ""  # type: ignore[attr-defined]
            path_info = inspect_path_data(path_data)
            if path_info is None:
                warnings.append(f"Không phân tích được path: {element_id}.")
                continue
            if is_tiny_path(path_info, min_path_length, min_bbox_side):
                errors.append(f"Path quá nhỏ hoặc zero-length: {element_id}.")

        is_group = local_name(element.tag) == "g"
        group_id = element.get("id")  # type: ignore[attr-defined]
        if is_group and not is_meaningful_group_id(group_id):
            warnings.append(f"Group/layer id chưa rõ nghĩa: {element_id}.")

    passed = not errors
    return ValidationReport(svg_path, passed=passed, errors=errors, warnings=warnings)


def validate_svg_input(input_path: Path, strict: bool = False) -> list[ValidationReport]:
    """Validate one SVG file or every SVG in a directory."""

    reports: list[ValidationReport] = []
    for svg_file in find_svg_inputs(input_path):
        reports.append(validate_svg_file(svg_file, strict=strict))
    return reports


def print_validation_report(report: ValidationReport) -> None:
    """Print a Vietnamese-friendly validation report."""

    print(f"Kiểm tra: {report.input_path}")
    if report.passed:
        print("  PASS: SVG đạt các kiểm tra bắt buộc.")
    else:
        print("  FAIL: SVG chưa đạt clean SVG contract.")
    for error in report.errors:
        print(f"  Lỗi: {error}")
    for warning in report.warnings:
        print(f"  Cảnh báo: {warning}")


def write_json_report(reports: list[ValidationReport], json_report: Path) -> None:
    """Write validation results to a JSON report file."""

    json_report.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for report in reports:
        data = asdict(report)
        data["input_path"] = str(report.input_path)
        payload.append(data)
    json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Kiểm tra SVG sạch trước khi đưa vào pipeline "
            "Tứ Phương Vô Lộ."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="File SVG hoặc thư mục chứa SVG.",
    )
    parser.add_argument("--json-report", type=Path, help="Ghi báo cáo JSON tùy chọn.")
    parser.add_argument("--strict", action="store_true", help="Fail nếu còn transform.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the SVG validation CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    print("TuPhuongVoLo-ArtPipeline — Kiểm tra SVG sạch")
    try:
        reports = validate_svg_input(args.input, strict=args.strict)
    except Exception as exc:
        print(f"Lỗi runtime: {exc}", file=sys.stderr)
        return 2

    for report in reports:
        print_validation_report(report)
    if args.json_report:
        write_json_report(reports, args.json_report)
        print(f"Đã ghi JSON report: {args.json_report}")

    if any(not report.passed for report in reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
