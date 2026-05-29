"""Ingest dropped art files into versioned pipeline folders.

Feature 003 vertical slice: copy files from `drops/`, apply the project naming
convention, and append a safe JSON manifest entry.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from manifest import (
    AssetNameParts,
    ManifestError,
    add_manifest_entry,
    configure_stdio,
    generate_filename,
    load_naming_convention,
    next_version,
    normalize_asset_name,
    parse_asset_filename,
    query_manifest,
    repo_root,
    resolve_manifest_path,
    validate_manifest_entries,
)

SUPPORTED_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
DETECTED_ONLY_EXTENSIONS = {".ai"}


@dataclass
class IngestResult:
    """Summary for one ingest command."""

    processed: list[Path] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def find_inputs(input_path: Path) -> list[Path]:
    """Return input files from a file or a directory."""

    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(path for path in input_path.iterdir() if path.is_file())
    raise FileNotFoundError(f"Không tìm thấy input: {input_path}")


def infer_stage(file_path: Path, requested_stage: str | None) -> str:
    """Infer stage for dropped files when the user did not provide one."""

    if requested_stage:
        return requested_stage.lower()
    if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        return "raw"
    return "raw"


def target_directory_for_stage(stage: str, config_path: Path | None = None) -> Path:
    """Resolve the configured output directory for a stage."""

    cfg = load_naming_convention(config_path)
    if stage not in cfg.output_directories:
        raise ValueError(f"Stage chưa có thư mục output trong config: {stage}")
    return repo_root() / cfg.output_directories[stage]


def source_asset_name(file_path: Path, asset_name: str | None) -> str:
    """Choose an asset name from CLI input, convention filename, or source stem."""

    if asset_name:
        return asset_name
    parsed = parse_asset_filename(file_path.name)
    if parsed:
        return parsed.asset_name
    return normalize_asset_name(file_path.stem)


def copy_asset(source: Path, target: Path) -> None:
    """Copy source to target without overwriting."""

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"Output đã tồn tại, không ghi đè: {target}")
    shutil.copy2(source, target)


def ingest_file(
    file_path: Path,
    stage: str | None,
    variant: str,
    move: bool,
    asset_name: str | None,
    pipeline_step: str,
    config_path: Path | None = None,
    manifest_path: Path | None = None,
) -> Path:
    """Copy/move one supported file into the configured pipeline folder."""

    suffix = file_path.suffix.lower()
    if suffix in DETECTED_ONLY_EXTENSIONS:
        raise ValueError(
            "File .ai được nhận diện nhưng chưa được ingest tự động. "
            "Hãy export SVG trước rồi đặt vào drops/."
        )
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Bỏ qua file không hỗ trợ: {file_path.name}")

    cfg = load_naming_convention(config_path)
    clean_stage = infer_stage(file_path, stage)
    clean_asset_name = source_asset_name(file_path, asset_name)
    target_dir = target_directory_for_stage(clean_stage, config_path=config_path)
    manifest = manifest_path or resolve_manifest_path(convention=cfg)
    version = next_version(
        target_dir=target_dir,
        asset_name=clean_asset_name,
        variant=variant,
        stage=clean_stage,
        extension=suffix,
        manifest_path=manifest,
        convention=cfg,
    )
    filename = generate_filename(
        AssetNameParts(clean_asset_name, variant, clean_stage, version),
        extension=suffix,
        convention=cfg,
    )
    output_path = target_dir / filename
    copy_asset(file_path, output_path)
    try:
        add_manifest_entry(
            manifest_path=manifest,
            source_file=file_path,
            output_path=output_path,
            stage=clean_stage,
            asset_name=clean_asset_name,
            variant=variant,
            pipeline_step=pipeline_step,
            version=version,
            convention=cfg,
        )
    except Exception:
        if output_path.exists():
            output_path.unlink()
        raise
    if move:
        file_path.unlink()
    return output_path


def ingest_path(
    input_path: Path,
    stage: str | None,
    variant: str,
    move: bool = False,
    asset_name: str | None = None,
    pipeline_step: str = "feature_003_asset_agent_ingest",
    config_path: Path | None = None,
    manifest_path: Path | None = None,
) -> IngestResult:
    """Ingest all supported files from a file or directory input."""

    result = IngestResult()
    for file_path in find_inputs(input_path):
        suffix = file_path.suffix.lower()
        if suffix in DETECTED_ONLY_EXTENSIONS:
            result.skipped.append(
                f"{file_path.name}: file .ai chưa ingest tự động; hãy export SVG trước."
            )
            continue
        if suffix not in SUPPORTED_EXTENSIONS:
            result.skipped.append(f"{file_path.name}: định dạng chưa hỗ trợ.")
            continue
        try:
            output_path = ingest_file(
                file_path=file_path,
                stage=stage,
                variant=variant,
                move=move,
                asset_name=asset_name,
                pipeline_step=pipeline_step,
                config_path=config_path,
                manifest_path=manifest_path,
            )
            result.processed.append(output_path)
        except Exception as exc:
            result.errors.append(f"{file_path.name}: {exc}")
    return result


def print_ingest_summary(result: IngestResult) -> None:
    """Print a Vietnamese-friendly ingest summary."""

    print("Tóm tắt ingest:")
    print(f"  Đã xử lý: {len(result.processed)} file")
    for output_path in result.processed:
        print(f"    - {output_path}")
    if result.skipped:
        print(f"  Bỏ qua: {len(result.skipped)} file")
        for skipped in result.skipped:
            print(f"    - {skipped}")
    if result.errors:
        print(f"  Lỗi: {len(result.errors)} file")
        for error in result.errors:
            print(f"    - {error}")
    print("File gốc không bị xóa trừ khi bạn dùng --move và mọi bước đã thành công.")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Ingest asset từ drops/ vào pipeline với tên và manifest chuẩn.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=repo_root() / "config/naming_convention.yaml",
    )
    parser.add_argument("--manifest", type=Path, help="Đường dẫn manifest JSON tùy chọn.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Copy file từ drops/ vào folder đúng.")
    ingest_parser.add_argument("--input", type=Path, required=True)
    ingest_parser.add_argument("--stage")
    ingest_parser.add_argument("--variant", default="main")
    ingest_parser.add_argument("--asset-name")
    ingest_parser.add_argument(
        "--move",
        action="store_true",
        help="Copy thành công rồi mới xóa file gốc.",
    )
    ingest_parser.add_argument("--pipeline-step", default="feature_003_asset_agent_ingest")

    query_parser = subparsers.add_parser("query", help="Tìm asset trong manifest.")
    query_parser.add_argument("--stage")
    query_parser.add_argument("--asset-name")
    query_parser.add_argument("--version")
    query_parser.add_argument("--variant")

    subparsers.add_parser("validate-manifest", help="Kiểm tra manifest.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the asset agent CLI."""

    configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_naming_convention(args.config)
    manifest_path = args.manifest or resolve_manifest_path(convention=cfg)

    try:
        if args.command == "ingest":
            print("TuPhuongVoLo-ArtPipeline - Ingest asset")
            result = ingest_path(
                input_path=args.input,
                stage=args.stage,
                variant=args.variant,
                move=args.move,
                asset_name=args.asset_name,
                pipeline_step=args.pipeline_step,
                config_path=args.config,
                manifest_path=manifest_path,
            )
            print_ingest_summary(result)
            return 1 if result.errors else 0

        if args.command == "query":
            entries = query_manifest(
                manifest_path,
                asset_name=args.asset_name,
                stage=args.stage,
                version=args.version,
                variant=args.variant,
            )
            if not entries:
                print("Không tìm thấy asset phù hợp.")
            for entry in entries:
                print(
                    f"- {entry.get('asset_name')} | {entry.get('variant')} | "
                    f"{entry.get('stage')} | v{entry.get('version')} | "
                    f"{entry.get('output_path')}"
                )
            return 0

        if args.command == "validate-manifest":
            errors = validate_manifest_entries(manifest_path, convention=cfg)
            if errors:
                print("FAIL: Manifest chưa hợp lệ.")
                for error in errors:
                    print(f"  Lỗi: {error}")
                return 1
            print("PASS: Manifest hợp lệ.")
            return 0
    except (ManifestError, OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    parser.error("Lệnh không hợp lệ.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
