"""Tests for the Phase 007A artist desktop app helpers.

These tests intentionally avoid creating a Tkinter window.
"""

from __future__ import annotations

import sys
from pathlib import Path

import artist_desktop_app as app


def _fake_repo(root: Path) -> Path:
    script_path = root / "scripts" / "python" / "build_maya_room.py"
    script_path.parent.mkdir(parents=True)
    script_path.write_text("print('fake pipeline')\n", encoding="utf-8")
    return root


def test_dry_run_command_wraps_build_maya_room(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=Path(r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"),
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
    assert "--maya-path" not in command


def test_default_mayapy_path_detection_when_path_exists(tmp_path: Path) -> None:
    mayapy = tmp_path / "Maya2024" / "bin" / "mayapy.exe"
    mayapy.parent.mkdir(parents=True)
    mayapy.write_text("fake mayapy", encoding="utf-8")

    assert app.default_mayapy_path(mayapy) == str(mayapy)


def test_default_mayapy_path_empty_when_path_missing(tmp_path: Path) -> None:
    assert app.default_mayapy_path(tmp_path / "missing" / "mayapy.exe") == ""


def test_find_repo_root_finds_fake_checkout(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv(app.REPO_ROOT_ENV_VAR, raising=False)
    fake_root = _fake_repo(tmp_path / "repo")
    nested_dir = fake_root / "dist" / "nested"
    nested_dir.mkdir(parents=True)

    detected_root = app.find_repo_root(extra_candidates=[nested_dir])

    assert detected_root == fake_root


def test_packaged_command_does_not_use_app_exe(monkeypatch, tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    fake_app_exe = fake_root / "dist" / "TuPhuongVoLo_MayaArtistApp.exe"
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        dry_run=True,
    )

    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_app_exe))
    monkeypatch.setattr(app.shutil, "which", lambda name: "C:/Python311/python.exe")

    command = app.build_maya_room_command(options, root=fake_root)

    assert command[0] == "C:/Python311/python.exe"
    assert command[0] != str(fake_app_exe)


def test_packaged_python_command_uses_py_launcher_fallback(monkeypatch) -> None:
    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    def fake_which(name: str) -> str | None:
        if name == "py":
            return "C:/Windows/py.exe"
        return None

    monkeypatch.setattr(app.shutil, "which", fake_which)

    assert app.pipeline_python_command_prefix() == ["C:/Windows/py.exe", "-3"]


def test_frozen_mode_without_external_python_returns_validation_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(app.shutil, "which", lambda name: None)

    errors = app.validate_runtime_environment(root=fake_root)

    assert app.PIPELINE_PYTHON_ERROR in errors


def test_missing_repo_root_returns_vietnamese_validation_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(app.REPO_ROOT_ENV_VAR, raising=False)
    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app, "__file__", str(tmp_path / "artist_desktop_app.py"))
    monkeypatch.setattr(sys, "frozen", False, raising=False)

    errors = app.validate_runtime_environment()

    assert app.REPO_ROOT_ERROR in errors


def test_missing_svg_returns_vietnamese_validation_error(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    options = app.ArtistAppOptions(
        svg_path=Path("tests/in/missing.svg"),
        room_name="phong_kho",
        output_dir=Path("outputs"),
        dry_run=True,
    )

    errors = app.validate_run_paths(options, root=fake_root)

    assert app.SVG_NOT_FOUND_ERROR in errors


def test_relative_svg_path_resolves_from_repo_root(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    svg = fake_root / "tests" / "in" / "illustrator_prop_markers.svg"
    svg.parent.mkdir(parents=True)
    svg.write_text("<svg />\n", encoding="utf-8")

    resolved = app.resolve_repo_relative_path(
        Path(r"tests\in\illustrator_prop_markers.svg"),
        fake_root,
    )

    assert resolved == fake_root / r"tests\in\illustrator_prop_markers.svg"
    assert app.validate_run_paths(
        app.ArtistAppOptions(
            svg_path=Path("tests/in/illustrator_prop_markers.svg"),
            room_name="phong_kho",
            output_dir=Path("outputs"),
            dry_run=True,
        ),
        root=fake_root,
    ) == []


def test_empty_room_name_returns_vietnamese_validation_error(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="",
        output_dir=tmp_path / "outputs",
        dry_run=True,
    )

    errors = app.validate_run_options(options)

    assert app.ROOM_EMPTY_ERROR in errors


def test_build_script_path_uses_detected_repo_root(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    assert app.build_script_path(fake_root) == (
        fake_root / "scripts" / "python" / "build_maya_room.py"
    )


def test_frozen_repo_root_uses_exe_location_not_appdata(monkeypatch, tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    appdata_root = _fake_repo(tmp_path / "AppData" / "Local")
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    fake_app_exe = fake_root / "dist" / "TuPhuongVoLo_MayaArtistApp.exe"
    fake_app_exe.parent.mkdir(parents=True)
    fake_app_exe.write_text("fake exe", encoding="utf-8")

    monkeypatch.delenv(app.REPO_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(empty_dir)
    monkeypatch.setattr(app, "__file__", str(appdata_root / "artist_desktop_app.py"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_app_exe))

    assert app.find_repo_root() == fake_root


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

    assert app.MAYAPY_REQUIRED_ERROR in errors


def test_actual_run_with_missing_mayapy_returns_validation_error(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    svg = fake_root / "tests" / "in" / "room.svg"
    svg.parent.mkdir(parents=True)
    svg.write_text("<svg />\n", encoding="utf-8")
    options = app.ArtistAppOptions(
        svg_path=Path("tests/in/room.svg"),
        room_name="phong_kho",
        output_dir=Path("outputs"),
        maya_path=tmp_path / "missing" / "mayapy.exe",
        dry_run=False,
    )

    errors = app.validate_run_paths(options, root=fake_root)

    assert app.MAYAPY_NOT_FOUND_ERROR in errors


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


def test_output_root_resolves_relative_path_from_repo_root(tmp_path: Path) -> None:
    fake_root = tmp_path / "repo"

    assert app.resolve_output_root(Path("outputs"), fake_root) == fake_root / "outputs"
    assert app.resolve_output_root(tmp_path / "custom_outputs", fake_root) == (
        tmp_path / "custom_outputs"
    )
