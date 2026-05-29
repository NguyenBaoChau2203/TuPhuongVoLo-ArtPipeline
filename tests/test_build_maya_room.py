"""Tests for Feature 005 Maya build CLI wrapper that do not require Maya."""

from __future__ import annotations

import json
from pathlib import Path

import build_maya_room as builder


def write_svg(path: Path) -> Path:
    """Write a clean SVG with two room groups."""

    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="100" height="100">
  <g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>
  <g id="g2" inkscape:label="Sảnh chính"><path d="M20 0 L40 0 L40 10 L20 10 Z"/></g>
</svg>
""",
        encoding="utf-8",
    )
    return path


def isolated_manifest(monkeypatch, tmp_path: Path) -> Path:
    """Redirect manifest lookups to a temp file."""

    manifest_path = tmp_path / "manifest" / "asset_manifest.json"
    monkeypatch.setattr(
        builder.asset_manifest,
        "resolve_manifest_path",
        lambda *args, **kwargs: manifest_path,
    )
    return manifest_path


def test_dry_run_builds_expected_ma_output_path(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.maya_output.name == "tu_phuong_vo_lo_kho_main_maya_v001.ma"
    assert plan.geometry_json.name == "tu_phuong_vo_lo_kho_main_blockout_v001.json"


def test_missing_svg_returns_error(tmp_path: Path, capsys) -> None:
    exit_code = builder.main(["--input", str(tmp_path / "missing.svg"), "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Không tìm thấy file SVG" in captured.err


def test_room_selection_by_normalized_vietnamese_name(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "Sảnh chính",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "sanh_chinh"


def test_missing_style_returns_clear_error(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(["--input", str(svg), "--style", "missing_style", "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Style preset không tồn tại" in captured.err


def test_missing_maya_executable_is_handled_gracefully(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--maya-path",
            str(tmp_path / "missing_mayapy.exe"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Maya" in captured.err or "mayapy" in captured.err


def test_actual_run_rejects_maya_or_mayabatch_path(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    for executable_name in ("maya.exe", "mayabatch.exe"):
        fake_executable = tmp_path / executable_name
        fake_executable.write_text("not a real executable", encoding="utf-8")

        exit_code = builder.main(
            [
                "--input",
                str(svg),
                "--room",
                "kho",
                "--maya-path",
                str(fake_executable),
            ]
        )
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Feature 005 MVP chỉ hỗ trợ mayapy.exe cho actual run" in captured.err
        assert "maya.exe/mayabatch.exe chưa được hỗ trợ" in captured.err


def test_dry_run_allows_non_mayapy_path_for_planning(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    fake_maya = tmp_path / "maya.exe"
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--maya-path",
            str(fake_maya),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.maya_command[0] == str(fake_maya)


def test_dry_run_does_not_update_manifest(tmp_path: Path, monkeypatch) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not manifest_path.exists()


def test_generated_maya_command_includes_scene_script(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    command = builder.build_plan(args).maya_command

    assert command[0]
    assert any("build_maya_room_scene.py" in part for part in command)
    assert "--geometry-json" in command
    assert "--maya-output" in command


def test_geometry_json_payload_contains_boundary_and_walls(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    assert payload["room_name"] == "kho"
    assert len(payload["boundary_points"]) == 4
    assert len(payload["wall_segments"]) == 4
    assert payload["units"]["maya_linear"] == "meter"


def test_output_naming_follows_convention(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.maya_output.parent.name == "maya"
    assert plan.maya_output.name == "tu_phuong_vo_lo_kho_main_maya_v001.ma"
