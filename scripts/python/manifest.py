"""Shared asset naming and manifest utilities for Feature 003.

This module implements the naming, versioning, checksum, and append-only JSON
manifest foundation used by later pipeline features.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - dependency is declared in requirements.txt
    yaml = None


PROJECT_PREFIX = "tu_phuong_vo_lo"
DEFAULT_PATTERN = "tu_phuong_vo_lo_{asset_name}_{variant}_{stage}_v{version}"
DEFAULT_ALLOWED_STAGES = [
    "raw",
    "traced",
    "svgraw",
    "svgclean",
    "blockout",
    "maya",
    "iso",
    "preview",
    "final_candidate",
]
DEFAULT_OUTPUT_DIRECTORIES = {
    "raw": "assets/2d/svg_raw/",
    "traced": "assets/2d/svg_raw/",
    "svgraw": "outputs/svg/",
    "svgclean": "assets/2d/svg_clean/",
    "blockout": "outputs/blender/",
    "maya": "outputs/maya/",
    "iso": "outputs/blender/",
    "preview": "outputs/preview/",
    "final_candidate": "outputs/png/",
}
DEFAULT_MANIFEST_PATH = "outputs/manifest/asset_manifest.json"
DEFAULT_REQUIRED_FIELDS = [
    "asset_name",
    "variant",
    "stage",
    "version",
    "source_file",
    "output_path",
    "timestamp",
    "checksum",
    "pipeline_step",
]
FIELD_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ASSET_RE = FIELD_RE
VERSION_RE = re.compile(r"^\d{3}$")
UTC = timezone.utc


class ManifestError(RuntimeError):
    """Raised when manifest data cannot be read or validated safely."""


@dataclass(frozen=True)
class AssetNameParts:
    """Naming-convention fields for one asset filename."""

    asset_name: str
    variant: str
    stage: str
    version: str


@dataclass(frozen=True)
class ManifestEntry:
    """One JSON manifest entry for a generated or organized asset."""

    asset_name: str
    variant: str
    stage: str
    version: str
    source_file: str
    output_path: str
    timestamp: str
    checksum: str
    pipeline_step: str


@dataclass(frozen=True)
class NamingConvention:
    """Loaded naming-convention configuration."""

    pattern: str
    allowed_stages: list[str]
    output_directories: dict[str, str]
    manifest_file: str
    required_fields: list[str]
    asset_name_max_length: int
    variant_max_length: int
    version_start: int


def configure_stdio() -> None:
    """Make Vietnamese CLI output safe on Windows terminals."""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def repo_root() -> Path:
    """Return the repository root based on this script location."""

    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    """Return the default naming-convention config path."""

    return repo_root() / "config" / "naming_convention.yaml"


def _warn(message: str) -> None:
    print(f"Cảnh báo: {message}", file=sys.stderr)


def _default_convention() -> NamingConvention:
    return NamingConvention(
        pattern=DEFAULT_PATTERN,
        allowed_stages=list(DEFAULT_ALLOWED_STAGES),
        output_directories=dict(DEFAULT_OUTPUT_DIRECTORIES),
        manifest_file=DEFAULT_MANIFEST_PATH,
        required_fields=list(DEFAULT_REQUIRED_FIELDS),
        asset_name_max_length=40,
        variant_max_length=20,
        version_start=1,
    )


def load_naming_convention(config_path: Path | None = None) -> NamingConvention:
    """Load naming settings from YAML, falling back safely when missing.

    Args:
        config_path: Optional path to `config/naming_convention.yaml`.

    Returns:
        Loaded naming convention settings.
    """

    convention = _default_convention()
    path = config_path or default_config_path()
    if not path.exists():
        _warn(
            "Không tìm thấy config/naming_convention.yaml; dùng quy ước mặc định an toàn."
        )
        return convention
    if yaml is None:
        _warn("Không có PyYAML; dùng quy ước mặc định an toàn.")
        return convention

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        _warn(f"Không đọc được naming_convention.yaml ({exc}); dùng mặc định an toàn.")
        return convention

    naming = data.get("naming", {}) if isinstance(data, dict) else {}
    fields = naming.get("fields", {}) if isinstance(naming, dict) else {}
    asset_field = fields.get("asset_name", {}) if isinstance(fields, dict) else {}
    variant_field = fields.get("variant", {}) if isinstance(fields, dict) else {}
    stage_field = fields.get("stage", {}) if isinstance(fields, dict) else {}
    version_field = fields.get("version", {}) if isinstance(fields, dict) else {}
    manifest = naming.get("manifest", {}) if isinstance(naming, dict) else {}

    return NamingConvention(
        pattern=str(naming.get("pattern", convention.pattern)),
        allowed_stages=list(stage_field.get("allowed_values", convention.allowed_stages)),
        output_directories=dict(naming.get("output_directories", convention.output_directories)),
        manifest_file=str(manifest.get("file", convention.manifest_file)),
        required_fields=list(manifest.get("required_fields", convention.required_fields)),
        asset_name_max_length=int(asset_field.get("max_length", convention.asset_name_max_length)),
        variant_max_length=int(variant_field.get("max_length", convention.variant_max_length)),
        version_start=int(version_field.get("start", convention.version_start)),
    )


def strip_extension(value: str) -> str:
    """Remove one filename extension from a raw name string."""

    return Path(value).stem if "." in value else value


def normalize_asset_name(value: str, max_length: int | None = None) -> str:
    """Normalize arbitrary artist text into safe snake_case asset_name.

    Vietnamese diacritics are converted with `unicodedata`; `đ` and `Đ` are
    handled explicitly because they do not decompose into ASCII.
    """

    limit = max_length or _default_convention().asset_name_max_length
    text = strip_extension(value).strip().lower().replace("đ", "d")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        text = "asset"
    if not re.match(r"^[a-z]", text):
        text = f"asset_{text}"
    text = text[:limit].rstrip("_")
    return text or "asset"


def normalize_variant(value: str, max_length: int | None = None) -> str:
    """Normalize arbitrary variant text into safe snake_case."""

    limit = max_length or _default_convention().variant_max_length
    text = normalize_asset_name(value or "main", max_length=limit)
    return text[:limit].rstrip("_") or "main"


def format_version(version: int | str) -> str:
    """Return a three-digit version string."""

    if isinstance(version, int):
        if not 1 <= version <= 999:
            raise ValueError("Phiên bản phải nằm trong khoảng 001-999.")
        return f"{version:03d}"
    version_text = str(version).strip()
    if version_text.startswith("v"):
        version_text = version_text[1:]
    if version_text.isdigit():
        return f"{int(version_text):03d}"
    raise ValueError("Phiên bản phải là số, ví dụ 001.")


def validate_asset_parts(
    parts: AssetNameParts,
    convention: NamingConvention | None = None,
) -> AssetNameParts:
    """Validate and normalize naming fields."""

    cfg = convention or load_naming_convention()
    asset_name = normalize_asset_name(parts.asset_name, cfg.asset_name_max_length)
    variant = normalize_variant(parts.variant, cfg.variant_max_length)
    stage = parts.stage.strip().lower()
    version = format_version(parts.version)

    if not ASSET_RE.match(asset_name):
        raise ValueError(f"Tên asset không hợp lệ: {asset_name}")
    if not FIELD_RE.match(variant):
        raise ValueError(f"Variant không hợp lệ: {variant}")
    if stage not in cfg.allowed_stages:
        raise ValueError(f"Stage không hợp lệ: {stage}")
    if not VERSION_RE.match(version):
        raise ValueError(f"Version không hợp lệ: {version}")
    return AssetNameParts(asset_name=asset_name, variant=variant, stage=stage, version=version)


def parse_asset_filename(
    path_or_name: Path | str,
    convention: NamingConvention | None = None,
) -> AssetNameParts | None:
    """Parse a filename that follows the project convention.

    Because both `asset_name` and `variant` may contain underscores, the parser
    treats the token immediately before the stage as the variant and all earlier
    body tokens as the asset name.
    """

    cfg = convention or load_naming_convention()
    stem = Path(path_or_name).stem
    prefix = f"{PROJECT_PREFIX}_"
    if not stem.startswith(prefix):
        return None

    body = stem[len(prefix) :]
    for stage in sorted(cfg.allowed_stages, key=len, reverse=True):
        suffix = f"_{stage}_v"
        if suffix not in body:
            continue
        before_stage, version = body.rsplit(suffix, 1)
        if not VERSION_RE.match(version):
            return None
        if "_" not in before_stage:
            return None
        asset_name, variant = before_stage.rsplit("_", 1)
        try:
            return validate_asset_parts(
                AssetNameParts(asset_name, variant, stage, version),
                convention=cfg,
            )
        except ValueError:
            return None
    return None


def generate_filename(
    parts: AssetNameParts,
    extension: str,
    convention: NamingConvention | None = None,
) -> str:
    """Generate a convention-compliant filename including extension."""

    cfg = convention or load_naming_convention()
    clean = validate_asset_parts(parts, convention=cfg)
    ext = extension.lower().lstrip(".")
    if not ext:
        raise ValueError("File cần có phần mở rộng.")
    stem = cfg.pattern.format(
        asset_name=clean.asset_name,
        variant=clean.variant,
        stage=clean.stage,
        version=clean.version,
    )
    return f"{stem}.{ext}"


def relative_to_repo(path: Path, root: Path | None = None) -> str:
    """Return a repo-relative path string when possible."""

    base = (root or repo_root()).resolve()
    try:
        return path.resolve().relative_to(base).as_posix()
    except ValueError:
        return str(path)


def resolve_manifest_path(
    manifest_path: Path | None = None,
    convention: NamingConvention | None = None,
    root: Path | None = None,
) -> Path:
    """Resolve the manifest JSON path."""

    if manifest_path is not None:
        return manifest_path
    cfg = convention or load_naming_convention()
    return (root or repo_root()) / cfg.manifest_file


def compute_checksum(file_path: Path) -> str:
    """Compute a SHA-256 checksum of a file."""

    sha256 = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def load_manifest(manifest_path: Path) -> list[dict[str, Any]]:
    """Load the JSON manifest as a list.

    Raises:
        ManifestError: If the manifest exists but is corrupted or not a list.
    """

    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(
            "Manifest JSON đang bị lỗi, không ghi đè tự động để tránh mất dữ liệu. "
            f"Hãy sao lưu/sửa file {manifest_path}. Chi tiết: {exc}"
        ) from exc
    if not isinstance(data, list):
        raise ManifestError(
            f"Manifest phải là danh sách JSON. Hãy kiểm tra lại file {manifest_path}."
        )
    return data


def save_manifest(manifest_path: Path, entries: list[dict[str, Any]]) -> None:
    """Write the manifest atomically."""

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(entries, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        dir=manifest_path.parent,
        prefix=f".{manifest_path.name}.",
        suffix=".tmp",
    ) as temp_file:
        temp_file.write(payload)
        temp_path = Path(temp_file.name)
    temp_path.replace(manifest_path)


def manifest_entry_to_dict(entry: ManifestEntry | dict[str, Any]) -> dict[str, Any]:
    """Return a plain dict for a manifest entry."""

    if isinstance(entry, ManifestEntry):
        return asdict(entry)
    return dict(entry)


def append_manifest_entry(
    manifest_path: Path,
    entry: ManifestEntry | dict[str, Any],
) -> list[dict[str, Any]]:
    """Append one manifest entry while preserving existing entries."""

    entries = load_manifest(manifest_path)
    entries.append(manifest_entry_to_dict(entry))
    save_manifest(manifest_path, entries)
    return entries


def query_manifest(
    manifest_path: Path,
    asset_name: str | None = None,
    stage: str | None = None,
    version: str | None = None,
    variant: str | None = None,
) -> list[dict[str, Any]]:
    """Query manifest entries by simple equality filters."""

    entries = load_manifest(manifest_path)
    filters = {
        "asset_name": normalize_asset_name(asset_name) if asset_name else None,
        "stage": stage.lower() if stage else None,
        "version": format_version(version) if version else None,
        "variant": normalize_variant(variant) if variant else None,
    }
    return [
        entry
        for entry in entries
        if all(value is None or str(entry.get(key)) == value for key, value in filters.items())
    ]


def _entry_version(entry: dict[str, Any], asset_name: str, variant: str, stage: str) -> int | None:
    if (
        entry.get("asset_name") == asset_name
        and entry.get("variant") == variant
        and entry.get("stage") == stage
    ):
        try:
            return int(format_version(str(entry.get("version", ""))))
        except ValueError:
            return None
    output_path = entry.get("output_path")
    if output_path:
        parsed = parse_asset_filename(str(output_path))
        if (
            parsed
            and parsed.asset_name == asset_name
            and parsed.variant == variant
            and parsed.stage == stage
        ):
            return int(parsed.version)
    return None


def next_version(
    target_dir: Path,
    asset_name: str,
    variant: str,
    stage: str,
    extension: str | None = None,
    manifest_path: Path | None = None,
    convention: NamingConvention | None = None,
) -> str:
    """Return the next available version from existing files and manifest entries."""

    cfg = convention or load_naming_convention()
    clean = validate_asset_parts(
        AssetNameParts(asset_name, variant, stage, cfg.version_start),
        convention=cfg,
    )
    max_version = cfg.version_start - 1
    ext = extension.lower().lstrip(".") if extension else None

    if target_dir.exists():
        for file_path in target_dir.iterdir():
            if not file_path.is_file():
                continue
            if ext and file_path.suffix.lower() != f".{ext}":
                continue
            parsed = parse_asset_filename(file_path.name, convention=cfg)
            if (
                parsed
                and parsed.asset_name == clean.asset_name
                and parsed.variant == clean.variant
                and parsed.stage == clean.stage
            ):
                max_version = max(max_version, int(parsed.version))

    if manifest_path and manifest_path.exists():
        for entry in load_manifest(manifest_path):
            version_number = _entry_version(
                entry,
                clean.asset_name,
                clean.variant,
                clean.stage,
            )
            if version_number is not None:
                max_version = max(max_version, version_number)

    next_number = max_version + 1
    if next_number > 999:
        raise ValueError("Không thể tạo phiên bản mới vì đã vượt quá v999.")
    return f"{next_number:03d}"


def build_manifest_entry(
    source_file: Path,
    output_path: Path,
    stage: str,
    asset_name: str,
    variant: str,
    pipeline_step: str,
    version: str | int | None = None,
    root: Path | None = None,
    convention: NamingConvention | None = None,
) -> ManifestEntry:
    """Build a manifest entry from source/output files."""

    cfg = convention or load_naming_convention()
    parsed = parse_asset_filename(output_path.name, convention=cfg)
    if version is None and parsed is not None:
        version = parsed.version
    parts = validate_asset_parts(
        AssetNameParts(asset_name, variant, stage, version or cfg.version_start),
        convention=cfg,
    )
    return ManifestEntry(
        asset_name=parts.asset_name,
        variant=parts.variant,
        stage=parts.stage,
        version=parts.version,
        source_file=relative_to_repo(source_file, root=root),
        output_path=relative_to_repo(output_path, root=root),
        timestamp=datetime.now(UTC).isoformat(),
        checksum=compute_checksum(output_path),
        pipeline_step=pipeline_step,
    )


def add_manifest_entry(
    manifest_path: Path,
    source_file: Path,
    output_path: Path,
    stage: str,
    asset_name: str,
    variant: str,
    pipeline_step: str,
    version: str | int | None = None,
    root: Path | None = None,
    convention: NamingConvention | None = None,
) -> ManifestEntry:
    """Build and append one manifest entry."""

    entry = build_manifest_entry(
        source_file=source_file,
        output_path=output_path,
        stage=stage,
        asset_name=asset_name,
        variant=variant,
        pipeline_step=pipeline_step,
        version=version,
        root=root,
        convention=convention,
    )
    append_manifest_entry(manifest_path, entry)
    return entry


def validate_manifest_entries(
    manifest_path: Path,
    convention: NamingConvention | None = None,
    check_files: bool = True,
    root: Path | None = None,
) -> list[str]:
    """Validate manifest structure and return human-readable error strings."""

    cfg = convention or load_naming_convention()
    base = root or repo_root()
    errors: list[str] = []
    entries = load_manifest(manifest_path)
    for index, entry in enumerate(entries, start=1):
        missing = [field for field in cfg.required_fields if field not in entry]
        if missing:
            errors.append(f"Dòng {index}: thiếu trường {', '.join(missing)}.")
            continue
        try:
            validate_asset_parts(
                AssetNameParts(
                    str(entry["asset_name"]),
                    str(entry["variant"]),
                    str(entry["stage"]),
                    str(entry["version"]),
                ),
                convention=cfg,
            )
        except ValueError as exc:
            errors.append(f"Dòng {index}: {exc}")

        parsed = parse_asset_filename(str(entry.get("output_path", "")), convention=cfg)
        if parsed is None:
            errors.append(f"Dòng {index}: output_path không theo quy ước tên file.")
        elif (
            parsed.asset_name != entry["asset_name"]
            or parsed.variant != entry["variant"]
            or parsed.stage != entry["stage"]
            or parsed.version != entry["version"]
        ):
            errors.append(f"Dòng {index}: tên file không khớp các trường manifest.")

        if check_files:
            output_path = Path(str(entry["output_path"]))
            if not output_path.is_absolute():
                output_path = base / output_path
            if not output_path.exists():
                errors.append(f"Dòng {index}: không tìm thấy output_path {output_path}.")
    return errors


def print_entries(entries: list[dict[str, Any]]) -> None:
    """Print manifest entries in a compact Vietnamese-friendly format."""

    if not entries:
        print("Không có entry nào.")
        return
    for entry in entries:
        print(
            f"- {entry.get('asset_name')} | {entry.get('variant')} | "
            f"{entry.get('stage')} | v{entry.get('version')} | {entry.get('output_path')}"
        )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Quản lý manifest asset cho TuPhuongVoLo-ArtPipeline.",
    )
    parser.add_argument("--config", type=Path, default=default_config_path())
    parser.add_argument("--manifest", type=Path, help="Đường dẫn manifest JSON tùy chọn.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Kiểm tra manifest.")
    subparsers.add_parser("list", help="Liệt kê tất cả manifest entries.")

    query_parser = subparsers.add_parser("query", help="Tìm entry trong manifest.")
    query_parser.add_argument("--stage")
    query_parser.add_argument("--asset-name")
    query_parser.add_argument("--version")
    query_parser.add_argument("--variant")

    add_parser = subparsers.add_parser("add", help="Thêm entry manifest cho file đã tạo.")
    add_parser.add_argument("--source", type=Path, required=True)
    add_parser.add_argument("--output", type=Path, required=True)
    add_parser.add_argument("--stage", required=True)
    add_parser.add_argument("--asset-name", required=True)
    add_parser.add_argument("--variant", default="main")
    add_parser.add_argument("--pipeline-step", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the manifest CLI."""

    configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_naming_convention(args.config)
    manifest_path = resolve_manifest_path(args.manifest, convention=cfg)

    try:
        if args.command == "validate":
            errors = validate_manifest_entries(manifest_path, convention=cfg)
            if errors:
                print("FAIL: Manifest chưa hợp lệ.")
                for error in errors:
                    print(f"  Lỗi: {error}")
                return 1
            print("PASS: Manifest hợp lệ.")
            return 0

        if args.command == "list":
            print_entries(load_manifest(manifest_path))
            return 0

        if args.command == "query":
            entries = query_manifest(
                manifest_path,
                asset_name=args.asset_name,
                stage=args.stage,
                version=args.version,
                variant=args.variant,
            )
            print_entries(entries)
            return 0

        if args.command == "add":
            entry = add_manifest_entry(
                manifest_path=manifest_path,
                source_file=args.source,
                output_path=args.output,
                stage=args.stage,
                asset_name=args.asset_name,
                variant=args.variant,
                pipeline_step=args.pipeline_step,
                convention=cfg,
            )
            print(f"Đã thêm manifest entry: {entry.output_path}")
            return 0
    except (ManifestError, OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    parser.error("Lệnh không hợp lệ.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
