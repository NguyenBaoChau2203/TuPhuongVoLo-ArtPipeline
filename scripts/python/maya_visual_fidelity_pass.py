"""Post-build Maya visual fidelity pass for warehouse-style room blockouts.

The CLI has two deliberately separate modes:

* dry-run/report mode: reads geometry JSON and plans additions without Maya
* actual mode: calls mayapy to open an input .ma and save a different output .ma

The actual Maya edits live in scripts/maya/apply_visual_fidelity_pass.py so this
module remains importable and testable on machines without Maya installed.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FEATURE_ID = "014A"
DEFAULT_PRESET = "warehouse_v0"
SUPPORTED_PRESETS = {DEFAULT_PRESET}
VISUAL_GROUP_NAME = "GRP_visual_fidelity_v0"
MAYA_SCRIPT = "apply_visual_fidelity_pass.py"

PROP_PREFIXES = ("prop_", "item_", "object_")
SUPPORTED_PROP_TYPES = {
    "wooden_crate",
    "barrel",
    "shelf_unit",
    "floor_grate",
    "electrical_cabinet",
}
PROP_ALIASES = {
    "crate": "wooden_crate",
    "wooden_box": "wooden_crate",
    "wooden_barrel": "barrel",
    "shelf": "shelf_unit",
    "shelving": "shelf_unit",
    "metal_shelf": "shelf_unit",
    "grate": "floor_grate",
    "floor_vent": "floor_grate",
    "electric_cabinet": "electrical_cabinet",
    "breaker_box": "electrical_cabinet",
}


@dataclass(frozen=True)
class VisualAddition:
    """One planned visual fidelity addition."""

    kind: str
    name: str
    template: str
    center: tuple[float, float] | None = None
    size: tuple[float, float, float] | None = None
    rotation_y_degrees: float = 0.0
    source_label: str | None = None
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable addition."""

        payload: dict[str, Any] = {
            "kind": self.kind,
            "name": self.name,
            "template": self.template,
            "rotation_y_degrees": self.rotation_y_degrees,
            "details": list(self.details),
        }
        if self.center is not None:
            payload["center"] = [self.center[0], self.center[1]]
        if self.size is not None:
            payload["size"] = [self.size[0], self.size[1], self.size[2]]
        if self.source_label:
            payload["source_label"] = self.source_label
        return payload


@dataclass(frozen=True)
class VisualPlan:
    """Resolved visual fidelity plan and safety metadata."""

    room_name: str
    preset: str
    group_name: str
    prop_counts: dict[str, int]
    planned_additions: list[VisualAddition]
    warnings: list[str]
    input_scene: Path | None = None
    output_scene: Path | None = None
    geometry_json: Path | None = None
    dry_run: bool = True
    boundary_points: list[tuple[float, float]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON report payload."""

        output_scene = str(self.output_scene) if self.output_scene else None
        input_scene = str(self.input_scene) if self.input_scene else None
        return {
            "feature": FEATURE_ID,
            "room_name": self.room_name,
            "preset": self.preset,
            "group_name": self.group_name,
            "prop_counts": dict(sorted(self.prop_counts.items())),
            "planned_additions": [addition.to_dict() for addition in self.planned_additions],
            "planned_addition_count": len(self.planned_additions),
            "warnings": list(self.warnings),
            "input_scene": input_scene,
            "output_scene": output_scene,
            "geometry_json": str(self.geometry_json) if self.geometry_json else None,
            "safety_status": {
                "dry_run": self.dry_run,
                "will_not_modify_input_scene": True,
                "input_output_paths_different": (
                    True
                    if self.input_scene is None or self.output_scene is None
                    else self.input_scene.resolve() != self.output_scene.resolve()
                ),
                "top_level_group": self.group_name,
                "production_groups_untouched": True,
                "maya_required": not self.dry_run,
            },
            "boundary_points": [[x, z] for x, z in self.boundary_points],
        }


def repo_root() -> Path:
    """Return the repository root from this script location."""

    return Path(__file__).resolve().parents[2]


def maya_apply_script() -> Path:
    """Return the Maya-side visual fidelity writer script."""

    return repo_root() / "scripts" / "maya" / MAYA_SCRIPT


def safe_token(value: Any, fallback: str = "unknown") -> str:
    """Return a conservative lowercase token for report and Maya names."""

    text = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or ""))
    text = "_".join(part for part in text.split("_") if part)
    if not text or not text[0].isalpha():
        return fallback
    return text


def canonical_prop_type(value: Any) -> str:
    """Normalize SVG marker names into canonical visual template names."""

    token = safe_token(value, fallback="unknown")
    for prefix in PROP_PREFIXES:
        if token.startswith(prefix) and len(token) > len(prefix):
            token = token[len(prefix) :]
            break
    return PROP_ALIASES.get(token, token)


def load_geometry_json(path: Path) -> dict[str, Any]:
    """Load the existing blockout geometry JSON without modifying it."""

    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Khong tim thay geometry JSON: {resolved}")
    data = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Geometry JSON phai la object.")
    return data


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _point2(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, list | tuple) or len(value) != 2:
        return None
    x = _safe_float(value[0])
    z = _safe_float(value[1])
    if x is None or z is None:
        return None
    return x, z


def _bbox_2d_size(marker: dict[str, Any], units_scale: float) -> tuple[float, float] | None:
    bbox_maya = marker.get("bbox_maya")
    if isinstance(bbox_maya, list | tuple) and len(bbox_maya) == 4:
        values = [_safe_float(item) for item in bbox_maya]
        if all(value is not None for value in values):
            min_x, min_z, max_x, max_z = values  # type: ignore[misc]
            return abs(max_x - min_x), abs(max_z - min_z)

    bbox_svg = marker.get("bbox_svg")
    if isinstance(bbox_svg, list | tuple) and len(bbox_svg) == 4:
        values = [_safe_float(item) for item in bbox_svg]
        if all(value is not None for value in values):
            min_x, min_y, max_x, max_y = values  # type: ignore[misc]
            return abs(max_x - min_x) * units_scale, abs(max_y - min_y) * units_scale

    return None


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _uses_approx_bbox(marker: dict[str, Any]) -> bool:
    if "path_bbox_fallback" in str(marker.get("source_kind", "")).lower():
        return True
    warnings = marker.get("warnings", [])
    return any("fallback approximate path bbox" in str(w).lower() for w in warnings)


def visual_size_for_marker(
    prop_type: str,
    marker: dict[str, Any],
    units_scale: float,
) -> tuple[tuple[float, float, float], list[str]]:
    """Infer a conservative visual template size from marker metadata."""

    bbox_size = _bbox_2d_size(marker, units_scale)
    warnings: list[str] = []
    approx_bbox = _uses_approx_bbox(marker)
    if approx_bbox:
        warnings.append(
            f"{marker.get('original_label', prop_type)}: bbox marker chi xap xi; "
            "dung size mac dinh an toan."
        )

    if prop_type == "wooden_crate":
        width, depth = bbox_size or (0.55, 0.55)
        width = _clamp(width * 0.70, 0.35, 0.95)
        depth = _clamp(depth * 0.45, 0.35, 0.85)
        height = _clamp(max(width, depth) * 0.82, 0.35, 0.75)
        return (width, height, depth), warnings

    if prop_type == "barrel":
        if approx_bbox or bbox_size is None:
            return (0.48, 0.72, 0.48), warnings
        width, depth = bbox_size
        diameter = _clamp(min(width, depth) * 0.55, 0.36, 0.62)
        return (diameter, 0.72, diameter), warnings

    if prop_type == "shelf_unit":
        width, depth = bbox_size or (1.1, 0.45)
        width = _clamp(width * 0.85, 0.75, 1.55)
        depth = _clamp(depth * 0.30, 0.28, 0.55)
        return (width, 1.55, depth), warnings

    if prop_type == "floor_grate":
        width, depth = bbox_size or (1.1, 0.45)
        return (_clamp(width, 0.70, 1.60), 0.04, _clamp(depth, 0.25, 0.70)), warnings

    if prop_type == "electrical_cabinet":
        width, depth = bbox_size or (0.45, 0.18)
        width = _clamp(width, 0.35, 0.65)
        depth = _clamp(depth * 0.10, 0.10, 0.20)
        return (width, 1.20, depth), warnings

    return (0.40, 0.40, 0.40), warnings


def _marker_rotation(marker: dict[str, Any]) -> float:
    rotation = _safe_float(marker.get("rotation_y_degrees"))
    if rotation in {0.0, 90.0, 180.0, 270.0}:
        return rotation
    return 0.0


def _boundary_points(data: dict[str, Any]) -> tuple[list[tuple[float, float]], list[str]]:
    points: list[tuple[float, float]] = []
    warnings: list[str] = []
    raw_points = data.get("boundary_points", [])
    if not isinstance(raw_points, list):
        return points, ["Geometry JSON thieu boundary_points hop le; bo qua floor tint helper."]
    for raw_point in raw_points:
        point = _point2(raw_point)
        if point is not None:
            points.append(point)
    if raw_points and len(points) < 3:
        warnings.append("boundary_points khong du 3 diem hop le; bo qua floor tint helper.")
    return points, warnings


def _prop_counts(prop_markers: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for marker in prop_markers:
        if not isinstance(marker, dict):
            counts["invalid_marker"] = counts.get("invalid_marker", 0) + 1
            continue
        prop_type = canonical_prop_type(marker.get("prop_type") or marker.get("name"))
        counts[prop_type] = counts.get(prop_type, 0) + 1
    return counts


def build_visual_plan(
    data: dict[str, Any],
    *,
    preset: str = DEFAULT_PRESET,
    input_scene: Path | None = None,
    output_scene: Path | None = None,
    geometry_json: Path | None = None,
    dry_run: bool = True,
) -> VisualPlan:
    """Plan all additive visual fidelity helpers from geometry JSON."""

    if preset not in SUPPORTED_PRESETS:
        available = ", ".join(sorted(SUPPORTED_PRESETS))
        raise ValueError(f"Preset khong ton tai: {preset}. Co san: {available}")

    room_name = safe_token(data.get("room_name") or data.get("room") or "room", fallback="room")
    units = data.get("units", {}) if isinstance(data.get("units"), dict) else {}
    units_scale = _safe_float(units.get("scale")) or 0.01
    raw_markers = data.get("prop_markers", [])
    prop_markers = raw_markers if isinstance(raw_markers, list) else []
    warnings: list[str] = []
    if not isinstance(raw_markers, list):
        warnings.append("Geometry JSON co prop_markers khong phai list; bo qua prop markers.")

    additions: list[VisualAddition] = []
    template_counts: dict[str, int] = {}
    for marker in prop_markers:
        if not isinstance(marker, dict):
            warnings.append("Bo qua prop marker khong phai object.")
            continue

        raw_prop_type = (
            marker.get("prop_type") or marker.get("name") or marker.get("original_label")
        )
        prop_type = canonical_prop_type(raw_prop_type)
        center = _point2(marker.get("center_maya"))
        label = str(marker.get("original_label") or raw_prop_type or prop_type)
        if center is None:
            warnings.append(f"{label}: thieu center_maya hop le; khong tao visual template.")
            continue

        if prop_type not in SUPPORTED_PROP_TYPES:
            warnings.append(
                f"{label}: chua co visual fidelity template cho '{prop_type}', da bo qua."
            )
            continue

        size, size_warnings = visual_size_for_marker(prop_type, marker, units_scale)
        warnings.extend(size_warnings)
        template_counts[prop_type] = template_counts.get(prop_type, 0) + 1
        count = template_counts[prop_type]
        additions.append(
            VisualAddition(
                kind="prop_template",
                name=f"vf_{prop_type}_{count:02d}",
                template=prop_type,
                center=center,
                size=size,
                rotation_y_degrees=_marker_rotation(marker),
                source_label=label,
                details=template_details(prop_type),
            )
        )

    boundary, boundary_warnings = _boundary_points(data)
    warnings.extend(boundary_warnings)
    if len(boundary) >= 3:
        additions.append(
            VisualAddition(
                kind="room_helper",
                name="vf_room_floor_tint",
                template="floor_wall_presentation",
                details=["subtle agent-only floor tint from room boundary"],
            )
        )
    additions.extend(
        [
            VisualAddition(
                kind="presentation_helper",
                name=f"cam_{room_name}_visual_review",
                template="review_camera",
                details=["orthographic isometric-like review angle"],
            ),
            VisualAddition(
                kind="presentation_helper",
                name="key_agent_visual_review",
                template="review_light",
                details=["directional key light", "soft ambient helper"],
            ),
            VisualAddition(
                kind="artist_note",
                name=f"NOTE_{room_name}_visual_fidelity",
                template="artist_note_locator",
                details=["metadata note describing this additive pass"],
            ),
        ]
    )

    return VisualPlan(
        room_name=room_name,
        preset=preset,
        group_name=VISUAL_GROUP_NAME,
        prop_counts=_prop_counts(prop_markers),
        planned_additions=additions,
        warnings=warnings,
        input_scene=input_scene.resolve() if input_scene else None,
        output_scene=output_scene.resolve() if output_scene else None,
        geometry_json=geometry_json.resolve() if geometry_json else None,
        dry_run=dry_run,
        boundary_points=boundary,
    )


def template_details(prop_type: str) -> list[str]:
    """Return human-readable subpart descriptions for one visual template."""

    return {
        "wooden_crate": ["box body", "dark trim strips", "front cross/face bands"],
        "barrel": ["cylinder proxy", "top ring", "bottom ring", "dark middle band"],
        "shelf_unit": ["vertical supports", "horizontal planks", "small crate fillers"],
        "floor_grate": ["dark slats", "thin frame"],
        "electrical_cabinet": ["cabinet body", "panel face", "handle", "warning detail"],
    }.get(prop_type, ["generic helper"])


def write_report(plan: VisualPlan, report_json: Path) -> None:
    """Write the dry-run/apply report JSON."""

    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(
        json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_scene_paths(
    input_scene: Path | None,
    output_scene: Path | None,
    *,
    dry_run: bool,
) -> None:
    """Validate non-destructive scene path behavior."""

    if dry_run:
        if input_scene and output_scene and input_scene.resolve() == output_scene.resolve():
            raise ValueError("--output-scene phai khac --input-scene de tranh ghi de scene nguon.")
        return

    if input_scene is None:
        raise ValueError("Actual run can --input-scene.")
    if output_scene is None:
        raise ValueError("Actual run can --output-scene.")
    resolved_input = input_scene.resolve()
    resolved_output = output_scene.resolve()
    if not resolved_input.exists():
        raise FileNotFoundError(f"Khong tim thay input scene: {resolved_input}")
    if resolved_input.suffix.lower() != ".ma":
        raise ValueError("--input-scene phai la file .ma.")
    if resolved_output.suffix.lower() != ".ma":
        raise ValueError("--output-scene phai la file .ma.")
    if resolved_input == resolved_output:
        raise ValueError("--output-scene phai khac --input-scene de tranh ghi de scene nguon.")
    if resolved_output.exists():
        raise FileExistsError(
            f"Output scene da ton tai; hay chon ten version moi: {resolved_output}"
        )


def is_mayapy_executable(executable: str) -> bool:
    """Return whether a path/command looks like mayapy."""

    return "mayapy" in Path(executable).name.lower()


def resolve_mayapy(maya_path: Path | None) -> str:
    """Resolve mayapy for actual mode."""

    if maya_path:
        candidate = str(maya_path)
        if not Path(candidate).exists():
            raise FileNotFoundError(f"Khong tim thay mayapy tai: {candidate}")
        if not is_mayapy_executable(candidate):
            raise ValueError("Feature 014A actual run chi ho tro mayapy.exe.")
        return candidate

    found = shutil.which("mayapy")
    if found:
        return found
    raise FileNotFoundError(
        "Khong tim thay mayapy. Hay truyen --maya-path toi Autodesk Maya mayapy.exe."
    )


def build_maya_command(
    mayapy: str,
    input_scene: Path,
    output_scene: Path,
    plan_json: Path,
    *,
    verbose: bool = False,
) -> list[str]:
    """Build the mayapy command that applies visual fidelity edits."""

    command = [
        mayapy,
        str(maya_apply_script()),
        "--input-scene",
        str(input_scene),
        "--output-scene",
        str(output_scene),
        "--plan-json",
        str(plan_json),
    ]
    if verbose:
        command.append("--verbose")
    return command


def run_maya_apply(args: argparse.Namespace, plan: VisualPlan) -> int:
    """Run mayapy to apply the additive visual fidelity pass."""

    assert args.input_scene is not None
    assert args.output_scene is not None
    mayapy = resolve_mayapy(args.maya_path)
    args.output_scene.resolve().parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tpvl_visual_fidelity_") as temp_dir:
        plan_json = Path(temp_dir) / "visual_fidelity_plan.json"
        write_report(plan, plan_json)
        command = build_maya_command(
            mayapy,
            args.input_scene.resolve(),
            args.output_scene.resolve(),
            plan_json,
            verbose=args.verbose,
        )
        if args.verbose:
            print("Maya visual fidelity command:")
            print(" ".join(f'"{part}"' if " " in part else part for part in command))
        result = subprocess.run(
            command,
            cwd=repo_root(),
            text=True,
            capture_output=not args.verbose,
            check=False,
        )
        if not args.verbose:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(
                f"ERR_VISUAL_FIDELITY_MAYA_FAILED: mayapy tra ve ma loi {result.returncode}.",
                file=sys.stderr,
            )
            return result.returncode

    if not args.output_scene.resolve().exists():
        print(
            f"ERR_VISUAL_FIDELITY_OUTPUT_MISSING: Thieu output scene {args.output_scene.resolve()}",
            file=sys.stderr,
        )
        return 1
    return 0


def print_plan(plan: VisualPlan) -> None:
    """Print a compact Vietnamese operator summary."""

    print("TuPhuongVoLo-ArtPipeline - Visual Fidelity MVP 014A")
    print(f"Phong: {plan.room_name}")
    print(f"Preset: {plan.preset}")
    print(f"Group moi: {plan.group_name}")
    if plan.prop_counts:
        counts = ", ".join(f"{name}={count}" for name, count in sorted(plan.prop_counts.items()))
        print(f"Prop markers: {counts}")
    else:
        print("Prop markers: 0")
    print(f"So addition du kien: {len(plan.planned_additions)}")
    if plan.output_scene:
        print(f"Output scene: {plan.output_scene}")
    if plan.warnings:
        print("Canh bao:")
        for warning in plan.warnings:
            print(f"  - {warning}")
    if plan.dry_run:
        print("Dry-run: khong chay Maya, khong tao .ma, khong sua file nguon.")


def build_parser() -> argparse.ArgumentParser:
    """Create CLI parser."""

    parser = argparse.ArgumentParser(
        description="Additive Maya visual fidelity pass for warehouse blockouts.",
    )
    parser.add_argument("--input-scene", type=Path, help="Source .ma scene to read in actual mode.")
    parser.add_argument("--geometry-json", required=True, type=Path, help="Existing blockout JSON.")
    parser.add_argument("--output-scene", type=Path, help="Different .ma scene path to write.")
    parser.add_argument(
        "--preset",
        default=DEFAULT_PRESET,
        choices=sorted(SUPPORTED_PRESETS),
        help="Visual fidelity preset name.",
    )
    parser.add_argument("--maya-path", type=Path, help="Path to mayapy.exe for actual mode.")
    parser.add_argument("--report-json", type=Path, help="Optional dry-run/apply report JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Plan only; does not require Maya.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed mayapy output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the visual fidelity pass CLI."""

    args = build_parser().parse_args(argv)
    try:
        validate_scene_paths(args.input_scene, args.output_scene, dry_run=args.dry_run)
        geometry = load_geometry_json(args.geometry_json)
        plan = build_visual_plan(
            geometry,
            preset=args.preset,
            input_scene=args.input_scene,
            output_scene=args.output_scene,
            geometry_json=args.geometry_json,
            dry_run=args.dry_run,
        )
        print_plan(plan)
        if args.report_json:
            write_report(plan, args.report_json.resolve())
            print(f"Report JSON: {args.report_json.resolve()}")
        if args.dry_run:
            return 0
        return run_maya_apply(args, plan)
    except (FileExistsError, FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Loi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
