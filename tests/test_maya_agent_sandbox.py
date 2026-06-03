"""Tests for Phase 010A Maya agent sandbox backup workflow."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import maya_agent_sandbox as sandbox


FIXED_TIMESTAMP = "20260603_201500"


def write_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create small test inputs that do not require Maya."""

    maya_scene = tmp_path / "scene.ma"
    geometry_json = tmp_path / "geometry.json"
    source_svg = tmp_path / "source.svg"
    maya_scene.write_text("// maya ascii scene\n", encoding="utf-8")
    geometry_json.write_text('{"room": "phong_kho"}\n', encoding="utf-8")
    source_svg.write_text("<svg><g id=\"room_phong_kho\" /></svg>\n", encoding="utf-8")
    return maya_scene, geometry_json, source_svg


def parse_args(items: list[str]):
    """Parse args through the real CLI parser."""

    return sandbox.build_parser().parse_args(items)


def session_dir(backup_root: Path, label: str = "phong_kho") -> Path:
    """Return the deterministic test session path."""

    return backup_root / f"{FIXED_TIMESTAMP}_{label}"


def test_help_works() -> None:
    script = Path(sandbox.__file__).resolve()

    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--maya-scene" in result.stdout
    assert "--dry-run" in result.stdout


def test_dry_run_does_not_create_files(tmp_path: Path, monkeypatch, capsys) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
            "--dry-run",
        ]
    )
    sandbox.run(args)

    output = capsys.readouterr().out
    assert "DRY RUN" in output
    assert str(session_dir(backup_root)) in output
    assert not backup_root.exists()


def test_creates_expected_folder_structure(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    created = session_dir(backup_root)
    assert (created / "original").is_dir()
    assert (created / "working").is_dir()
    assert (created / "reports").is_dir()


def test_copies_ma_into_original_and_working(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    created = session_dir(backup_root)
    assert (created / "original" / "scene_before_agent.ma").read_text(encoding="utf-8") == (
        "// maya ascii scene\n"
    )
    assert (created / "working" / "scene_agent_work.ma").read_text(encoding="utf-8") == (
        "// maya ascii scene\n"
    )


def test_copies_optional_geometry_json_and_source_svg(tmp_path: Path, monkeypatch) -> None:
    maya_scene, geometry_json, source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--geometry-json",
            str(geometry_json),
            "--source-svg",
            str(source_svg),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    original = session_dir(backup_root) / "original"
    assert (original / "geometry_before_agent.json").read_text(encoding="utf-8") == (
        '{"room": "phong_kho"}\n'
    )
    assert (original / "source_svg_snapshot.svg").read_text(encoding="utf-8") == (
        "<svg><g id=\"room_phong_kho\" /></svg>\n"
    )


def test_writes_agent_session_json_with_expected_fields(tmp_path: Path, monkeypatch) -> None:
    maya_scene, geometry_json, source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--geometry-json",
            str(geometry_json),
            "--source-svg",
            str(source_svg),
            "--room",
            "phong_kho",
            "--session-name",
            "agent_test",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    report_path = backup_root / f"{FIXED_TIMESTAMP}_agent_test" / "reports" / "agent_session.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["timestamp"] == FIXED_TIMESTAMP
    assert report["room"] == "phong_kho"
    assert report["session_name"] == "agent_test"
    assert "git_commit" in report
    assert report["original_input_paths"]["maya_scene"] == str(maya_scene.resolve())
    assert report["copied_sandbox_paths"]["scene_agent_work"].endswith(
        "working\\scene_agent_work.ma"
    ) or report["copied_sandbox_paths"]["scene_agent_work"].endswith(
        "working/scene_agent_work.ma"
    )
    assert report["intended_working_scene_path"] == report["copied_sandbox_paths"][
        "scene_agent_work"
    ]
    assert report["restore_script_path"].endswith("restore_agent_backup.ps1")
    assert "safety_notes" in report


def test_writes_agent_notes_md(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    notes = (session_dir(backup_root) / "reports" / "agent_notes.md").read_text(
        encoding="utf-8"
    )
    assert "Agent chỉ được mở file" in notes
    assert "working/scene_agent_work.ma" in notes
    assert "Không cài MayaMCP" in notes


def test_writes_restore_agent_backup_ps1(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    restore_script = (session_dir(backup_root) / "restore_agent_backup.ps1").read_text(
        encoding="utf-8"
    )
    assert "param(" in restore_script
    assert "scene_before_agent.ma" in restore_script
    assert "Copy-Item" in restore_script
    assert "RestoreTarget" in restore_script


def test_refuses_overwrite_without_force(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)
    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    with pytest.raises(FileExistsError):
        sandbox.run(args)


def test_force_allows_replacing_existing_session_folder(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)
    first_args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(first_args)
    stale_file = session_dir(backup_root) / "working" / "stale.txt"
    stale_file.write_text("old", encoding="utf-8")

    maya_scene.write_text("// replacement scene\n", encoding="utf-8")
    force_args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
            "--force",
        ]
    )
    sandbox.run(force_args)

    assert not stale_file.exists()
    assert (session_dir(backup_root) / "working" / "scene_agent_work.ma").read_text(
        encoding="utf-8"
    ) == "// replacement scene\n"


def test_missing_optional_inputs_are_not_required(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    original = session_dir(backup_root) / "original"
    assert not (original / "geometry_before_agent.json").exists()
    assert not (original / "source_svg_snapshot.svg").exists()


def test_fails_clearly_if_required_maya_scene_does_not_exist(tmp_path: Path, capsys) -> None:
    missing_scene = tmp_path / "missing.ma"

    exit_code = sandbox.main(
        [
            "--maya-scene",
            str(missing_scene),
            "--backup-root",
            str(tmp_path / "backups"),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Không tìm thấy Maya scene" in captured.err


def test_sandbox_does_not_require_maya_installed(tmp_path: Path, monkeypatch) -> None:
    maya_scene, _geometry_json, _source_svg = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--maya-scene",
            str(maya_scene),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    assert (session_dir(backup_root) / "working" / "scene_agent_work.ma").is_file()
