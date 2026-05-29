"""Tests for Feature 003 manifest and naming utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from manifest import (
    AssetNameParts,
    ManifestEntry,
    ManifestError,
    append_manifest_entry,
    compute_checksum,
    generate_filename,
    load_manifest,
    next_version,
    normalize_asset_name,
    parse_asset_filename,
    query_manifest,
)


def make_entry(asset_name: str, stage: str, version: str, output_path: str) -> ManifestEntry:
    """Return a minimal manifest entry for tests."""

    return ManifestEntry(
        asset_name=asset_name,
        variant="main",
        stage=stage,
        version=version,
        source_file=f"drops/{asset_name}.svg",
        output_path=output_path,
        timestamp="2026-05-29T00:00:00+00:00",
        checksum="sha256:test",
        pipeline_step="test",
    )


def test_generate_filename_normalizes_vietnamese_name() -> None:
    """Vietnamese diacritics are converted into safe snake_case names."""

    asset_name = normalize_asset_name("Sảnh chính.svg")
    filename = generate_filename(AssetNameParts(asset_name, "main", "raw", "001"), ".svg")

    assert asset_name == "sanh_chinh"
    assert filename == "tu_phuong_vo_lo_sanh_chinh_main_raw_v001.svg"


def test_parse_existing_convention_fields() -> None:
    """Existing convention-compliant filenames preserve fields."""

    parsed = parse_asset_filename("tu_phuong_vo_lo_motel_room_ab01_svgraw_v003.svg")

    assert parsed == AssetNameParts(
        asset_name="motel_room",
        variant="ab01",
        stage="svgraw",
        version="003",
    )


def test_auto_increment_version_if_v001_exists(tmp_path: Path) -> None:
    """Version generation scans existing files."""

    target_dir = tmp_path / "assets"
    target_dir.mkdir()
    (target_dir / "tu_phuong_vo_lo_kho_main_raw_v001.svg").write_text("<svg/>", encoding="utf-8")

    version = next_version(target_dir, "kho", "main", "raw", extension=".svg")

    assert version == "002"


def test_manifest_append_preserves_existing_entries(tmp_path: Path) -> None:
    """Appending one entry does not overwrite existing manifest entries."""

    manifest_path = tmp_path / "manifest.json"
    first = make_entry("kho", "raw", "001", "assets/2d/svg_raw/kho.svg")
    second = make_entry("sanh", "raw", "001", "assets/2d/svg_raw/sanh.svg")

    append_manifest_entry(manifest_path, first)
    append_manifest_entry(manifest_path, second)

    entries = load_manifest(manifest_path)
    assert len(entries) == 2
    assert entries[0]["asset_name"] == "kho"
    assert entries[1]["asset_name"] == "sanh"


def test_corrupted_manifest_fails_safely(tmp_path: Path) -> None:
    """Corrupted JSON is not silently replaced."""

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ManifestError, match="Manifest JSON"):
        load_manifest(manifest_path)


def test_checksum_is_computed(tmp_path: Path) -> None:
    """SHA-256 checksum includes the expected prefix and digest."""

    file_path = tmp_path / "asset.svg"
    file_path.write_text("abc", encoding="utf-8")

    assert compute_checksum(file_path) == (
        "sha256:ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


def test_query_by_stage(tmp_path: Path) -> None:
    """Manifest query filters by stage."""

    manifest_path = tmp_path / "manifest.json"
    append_manifest_entry(
        manifest_path,
        make_entry("kho", "raw", "001", "assets/2d/svg_raw/kho.svg"),
    )
    append_manifest_entry(
        manifest_path,
        make_entry("kho", "svgclean", "001", "assets/2d/svg_clean/kho.svg"),
    )

    entries = query_manifest(manifest_path, stage="svgclean")

    assert len(entries) == 1
    assert entries[0]["stage"] == "svgclean"


def test_query_by_asset_name(tmp_path: Path) -> None:
    """Manifest query normalizes asset_name filters."""

    manifest_path = tmp_path / "manifest.json"
    payload = [
        make_entry(
            "sanh_chinh",
            "raw",
            "001",
            "assets/2d/svg_raw/tu_phuong_vo_lo_sanh_chinh_main_raw_v001.svg",
        ).__dict__,
        make_entry(
            "kho",
            "raw",
            "001",
            "assets/2d/svg_raw/tu_phuong_vo_lo_kho_main_raw_v001.svg",
        ).__dict__,
    ]
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    entries = query_manifest(manifest_path, asset_name="Sảnh chính")

    assert len(entries) == 1
    assert entries[0]["asset_name"] == "sanh_chinh"
