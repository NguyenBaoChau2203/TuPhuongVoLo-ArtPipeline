"""Tests for Phase 011A Illustrator agent sandbox backup workflow."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import illustrator_agent_sandbox as sandbox


FIXED_TIMESTAMP = "20260604_101500"


def write_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create small dummy inputs that do not require Illustrator."""

    source_ai = tmp_path / "phong_kho.ai"
    source_svg = tmp_path / "phong_kho.svg"
    source_png = tmp_path / "phong_kho.png"
    source_ai.write_text("dummy ai bytes are not parsed\n", encoding="utf-8")
    source_svg.write_text("<svg><g id=\"room_phong_kho\" /></svg>\n", encoding="utf-8")
    source_png.write_bytes(b"\x89PNG\r\n\x1a\n")
    return source_ai, source_svg, source_png


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
    assert "--source-ai" in result.stdout
    assert "--source-svg" in result.stdout
    assert "--source-png" in result.stdout
    assert "--dry-run" in result.stdout


def test_dry_run_creates_no_files_or_folders(tmp_path: Path, monkeypatch, capsys) -> None:
    source_ai, source_svg, _source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
            "--source-svg",
            str(source_svg),
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
    assert "Source paths:" in output
    assert "Original paths:" in output
    assert "Working paths:" in output
    assert "Report paths:" in output
    assert str(session_dir(backup_root)) in output
    assert not backup_root.exists()


def test_sandbox_creation_copies_ai_svg_and_png(tmp_path: Path, monkeypatch) -> None:
    source_ai, source_svg, source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
            "--source-svg",
            str(source_svg),
            "--source-png",
            str(source_png),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    created = session_dir(backup_root)
    assert (created / "original" / "source_ai_before_agent.ai").read_text(
        encoding="utf-8"
    ) == "dummy ai bytes are not parsed\n"
    assert (created / "working" / "scene_agent_work.ai").read_text(encoding="utf-8") == (
        "dummy ai bytes are not parsed\n"
    )
    assert (created / "original" / "source_svg_before_agent.svg").read_text(
        encoding="utf-8"
    ) == "<svg><g id=\"room_phong_kho\" /></svg>\n"
    assert (created / "working" / "scene_agent_work.svg").read_text(encoding="utf-8") == (
        "<svg><g id=\"room_phong_kho\" /></svg>\n"
    )
    assert (created / "original" / "source_png_before_agent.png").read_bytes() == b"\x89PNG\r\n\x1a\n"
    assert (created / "working" / "scene_agent_work.png").read_bytes() == b"\x89PNG\r\n\x1a\n"


def test_svg_png_only_session_works_without_ai(tmp_path: Path, monkeypatch) -> None:
    _source_ai, source_svg, source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--source-svg",
            str(source_svg),
            "--source-png",
            str(source_png),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    created = session_dir(backup_root)
    assert not (created / "original" / "source_ai_before_agent.ai").exists()
    assert not (created / "working" / "scene_agent_work.ai").exists()
    assert (created / "original" / "source_svg_before_agent.svg").is_file()
    assert (created / "working" / "scene_agent_work.svg").is_file()
    assert (created / "original" / "source_png_before_agent.png").is_file()
    assert (created / "working" / "scene_agent_work.png").is_file()


def test_at_least_one_source_file_is_required(tmp_path: Path, capsys) -> None:
    exit_code = sandbox.main(["--backup-root", str(tmp_path / "backups")])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Cần cung cấp ít nhất một file" in captured.err


def test_missing_provided_file_fails_clearly(tmp_path: Path, capsys) -> None:
    missing_svg = tmp_path / "missing.svg"

    exit_code = sandbox.main(
        ["--source-svg", str(missing_svg), "--backup-root", str(tmp_path / "backups")]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Không tìm thấy source SVG" in captured.err
    assert str(missing_svg) in captured.err


def test_report_json_contains_expected_paths(tmp_path: Path, monkeypatch) -> None:
    source_ai, source_svg, source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
            "--source-svg",
            str(source_svg),
            "--source-png",
            str(source_png),
            "--room",
            "Phòng Kho",
            "--session-name",
            "Layer Audit",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    created = backup_root / f"{FIXED_TIMESTAMP}_phong_kho_layer_audit"
    report_path = created / "reports" / "illustrator_agent_session.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["timestamp"] == FIXED_TIMESTAMP
    assert report["room"] == "Phòng Kho"
    assert report["session_name"] == "Layer Audit"
    assert report["label"] == "phong_kho_layer_audit"
    assert report["backup_root"] == str(backup_root.resolve())
    assert report["session_dir"] == str(created.resolve())
    assert "git_commit" in report
    assert report["inputs"]["source_ai"] == str(source_ai.resolve())
    assert report["inputs"]["source_svg"] == str(source_svg.resolve())
    assert report["inputs"]["source_png"] == str(source_png.resolve())
    assert report["original_paths"]["source_ai_before_agent"].endswith(
        "original\\source_ai_before_agent.ai"
    ) or report["original_paths"]["source_ai_before_agent"].endswith(
        "original/source_ai_before_agent.ai"
    )
    assert report["working_paths"]["scene_agent_work_ai"].endswith(
        "working\\scene_agent_work.ai"
    ) or report["working_paths"]["scene_agent_work_ai"].endswith(
        "working/scene_agent_work.ai"
    )
    assert "safety_notes" in report


def test_vietnamese_agent_notes_mention_working_ai_file(tmp_path: Path, monkeypatch) -> None:
    source_ai, _source_svg, _source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
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
    assert "working/scene_agent_work.ai" in notes
    assert "File gốc `.ai`, `.svg`, `.png`" in notes
    assert "Họa sĩ phải review" in notes


def test_restore_illustrator_backup_ps1_exists(tmp_path: Path, monkeypatch) -> None:
    source_ai, _source_svg, _source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)

    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    restore_script = (session_dir(backup_root) / "restore_illustrator_backup.ps1").read_text(
        encoding="utf-8"
    )
    assert "RestoreTargetFolder" in restore_script
    assert "source_ai_before_agent.ai" in restore_script
    assert "Copy-Item" in restore_script
    assert "-Force" in restore_script


def test_existing_session_is_refused_without_force(tmp_path: Path, monkeypatch) -> None:
    source_ai, _source_svg, _source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)
    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    sandbox.run(args)

    with pytest.raises(FileExistsError):
        sandbox.run(args)


def test_force_replaces_only_a_direct_child_session_folder(tmp_path: Path, monkeypatch) -> None:
    source_ai, _source_svg, _source_png = write_inputs(tmp_path)
    backup_root = tmp_path / "backups"
    monkeypatch.setattr(sandbox, "current_timestamp", lambda: FIXED_TIMESTAMP)
    args = parse_args(
        [
            "--source-ai",
            str(source_ai),
            "--room",
            "phong_kho",
            "--backup-root",
            str(backup_root),
        ]
    )
    plan = sandbox.run(args)
    stale_file = session_dir(backup_root) / "working" / "stale.txt"
    stale_file.write_text("old", encoding="utf-8")

    source_ai.write_text("replacement\n", encoding="utf-8")
    sandbox.run(parse_args([*args_to_list(args), "--force"]))

    assert not stale_file.exists()
    assert (session_dir(backup_root) / "working" / "scene_agent_work.ai").read_text(
        encoding="utf-8"
    ) == "replacement\n"

    nested_session = backup_root / "nested" / "unsafe_session"
    nested_session.mkdir(parents=True)
    unsafe_plan = replace(
        plan,
        session_dir=nested_session,
        original_dir=nested_session / "original",
        working_dir=nested_session / "working",
        reports_dir=nested_session / "reports",
        restore_script=nested_session / "restore_illustrator_backup.ps1",
    )

    with pytest.raises(ValueError):
        sandbox.create_sandbox(unsafe_plan, force=True)
    assert nested_session.exists()


def args_to_list(args) -> list[str]:
    """Return the CLI args used by the force replacement test."""

    items: list[str] = []
    if args.source_ai:
        items.extend(["--source-ai", str(args.source_ai)])
    if args.source_svg:
        items.extend(["--source-svg", str(args.source_svg)])
    if args.source_png:
        items.extend(["--source-png", str(args.source_png)])
    if args.room:
        items.extend(["--room", args.room])
    if args.session_name:
        items.extend(["--session-name", args.session_name])
    if args.backup_root:
        items.extend(["--backup-root", str(args.backup_root)])
    return items


def test_gitignore_contains_ai_and_ait_rules() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "*.ai" in gitignore.splitlines()
    assert "*.ait" in gitignore.splitlines()
