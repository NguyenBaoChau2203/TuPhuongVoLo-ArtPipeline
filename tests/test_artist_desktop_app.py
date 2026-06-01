"""Tests for the Phase 007A artist desktop app helpers.

These tests intentionally avoid creating a Tkinter window.
"""

from __future__ import annotations

from pathlib import Path

import artist_desktop_app as app


def test_dry_run_command_wraps_build_maya_room(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        dry_run=True,
    )

    command = app.build_maya_room_command(
        options,
        python_executable="python",
        root=Path("D:/repo"),
    )

    assert command[0] == "python"
    assert any("build_maya_room.py" in part for part in command)
    assert "--input" in command
    assert str(tmp_path / "room.svg") in command
    assert "--room" in command
    assert "phong_kho" in command
    assert "--output-dir" in command
    assert str(tmp_path / "outputs") in command
    assert "--dry-run" in command


def test_render_preview_command_includes_size(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        dry_run=True,
        render_preview=True,
        render_width=800,
        render_height=600,
    )

    command = app.build_maya_room_command(options, python_executable="python")

    assert "--render-preview" in command
    assert command[command.index("--render-width") + 1] == "800"
    assert command[command.index("--render-height") + 1] == "600"


def test_actual_run_includes_mayapy_when_provided(tmp_path: Path) -> None:
    mayapy = Path(r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe")
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=mayapy,
        dry_run=False,
    )

    command = app.build_maya_room_command(options, python_executable="python")

    assert "--dry-run" not in command
    assert "--maya-path" in command
    assert command[command.index("--maya-path") + 1] == str(mayapy)


def test_actual_run_without_mayapy_returns_clear_validation_message(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=None,
        dry_run=False,
    )

    errors = app.validate_run_options(options)

    assert any("mayapy.exe" in error for error in errors)
    assert any("Dry-run" in error for error in errors)


def test_dry_run_does_not_require_mayapy(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=None,
        dry_run=True,
    )

    errors = app.validate_run_options(options)

    assert errors == []


def test_output_folder_helper_only_builds_expected_paths(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"

    assert app.output_subdir_path(output_dir, "maya") == output_dir / "maya"
    assert app.output_subdir_path(output_dir, "preview") == output_dir / "preview"
    assert app.output_subdir_path(output_dir, "reports") == output_dir / "reports"
    assert not output_dir.exists()

