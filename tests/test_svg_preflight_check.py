"""Tests for Phase 007M SVG preflight checker."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import svg_preflight_check as preflight


def write_text(path: Path, text: str) -> Path:
    """Write a UTF-8 text fixture."""

    path.write_text(text, encoding="utf-8")
    return path


def write_svg(
    path: Path,
    body: str,
    attrs: str = 'width="100" height="80" viewBox="0 0 100 80"',
) -> Path:
    """Write a minimal SVG fixture."""

    return write_text(
        path,
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" {attrs}>
{body}
</svg>
""",
    )


def test_ok_svg_with_supported_shape_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    svg_path = write_svg(
        tmp_path / "room.svg",
        '<g id="room_kho"><rect id="wall_main" width="50" height="40"/></g>',
    )

    exit_code = preflight.main(["--input", str(svg_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Kết quả: OK" in captured.out
    assert "Shape đang hiển thị: 1" in captured.out


def test_warning_svg_still_exits_zero_and_reports_markers(tmp_path: Path) -> None:
    svg_path = write_svg(
        tmp_path / "real_export.svg",
        """
<g id="room_kho">
  <rect id="prop_table_rot90_mat_wood" width="10" height="8"/>
  <path id="door_main" d="M0 0 L10 0"/>
  <text id="note">artist note</text>
  <image id="paint_ref" href="ref.png"/>
  <clipPath id="clip_ref"/>
  <circle id="window_round" r="4"/>
</g>
""",
        attrs='width="100" height="80"',
    )

    report = preflight.check_svg(svg_path)

    assert report.status == "WARNING"
    assert report.checks["has_viewBox"] is False
    assert report.counts["visible_shape_candidates"] == 2
    assert report.risky_elements == {"text": 1, "image": 1, "clipPath": 1, "circle": 1}
    assert report.counts["prop_marker_candidates"] == 1
    assert report.counts["orientation_marker_candidates"] == 1
    assert report.counts["door_window_marker_candidates"] == 2
    assert report.counts["material_color_candidates"] == 1


def test_console_summary_lists_marker_names_and_missing_openings(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    svg_path = write_svg(
        tmp_path / "props_only.svg",
        """
<g id="room_kho">
  <path id="room_boundary" d="M0 0 L100 0 L100 80 L0 80 Z"/>
  <g id="prop_barrel_01"><path d="M20,20 c10,0 20,5 30,0"/></g>
</g>
""",
    )

    exit_code = preflight.main(["--input", str(svg_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Danh sách prop marker: prop_barrel_01" in captured.out
    assert "Door/window marker: 0" in captured.out
    assert "Không tìm thấy door_/window_ marker trong SVG export" in captured.out


def test_console_summary_lists_door_window_marker_names(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    svg_path = write_svg(
        tmp_path / "openings.svg",
        """
<g id="room_kho">
  <path id="room_boundary" d="M0 0 L100 0 L100 80 L0 80 Z"/>
  <g id="door_main"><rect width="10" height="4"/></g>
</g>
""",
    )

    exit_code = preflight.main(["--input", str(svg_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Danh sách door/window marker: door_main" in captured.out


@pytest.mark.parametrize(
    "marker_markup",
    [
        '<g id="some_exported_id" data-name="door_main"><rect width="10" height="4"/></g>',
        '<g id="some_exported_id" aria-label="door_main"><rect width="10" height="4"/></g>',
        '<g id="some_exported_id" title="door_main"><rect width="10" height="4"/></g>',
        '<g id="some_exported_id"><title>window_back</title><rect width="10" height="4"/></g>',
    ],
)
def test_preflight_detects_opening_marker_from_preserved_metadata_names(
    tmp_path: Path,
    marker_markup: str,
) -> None:
    svg_path = write_svg(
        tmp_path / "metadata_opening.svg",
        f"""
<g id="room_kho">
  <path id="room_boundary" d="M0 0 L100 0 L100 80 L0 80 Z"/>
  {marker_markup}
</g>
""",
    )

    report = preflight.check_svg(svg_path)

    assert report.counts["door_window_marker_candidates"] == 1
    assert report.door_window_marker_candidates[0].value in {"door_main", "window_back"}


def test_hidden_shapes_are_reported_and_not_counted_visible(tmp_path: Path) -> None:
    svg_path = write_svg(
        tmp_path / "hidden.svg",
        """
<g id="hidden_group" display="none">
  <rect id="hidden_rect" width="10" height="10"/>
</g>
<path id="visible_path" d="M0 0 L20 0"/>
""",
    )

    report = preflight.check_svg(svg_path)

    assert report.status == "WARNING"
    assert report.counts["visible_shape_candidates"] == 1
    assert "g#hidden_group" in report.hidden_elements
    assert "rect#hidden_rect" in report.hidden_elements


def test_json_output_is_written_without_modifying_svg(tmp_path: Path) -> None:
    svg_path = write_svg(
        tmp_path / "room.svg",
        '<path id="object_chair_color_red" d="M0 0 L20 0"/>',
    )
    before = svg_path.read_text(encoding="utf-8")
    json_output = tmp_path / "outputs" / "reports" / "svg_preflight_report.json"

    exit_code = preflight.main(["--input", str(svg_path), "--json-output", str(json_output)])

    payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert svg_path.read_text(encoding="utf-8") == before
    assert payload["input_path"] == str(svg_path.resolve())
    assert payload["status"] == "OK"
    assert payload["counts"]["prop_marker_candidates"] == 1
    assert payload["counts"]["material_color_candidates"] == 1


def test_missing_file_is_fatal_nonzero(tmp_path: Path) -> None:
    exit_code = preflight.main(["--input", str(tmp_path / "missing.svg")])

    assert exit_code == 2


def test_invalid_xml_is_fatal(tmp_path: Path) -> None:
    svg_path = write_text(tmp_path / "bad.svg", "<svg><g></svg>")

    report = preflight.check_svg(svg_path)

    assert report.status == "FATAL"
    assert report.checks["xml_parseable"] is False
    assert "XML không hợp lệ" in report.fatal_errors[0]


def test_non_svg_root_is_fatal(tmp_path: Path) -> None:
    xml_path = write_text(tmp_path / "not_svg.svg", "<html></html>")

    report = preflight.check_svg(xml_path)

    assert report.status == "FATAL"
    assert report.checks["xml_parseable"] is True
    assert report.checks["root_is_svg"] is False


def test_non_svg_extension_is_warning_not_fatal(tmp_path: Path) -> None:
    svg_path = write_svg(tmp_path / "export.txt", '<path id="wall" d="M0 0 L20 0"/>')

    exit_code = preflight.main(["--input", str(svg_path)])

    assert exit_code == 0


def test_version_output(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        preflight.main(["--version"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "svg-preflight-check 0.7.10 (007M)" in captured.out
