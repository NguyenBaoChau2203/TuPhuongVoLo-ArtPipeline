"""Tests for Feature 001 build CLI wrapper that do not require Blender."""

from __future__ import annotations

from pathlib import Path

import build_isometric_room as builder


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


def test_dry_run_builds_expected_output_paths(tmp_path: Path, monkeypatch) -> None:
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

    assert plan.blend_output.name == "tu_phuong_vo_lo_kho_main_iso_v001.blend"
    assert plan.preview_output.name == "tu_phuong_vo_lo_kho_main_preview_v001.png"
    assert plan.blender_command[1:4] == [
        "--background",
        "--python",
        str(builder.repo_root() / "scripts" / "blender" / "build_isometric_room_blender.py"),
    ]


def test_missing_svg_returns_error(tmp_path: Path, capsys) -> None:
    exit_code = builder.main(["--input", str(tmp_path / "missing.svg"), "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Không tìm thấy file SVG" in captured.err


def test_room_selection_by_normalized_name(tmp_path: Path, monkeypatch) -> None:
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


def test_missing_style_preset_returns_clear_error(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(["--input", str(svg), "--style", "missing_style", "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Style preset không tồn tại" in captured.err


def test_missing_blender_executable_is_handled_gracefully(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--blender-path",
            str(tmp_path / "missing_blender.exe"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Blender" in captured.err


def test_generated_command_includes_blender_background_python(tmp_path: Path, monkeypatch) -> None:
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

    command = builder.build_plan(args).blender_command

    assert command[0]
    assert "--background" in command
    assert "--python" in command
    assert (
        str(builder.repo_root() / "scripts" / "blender" / "build_isometric_room_blender.py")
        in command
    )


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
