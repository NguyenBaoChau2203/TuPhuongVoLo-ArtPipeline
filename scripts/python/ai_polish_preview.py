"""Local mock AI polish preview workflow for Phase 005.5B.

This module intentionally has no provider SDKs, network calls, secrets, or
dependencies beyond the Python standard library. The mock provider only copies
an existing PNG into the AI preview output folder and writes a local JSON report.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AI_PREVIEW_VERSION = "0.5.5B"
DEFAULT_PROVIDER = "mock"
DEFAULT_PROMPT_PRESET = "tropical-island-room"
PIPELINE_STEP = "phase_005_5b_ai_polish_preview_mock"
MOCK_ONLY_NOTE = (
    "Mock-only local preview. No external API was called; no API key, secret, "
    "or internet access was used."
)
STATUS_PLANNED = "planned"
STATUS_MOCK_CREATED = "mock_created"


@dataclass(frozen=True)
class AiPreviewPlan:
    """Resolved local mock AI preview paths and metadata."""

    input_path: Path
    output_path: Path
    report_path: Path
    provider: str
    prompt: str | None
    prompt_preset: str | None

    def to_report(self, status: str) -> dict[str, Any]:
        """Return the JSON report payload."""

        return {
            "pipeline_step": PIPELINE_STEP,
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "report_path": str(self.report_path),
            "provider": self.provider,
            "prompt": self.prompt,
            "prompt_preset": self.prompt_preset,
            "status": status,
            "note": MOCK_ONLY_NOTE,
        }


def repo_root() -> Path:
    """Return repository root from this script location."""

    return Path(__file__).resolve().parents[2]


def configure_stdio() -> None:
    """Prefer UTF-8 console output for Vietnamese messages on Windows."""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def validate_png_input(input_path: Path) -> Path:
    """Validate that input path exists and points to a PNG file."""

    resolved = input_path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh PNG input: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Input phải là file .png, không phải thư mục: {resolved}")
    if resolved.suffix.lower() != ".png":
        raise ValueError(f"Input phải là file .png: {resolved}")
    return resolved


def resolve_output_dir(output_dir: Path) -> Path:
    """Resolve the output directory without creating it."""

    return output_dir.resolve()


def plan_output_paths(input_path: Path, output_dir: Path) -> tuple[Path, Path]:
    """Return the next versioned mock PNG and report paths."""

    output_root = resolve_output_dir(output_dir)
    stem = input_path.stem
    for version in range(1, 1000):
        version_tag = f"v{version:03d}"
        base_name = f"{stem}_{version_tag}_mock_ai_preview"
        output_path = output_root / f"{base_name}.png"
        report_path = output_root / f"{base_name}_report.json"
        if not output_path.exists() and not report_path.exists():
            return output_path, report_path
    raise FileExistsError(
        f"Không tìm được tên output còn trống trong {output_root} sau 999 phiên bản."
    )


def build_plan(args: argparse.Namespace) -> AiPreviewPlan:
    """Validate CLI args and build the mock preview plan."""

    input_path = validate_png_input(args.input)
    output_path, report_path = plan_output_paths(input_path, args.output_dir)
    return AiPreviewPlan(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        provider=args.provider,
        prompt=args.prompt,
        prompt_preset=args.prompt_preset,
    )


def print_dry_run(plan: AiPreviewPlan) -> None:
    """Print a Vietnamese dry-run plan without creating files."""

    print("TuPhuongVoLo-ArtPipeline - AI polish preview mock")
    print("Dry-run: chỉ lập kế hoạch, không tạo output và không gọi API.")
    print(f"Provider: {plan.provider}")
    print(f"Input PNG: {plan.input_path}")
    print(f"Output PNG dự kiến: {plan.output_path}")
    print(f"Report JSON dự kiến: {plan.report_path}")
    if plan.prompt_preset:
        print(f"Prompt preset: {plan.prompt_preset}")
    if plan.prompt:
        print(f"Prompt: {plan.prompt}")
    print(MOCK_ONLY_NOTE)


def run_mock_preview(plan: AiPreviewPlan) -> None:
    """Create the local mock PNG copy and JSON report."""

    plan.output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(plan.input_path, plan.output_path)
    plan.report_path.write_text(
        json.dumps(plan.to_report(STATUS_MOCK_CREATED), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_success(plan: AiPreviewPlan) -> None:
    """Print a concise artist-facing completion message."""

    print("Đã tạo mock AI polish preview local.")
    print(f"Output PNG: {plan.output_path}")
    print(f"Report JSON: {plan.report_path}")
    print(MOCK_ONLY_NOTE)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Local mock AI polish preview cho Phase 005.5B. "
            "Không gọi API, không cần internet, không cần API key."
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="Ảnh PNG preview đầu vào.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root() / "outputs" / "ai_preview",
        help="Thư mục output mock AI preview (mặc định: outputs/ai_preview).",
    )
    parser.add_argument(
        "--provider",
        choices=[DEFAULT_PROVIDER],
        default=DEFAULT_PROVIDER,
        help="Provider cho phase này. 005.5B chỉ hỗ trợ mock.",
    )
    parser.add_argument("--prompt", help="Prompt tuỳ chọn để ghi vào report mock.")
    parser.add_argument(
        "--prompt-preset",
        choices=[DEFAULT_PROMPT_PRESET],
        help="Preset prompt tuỳ chọn để ghi vào report mock.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ in kế hoạch, không tạo PNG/report.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ai_polish_preview {AI_PREVIEW_VERSION}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the local mock AI polish preview CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        plan = build_plan(args)
        if args.dry_run:
            print_dry_run(plan)
            return 0
        run_mock_preview(plan)
        print_success(plan)
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
