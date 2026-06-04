"""Tests for Feature 014A Maya visual fidelity MVP pass."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import maya_visual_fidelity_pass as vf


def write_geometry(path: Path, extra_markers: list[dict] | None = None) -> Path:
    """Write a compact geometry JSON fixture for visual fidelity planning."""

    markers = [
        {
            "prop_type": "wooden_crate",
            "original_label": "prop_wooden_crate_01",
            "center_maya": [0.5, -0.4],
            "bbox_svg": [0, 0, 60, 60],
            "rotation_y_degrees": 0,
        },
        {
            "prop_type": "barrel",
            "original_label": "prop_barrel_01",
            "center_maya": [1.2, -0.7],
            "bbox_svg": [0, 0, 120, 140],
            "source_kind": "path_bbox_fallback",
            "warnings": ["fallback approximate path bbox used"],
        },
        {
            "prop_type": "shelf_unit",
            "original_label": "prop_shelf_unit_01",
            "center_maya": [2.2, -0.6],
            "bbox_svg": [0, 0, 140, 120],
        },
        {
            "prop_type": "floor_grate",
            "original_label": "prop_floor_grate_01_mat_metal",
            "center_maya": [3.0, -1.0],
            "bbox_svg": [0, 0, 100, 45],
        },
        {
            "prop_type": "electrical_cabinet",
            "original_label": "prop_electrical_cabinet_01_mat_metal",
            "center_maya": [3.8, -0.5],
            "bbox_svg": [0, 0, 45, 120],
        },
    ]
    if extra_markers:
        markers.extend(extra_markers)
    path.write_text(
        json.dumps(
            {
                "room_name": "phong_kho",
                "units": {"scale": 0.01},
                "boundary_points": [[0, 0], [4, 0], [4, -2], [0, -2]],
                "prop_markers": markers,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def test_cli_help_works() -> None:
    script = Path(vf.__file__).resolve()

    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--geometry-json" in result.stdout
    assert "--dry-run" in result.stdout
    assert "warehouse_v0" in result.stdout


def test_dry_run_without_maya_writes_report(tmp_path: Path) -> None:
    geometry = write_geometry(tmp_path / "geometry.json")
    report = tmp_path / "visual_report.json"

    exit_code = vf.main(
        [
            "--geometry-json",
            str(geometry),
            "--preset",
            "warehouse_v0",
            "--dry-run",
            "--report-json",
            str(report),
        ]
    )

    assert exit_code == 0
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["room_name"] == "phong_kho"
    assert payload["group_name"] == vf.VISUAL_GROUP_NAME
    assert payload["safety_status"]["dry_run"] is True
    assert payload["planned_addition_count"] >= 8


def test_prop_type_detection_and_counts(tmp_path: Path) -> None:
    data = vf.load_geometry_json(write_geometry(tmp_path / "geometry.json"))

    plan = vf.build_visual_plan(data)

    assert plan.prop_counts["wooden_crate"] == 1
    assert plan.prop_counts["barrel"] == 1
    assert plan.prop_counts["shelf_unit"] == 1
    assert plan.prop_counts["floor_grate"] == 1
    assert plan.prop_counts["electrical_cabinet"] == 1


def test_output_path_must_not_equal_input_path(tmp_path: Path, capsys) -> None:
    geometry = write_geometry(tmp_path / "geometry.json")
    scene = tmp_path / "scene.ma"
    scene.write_text("// maya ascii\n", encoding="utf-8")

    exit_code = vf.main(
        [
            "--input-scene",
            str(scene),
            "--output-scene",
            str(scene),
            "--geometry-json",
            str(geometry),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "--output-scene" in captured.err
    assert "khac --input-scene" in captured.err


def test_planned_group_name_is_stable(tmp_path: Path) -> None:
    data = vf.load_geometry_json(write_geometry(tmp_path / "geometry.json"))

    plan = vf.build_visual_plan(data)

    assert plan.group_name == "GRP_visual_fidelity_v0"
    assert plan.to_dict()["safety_status"]["top_level_group"] == "GRP_visual_fidelity_v0"


def test_known_prop_types_produce_visual_plans(tmp_path: Path) -> None:
    data = vf.load_geometry_json(write_geometry(tmp_path / "geometry.json"))

    plan = vf.build_visual_plan(data)
    templates = {
        addition.template
        for addition in plan.planned_additions
        if addition.kind == "prop_template"
    }

    assert templates == {
        "wooden_crate",
        "barrel",
        "shelf_unit",
        "floor_grate",
        "electrical_cabinet",
    }


def test_unknown_prop_types_do_not_crash(tmp_path: Path) -> None:
    geometry = write_geometry(
        tmp_path / "geometry.json",
        extra_markers=[
            {
                "prop_type": "mystery_totem",
                "original_label": "prop_mystery_totem_01",
                "center_maya": [2.0, -1.0],
            }
        ],
    )
    data = vf.load_geometry_json(geometry)

    plan = vf.build_visual_plan(data)

    assert plan.prop_counts["mystery_totem"] == 1
    assert any("mystery_totem" in warning for warning in plan.warnings)
    assert all(addition.template != "mystery_totem" for addition in plan.planned_additions)


def test_dry_run_does_not_create_scene_files(tmp_path: Path) -> None:
    geometry = write_geometry(tmp_path / "geometry.json")
    output_scene = tmp_path / "visual_v001.ma"

    exit_code = vf.main(
        [
            "--geometry-json",
            str(geometry),
            "--output-scene",
            str(output_scene),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not output_scene.exists()


def test_repo_outputs_only_track_gitkeep_files() -> None:
    result = subprocess.run(
        ["git", "ls-files", "outputs"],
        check=False,
        capture_output=True,
        text=True,
        cwd=vf.repo_root(),
    )

    assert result.returncode == 0
    tracked_outputs = [line.strip().replace("\\", "/") for line in result.stdout.splitlines()]
    assert tracked_outputs
    assert all(path.endswith("/.gitkeep") for path in tracked_outputs)
