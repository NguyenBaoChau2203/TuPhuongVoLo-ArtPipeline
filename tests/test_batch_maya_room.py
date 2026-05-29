"""Tests for Feature 005 batch Maya planning without Maya."""

from __future__ import annotations

import json
from pathlib import Path

import batch_maya_room as batch


def write_svg(path: Path, body: str | None = None) -> Path:
    """Write a minimal clean SVG test file."""

    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="100" height="100">
{body or '<g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>'}
</svg>
""",
        encoding="utf-8",
    )
    return path


def parser_args(items: list[str]):
    """Parse test args through the real CLI parser."""

    return batch.build_parser().parse_args(items)


def isolated_manifest(monkeypatch, tmp_path: Path) -> Path:
    """Redirect Feature 005 manifest lookups to a temp path."""

    manifest_path = tmp_path / "manifest" / "asset_manifest.json"
    monkeypatch.setattr(
        batch.builder.asset_manifest,
        "resolve_manifest_path",
        lambda *args, **kwargs: manifest_path,
    )
    return manifest_path


def test_input_dir_scans_multiple_svg_files(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    input_dir = tmp_path / "svg_clean"
    input_dir.mkdir()
    write_svg(input_dir / "b.svg")
    write_svg(input_dir / "a.svg")

    args = parser_args(
        [
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)

    assert report.scanned_files == 2
    assert report.detected_rooms == 2
    assert report.planned_jobs == 2
    assert [job.source_svg.name for job in report.jobs] == ["a.svg", "b.svg"]


def test_input_file_creates_one_maya_job(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "one.svg")

    args = parser_args(
        [
            "--input-file",
            str(svg),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)

    assert report.scanned_files == 1
    assert report.planned_jobs == 1
    assert report.jobs[0].room_name == "kho"


def test_all_rooms_creates_multiple_jobs_from_one_svg(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(
        tmp_path / "rooms.svg",
        """
<g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>
<g id="room_sanh_chinh"><path d="M20 0 L30 0 L30 10 L20 10 Z"/></g>
""",
    )

    args = parser_args(
        [
            "--input-file",
            str(svg),
            "--all-rooms",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)

    assert report.planned_jobs == 2
    assert [job.room_name for job in report.jobs] == ["kho", "sanh_chinh"]


def test_room_filter_selects_normalized_vietnamese_room_name(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(
        tmp_path / "rooms.svg",
        """
<g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>
<g id="g2" inkscape:label="Sảnh chính">
  <path d="M20 0 L30 0 L30 10 L20 10 Z"/>
</g>
""",
    )

    args = parser_args(
        [
            "--input-file",
            str(svg),
            "--room",
            "Sảnh chính",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)

    assert report.planned_jobs == 1
    assert report.jobs[0].room_name == "sanh_chinh"


def test_corrupt_svg_is_failed_but_batch_continues_by_default(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    input_dir = tmp_path / "svg_clean"
    input_dir.mkdir()
    (input_dir / "bad.svg").write_text("<svg><g>", encoding="utf-8")
    write_svg(input_dir / "good.svg")

    args = parser_args(
        [
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)

    assert report.scanned_files == 2
    assert report.planned_jobs == 1
    assert report.failed == 1
    assert report.jobs[-1].room_name == "kho"


def test_stop_on_error_stops_after_first_failure(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    input_dir = tmp_path / "svg_clean"
    input_dir.mkdir()
    (input_dir / "a_bad.svg").write_text("<svg><g>", encoding="utf-8")
    write_svg(input_dir / "b_good.svg")

    args = parser_args(
        [
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
            "--stop-on-error",
        ]
    )
    report = batch.run_batch(args)

    assert report.failed == 1
    assert report.planned_jobs == 0
    assert len(report.jobs) == 1


def test_dry_run_writes_json_report(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "one.svg")
    report_path = tmp_path / "reports" / "batch_maya.json"

    exit_code = batch.main(
        [
            "--input-file",
            str(svg),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
            "--json-report",
            str(report_path),
        ]
    )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["planned_jobs"] == 1
    assert payload["jobs"][0]["status"] == "planned"


def test_dry_run_does_not_write_manifest(tmp_path: Path, monkeypatch) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "one.svg")

    exit_code = batch.main(
        [
            "--input-file",
            str(svg),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
            "--json-report",
            str(tmp_path / "report.json"),
        ]
    )

    assert exit_code == 0
    assert not manifest_path.exists()


def test_job_file_can_be_loaded(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "one.svg")
    job_file = tmp_path / "jobs.json"
    planned_output = tmp_path / "outputs" / "maya" / "tu_phuong_vo_lo_kho_main_maya_v001.ma"
    job_file.write_text(
        json.dumps(
            {
                "jobs": [
                    {
                        "source_svg": str(svg),
                        "room_name": "kho",
                        "style": "line_art_green_floor",
                        "room_preset": "kho",
                        "planned_maya_output": str(planned_output),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    args = parser_args(
        [
            "--job-file",
            str(job_file),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)

    assert report.input_mode == "job-file"
    assert report.planned_jobs == 1
    assert report.jobs[0].source_svg == svg.resolve()


def test_planned_maya_outputs_follow_naming_convention(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "one.svg")

    args = parser_args(
        [
            "--input-file",
            str(svg),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    report = batch.run_batch(args)
    job = report.jobs[0]

    assert job.planned_maya_output is not None
    assert job.planned_maya_output.name == "tu_phuong_vo_lo_kho_main_maya_v001.ma"
