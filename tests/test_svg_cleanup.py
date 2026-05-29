"""Tests for Feature 002 SVG cleanup and validation."""

from __future__ import annotations

from pathlib import Path

from clean_svg_paths import clean_output_name, clean_svg_file, clean_svg_input
from validate_svg_contract import validate_svg_file


def write_svg(path: Path, body: str) -> Path:
    """Write a minimal SVG test file."""

    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
{body}
</svg>
""",
        encoding="utf-8",
    )
    return path


def test_hidden_elements_removed(tmp_path: Path) -> None:
    """Cleanup removes display:none, visibility:hidden, and opacity:0 elements."""

    raw_svg = write_svg(
        tmp_path / "raw.svg",
        """
<g id="room_kho">
  <path id="visible" d="M0 0 L10 0 L10 10 Z"/>
  <path id="hidden_a" display="none" d="M0 0 L10 0"/>
  <path id="hidden_b" visibility="hidden" d="M0 0 L10 0"/>
  <path id="hidden_c" opacity="0" d="M0 0 L10 0"/>
</g>
""",
    )
    output_svg = tmp_path / "clean.svg"

    report = clean_svg_file(raw_svg, output_svg)

    text = output_svg.read_text(encoding="utf-8")
    assert report.removed_hidden == 3
    assert "hidden_a" not in text
    assert "hidden_b" not in text
    assert "hidden_c" not in text
    assert "visible" in text


def test_tiny_path_removed(tmp_path: Path) -> None:
    """Cleanup removes clearly tiny path artifacts."""

    raw_svg = write_svg(
        tmp_path / "tiny.svg",
        """
<g id="room_kho">
  <path id="tiny" d="M0 0 L0.1 0.1"/>
  <path id="wall" d="M0 0 L20 0 L20 20 Z"/>
</g>
""",
    )
    output_svg = tmp_path / "clean.svg"

    report = clean_svg_file(raw_svg, output_svg, min_path_length=1.0, min_bbox_side=1.0)

    text = output_svg.read_text(encoding="utf-8")
    assert report.removed_tiny_paths == 1
    assert "tiny" not in text
    assert "wall" in text


def test_embedded_raster_image_detected(tmp_path: Path) -> None:
    """Cleanup reports embedded raster image elements without deleting source files."""

    raw_svg = write_svg(
        tmp_path / "raster.svg",
        """
<g id="room_kho">
  <image id="painted_ref" href="data:image/png;base64,AAAA" width="10" height="10"/>
  <path id="wall" d="M0 0 L20 0 L20 20 Z"/>
</g>
""",
    )
    output_svg = tmp_path / "clean.svg"

    report = clean_svg_file(raw_svg, output_svg)

    assert report.raster_images
    assert "painted_ref" in report.raster_images[0]
    assert raw_svg.exists()


def test_validator_fails_on_transform_in_strict_mode(tmp_path: Path) -> None:
    """Strict validation fails if transforms remain."""

    svg_path = write_svg(
        tmp_path / "transform.svg",
        """
<g id="room_kho" transform="translate(10 0)">
  <path id="wall" d="M0 0 L20 0 L20 20 Z"/>
</g>
""",
    )

    report = validate_svg_file(svg_path, strict=True)

    assert not report.passed
    assert any("transform" in error for error in report.errors)


def test_validator_passes_minimal_clean_svg(tmp_path: Path) -> None:
    """Validator passes a minimal clean SVG with meaningful layer IDs."""

    svg_path = write_svg(
        tmp_path / "clean.svg",
        """
<g id="room_kho">
  <path id="wall_main" d="M0 0 L20 0 L20 20 L0 20 Z"/>
</g>
""",
    )

    report = validate_svg_file(svg_path, strict=True)

    assert report.passed
    assert report.errors == []


def test_directory_input_processes_multiple_svg_files(tmp_path: Path) -> None:
    """Directory input cleans each SVG into the output directory."""

    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    output_dir.mkdir()
    write_svg(input_dir / "a.svg", '<g id="room_a"><path id="wall_a" d="M0 0 L20 0 Z"/></g>')
    write_svg(input_dir / "b.svg", '<g id="room_b"><path id="wall_b" d="M0 0 L30 0 Z"/></g>')

    reports = clean_svg_input(input_dir, output_dir)

    assert len(reports) == 2
    assert (output_dir / "tu_phuong_vo_lo_a_main_svgclean_v001.svg").exists()
    assert (output_dir / "tu_phuong_vo_lo_b_main_svgclean_v001.svg").exists()


def test_file_output_path_still_uses_convention_name(tmp_path: Path) -> None:
    """Even explicit file outputs are normalized to the repository convention."""

    raw_svg = write_svg(
        tmp_path / "a.svg",
        '<g id="room_a"><path id="wall_a" d="M0 0 L20 0 Z"/></g>',
    )

    reports = clean_svg_input(raw_svg, tmp_path / "custom.svg")

    assert reports[0].output_path.name == "tu_phuong_vo_lo_a_main_svgclean_v001.svg"
    assert (tmp_path / "tu_phuong_vo_lo_a_main_svgclean_v001.svg").exists()


def test_clean_output_name_normalizes_arbitrary_input() -> None:
    """Arbitrary SVG names are normalized into the repository convention."""

    assert clean_output_name(Path("a.svg")) == "tu_phuong_vo_lo_a_main_svgclean_v001.svg"


def test_clean_output_name_normalizes_vietnamese_diacritics() -> None:
    """Vietnamese names use the shared Feature 003 normalization."""

    source = Path("S\u1ea3nh ch\u00ednh.svg")

    assert clean_output_name(source) == "tu_phuong_vo_lo_sanh_chinh_main_svgclean_v001.svg"


def test_clean_output_name_preserves_convention_fields() -> None:
    """Convention input preserves asset, variant, and version while changing stage."""

    source = Path("tu_phuong_vo_lo_motel_room_ab01_svgraw_v003.svg")

    assert clean_output_name(source) == "tu_phuong_vo_lo_motel_room_ab01_svgclean_v003.svg"
