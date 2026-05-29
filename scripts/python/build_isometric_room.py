"""CLI wrapper for building an isometric room draft with Blender.

This script performs all testable Python work for Feature 001: SVG room
detection, config loading, naming, command construction, and manifest updates.
The actual Blender scene generation lives in scripts/blender.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import manifest as asset_manifest
import yaml
from clean_svg_paths import configure_stdio
from detect_rooms_from_svg import RoomReport, detect_rooms, normalize_room_name
from room_geometry import (
    create_wall_segments,
    normalize_points_to_origin,
    scale_points_to_blender,
)

PIPELINE_STEP = "feature_001_floorplan_to_isometric_room"
DEFAULT_STYLE = "line_art_green_floor"
DEFAULT_VARIANT = "main"
SVG_TO_BLENDER_SCALE = 0.01


@dataclass(frozen=True)
class BuildPlan:
    """Resolved build inputs and outputs."""

    room: RoomReport
    style_name: str
    style_preset: dict[str, Any]
    room_preset_name: str | None
    room_preset: dict[str, Any]
    input_path: Path
    geometry_json: Path
    blend_output: Path
    preview_output: Path
    blender_command: list[str]
    version: str
    warnings: list[str]


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
    """Select a usable room by normalized name or choose the first one."""

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


def resolve_output_dirs(
    output_dir: Path,
    pipeline_config: dict[str, Any],
) -> tuple[Path, Path, Path]:
    """Resolve Blender, preview, and temp output directories."""

    paths = pipeline_config.get("paths", {}) if isinstance(pipeline_config, dict) else {}
    root = output_dir.resolve()
    blend_dir = root / Path(str(paths.get("output_blender", "outputs/blender/"))).name
    preview_dir = root / Path(str(paths.get("output_preview", "outputs/preview/"))).name
    temp_dir = root / "tmp"
    return blend_dir, preview_dir, temp_dir


def next_shared_version(
    blend_dir: Path,
    preview_dir: Path,
    asset_name: str,
    manifest_path: Path,
) -> str:
    """Return a version that keeps .blend and preview PNG aligned."""

    iso_version = int(
        asset_manifest.next_version(
            blend_dir,
            asset_name,
            DEFAULT_VARIANT,
            "iso",
            extension=".blend",
            manifest_path=manifest_path,
        )
    )
    preview_version = int(
        asset_manifest.next_version(
            preview_dir,
            asset_name,
            DEFAULT_VARIANT,
            "preview",
            extension=".png",
            manifest_path=manifest_path,
        )
    )
    return f"{max(iso_version, preview_version):03d}"


def output_filename(asset_name: str, stage: str, version: str, extension: str) -> str:
    """Generate one convention-compliant output filename."""

    return asset_manifest.generate_filename(
        asset_manifest.AssetNameParts(asset_name, DEFAULT_VARIANT, stage, version),
        extension=extension,
    )


def resolve_blender_executable(
    blender_path: Path | None,
    pipeline_config: dict[str, Any],
    require_exists: bool,
) -> str:
    """Resolve Blender executable from CLI, config, or PATH."""

    if blender_path:
        candidate = str(blender_path)
        if require_exists and not Path(candidate).exists():
            raise FileNotFoundError(f"Không tìm thấy Blender tại: {candidate}")
        return candidate

    tool_paths = pipeline_config.get("tool_paths", {}) if isinstance(pipeline_config, dict) else {}
    configured = str(tool_paths.get("blender", "auto")).strip()
    if configured and configured.lower() != "auto":
        if require_exists and not Path(configured).exists():
            raise FileNotFoundError(f"Không tìm thấy Blender theo config: {configured}")
        return configured

    found = shutil.which("blender")
    if found:
        return found
    if require_exists:
        raise FileNotFoundError(
            "Không tìm thấy Blender. Hãy cài Blender 4.x hoặc đặt tool_paths.blender "
            "trong config/pipeline.yaml."
        )
    return "blender"


def render_resolution_from_config(pipeline_config: dict[str, Any]) -> dict[str, int]:
    """Return render resolution from pipeline config with a safe fallback."""

    defaults = pipeline_config.get("defaults", {}) if isinstance(pipeline_config, dict) else {}
    resolution = defaults.get("render_resolution", {}) if isinstance(defaults, dict) else {}
    return {
        "width": int(resolution.get("width", 1920)),
        "height": int(resolution.get("height", 1080)),
    }


def geometry_payload(
    room: RoomReport,
    style_name: str,
    style_preset: dict[str, Any],
    room_preset_name: str | None,
    room_preset: dict[str, Any],
    pipeline_config: dict[str, Any],
) -> dict[str, Any]:
    """Build the JSON handoff consumed by Blender."""

    if room.boundary is None:
        raise ValueError("Room không có boundary để dựng geometry.")

    local_points = normalize_points_to_origin(room.boundary.points)
    blender_points = scale_points_to_blender(local_points, SVG_TO_BLENDER_SCALE)
    wall_segments = create_wall_segments(blender_points)

    return {
        "room_name": room.room_name,
        "original_label": room.original_label,
        "source_bbox_svg": list(room.boundary.bbox),
        "scale": SVG_TO_BLENDER_SCALE,
        "boundary_points": [[x, y] for x, y in blender_points],
        "wall_segments": [
            {"start": [start[0], start[1]], "end": [end[0], end[1]]}
            for start, end in wall_segments
        ],
        "style_name": style_name,
        "style_preset": style_preset,
        "room_preset_name": room_preset_name,
        "room_preset": room_preset,
        "render_resolution": render_resolution_from_config(pipeline_config),
    }


def build_blender_command(
    blender_executable: str,
    geometry_json: Path,
    blend_output: Path,
    preview_output: Path,
    style_name: str,
    room_preset_name: str | None,
) -> list[str]:
    """Build the subprocess command for Blender."""

    script_path = repo_root() / "scripts" / "blender" / "build_isometric_room_blender.py"
    command = [
        blender_executable,
        "--background",
        "--python",
        str(script_path),
        "--",
        "--geometry-json",
        str(geometry_json),
        "--blend-output",
        str(blend_output),
        "--preview-output",
        str(preview_output),
        "--style",
        style_name,
    ]
    if room_preset_name:
        command.extend(["--room-preset", room_preset_name])
    return command


def build_plan(args: argparse.Namespace) -> BuildPlan:
    """Resolve all inputs, outputs, config, and command for a build."""

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
        warnings.append(f"Không tìm thấy room preset '{room_preset_name}'; dựng phòng trống.")
        room_preset_name = None
    else:
        room_preset_name = None

    output_dir = args.output_dir.resolve()
    blend_dir, preview_dir, temp_dir = resolve_output_dirs(output_dir, pipeline_config)
    manifest_path = asset_manifest.resolve_manifest_path(root=root)
    version = next_shared_version(blend_dir, preview_dir, room.room_name, manifest_path)

    blend_output = blend_dir / output_filename(room.room_name, "iso", version, ".blend")
    preview_output = preview_dir / output_filename(room.room_name, "preview", version, ".png")
    geometry_json = temp_dir / output_filename(room.room_name, "blockout", version, ".json")
    blender_executable = resolve_blender_executable(
        args.blender_path,
        pipeline_config,
        require_exists=not args.dry_run,
    )
    command = build_blender_command(
        blender_executable,
        geometry_json,
        blend_output,
        preview_output,
        args.style,
        room_preset_name,
    )

    return BuildPlan(
        room=room,
        style_name=args.style,
        style_preset=style_preset,
        room_preset_name=room_preset_name,
        room_preset=room_preset,
        input_path=input_path,
        geometry_json=geometry_json,
        blend_output=blend_output,
        preview_output=preview_output,
        blender_command=command,
        version=version,
        warnings=warnings,
    )


def write_geometry_json(plan: BuildPlan) -> None:
    """Write the Blender handoff JSON."""

    payload = geometry_payload(
        plan.room,
        plan.style_name,
        plan.style_preset,
        plan.room_preset_name,
        plan.room_preset,
        load_pipeline_config(),
    )
    plan.geometry_json.parent.mkdir(parents=True, exist_ok=True)
    plan.geometry_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_plan(plan: BuildPlan) -> None:
    """Print the resolved build plan in Vietnamese."""

    print(f"Phòng đã chọn: {plan.room.room_name}")
    print(f"Style: {plan.style_name}")
    print(f"Room preset: {plan.room_preset_name or '(không dùng)'}")
    print(f"Blend output: {plan.blend_output}")
    print(f"PNG preview: {plan.preview_output}")
    print(f"Geometry JSON: {plan.geometry_json}")
    print("Blender command:")
    print(" ".join(f'"{part}"' if " " in part else part for part in plan.blender_command))
    for warning in plan.warnings:
        print(f"Cảnh báo: {warning}")


def append_output_manifest_entries(plan: BuildPlan) -> None:
    """Append manifest entries for the generated .blend and PNG outputs."""

    manifest_path = asset_manifest.resolve_manifest_path(root=repo_root())
    asset_manifest.add_manifest_entry(
        manifest_path=manifest_path,
        source_file=plan.input_path,
        output_path=plan.blend_output,
        stage="iso",
        asset_name=plan.room.room_name,
        variant=DEFAULT_VARIANT,
        pipeline_step=PIPELINE_STEP,
        version=plan.version,
        root=repo_root(),
    )
    asset_manifest.add_manifest_entry(
        manifest_path=manifest_path,
        source_file=plan.input_path,
        output_path=plan.preview_output,
        stage="preview",
        asset_name=plan.room.room_name,
        variant=DEFAULT_VARIANT,
        pipeline_step=PIPELINE_STEP,
        version=plan.version,
        root=repo_root(),
    )


def run_blender(plan: BuildPlan, verbose: bool = False) -> int:
    """Run Blender and update manifest after verified outputs exist."""

    plan.blend_output.parent.mkdir(parents=True, exist_ok=True)
    plan.preview_output.parent.mkdir(parents=True, exist_ok=True)
    write_geometry_json(plan)
    result = subprocess.run(
        plan.blender_command,
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
        print(f"ERR_BLENDER_FAILED: Blender trả về mã lỗi {result.returncode}.", file=sys.stderr)
        return result.returncode
    missing = [path for path in (plan.blend_output, plan.preview_output) if not path.exists()]
    if missing:
        print(
            "ERR_OUTPUT_MISSING: Blender chạy xong nhưng thiếu output: "
            + ", ".join(str(path) for path in missing),
            file=sys.stderr,
        )
        return 1
    append_output_manifest_entries(plan)
    print("Hoàn tất. Đã tạo .blend, PNG preview và cập nhật manifest.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Dựng phòng isometric từ SVG sạch bằng Blender.",
    )
    parser.add_argument("--input", required=True, type=Path, help="File SVG sạch.")
    parser.add_argument("--room", help="Tên phòng/layer cần dựng, ví dụ kho hoặc sanh_chinh.")
    parser.add_argument("--style", default=DEFAULT_STYLE, help="Tên style preset.")
    parser.add_argument("--room-preset", help="Tên room preset cho prop placeholder.")
    parser.add_argument("--output-dir", type=Path, default=repo_root() / "outputs")
    parser.add_argument("--blender-path", type=Path, help="Đường dẫn blender.exe tùy chọn.")
    parser.add_argument("--dry-run", action="store_true", help="In kế hoạch, không chạy Blender.")
    parser.add_argument("--verbose", action="store_true", help="In log Blender trực tiếp.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the build CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        plan = build_plan(args)
    except FileNotFoundError as exc:
        if "Blender" in str(exc):
            print(f"ERR_BLENDER_NOT_FOUND: {exc}", file=sys.stderr)
        else:
            print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    print("TuPhuongVoLo-ArtPipeline - Tạo phòng isometric")
    print_plan(plan)
    if args.dry_run:
        print("Dry-run: không chạy Blender và không cập nhật manifest.")
        return 0

    try:
        return run_blender(plan, verbose=args.verbose)
    except FileNotFoundError as exc:
        print(f"ERR_BLENDER_NOT_FOUND: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERR_RUNTIME: Không thể chạy Blender. Chi tiết: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
