"""
manifest.py — TuPhuongVoLo-ArtPipeline

Purpose:
    Read, write, and query the asset manifest (JSON format).
    Tracks all generated outputs with metadata, versions, and checksums.

Usage (future):
    from manifest import ManifestManager
    mgr = ManifestManager(manifest_path)
    mgr.add_entry(asset_name="kho", stage="iso", ...)
    entries = mgr.query(stage="svgclean")

Status: PLACEHOLDER — TODO: Implement manifest logic

See: specs/003-asset-naming-and-manifest/spec.md
"""

import hashlib
from pathlib import Path


def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    # TODO: Implement checksum calculation
    # sha256 = hashlib.sha256()
    # with open(file_path, "rb") as f:
    #     for chunk in iter(lambda: f.read(8192), b""):
    #         sha256.update(chunk)
    # return f"sha256:{sha256.hexdigest()}"
    return "sha256:placeholder"


def add_manifest_entry(manifest_path: Path, entry: dict) -> None:
    """Append an entry to the asset manifest."""
    # TODO: Implement manifest append:
    # 1. Read existing manifest (or create empty list)
    # 2. Append new entry
    # 3. Write back to file
    print(f"TODO: Add manifest entry to {manifest_path}")


def query_manifest(manifest_path: Path, **filters) -> list[dict]:
    """Query manifest entries by field filters."""
    # TODO: Implement manifest query
    print(f"TODO: Query manifest at {manifest_path} with filters {filters}")
    return []


def main() -> None:
    """CLI entry point for manifest operations."""
    print("=" * 60)
    print("TuPhuongVoLo-ArtPipeline — Manifest Manager")
    print("=" * 60)
    print()
    print("⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)")
    print("TODO: Implement manifest read/write/query")
    print("See: specs/003-asset-naming-and-manifest/spec.md")


if __name__ == "__main__":
    main()
