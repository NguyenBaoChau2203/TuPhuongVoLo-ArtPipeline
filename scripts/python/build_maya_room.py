"""Maya-first room build wrapper for Feature 005.

This CLI keeps SVG parsing in the existing pure-Python layer, writes a geometry
JSON handoff, then launches Maya/mayapy to create an editable .ma blockout.
Dry-run mode is intentionally useful without Maya installed.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import manifest as asset_manifest
import yaml
from clean_svg_paths import configure_stdio
from detect_rooms_from_svg import RoomReport, detect_rooms, normalize_room_name
from room_geometry import create_wall_segments, normalize_points_to_origin, scale_points_to_blender

PIPELINE_STEP = "feature_005_maya_bridge"
DEFAULT_STYLE = "line_art_green_floor"
DEFAULT_VARIANT = "main"
SVG_TO_MAYA_SCALE = 0.01
MAYA_STAGE = "maya"
# PNG isometric preview render (Feature 005.2). The naming convention reserves
# the "preview" stage for preview PNG renders mapped to outputs/preview/.
RENDER_STAGE = "preview"
DEFAULT_RENDER_WIDTH = 1280
DEFAULT_RENDER_HEIGHT = 720


@dataclass(frozen=True)
class MayaBuildPlan:
    """Resolved Maya build inputs and outputs."""

    room: RoomReport
    style_name: str
    style_preset: dict[str, Any]
    room_preset_name: str | None
    room_preset: dict[str, Any]
    input_path: Path
    geometry_json: Path
    maya_output: Path
    maya_command: list[str]
    version: str
    warnings: list[str]
    candidate_rooms: int = 0
    usable_rooms: int = 0
    unsupported_elements: list[str] = field(default_factory=list)
    transform_applied: bool = False
    render_preview: bool = False
    render_output: Path | None = None
    render_width: int = DEFAULT_RENDER_WIDTH
    render_height: int = DEFAULT_RENDER_HEIGHT
    render_command: list[str] = field(default_factory=list)


def repo_root() -> Path:
    """Return repository root from this script location."""

    return Path(__file__).resolve().parents[2]


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file as a dictionary."""

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise ValueError(f"Không tìm thấy file config: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Config YAML không hợp lệ: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Config YAML phải là object/dict: {path}")
    return data


def load_pipeline_config(root: Path | None = None) -> dict[str, Any]:
    """Load config/pipeline.yaml."""

    return load_yaml_file((root or repo_root()) / "config" / "pipeline.yaml")


def load_style_presets(root: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load style presets from config/style_presets.yaml."""

    data = load_yaml_file((root or repo_root()) / "config" / "style_presets.yaml")
    presets = data.get("style_presets", {})
    if not isinstance(presets, dict):
        raise ValueError("style_presets.yaml thiếu khóa style_presets hợp lệ.")
    return presets


def load_room_presets(root: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load room presets from config/room_presets.yaml."""

    data = load_yaml_file((root or repo_root()) / "config" / "room_presets.yaml")
    presets = data.get("room_presets", {})
    if not isinstance(presets, dict):
        raise ValueError("room_presets.yaml thiếu khóa room_presets hợp lệ.")
    return presets


def validate_input_svg(input_path: Path) -> Path:
    """Validate the SVG input path without modifying it."""

    resolved = input_path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy file SVG: {resolved}")
    if resolved.suffix.lower() != ".svg":
        raise ValueError("Input phải là file .svg sạch.")
    return resolved


def select_room(
    reports: list[RoomReport],
    requested_room: str | None,
) -> tuple[RoomReport, list[str]]:
    """Select a usable room by normalized name or choose the first usable room."""

    usable = [report for report in reports if report.has_usable_boundary]
    if not usable:
        raise ValueError("Không tìm thấy boundary phòng đóng kín trong SVG.")

    warnings: list[str] = []
    if requested_room:
        normalized = normalize_room_name(requested_room)
        for report in usable:
            if report.room_name == normalized:
                return report, warnings
        available = ", ".join(report.room_name for report in usable)
        raise ValueError(f"Không tìm thấy phòng '{normalized}'. Phòng có sẵn: {available}")

    selected = usable[0]
    warnings.append(
        f"Bạn chưa chọn --room; pipeline sẽ dùng phòng đầu tiên: {selected.room_name}."
    )
    return selected, warnings


def resolve_output_dirs(output_dir: Path, pipeline_config: dict[str, Any]) -> tuple[Path, Path]:
    """Resolve Maya scene and temp output directories."""

    paths = pipeline_config.get("paths", {}) if isinstance(pipeline_config, dict) else {}
    root = output_dir.resolve()
    maya_dir = root / Path(str(paths.get("output_maya", "outputs/maya/"))).name
    temp_dir = root / "tmp"
    return maya_dir, temp_dir


def resolve_render_dir(output_dir: Path, pipeline_config: dict[str, Any]) -> Path:
    """Resolve the PNG preview render output directory."""

    paths = pipeline_config.get("paths", {}) if isinstance(pipeline_config, dict) else {}
    root = output_dir.resolve()
    return root / Path(str(paths.get("output_preview", "outputs/preview/"))).name


def output_filename(asset_name: str, stage: str, version: str, extension: str) -> str:
    """Generate one convention-compliant output filename."""

    return asset_manifest.generate_filename(
        asset_manifest.AssetNameParts(asset_name, DEFAULT_VARIANT, stage, version),
        extension=extension,
    )


def next_maya_version(maya_dir: Path, asset_name: str, manifest_path: Path) -> str:
    """Return the next available Maya scene version."""

    return asset_manifest.next_version(
        maya_dir,
        asset_name,
        DEFAULT_VARIANT,
        MAYA_STAGE,
        extension=".ma",
        manifest_path=manifest_path,
    )


def is_mayapy_executable(executable: str) -> bool:
    """Return whether a path/command looks like mayapy."""

    return "mayapy" in Path(executable).name.lower()


def unsupported_maya_runtime_message() -> str:
    """Return the Feature 005 MVP runtime limitation message."""

    return (
        "Feature 005 MVP chỉ hỗ trợ mayapy.exe cho actual run. "
        "maya.exe/mayabatch.exe chưa được hỗ trợ."
    )


def resolve_maya_executable(
    maya_path: Path | None,
    pipeline_config: dict[str, Any],
    require_exists: bool,
) -> str:
    """Resolve mayapy from CLI, config, or PATH."""

    if maya_path:
        candidate = str(maya_path)
        if require_exists and not Path(candidate).exists():
            raise FileNotFoundError(f"Không tìm thấy Maya/mayapy tại: {candidate}")
        if require_exists and not is_mayapy_executable(candidate):
            raise ValueError(unsupported_maya_runtime_message())
        return candidate

    tool_paths = pipeline_config.get("tool_paths", {}) if isinstance(pipeline_config, dict) else {}
    configured = str(tool_paths.get("mayapy", "auto")).strip()
    if configured and configured.lower() != "auto":
        if require_exists and not Path(configured).exists():
            raise FileNotFoundError(f"Không tìm thấy mayapy theo config: {configured}")
        if require_exists and not is_mayapy_executable(configured):
            raise ValueError(unsupported_maya_runtime_message())
        return configured

    found = shutil.which("mayapy")
    if found:
        return found

    if require_exists:
        raise FileNotFoundError(
            "Không tìm thấy mayapy. Hãy cài Autodesk Maya hoặc đặt "
            "tool_paths.mayapy trong config/pipeline.yaml."
        )
    return "mayapy"


def build_maya_command(maya_executable: str, geometry_json: Path, maya_output: Path) -> list[str]:
    """Build the preferred mayapy subprocess command."""

    script_path = repo_root() / "scripts" / "maya" / "build_maya_room_scene.py"
    return [
        maya_executable,
        str(script_path),
        "--geometry-json",
        str(geometry_json),
        "--maya-output",
        str(maya_output),
    ]


def build_render_command(
    maya_executable: str,
    maya_output: Path,
    render_output: Path,
    render_width: int,
    render_height: int,
) -> list[str]:
    """Build the mayapy subprocess command for the isometric PNG preview."""

    script_path = repo_root() / "scripts" / "maya" / "render_maya_room_preview.py"
    return [
        maya_executable,
        str(script_path),
        "--scene",
        str(maya_output),
        "--render-output",
        str(render_output),
        "--width",
        str(render_width),
        "--height",
        str(render_height),
    ]


def geometry_payload(
    room: RoomReport,
    style_name: str,
    style_preset: dict[str, Any],
    room_preset_name: str | None,
    room_preset: dict[str, Any],
) -> dict[str, Any]:
    """Build the JSON handoff consumed by Maya."""

    if room.boundary is None:
        raise ValueError("Room không có boundary để dựng geometry.")

    local_points = normalize_points_to_origin(room.boundary.points)
    maya_points = scale_points_to_blender(local_points, SVG_TO_MAYA_SCALE)
    wall_segments = create_wall_segments(maya_points)
    source_min_x, source_min_y, _, _ = room.boundary.bbox
    prop_markers: list[dict[str, Any]] = []
    for marker in room.prop_markers:
        local_center = (
            marker.center_svg[0] - source_min_x,
            marker.center_svg[1] - source_min_y,
        )
        maya_center = scale_points_to_blender([local_center], SVG_TO_MAYA_SCALE)[0]
        marker_payload = marker.to_dict()
        marker_payload["center_local"] = [local_center[0], local_center[1]]
        marker_payload["center_maya"] = [maya_center[0], maya_center[1]]
        prop_markers.append(marker_payload)

    return {
        "room_name": room.room_name,
        "original_label": room.original_label,
        "source_bbox_svg": list(room.boundary.bbox),
        "units": {
            "maya_linear": "meter",
            "source": "svg_units",
            "scale": SVG_TO_MAYA_SCALE,
            "axis_mapping": "SVG x/y -> Maya x/z, Maya y is vertical",
        },
        "boundary_points": [[x, z] for x, z in maya_points],
        "wall_segments": [
            {"start": [start[0], start[1]], "end": [end[0], end[1]]}
            for start, end in wall_segments
        ],
        "style_name": style_name,
        "style_preset": style_preset,
        "room_preset_name": room_preset_name,
        "room_preset": room_preset,
        "prop_markers": prop_markers,
    }


def build_plan(args: argparse.Namespace) -> MayaBuildPlan:
    """Resolve all inputs, outputs, config, and command for a Maya build."""

    root = repo_root()
    input_path = validate_input_svg(args.input)
    pipeline_config = load_pipeline_config(root)
    style_presets = load_style_presets(root)
    room_presets = load_room_presets(root)

    if args.style not in style_presets:
        available = ", ".join(sorted(style_presets))
        raise ValueError(f"Style preset không tồn tại: {args.style}. Có sẵn: {available}")
    style_preset = dict(style_presets[args.style])

    reports = detect_rooms(input_path)
    room, warnings = select_room(reports, args.room)

    explicit_room_preset = args.room_preset is not None
    room_preset_name = normalize_room_name(args.room_preset) if args.room_preset else room.room_name
    room_preset: dict[str, Any] = {}
    if room_preset_name in room_presets:
        room_preset = dict(room_presets[room_preset_name])
    elif explicit_room_preset:
        warnings.append(
            f"Không tìm thấy room preset '{room_preset_name}'; dựng phòng trống."
        )
        room_preset_name = None
    else:
        room_preset_name = None

    output_dir = args.output_dir.resolve()
    maya_dir, temp_dir = resolve_output_dirs(output_dir, pipeline_config)
    manifest_path = asset_manifest.resolve_manifest_path(root=root)
    version = next_maya_version(maya_dir, room.room_name, manifest_path)

    maya_output = maya_dir / output_filename(room.room_name, MAYA_STAGE, version, ".ma")
    geometry_json = temp_dir / output_filename(room.room_name, "blockout", version, ".json")
    maya_executable = resolve_maya_executable(
        args.maya_path,
        pipeline_config,
        require_exists=not args.dry_run,
    )
    command = build_maya_command(maya_executable, geometry_json, maya_output)

    render_preview = bool(getattr(args, "render_preview", False))
    render_width = int(getattr(args, "render_width", DEFAULT_RENDER_WIDTH) or DEFAULT_RENDER_WIDTH)
    render_height = int(
        getattr(args, "render_height", DEFAULT_RENDER_HEIGHT) or DEFAULT_RENDER_HEIGHT
    )
    render_output: Path | None = None
    render_command: list[str] = []
    if render_preview:
        if render_width <= 0 or render_height <= 0:
            raise ValueError("Kích thước render phải là số dương.")
        explicit_render = getattr(args, "render_output", None)
        if explicit_render:
            render_output = Path(explicit_render).resolve()
        else:
            render_dir = resolve_render_dir(output_dir, pipeline_config)
            render_output = render_dir / output_filename(
                room.room_name, RENDER_STAGE, version, ".png"
            )
        render_command = build_render_command(
            maya_executable,
            maya_output,
            render_output,
            render_width,
            render_height,
        )

    aggregated_unsupported: list[str] = []
    for report in reports:
        aggregated_unsupported.extend(report.unsupported_elements)
    usable_rooms = sum(1 for report in reports if report.has_usable_boundary)

    return MayaBuildPlan(
        room=room,
        style_name=args.style,
        style_preset=style_preset,
        room_preset_name=room_preset_name,
        room_preset=room_preset,
        input_path=input_path,
        geometry_json=geometry_json,
        maya_output=maya_output,
        maya_command=command,
        version=version,
        warnings=warnings,
        candidate_rooms=len(reports),
        usable_rooms=usable_rooms,
        unsupported_elements=list(dict.fromkeys(aggregated_unsupported)),
        transform_applied=room.transform_applied,
        render_preview=render_preview,
        render_output=render_output,
        render_width=render_width,
        render_height=render_height,
        render_command=render_command,
    )


def write_geometry_json(plan: MayaBuildPlan) -> None:
    """Write the Maya handoff JSON."""

    payload = geometry_payload(
        plan.room,
        plan.style_name,
        plan.style_preset,
        plan.room_preset_name,
        plan.room_preset,
    )
    plan.geometry_json.parent.mkdir(parents=True, exist_ok=True)
    plan.geometry_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_plan(plan: MayaBuildPlan) -> None:
    """Print the resolved Maya build plan in Vietnamese."""

    print(f"Phòng đã chọn: {plan.room.room_name}")
    if plan.room.group_path:
        print(f"Đường dẫn group: {' > '.join(plan.room.group_path)}")
    print(f"Số phòng/đường bao phát hiện: {plan.candidate_rooms} (dùng được: {plan.usable_rooms})")
    if plan.room.shape_kinds:
        kinds = ", ".join(
            f"{kind}={count}" for kind, count in sorted(plan.room.shape_kinds.items())
        )
        print(f"Loại hình trong phòng: {kinds}")
    if plan.room.prop_markers:
        props = ", ".join(marker.prop_type for marker in plan.room.prop_markers)
        print(f"Prop marker SVG ({len(plan.room.prop_markers)}): {props}")
    print(
        "Transform: "
        + ("đã áp dụng vào tọa độ phòng." if plan.transform_applied else "không có/không cần.")
    )
    if plan.unsupported_elements:
        print(
            "Phần tử SVG chưa hỗ trợ (đã bỏ qua): "
            + ", ".join(plan.unsupported_elements)
        )
    print(f"Style: {plan.style_name}")
    print(f"Room preset: {plan.room_preset_name or '(không dùng)'}")
    print(f"Maya scene output: {plan.maya_output}")
    print(f"Geometry JSON: {plan.geometry_json}")
    if plan.render_preview:
        print(f"Render PNG preview: {plan.render_output}")
        print(f"Kích thước render: {plan.render_width}x{plan.render_height}")
    else:
        print("Render PNG preview: (tắt) — dùng --render-preview để bật.")
    print("Maya command:")
    print(" ".join(f'"{part}"' if " " in part else part for part in plan.maya_command))
    if plan.render_preview and plan.render_command:
        print("Maya render command:")
        print(
            " ".join(
                f'"{part}"' if " " in part else part for part in plan.render_command
            )
        )
    for warning in plan.warnings:
        print(f"Cảnh báo: {warning}")


def append_output_manifest_entries(plan: MayaBuildPlan) -> None:
    """Append manifest entry for the generated Maya scene."""

    manifest_path = asset_manifest.resolve_manifest_path(root=repo_root())
    asset_manifest.add_manifest_entry(
        manifest_path=manifest_path,
        source_file=plan.input_path,
        output_path=plan.maya_output,
        stage=MAYA_STAGE,
        asset_name=plan.room.room_name,
        variant=DEFAULT_VARIANT,
        pipeline_step=PIPELINE_STEP,
        version=plan.version,
        root=repo_root(),
    )


def append_render_manifest_entry(plan: MayaBuildPlan) -> None:
    """Append a manifest entry for the verified PNG preview render.

    Called only after the render PNG exists on disk. The "preview" stage is part
    of the naming convention, so the manifest safely tracks render outputs the
    same way it tracks the .ma scene.
    """

    if plan.render_output is None:
        return
    manifest_path = asset_manifest.resolve_manifest_path(root=repo_root())
    asset_manifest.add_manifest_entry(
        manifest_path=manifest_path,
        source_file=plan.input_path,
        output_path=plan.render_output,
        stage=RENDER_STAGE,
        asset_name=plan.room.room_name,
        variant=DEFAULT_VARIANT,
        pipeline_step=PIPELINE_STEP,
        version=plan.version,
        root=repo_root(),
    )


def run_render(plan: MayaBuildPlan, verbose: bool = False) -> int:
    """Render the isometric PNG preview from the saved .ma scene.

    Requires the .ma scene to already exist. The render command opens the scene
    read-only (the .ma stays editable), produces the PNG, and the PNG is then
    verified before a manifest entry is appended.
    """

    if plan.render_output is None or not plan.render_command:
        return 0
    if not plan.maya_output.exists():
        print(
            f"ERR_OUTPUT_MISSING: Cần file .ma trước khi render: {plan.maya_output}",
            file=sys.stderr,
        )
        return 1
    plan.render_output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        plan.render_command,
        cwd=repo_root(),
        text=True,
        capture_output=not verbose,
        check=False,
    )
    if not verbose:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(
            f"ERR_RENDER_FAILED: Maya render trả về mã lỗi {result.returncode}.",
            file=sys.stderr,
        )
        return result.returncode
    if not plan.render_output.exists():
        print(
            "ERR_RENDER_MISSING: Maya render chạy xong nhưng thiếu PNG: "
            f"{plan.render_output}",
            file=sys.stderr,
        )
        return 1
    append_render_manifest_entry(plan)
    print(f"Hoàn tất render preview. Đã tạo PNG và cập nhật manifest: {plan.render_output}")
    return 0


def run_maya(plan: MayaBuildPlan, verbose: bool = False) -> int:
    """Run Maya and update manifest after verified .ma output exists."""

    plan.maya_output.parent.mkdir(parents=True, exist_ok=True)
    write_geometry_json(plan)
    result = subprocess.run(
        plan.maya_command,
        cwd=repo_root(),
        text=True,
        capture_output=not verbose,
        check=False,
    )
    if not verbose:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"ERR_MAYA_FAILED: Maya trả về mã lỗi {result.returncode}.", file=sys.stderr)
        return result.returncode
    if not plan.maya_output.exists():
        print(
            f"ERR_OUTPUT_MISSING: Maya chạy xong nhưng thiếu output: {plan.maya_output}",
            file=sys.stderr,
        )
        return 1
    append_output_manifest_entries(plan)
    print("Hoàn tất. Đã tạo .ma và cập nhật manifest.")
    if plan.render_preview:
        return run_render(plan, verbose=verbose)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Dựng phòng blockout Maya từ SVG sạch.",
    )
    parser.add_argument("--input", required=True, type=Path, help="File SVG sạch.")
    parser.add_argument(
        "--room",
        help="Tên phòng/layer cần dựng, ví dụ kho hoặc sanh_chinh.",
    )
    parser.add_argument("--style", default=DEFAULT_STYLE, help="Tên style preset.")
    parser.add_argument("--room-preset", help="Tên room preset cho prop placeholder.")
    parser.add_argument("--output-dir", type=Path, default=repo_root() / "outputs")
    parser.add_argument(
        "--maya-path",
        type=Path,
        help="Đường dẫn mayapy.exe tùy chọn.",
    )
    parser.add_argument(
        "--render-preview",
        action="store_true",
        help="Render thêm ảnh PNG isometric preview từ scene .ma (cần mayapy).",
    )
    parser.add_argument(
        "--render-output",
        type=Path,
        help="Đường dẫn PNG preview tùy chọn; mặc định theo quy ước tên file.",
    )
    parser.add_argument(
        "--render-width",
        type=int,
        default=DEFAULT_RENDER_WIDTH,
        help=f"Chiều rộng render (mặc định {DEFAULT_RENDER_WIDTH}).",
    )
    parser.add_argument(
        "--render-height",
        type=int,
        default=DEFAULT_RENDER_HEIGHT,
        help=f"Chiều cao render (mặc định {DEFAULT_RENDER_HEIGHT}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="In kế hoạch, không chạy Maya.",
    )
    parser.add_argument("--verbose", action="store_true", help="In log Maya trực tiếp.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the Maya build CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        plan = build_plan(args)
    except FileNotFoundError as exc:
        if "Maya" in str(exc) or "mayapy" in str(exc):
            print(f"ERR_MAYA_NOT_FOUND: {exc}", file=sys.stderr)
        else:
            print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    print("TuPhuongVoLo-ArtPipeline - Tạo phòng Maya")
    print_plan(plan)
    if args.dry_run:
        print(
            "Dry-run: chỉ kiểm tra kế hoạch, không chạy Maya và không ghi manifest. "
            "File gốc không bị thay đổi."
        )
        if plan.render_preview:
            print(
                "Dry-run render: chỉ in đường dẫn/kích thước PNG, "
                "không render và không tạo file PNG."
            )
        return 0

    try:
        return run_maya(plan, verbose=args.verbose)
    except FileNotFoundError as exc:
        print(f"ERR_MAYA_NOT_FOUND: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERR_RUNTIME: Không thể chạy Maya. Chi tiết: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
