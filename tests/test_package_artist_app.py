"""Tests for the Phase 007B desktop app packaging helper."""

from __future__ import annotations

import sys
from pathlib import Path

import package_artist_app as package_app


def test_packaging_version_matches_desktop_app() -> None:
    assert package_app.PACKAGE_SCRIPT_VERSION == package_app.APP_VERSION
    assert package_app.PACKAGE_SCRIPT_VERSION in package_app.app_version_display()


def test_dry_run_prints_app_version_when_pyinstaller_missing(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(package_app.shutil, "which", lambda name: None)
    monkeypatch.setattr(package_app.importlib.util, "find_spec", lambda name: None)

    return_code = package_app.main(["--dry-run"])

    captured = capsys.readouterr()
    assert return_code == 0
    assert "App version:" in captured.out
    assert package_app.PACKAGE_SCRIPT_VERSION in captured.out
    assert "pyinstaller" in captured.out
    assert "Chưa cài PyInstaller" in captured.err


def test_path_pyinstaller_command_contains_expected_flags(monkeypatch) -> None:
    monkeypatch.setattr(package_app.shutil, "which", lambda name: "C:/Tools/pyinstaller.exe")

    command = package_app.build_pyinstaller_command()

    assert command[0] == "C:/Tools/pyinstaller.exe"
    assert "--onefile" in command
    assert "--windowed" in command
    assert "--name" in command
    assert command[command.index("--name") + 1] == "TuPhuongVoLo_MayaArtistApp"
    assert "scripts/python/artist_desktop_app.py" in command


def test_module_pyinstaller_fallback_uses_current_python(monkeypatch) -> None:
    monkeypatch.setattr(package_app.shutil, "which", lambda name: None)
    monkeypatch.setattr(package_app.importlib.util, "find_spec", lambda name: object())

    command = package_app.build_pyinstaller_command()

    assert command[:3] == [sys.executable, "-m", "PyInstaller"]
    assert "--onefile" in command
    assert "scripts/python/artist_desktop_app.py" in command


def test_pyinstaller_missing_returns_clear_vietnamese_message(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(package_app.shutil, "which", lambda name: None)
    monkeypatch.setattr(package_app.importlib.util, "find_spec", lambda name: None)

    return_code = package_app.run_pyinstaller_build(["pyinstaller", "--version"], root=tmp_path)

    captured = capsys.readouterr()
    assert return_code != 0
    assert "Chưa cài PyInstaller" in captured.err
    assert "python -m pip install pyinstaller" in captured.err


def test_clean_targets_never_include_artist_outputs_or_sources() -> None:
    clean_parts = {
        part
        for relative_path in package_app.PACKAGING_CLEAN_RELATIVE_PATHS
        for part in relative_path.parts
    }

    assert "outputs" not in clean_parts
    assert "maya" not in clean_parts
    assert "preview" not in clean_parts
    assert "tmp" not in clean_parts
    assert "assets" not in clean_parts
    assert "drops" not in clean_parts


def test_clean_packaging_outputs_only_removes_build_and_dist(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    dist_dir = tmp_path / "dist"
    protected_dir = tmp_path / "outputs" / "maya"
    build_dir.mkdir()
    dist_dir.mkdir()
    protected_dir.mkdir(parents=True)
    (protected_dir / "keep.ma").write_text("maya output", encoding="utf-8")

    package_app.clean_packaging_outputs(tmp_path)

    assert not build_dir.exists()
    assert not dist_dir.exists()
    assert protected_dir.exists()
    assert (protected_dir / "keep.ma").exists()
