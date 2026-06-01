"""Optional AI polish preview workflow for Phase 005.5C.

The default mock provider remains fully local and performs no network calls. The
fal provider is optional, uses a lazy import, and only calls fal.ai when the user
explicitly selects ``--provider fal`` in non-dry-run mode with ``FAL_KEY`` set.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen

AI_PREVIEW_VERSION = "0.5.5C"
DEFAULT_PROVIDER = "mock"
PROVIDER_MOCK = "mock"
PROVIDER_FAL = "fal"
SUPPORTED_PROVIDERS = (PROVIDER_MOCK, PROVIDER_FAL)
DEFAULT_PROMPT_PRESET = "tropical-island-room"
DEFAULT_FAL_MODEL = "fal-ai/flux-pro/kontext"
DEFAULT_TIMEOUT_SECONDS = 120
MOCK_PIPELINE_STEP = "phase_005_5b_ai_polish_preview_mock"
FAL_PIPELINE_STEP = "phase_005_5c_ai_polish_preview_fal"
MOCK_ONLY_NOTE = (
    "Mock-only local preview. No external API was called; no API key, secret, "
    "or internet access was used."
)
FAL_REFERENCE_NOTE = (
    "AI polish preview fal là ảnh tham khảo tùy chọn. Output Maya/SVG/geometry "
    "JSON/manifest vẫn là nguồn chính và không bị thay đổi."
)
PROMPT_PRESETS = {
    DEFAULT_PROMPT_PRESET: (
        "Mysterious tropical archipelago survival adventure; stylized indie game "
        "environment concept preview. Preserve the isometric room layout and "
        "major objects. Improve lighting, mood, materials, and atmosphere. Do not "
        "add text, watermark, UI, logos, or characters unless they are already "
        "present."
    )
}
STATUS_PLANNED = "planned"
STATUS_MOCK_CREATED = "mock_created"
STATUS_FAL_CREATED = "fal_created"
STATUS_SKIPPED = "skipped"
STATUS_FAILED = "failed"
ERROR_MISSING_FAL_KEY = "missing_fal_key"
ERROR_MISSING_FAL_CLIENT = "missing_fal_client"
ERROR_FAL_CLIENT_API = "fal_client_api_unavailable"
ERROR_FAL_RESULT = "fal_result_missing_image_url"
ERROR_FAL_CALL = "fal_call_failed"


@dataclass(frozen=True)
class AiPreviewPlan:
    """Resolved AI preview paths and metadata."""

    input_path: Path
    output_path: Path
    report_path: Path
    provider: str
    prompt: str | None
    prompt_preset: str | None
    model: str | None = None
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    resolved_prompt: str | None = None

    def to_report(
        self,
        status: str,
        *,
        external_api_called: bool = False,
        skipped: bool = False,
        error_type: str | None = None,
        message: str | None = None,
        source_image_url: str | None = None,
        result_image_url: str | None = None,
    ) -> dict[str, Any]:
        """Return the JSON report payload."""

        payload: dict[str, Any] = {
            "pipeline_step": (
                FAL_PIPELINE_STEP if self.provider == PROVIDER_FAL else MOCK_PIPELINE_STEP
            ),
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "report_path": str(self.report_path),
            "provider": self.provider,
            "prompt": self.resolved_prompt if self.provider == PROVIDER_FAL else self.prompt,
            "prompt_preset": self.prompt_preset,
            "status": status,
        }
        if self.provider == PROVIDER_FAL:
            payload.update(
                {
                    "model": self.model,
                    "external_api_called": external_api_called,
                    "skipped": skipped,
                    "error_type": error_type,
                    "note": FAL_REFERENCE_NOTE,
                }
            )
            if message:
                payload["message"] = message
            if source_image_url:
                payload["source_image_url"] = source_image_url
            if result_image_url:
                payload["result_image_url"] = result_image_url
        else:
            payload["note"] = MOCK_ONLY_NOTE
        return payload


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


def plan_output_paths(input_path: Path, output_dir: Path, provider: str) -> tuple[Path, Path]:
    """Return the next versioned PNG and report paths for the provider."""

    output_root = resolve_output_dir(output_dir)
    stem = input_path.stem
    for version in range(1, 1000):
        version_tag = f"v{version:03d}"
        base_name = f"{stem}_{version_tag}_{provider}_ai_preview"
        output_path = output_root / f"{base_name}.png"
        report_path = output_root / f"{base_name}_report.json"
        if not output_path.exists() and not report_path.exists():
            return output_path, report_path
    raise FileExistsError(
        f"Không tìm được tên output còn trống trong {output_root} sau 999 phiên bản."
    )


def positive_int(value: str) -> int:
    """Parse a positive integer for argparse."""

    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout-seconds phải là số nguyên.") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("timeout-seconds phải lớn hơn 0.")
    return parsed


def resolve_fal_prompt(
    prompt: str | None, prompt_preset: str | None
) -> tuple[str, str | None]:
    """Return the prompt text sent to fal and the report preset value."""

    if prompt:
        if prompt_preset:
            preset_text = PROMPT_PRESETS[prompt_preset]
            return f"{preset_text}\n\nArtist instruction: {prompt}", prompt_preset
        return prompt, None

    selected_preset = prompt_preset or DEFAULT_PROMPT_PRESET
    return PROMPT_PRESETS[selected_preset], selected_preset


def build_plan(args: argparse.Namespace) -> AiPreviewPlan:
    """Validate CLI args and build the preview plan."""

    input_path = validate_png_input(args.input)
    output_path, report_path = plan_output_paths(input_path, args.output_dir, args.provider)
    prompt = args.prompt
    prompt_preset = args.prompt_preset
    model = None
    resolved_prompt = args.prompt
    if args.provider == PROVIDER_FAL:
        resolved_prompt, prompt_preset = resolve_fal_prompt(args.prompt, args.prompt_preset)
        model = args.model or DEFAULT_FAL_MODEL
    return AiPreviewPlan(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        provider=args.provider,
        prompt=prompt,
        prompt_preset=prompt_preset,
        model=model,
        timeout_seconds=args.timeout_seconds,
        resolved_prompt=resolved_prompt,
    )


def print_dry_run(plan: AiPreviewPlan) -> None:
    """Print a Vietnamese dry-run plan without creating files."""

    print(f"TuPhuongVoLo-ArtPipeline - AI polish preview {plan.provider}")
    print("Dry-run: chỉ lập kế hoạch, không tạo output và không gọi API.")
    print(f"Provider: {plan.provider}")
    if plan.provider == PROVIDER_FAL:
        print(f"Model: {plan.model}")
        print(f"Timeout giây: {plan.timeout_seconds}")
    print(f"Input PNG: {plan.input_path}")
    print(f"Output PNG dự kiến: {plan.output_path}")
    print(f"Report JSON dự kiến: {plan.report_path}")
    if plan.prompt_preset:
        print(f"Prompt preset: {plan.prompt_preset}")
    prompt = plan.resolved_prompt if plan.provider == PROVIDER_FAL else plan.prompt
    if prompt:
        print(f"Prompt: {prompt}")
    print(FAL_REFERENCE_NOTE if plan.provider == PROVIDER_FAL else MOCK_ONLY_NOTE)


def run_mock_preview(plan: AiPreviewPlan) -> None:
    """Create the local mock PNG copy and JSON report."""

    plan.output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(plan.input_path, plan.output_path)
    plan.report_path.write_text(
        json.dumps(plan.to_report(STATUS_MOCK_CREATED), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_report(plan: AiPreviewPlan, payload: dict[str, Any]) -> None:
    """Write a JSON report beside the planned AI preview output."""

    plan.report_path.parent.mkdir(parents=True, exist_ok=True)
    plan.report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_success(plan: AiPreviewPlan) -> None:
    """Print a concise artist-facing completion message."""

    if plan.provider == PROVIDER_FAL:
        print("Đã tạo fal AI polish preview tham khảo.")
    else:
        print("Đã tạo mock AI polish preview local.")
    print(f"Output PNG: {plan.output_path}")
    print(f"Report JSON: {plan.report_path}")
    print(FAL_REFERENCE_NOTE if plan.provider == PROVIDER_FAL else MOCK_ONLY_NOTE)


def print_report_path(plan: AiPreviewPlan, *, stderr: bool = False) -> None:
    """Print report path to stdout or stderr."""

    stream = sys.stderr if stderr else sys.stdout
    print(f"Report JSON: {plan.report_path}", file=stream)


def import_fal_client() -> Any:
    """Lazy-import the optional fal-client dependency."""

    return importlib.import_module("fal_client")


def get_required_fal_callable(fal_client: Any, name: str) -> Any:
    """Return a callable from fal_client or raise a controlled error."""

    func = getattr(fal_client, name, None)
    if not callable(func):
        raise RuntimeError(name)
    return func


def upload_input_image(fal_client: Any, input_path: Path) -> str:
    """Upload the input PNG through fal-client and return its hosted URL."""

    upload_file = get_required_fal_callable(fal_client, "upload_file")
    return str(upload_file(str(input_path)))


def subscribe_fal_model(fal_client: Any, plan: AiPreviewPlan, image_url: str) -> dict[str, Any]:
    """Submit the fal model request and wait for the result."""

    subscribe = get_required_fal_callable(fal_client, "subscribe")
    result = subscribe(
        plan.model,
        arguments={
            "prompt": plan.resolved_prompt,
            "image_url": image_url,
            "num_images": 1,
            "output_format": "png",
        },
        with_logs=False,
        client_timeout=plan.timeout_seconds,
    )
    if not isinstance(result, dict):
        raise ValueError("fal-client result is not a JSON object")
    return result


def extract_result_image_url(result: dict[str, Any]) -> str:
    """Extract the first generated image URL from a fal result payload."""

    images = result.get("images")
    if not isinstance(images, list) or not images:
        raise ValueError(ERROR_FAL_RESULT)
    first_image = images[0]
    if isinstance(first_image, dict):
        url = first_image.get("url")
    else:
        url = getattr(first_image, "url", None)
    if not isinstance(url, str) or not url:
        raise ValueError(ERROR_FAL_RESULT)
    return url


def download_url_to_file(url: str, output_path: Path, timeout_seconds: int) -> None:
    """Download the generated fal image to the planned PNG path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=timeout_seconds) as response:
        data = response.read()
    if not data:
        raise ValueError("fal returned an empty image download")
    output_path.write_bytes(data)


def write_fal_failure_report(
    plan: AiPreviewPlan,
    *,
    error_type: str,
    message: str,
    external_api_called: bool = False,
    skipped: bool = False,
) -> None:
    """Write a fal skipped/failed report without storing secrets."""

    status = STATUS_SKIPPED if skipped else STATUS_FAILED
    write_report(
        plan,
        plan.to_report(
            status,
            external_api_called=external_api_called,
            skipped=skipped,
            error_type=error_type,
            message=message,
        ),
    )


def run_fal_preview(plan: AiPreviewPlan, *, skip_on_missing_config: bool) -> int:
    """Run the optional fal provider or skip/fail with Vietnamese messages."""

    if not os.environ.get("FAL_KEY"):
        message = (
            "Bỏ qua AI polish preview fal: chưa có biến môi trường FAL_KEY. "
            "Output Maya pipeline hiện tại vẫn hợp lệ."
        )
        if skip_on_missing_config:
            write_fal_failure_report(
                plan,
                error_type=ERROR_MISSING_FAL_KEY,
                message=message,
                skipped=True,
            )
            print(message)
            print_report_path(plan)
            return 0

        message = (
            "Thiếu FAL_KEY cho provider fal. Hãy set biến môi trường FAL_KEY "
            "trên máy chạy nếu muốn gọi fal.ai. Không commit API key hoặc .env."
        )
        write_fal_failure_report(
            plan,
            error_type=ERROR_MISSING_FAL_KEY,
            message=message,
        )
        print(f"Lỗi: {message}", file=sys.stderr)
        print_report_path(plan, stderr=True)
        return 2

    try:
        fal_client = import_fal_client()
    except ImportError:
        message = (
            "Chưa cài optional dependency fal-client. Cài khi cần AI thật bằng: "
            "python -m pip install fal-client"
        )
        write_fal_failure_report(
            plan,
            error_type=ERROR_MISSING_FAL_CLIENT,
            message=message,
        )
        print(f"Lỗi: {message}", file=sys.stderr)
        print_report_path(plan, stderr=True)
        return 2

    try:
        get_required_fal_callable(fal_client, "upload_file")
        get_required_fal_callable(fal_client, "subscribe")
    except RuntimeError as exc:
        message = (
            "fal-client hiện tại không có API cần thiết "
            f"({exc}). Hãy cập nhật bằng: python -m pip install --upgrade fal-client"
        )
        write_fal_failure_report(
            plan,
            error_type=ERROR_FAL_CLIENT_API,
            message=message,
        )
        print(f"Lỗi: {message}", file=sys.stderr)
        print_report_path(plan, stderr=True)
        return 2

    external_api_called = False
    source_image_url = None
    result_image_url = None
    try:
        external_api_called = True
        source_image_url = upload_input_image(fal_client, plan.input_path)
        result = subscribe_fal_model(fal_client, plan, source_image_url)
        result_image_url = extract_result_image_url(result)
        download_url_to_file(result_image_url, plan.output_path, plan.timeout_seconds)
        write_report(
            plan,
            plan.to_report(
                STATUS_FAL_CREATED,
                external_api_called=True,
                skipped=False,
                error_type=None,
                source_image_url=source_image_url,
                result_image_url=result_image_url,
            ),
        )
        print_success(plan)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        error_type = ERROR_FAL_RESULT if str(exc) == ERROR_FAL_RESULT else ERROR_FAL_CALL
        message = (
            "Lỗi khi gọi fal.ai hoặc tải ảnh kết quả. Không có SVG, Maya .ma, "
            "geometry JSON, manifest, hay render pipeline nào bị thay đổi."
        )
        write_report(
            plan,
            plan.to_report(
                STATUS_FAILED,
                external_api_called=external_api_called,
                skipped=False,
                error_type=error_type,
                message=message,
                source_image_url=source_image_url,
                result_image_url=result_image_url,
            ),
        )
        print(f"Lỗi: {message}", file=sys.stderr)
        print_report_path(plan, stderr=True)
        return 2


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "AI polish preview tùy chọn cho Phase 005.5C. "
            "Provider mock không gọi API; provider fal chỉ chạy khi chọn rõ ràng."
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="Ảnh PNG preview đầu vào.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root() / "outputs" / "ai_preview",
        help="Thư mục output AI preview (mặc định: outputs/ai_preview).",
    )
    parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        default=DEFAULT_PROVIDER,
        help="Provider AI preview. mock là local-only; fal là optional fal.ai.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_FAL_MODEL,
        help=f"Model fal khi dùng --provider fal (mặc định: {DEFAULT_FAL_MODEL}).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=positive_int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Timeout cho fal upload/subscribe/download (mặc định: {DEFAULT_TIMEOUT_SECONDS}).",
    )
    parser.add_argument(
        "--skip-on-missing-config",
        action="store_true",
        help="Với provider fal, thiếu FAL_KEY thì bỏ qua và exit 0 thay vì lỗi.",
    )
    parser.add_argument("--prompt", help="Prompt tuỳ chọn cho AI preview/report.")
    parser.add_argument(
        "--prompt-preset",
        choices=[DEFAULT_PROMPT_PRESET],
        help="Preset prompt tuỳ chọn. Với fal, nếu không truyền --prompt thì dùng preset này.",
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
    """Run the AI polish preview CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        plan = build_plan(args)
        if args.dry_run:
            print_dry_run(plan)
            return 0
        if plan.provider == PROVIDER_FAL:
            return run_fal_preview(
                plan,
                skip_on_missing_config=args.skip_on_missing_config,
            )
        run_mock_preview(plan)
        print_success(plan)
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
