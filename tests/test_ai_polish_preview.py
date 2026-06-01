"""Tests for Phase 005.5C optional AI polish preview providers."""

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


def test_fal_dry_run_creates_no_output_and_does_not_import_client(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"

    def fail_import() -> None:
        pytest.fail("dry-run must not import fal_client")

    monkeypatch.setattr(ai_preview, "import_fal_client", fail_import)
    monkeypatch.setenv("FAL_KEY", "test-secret")

    exit_code = ai_preview.main(
        [
            "--dry-run",
            "--provider",
            "fal",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--model",
            "fal-ai/flux-pro/kontext",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dry-run" in captured.out
    assert "fal-ai/flux-pro/kontext" in captured.out
    assert "không gọi API" in captured.out
    assert not output_dir.exists()


def test_fal_missing_key_with_skip_exits_zero_and_writes_skipped_report(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"
    monkeypatch.delenv("FAL_KEY", raising=False)

    exit_code = ai_preview.main(
        [
            "--provider",
            "fal",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--skip-on-missing-config",
        ]
    )

    captured = capsys.readouterr()
    report_json = output_dir / "sample_preview_v001_fal_ai_preview_report.json"
    output_png = output_dir / "sample_preview_v001_fal_ai_preview.png"
    report = json.loads(report_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert "Bỏ qua AI polish preview fal" in captured.out
    assert not output_png.exists()
    assert report["provider"] == "fal"
    assert report["status"] == "skipped"
    assert report["skipped"] is True
    assert report["external_api_called"] is False
    assert report["error_type"] == "missing_fal_key"


def test_fal_missing_key_without_skip_returns_vietnamese_error(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"
    monkeypatch.delenv("FAL_KEY", raising=False)

    exit_code = ai_preview.main(
        [
            "--provider",
            "fal",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
        ]
    )

    captured = capsys.readouterr()
    report_json = output_dir / "sample_preview_v001_fal_ai_preview_report.json"
    report = json.loads(report_json.read_text(encoding="utf-8"))

    assert exit_code == 2
    assert "Thiếu FAL_KEY" in captured.err
    assert report["status"] == "failed"
    assert report["skipped"] is False
    assert report["external_api_called"] is False
    assert report["error_type"] == "missing_fal_key"


def test_fal_missing_client_returns_optional_dependency_error(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"
    monkeypatch.setenv("FAL_KEY", "test-secret")
    monkeypatch.setattr(
        ai_preview,
        "import_fal_client",
        lambda: (_ for _ in ()).throw(ImportError("No module named fal_client")),
    )

    exit_code = ai_preview.main(
        [
            "--provider",
            "fal",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
        ]
    )

    captured = capsys.readouterr()
    report_text = (output_dir / "sample_preview_v001_fal_ai_preview_report.json").read_text(
        encoding="utf-8"
    )
    report = json.loads(report_text)

    assert exit_code == 2
    assert "python -m pip install fal-client" in captured.err
    assert report["error_type"] == "missing_fal_client"
    assert report["external_api_called"] is False
    assert "test-secret" not in report_text


def test_fal_fake_success_downloads_image_and_writes_safe_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = write_png(tmp_path / "sample_preview.png")
    output_dir = tmp_path / "outputs" / "ai_preview"
    calls: dict[str, object] = {}

    class FakeFalClient:
        @staticmethod
        def upload_file(path: str) -> str:
            calls["uploaded_path"] = path
            return "https://fal.example/uploaded/sample_preview.png"

        @staticmethod
        def subscribe(
            application: str,
            *,
            arguments: dict[str, object],
            with_logs: bool,
            client_timeout: int,
        ) -> dict[str, object]:
            calls["application"] = application
            calls["arguments"] = arguments
            calls["with_logs"] = with_logs
            calls["client_timeout"] = client_timeout
            return {"images": [{"url": "https://fal.example/generated/result.png"}]}

    def fake_download(url: str, output_path: Path, timeout_seconds: int) -> None:
        calls["download_url"] = url
        calls["download_timeout"] = timeout_seconds
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(PNG_BYTES)

    monkeypatch.setenv("FAL_KEY", "test-secret")
    monkeypatch.setattr(ai_preview, "import_fal_client", lambda: FakeFalClient)
    monkeypatch.setattr(ai_preview, "download_url_to_file", fake_download)

    exit_code = ai_preview.main(
        [
            "--provider",
            "fal",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--model",
            "fal-ai/custom-kontext",
            "--timeout-seconds",
            "33",
            "--prompt",
            "Improve humid lantern lighting",
        ]
    )

    output_png = output_dir / "sample_preview_v001_fal_ai_preview.png"
    report_json = output_dir / "sample_preview_v001_fal_ai_preview_report.json"
    report_text = report_json.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert exit_code == 0
    assert output_png.read_bytes() == PNG_BYTES
    assert calls["uploaded_path"] == str(source.resolve())
    assert calls["application"] == "fal-ai/custom-kontext"
    assert calls["arguments"] == {
        "prompt": "Improve humid lantern lighting",
        "image_url": "https://fal.example/uploaded/sample_preview.png",
        "num_images": 1,
        "output_format": "png",
    }
    assert calls["with_logs"] is False
    assert calls["client_timeout"] == 33
    assert calls["download_url"] == "https://fal.example/generated/result.png"
    assert calls["download_timeout"] == 33
    assert report["provider"] == "fal"
    assert report["model"] == "fal-ai/custom-kontext"
    assert report["status"] == "fal_created"
    assert report["external_api_called"] is True
    assert report["skipped"] is False
    assert report["error_type"] is None
    assert report["output_path"] == str(output_png.resolve())
    assert report["report_path"] == str(report_json.resolve())
    assert report["prompt"] == "Improve humid lantern lighting"
    assert "test-secret" not in report_text


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
