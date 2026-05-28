"""Clean Illustrator-exported SVG files for the TuPhuongVoLo art pipeline.

This module implements Feature 002 tasks T009, T010, and T011. It removes
safe-to-drop SVG clutter, reports embedded raster images, removes tiny path
artifacts, and writes versioned clean SVG files without touching source files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

try:  # lxml is the project dependency; ElementTree keeps tests runnable if absent.
    from lxml import etree as XML_ETREE

    LXML_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal local envs
    import xml.etree.ElementTree as XML_ETREE  # type: ignore[no-redef]

    LXML_AVAILABLE = False

try:
    from svgpathtools import parse_path
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal local envs
    parse_path = None


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
RASTER_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff")
DEFAULT_OUTPUT_DIR = Path("assets/2d/svg_clean")
DEFAULT_MANIFEST_PATH = Path("outputs/manifest/asset_manifest.json")

try:
    if LXML_AVAILABLE:
        XML_ETREE.register_namespace("svg", SVG_NS)
    else:
        XML_ETREE.register_namespace("", SVG_NS)
    XML_ETREE.register_namespace("xlink", XLINK_NS)
except (AttributeError, ValueError):  # Namespace registration differs by XML backend.
    pass


def configure_stdio() -> None:
    """Make Vietnamese CLI text safe on Windows shells with legacy code pages."""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class PathInfo:
    """Basic geometry facts for an SVG path."""

    length: float
    bbox_width: float
    bbox_height: float


@dataclass
class CleanupReport:
    """Summary of one SVG cleanup run."""

    input_path: Path
    output_path: Path
    removed_hidden: int = 0
    removed_metadata: int = 0
    removed_empty_groups: int = 0
    removed_tiny_paths: int = 0
    flattened_transforms: int = 0
    raster_images: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    dry_run: bool = False


def repo_root() -> Path:
    """Return the repository root based on this script location."""

    return Path(__file__).resolve().parents[2]


def local_name(tag: str) -> str:
    """Return an XML tag name without namespace."""

    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def iter_elements(root: object) -> Iterable[object]:
    """Yield XML elements under root, excluding comments when lxml is present."""

    for element in root.iter():  # type: ignore[attr-defined]
        tag = getattr(element, "tag", "")
        if isinstance(tag, str):
            yield element


def parent_map(root: object) -> dict[object, object]:
    """Build a child-to-parent map for lxml or ElementTree nodes."""

    return {child: parent for parent in iter_elements(root) for child in list(parent)}


def load_svg_tree(svg_path: Path) -> tuple[object, object]:
    """Load an SVG XML tree with UTF-8-safe parsing."""

    if LXML_AVAILABLE:
        parser = XML_ETREE.XMLParser(remove_blank_text=False, resolve_entities=False)
        tree = XML_ETREE.parse(str(svg_path), parser)
        return tree, tree.getroot()
    tree = XML_ETREE.parse(svg_path)
    return tree, tree.getroot()


def write_svg_tree(tree: object, output_path: Path) -> None:
    """Write an XML tree as UTF-8 SVG."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if LXML_AVAILABLE:
        tree.write(  # type: ignore[attr-defined]
            str(output_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )
        return
    tree.write(output_path, encoding="utf-8", xml_declaration=True)  # type: ignore[attr-defined]


def relative_to_repo(path: Path) -> str:
    """Return a repo-relative path string when possible."""

    try:
        return path.resolve().relative_to(repo_root()).as_posix()
    except ValueError:
        return str(path)


def compute_checksum(file_path: Path) -> str:
    """Compute a SHA-256 checksum for a generated file."""

    sha256 = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def append_manifest_entry(input_path: Path, output_path: Path, manifest_path: Path) -> None:
    """Append a minimal Feature 002 manifest entry for a generated SVG."""

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest_data = []
    else:
        manifest_data = []
    if not isinstance(manifest_data, list):
        manifest_data = []

    version_match = re.search(r"_v(\d{3})$", output_path.stem)
    asset_stem = re.sub(r"_svgclean_v\d{3}$", "", output_path.stem)
    if asset_stem.startswith("tu_phuong_vo_lo_"):
        asset_stem = asset_stem.removeprefix("tu_phuong_vo_lo_")

    entry = {
        "asset_name": asset_stem or output_path.stem,
        "variant": "main",
        "stage": "svgclean",
        "version": version_match.group(1) if version_match else "001",
        "source_file": relative_to_repo(input_path),
        "output_path": relative_to_repo(output_path),
        "timestamp": datetime.now(UTC).isoformat(),
        "checksum": compute_checksum(output_path),
        "pipeline_step": "feature_002_clean_svg_paths",
    }
    manifest_data.append(entry)
    manifest_path.write_text(
        json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_style(style_value: str | None) -> dict[str, str]:
    """Parse an inline SVG style attribute into lowercase key/value pairs."""

    styles: dict[str, str] = {}
    if not style_value:
        return styles
    for item in style_value.split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        styles[key.strip().lower()] = value.strip().lower()
    return styles


def is_hidden_element(element: object) -> bool:
    """Return whether an SVG element is visually hidden."""

    get = element.get  # type: ignore[attr-defined]
    style = parse_style(get("style"))
    display = (get("display") or style.get("display") or "").strip().lower()
    visibility = (get("visibility") or style.get("visibility") or "").strip().lower()
    opacity = (get("opacity") or style.get("opacity") or "").strip()
    return display == "none" or visibility == "hidden" or opacity in {"0", "0.0", "0.00"}


def remove_element(element: object, parents: dict[object, object]) -> bool:
    """Remove an element if it has a parent."""

    parent = parents.get(element)
    if parent is None:
        return False
    parent.remove(element)  # type: ignore[attr-defined]
    return True


def remove_hidden_elements(root: object) -> int:
    """Remove display:none, visibility:hidden, and opacity:0 elements."""

    parents = parent_map(root)
    removed = 0
    for element in list(iter_elements(root)):
        if element is root:
            continue
        if is_hidden_element(element) and remove_element(element, parents):
            removed += 1
    return removed


def remove_comments_and_metadata(root: object) -> int:
    """Remove comments and metadata nodes where they are safe to drop."""

    removed = 0
    parents = parent_map(root)
    for element in list(iter_elements(root)):
        if local_name(element.tag) == "metadata" and remove_element(element, parents):
            removed += 1

    if LXML_AVAILABLE:
        for comment in root.xpath("//comment()"):  # type: ignore[attr-defined]
            parent = comment.getparent()
            if parent is not None:
                parent.remove(comment)
                removed += 1
    return removed


def remove_empty_groups(root: object) -> int:
    """Remove empty SVG groups without deleting artwork."""

    removed = 0
    changed = True
    while changed:
        changed = False
        parents = parent_map(root)
        for element in reversed(list(iter_elements(root))):
            if local_name(element.tag) != "g":
                continue
            if list(element):
                continue
            text = (getattr(element, "text", None) or "").strip()
            if text:
                continue
            if remove_element(element, parents):
                removed += 1
                changed = True
    return removed


def detect_raster_images(root: object) -> list[str]:
    """Return descriptions of embedded or linked raster image elements."""

    rasters: list[str] = []
    for element in iter_elements(root):
        if local_name(element.tag) != "image":
            continue
        href = (
            element.get("href")  # type: ignore[attr-defined]
            or element.get(f"{{{XLINK_NS}}}href")  # type: ignore[attr-defined]
            or ""
        )
        element_id = element.get("id") or "(không có id)"  # type: ignore[attr-defined]
        href_lower = href.lower()
        if (
            href_lower.startswith("data:image")
            or href_lower.endswith(RASTER_EXTENSIONS)
            or not href
        ):
            rasters.append(f"{element_id}: {href or '(không có href)'}")
    return rasters


def inspect_path_data(path_data: str) -> PathInfo | None:
    """Inspect path length and bbox using svgpathtools when available."""

    if not path_data.strip():
        return PathInfo(length=0.0, bbox_width=0.0, bbox_height=0.0)
    if parse_path is not None:
        try:
            path = parse_path(path_data)
            xmin, xmax, ymin, ymax = path.bbox()
            return PathInfo(
                length=float(path.length(error=1e-4)),
                bbox_width=float(abs(xmax - xmin)),
                bbox_height=float(abs(ymax - ymin)),
            )
        except Exception:
            return inspect_path_data_simple(path_data)
    return inspect_path_data_simple(path_data)


TOKEN_RE = re.compile(r"[MmLlHhVvZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def _read_number(tokens: list[str], index: int) -> tuple[float | None, int]:
    if index >= len(tokens) or re.match(r"^[A-Za-z]$", tokens[index]):
        return None, index
    return float(tokens[index]), index + 1


def path_to_absolute_line_commands(path_data: str) -> list[tuple[str, float | None, float | None]]:
    """Parse simple M/L/H/V/Z path data into absolute commands."""

    tokens = TOKEN_RE.findall(path_data)
    commands: list[tuple[str, float | None, float | None]] = []
    index = 0
    command = ""
    current = (0.0, 0.0)
    subpath_start = (0.0, 0.0)

    while index < len(tokens):
        token = tokens[index]
        if re.match(r"^[A-Za-z]$", token):
            command = token
            index += 1
        if command in {"M", "m", "L", "l"}:
            first_pair = True
            while index < len(tokens) and not re.match(r"^[A-Za-z]$", tokens[index]):
                x_value, index = _read_number(tokens, index)
                y_value, index = _read_number(tokens, index)
                if x_value is None or y_value is None:
                    break
                if command.islower():
                    x_value += current[0]
                    y_value += current[1]
                draw_command = "M" if command in {"M", "m"} and first_pair else "L"
                current = (x_value, y_value)
                if draw_command == "M":
                    subpath_start = current
                commands.append((draw_command, current[0], current[1]))
                first_pair = False
            if command in {"M", "m"}:
                command = "l" if command.islower() else "L"
        elif command in {"H", "h"}:
            while index < len(tokens) and not re.match(r"^[A-Za-z]$", tokens[index]):
                x_value, index = _read_number(tokens, index)
                if x_value is None:
                    break
                if command.islower():
                    x_value += current[0]
                current = (x_value, current[1])
                commands.append(("L", current[0], current[1]))
        elif command in {"V", "v"}:
            while index < len(tokens) and not re.match(r"^[A-Za-z]$", tokens[index]):
                y_value, index = _read_number(tokens, index)
                if y_value is None:
                    break
                if command.islower():
                    y_value += current[1]
                current = (current[0], y_value)
                commands.append(("L", current[0], current[1]))
        elif command in {"Z", "z"}:
            commands.append(("Z", None, None))
            current = subpath_start
            command = ""
        else:
            return []
    return commands


def inspect_path_data_simple(path_data: str) -> PathInfo | None:
    """Inspect simple line-based path data without svgpathtools."""

    commands = path_to_absolute_line_commands(path_data)
    if not commands:
        return None

    points = [
        (x, y)
        for command, x, y in commands
        if command in {"M", "L"} and x is not None and y is not None
    ]
    if not points:
        return PathInfo(length=0.0, bbox_width=0.0, bbox_height=0.0)

    length = 0.0
    current: tuple[float, float] | None = None
    subpath_start: tuple[float, float] | None = None
    for command, x_value, y_value in commands:
        if command == "M" and x_value is not None and y_value is not None:
            current = (x_value, y_value)
            subpath_start = current
        elif command == "L" and current is not None and x_value is not None and y_value is not None:
            next_point = (x_value, y_value)
            length += math.dist(current, next_point)
            current = next_point
        elif command == "Z" and current is not None and subpath_start is not None:
            length += math.dist(current, subpath_start)
            current = subpath_start

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return PathInfo(length=length, bbox_width=max(xs) - min(xs), bbox_height=max(ys) - min(ys))


def is_tiny_path(path_info: PathInfo, min_path_length: float, min_bbox_side: float) -> bool:
    """Return whether path geometry is a likely tracing artifact."""

    return path_info.length < min_path_length or (
        path_info.bbox_width < min_bbox_side and path_info.bbox_height < min_bbox_side
    )


def remove_tiny_paths(
    root: object,
    min_path_length: float,
    min_bbox_side: float,
) -> tuple[int, list[str]]:
    """Remove zero-length and tiny path artifacts."""

    removed = 0
    warnings: list[str] = []
    parents = parent_map(root)
    for element in list(iter_elements(root)):
        if local_name(element.tag) != "path":
            continue
        path_info = inspect_path_data(element.get("d") or "")  # type: ignore[attr-defined]
        if path_info is None:
            path_id = element.get("id") or "(không có id)"  # type: ignore[attr-defined]
            warnings.append(f"Không đọc được path id={path_id}.")
            continue
        should_remove = is_tiny_path(path_info, min_path_length, min_bbox_side)
        if should_remove and remove_element(element, parents):
            removed += 1
    return removed, warnings


def parse_simple_transform(transform: str) -> list[tuple[str, float, float]] | None:
    """Parse safe translate/scale transform sequences."""

    operations: list[tuple[str, float, float]] = []
    cursor = 0
    transform_pattern = r"(translate|scale)\s*\(([^)]*)\)"
    for match in re.finditer(transform_pattern, transform.strip(), flags=re.IGNORECASE):
        if transform[cursor : match.start()].strip():
            return None
        name = match.group(1).lower()
        values = [float(value) for value in re.split(r"[\s,]+", match.group(2).strip()) if value]
        if name == "translate":
            if not 1 <= len(values) <= 2:
                return None
            operations.append(("translate", values[0], values[1] if len(values) == 2 else 0.0))
        elif name == "scale":
            if not 1 <= len(values) <= 2:
                return None
            operations.append(("scale", values[0], values[1] if len(values) == 2 else values[0]))
        cursor = match.end()
    if transform[cursor:].strip() or not operations:
        return None
    return operations


def format_number(value: float) -> str:
    """Format SVG coordinate values compactly."""

    if abs(value) < 1e-9:
        value = 0.0
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def serialize_line_commands(commands: list[tuple[str, float | None, float | None]]) -> str:
    """Serialize absolute line commands back into SVG path data."""

    parts: list[str] = []
    for command, x_value, y_value in commands:
        if command == "Z":
            parts.append("Z")
        elif x_value is not None and y_value is not None:
            parts.append(f"{command}{format_number(x_value)} {format_number(y_value)}")
    return " ".join(parts)


def flatten_simple_path_transform(element: object) -> bool:
    """Flatten translate/scale transforms on simple line-only path elements."""

    transform = element.get("transform")  # type: ignore[attr-defined]
    path_data = element.get("d") or ""  # type: ignore[attr-defined]
    if not transform:
        return False
    operations = parse_simple_transform(transform)
    commands = path_to_absolute_line_commands(path_data)
    if operations is None or not commands:
        return False

    transformed: list[tuple[str, float | None, float | None]] = []
    for command, x_value, y_value in commands:
        if x_value is None or y_value is None:
            transformed.append((command, x_value, y_value))
            continue
        x_new = x_value
        y_new = y_value
        for op_name, first, second in operations:
            if op_name == "translate":
                x_new += first
                y_new += second
            elif op_name == "scale":
                x_new *= first
                y_new *= second
        transformed.append((command, x_new, y_new))

    element.set("d", serialize_line_commands(transformed))  # type: ignore[attr-defined]
    del element.attrib["transform"]  # type: ignore[attr-defined]
    return True


def flatten_safe_transforms(root: object) -> tuple[int, list[str]]:
    """Flatten only transforms that are safe for this vertical slice."""

    flattened = 0
    warnings: list[str] = []
    for element in iter_elements(root):
        transform = element.get("transform")  # type: ignore[attr-defined]
        if not transform:
            continue
        if transform.strip() in {"matrix(1 0 0 1 0 0)", "matrix(1,0,0,1,0,0)"}:
            del element.attrib["transform"]  # type: ignore[attr-defined]
            flattened += 1
            continue
        if local_name(element.tag) == "path" and flatten_simple_path_transform(element):
            flattened += 1
            continue
        element_id = element.get("id") or local_name(element.tag)  # type: ignore[attr-defined]
        warnings.append(f"Giữ nguyên transform chưa an toàn: {element_id} ({transform}).")
    return flattened, warnings


def clean_svg_file(
    input_path: Path,
    output_path: Path,
    min_path_length: float = 1.0,
    min_bbox_side: float = 1.0,
    dry_run: bool = False,
    update_manifest: bool = False,
    manifest_path: Path | None = None,
) -> CleanupReport:
    """Clean a single raw SVG file and write a non-destructive output."""

    input_path = input_path.resolve()
    output_path = output_path.resolve()
    if input_path == output_path:
        raise ValueError("Không được ghi đè lên file SVG nguồn.")
    if not input_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file SVG: {input_path}")

    tree, root = load_svg_tree(input_path)
    if local_name(root.tag).lower() != "svg":  # type: ignore[attr-defined]
        raise ValueError("File không phải SVG hợp lệ.")

    report = CleanupReport(input_path=input_path, output_path=output_path, dry_run=dry_run)
    report.raster_images = detect_raster_images(root)
    report.removed_hidden = remove_hidden_elements(root)
    report.removed_metadata = remove_comments_and_metadata(root)
    report.flattened_transforms, transform_warnings = flatten_safe_transforms(root)
    report.warnings.extend(transform_warnings)
    report.removed_tiny_paths, path_warnings = remove_tiny_paths(
        root,
        min_path_length=min_path_length,
        min_bbox_side=min_bbox_side,
    )
    report.warnings.extend(path_warnings)
    report.removed_empty_groups = remove_empty_groups(root)

    if not dry_run:
        write_svg_tree(tree, output_path)
        if update_manifest:
            append_manifest_entry(
                input_path=input_path,
                output_path=output_path,
                manifest_path=manifest_path or repo_root() / DEFAULT_MANIFEST_PATH,
            )
    return report


def clean_output_name(input_path: Path) -> str:
    """Return a versioned svgclean filename for a raw SVG input."""

    stem = input_path.stem
    stem = re.sub(r"_svgraw_v(\d{3})$", r"_svgclean_v\1", stem)
    if not re.search(r"_svgclean_v\d{3}$", stem):
        stem = f"{stem}_svgclean_v001"
    return f"{stem}.svg"


def next_available_path(path: Path) -> Path:
    """Return a path that does not overwrite an existing output."""

    if not path.exists():
        return path
    match = re.search(r"_v(\d{3})$", path.stem)
    for version in range(2, 1000):
        if match:
            stem = re.sub(r"_v\d{3}$", f"_v{version:03d}", path.stem)
        else:
            stem = f"{path.stem}_v{version:03d}"
        candidate = path.with_name(f"{stem}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Không thể tạo tên phiên bản mới cho output.")


def resolve_output_path(input_file: Path, output_path: Path, multiple_inputs: bool) -> Path:
    """Resolve a non-destructive output path for one input file."""

    if multiple_inputs or output_path.suffix.lower() != ".svg":
        target = output_path / clean_output_name(input_file)
    else:
        target = output_path
    return next_available_path(target)


def find_svg_inputs(input_path: Path) -> list[Path]:
    """Return SVG files for a file or directory input."""

    if input_path.is_file():
        if input_path.suffix.lower() != ".svg":
            raise ValueError("Input phải là file .svg hoặc thư mục chứa SVG.")
        return [input_path]
    if input_path.is_dir():
        return sorted(path for path in input_path.iterdir() if path.suffix.lower() == ".svg")
    raise FileNotFoundError(f"Không tìm thấy input: {input_path}")


def clean_svg_input(
    input_path: Path,
    output_path: Path,
    min_path_length: float = 1.0,
    min_bbox_side: float = 1.0,
    dry_run: bool = False,
    update_manifest: bool = False,
    manifest_path: Path | None = None,
) -> list[CleanupReport]:
    """Clean a single SVG or every SVG in a directory."""

    svg_inputs = find_svg_inputs(input_path)
    if not svg_inputs:
        raise ValueError("Không tìm thấy file SVG nào để xử lý.")

    multiple = len(svg_inputs) > 1 or input_path.is_dir()
    reports: list[CleanupReport] = []
    for svg_input in svg_inputs:
        target = resolve_output_path(svg_input, output_path, multiple_inputs=multiple)
        reports.append(
            clean_svg_file(
                input_path=svg_input,
                output_path=target,
                min_path_length=min_path_length,
                min_bbox_side=min_bbox_side,
                dry_run=dry_run,
                update_manifest=update_manifest,
                manifest_path=manifest_path,
            )
        )
    return reports


def print_report(report: CleanupReport, verbose: bool = False) -> None:
    """Print a Vietnamese-friendly cleanup report."""

    print(f"Đã xử lý: {report.input_path}")
    print(f"  Kết quả: {report.output_path}")
    print(f"  Hidden removed: {report.removed_hidden}")
    print(f"  Tiny paths removed: {report.removed_tiny_paths}")
    if report.raster_images:
        print("  Cảnh báo: SVG có raster image, nên kiểm tra lại trong Illustrator:")
        for raster in report.raster_images:
            print(f"    - {raster}")
    if verbose and report.warnings:
        print("  Cảnh báo kỹ thuật:")
        for warning in report.warnings:
            print(f"    - {warning}")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Làm sạch SVG thô thành SVG sạch cho pipeline Tứ Phương Vô Lộ.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="File SVG hoặc thư mục chứa SVG.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root() / DEFAULT_OUTPUT_DIR,
        help="File/thư mục output. Mặc định: assets/2d/svg_clean/.",
    )
    parser.add_argument("--min-path-length", type=float, default=1.0)
    parser.add_argument("--min-bbox-side", type=float, default=1.0)
    parser.add_argument("--dry-run", action="store_true", help="Kiểm tra mà không ghi file.")
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        help="Không ghi manifest cho lần chạy này.",
    )
    parser.add_argument("--verbose", action="store_true", help="In thêm chi tiết kỹ thuật.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the SVG cleanup CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    print("TuPhuongVoLo-ArtPipeline — Làm sạch SVG")
    if shutil.which("vpype") is None:
        print("Cảnh báo: Không tìm thấy vpype; dùng cleanup nội bộ an toàn.")

    try:
        reports = clean_svg_input(
            input_path=args.input,
            output_path=args.output,
            min_path_length=args.min_path_length,
            min_bbox_side=args.min_bbox_side,
            dry_run=args.dry_run,
            update_manifest=not args.dry_run and not args.no_manifest,
        )
    except Exception as exc:
        print(f"Lỗi: Không thể làm sạch SVG. Chi tiết: {exc}", file=sys.stderr)
        return 1

    for report in reports:
        print_report(report, verbose=args.verbose)
    print("Hoàn tất. File gốc không bị thay đổi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
