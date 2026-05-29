"""Tests for Feature 001 SVG room detection."""

from __future__ import annotations

from pathlib import Path

from detect_rooms_from_svg import detect_rooms, main


def write_svg(path: Path, body: str) -> Path:
    """Write a minimal SVG test file."""

    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="100" height="100">
{body}
</svg>
""",
        encoding="utf-8",
    )
    return path


def test_detect_group_id_room_kho(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "rooms.svg",
        '<g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>',
    )

    reports = detect_rooms(svg)

    assert len(reports) == 1
    assert reports[0].room_name == "kho"
    assert reports[0].closed_path_count == 1
    assert reports[0].has_usable_boundary


def test_normalize_vietnamese_inkscape_label(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "rooms.svg",
        '<g id="g123" inkscape:label="Sảnh chính">'
        '<path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>',
    )

    reports = detect_rooms(svg)

    assert reports[0].room_name == "sanh_chinh"
    assert reports[0].original_label == "Sảnh chính"


def test_detect_multiple_rooms(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "rooms.svg",
        """
<g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>
<g id="room_sanh_chinh"><path d="M20 0 L40 0 L40 10 L20 10 Z"/></g>
""",
    )

    reports = detect_rooms(svg)

    assert [report.room_name for report in reports] == ["kho", "sanh_chinh"]


def test_fallback_top_level_path_to_filename_room(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "Sảnh chính.svg",
        '<path d="M0 0 L10 0 L10 10 L0 10 Z"/>',
    )

    reports = detect_rooms(svg)

    assert len(reports) == 1
    assert reports[0].room_name == "sanh_chinh"
    assert reports[0].has_usable_boundary


def test_invalid_svg_fails_gracefully(tmp_path: Path, capsys) -> None:
    bad_svg = tmp_path / "bad.svg"
    bad_svg.write_text("<svg><g>", encoding="utf-8")

    exit_code = main(["--input", str(bad_svg)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "ERR_SVG_INVALID" in captured.err


def test_group_with_no_closed_path_is_reported_with_warning(tmp_path: Path) -> None:
    svg = write_svg(
        tmp_path / "rooms.svg",
        '<g id="room_kho"><path d="M0 0 L10 0"/></g>',
    )

    reports = detect_rooms(svg)

    assert len(reports) == 1
    assert not reports[0].has_usable_boundary
    assert any("Không có path đóng kín" in warning for warning in reports[0].warnings)
