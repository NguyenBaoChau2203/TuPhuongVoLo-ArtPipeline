"""Tests for Phase 005.5B local mock AI polish preview."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

import ai_polish_preview as ai_preview

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def write_png(path: Path) -> Path:
    """Write a tiny PNG fixture for tests."""

    path.write_bytes(PNG_BYTES)
    return path


def test_cli_dry_run_does_not_create_output(tmp_path: Path, capsys) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"

    exit_code = ai_preview.main(
        [
            "--dry-run",
            "--provider",
            "mock",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--prompt-preset",
            "tropical-island-room",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dry-run" in captured.out
    assert "không gọi API" in captured.out
    assert not output_dir.exists()


def test_mock_mode_creates_output_png_copy_and_report_json(tmp_path: Path) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"

    exit_code = ai_preview.main(
        [
            "--provider",
            "mock",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--prompt",
            "soft tropical lighting",
            "--prompt-preset",
            "tropical-island-room",
        ]
    )

    output_png = output_dir / "sample_preview_v001_mock_ai_preview.png"
    report_json = output_dir / "sample_preview_v001_mock_ai_preview_report.json"
    report = json.loads(report_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert output_png.read_bytes() == source.read_bytes()
    assert report["input_path"] == str(source.resolve())
    assert report["output_path"] == str(output_png.resolve())
    assert report["provider"] == "mock"
    assert report["prompt"] == "soft tropical lighting"
    assert report["prompt_preset"] == "tropical-island-room"
    assert report["status"] == "mock_created"
    assert "No external API was called" in report["note"]


def test_missing_input_returns_clear_vietnamese_error(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.png"

    exit_code = ai_preview.main(["--input", str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Không tìm thấy ảnh PNG input" in captured.err


def test_non_png_input_returns_clear_vietnamese_error(tmp_path: Path, capsys) -> None:
    source = tmp_path / "preview.txt"
    source.write_text("not a png", encoding="utf-8")

    exit_code = ai_preview.main(["--input", str(source)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Input phải là file .png" in captured.err


def test_version_works(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        ai_preview.main(["--version"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "ai_polish_preview" in captured.out
    assert ai_preview.AI_PREVIEW_VERSION in captured.out
