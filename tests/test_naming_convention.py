"""Tests for Feature 003 naming convention behavior."""

from __future__ import annotations

import pytest
from manifest import (
    AssetNameParts,
    format_version,
    load_naming_convention,
    normalize_asset_name,
    validate_asset_parts,
)


def test_valid_asset_names_accepted() -> None:
    """Snake_case asset names are accepted."""

    parts = validate_asset_parts(AssetNameParts("motel_room", "main", "raw", "001"))

    assert parts.asset_name == "motel_room"


def test_invalid_asset_names_are_normalized() -> None:
    """Uppercase, spaces, diacritics, and leading digits are normalized."""

    assert normalize_asset_name("  12 S\u1ea3nh Ch\u00ednh!!! ") == "asset_12_sanh_chinh"


def test_allowed_stages_loaded_from_config() -> None:
    """The stage list comes from naming_convention.yaml."""

    cfg = load_naming_convention()

    assert "raw" in cfg.allowed_stages
    assert "svgclean" in cfg.allowed_stages
    with pytest.raises(ValueError, match="Stage"):
        validate_asset_parts(AssetNameParts("motel_room", "main", "unknown", "001"), cfg)


def test_version_format_is_three_digits() -> None:
    """Versions are always zero-padded to three digits."""

    assert format_version(1) == "001"
    assert format_version("3") == "003"
    assert format_version("v015") == "015"


def test_output_directory_mapping_exists_for_required_stages() -> None:
    """Each required pipeline stage has an output directory mapping."""

    cfg = load_naming_convention()
    required_stages = {
        "raw",
        "svgraw",
        "svgclean",
        "blockout",
        "iso",
        "preview",
        "final_candidate",
    }

    assert required_stages.issubset(set(cfg.output_directories))
