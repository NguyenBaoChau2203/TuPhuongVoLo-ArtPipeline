"""Batch wrapper for Feature 001 isometric room builds.

Feature 004 keeps orchestration thin: it scans clean SVG files, asks Feature 001
to plan/build each room, writes an artist-readable batch report, and never
modifies source SVG files.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import build_isometric_room as builder
from clean_svg_paths import configure_stdio
from detect_rooms_from_svg import RoomReport, detect_rooms, normalize_room_name

DEFAULT_STYLE = "line_art_green_floor"
DEFAULT_REPORT = builder.repo_root() / "outputs" / "reports" / "batch_isometric_report.json"
PIPELINE_STEP = "feature_004_batch_isometric_render"
STATUS_PLANNED = "planned"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"


@dataclass
class BatchJob:
    """One planned or executed room build."""

    source_svg: Path
    room_name: str
    style: str
    room_preset: str | None
    planned_blend_output: Path | None
    planned_preview_output: Path | None
    status: str = STATUS_PLANNED
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly job representation."""

        return {
            "source_svg": str(self.source_svg),
            "room_name": self.room_name,
            "style": self.style,
            "room_preset": self.room_preset,
            "planned_blend_output": str(self.planned_blend_output)
            if self.planned_blend_output
            else None,
            "planned_preview_output": str(self.planned_preview_output)
            if self.planned_preview_output
            else None,
            "status": self.status,
            "message": self.message,
            "feature001_command": build_feature001_command(self, dry_run=True)
            if self.room_name
            else [],
        }


@dataclass
class BatchReport:
    """Summary report for one batch run."""

    input_mode: str
    scanned_files: int
    detected_rooms: int
    planned_jobs: int
    succeeded: int
    failed: int
    skipped: int
    jobs: list[BatchJob]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly report representation."""

        return {
            "input_mode": self.input_mode,
            "pipeline_step": PIPELINE_STEP,
            "scanned_files": self.scanned_files,
            "detected_rooms": self.detected_rooms,
            "planned_jobs": self.planned_jobs,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
            "jobs": [job.to_dict() for job in self.jobs],
        }


def scan_svg_files(input_dir: Path) -> list[Path]:
    """Return deterministic, non-recursive SVG inputs from a folder."""

    resolved = input_dir.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục input: {resolved}")
    if not resolved.is_dir():
        raise ValueError(f"Input-dir phải là thư mục: {resolved}")
    svg_files = [
        path.resolve()
        for path in resolved.iterdir()
        if path.is_file() and path.suffix.lower() == ".svg"
    ]
    return sorted(svg_files, key=lambda path: path.name.lower())


def build_feature001_command(job: BatchJob, dry_run: bool) -> list[str]:
    """Return the equivalent Feature 001 CLI command for this job."""

    command = [
        sys.executable or "python",
        str(builder.repo_root() / "scripts" / "python" / "build_isometric_room.py"),
        "--input",
        str(job.source_svg),
        "--room",
        job.room_name,
        "--style",
        job.style,
    ]
    if job.room_preset:
        command.extend(["--room-preset", job.room_preset])
    if dry_run:
        command.append("--dry-run")
    return command


def select_target_rooms(
    reports: list[RoomReport],
    requested_room: str | None,
    all_rooms: bool,
) -> list[RoomReport]:
    """Select usable rooms according to the batch CLI rules."""

    usable = [report for report in reports if report.has_usable_boundary]
    if not usable:
        raise ValueError("Không tìm thấy phòng có boundary đóng kín để dựng Blender.")

    if requested_room:
        normalized = normalize_room_name(requested_room)
        selected = [report for report in usable if report.room_name == normalized]
        if not selected:
            available = ", ".join(report.room_name for report in usable)
            raise ValueError(f"Không tìm thấy phòng '{normalized}'. Phòng có sẵn: {available}")
        return selected

    if all_rooms:
        return usable

    return [usable[0]]


def make_plan_args(
    args: argparse.Namespace,
    source_svg: Path,
    room_name: str,
    dry_run: bool,
) -> argparse.Namespace:
    """Build a Feature 001 args namespace for a single room."""

    return argparse.Namespace(
        input=source_svg,
        room=room_name,
        style=args.style,
        room_preset=args.room_preset,
        output_dir=args.output_dir,
        blender_path=args.blender_path,
        dry_run=dry_run,
        verbose=args.verbose,
    )


def create_job_from_room(args: argparse.Namespace, source_svg: Path, room: RoomReport) -> BatchJob:
    """Create one job by reusing Feature 001 dry-run planning."""

    plan = builder.build_plan(make_plan_args(args, source_svg, room.room_name, dry_run=True))
    message = "; ".join(plan.warnings)
    return BatchJob(
        source_svg=plan.input_path,
        room_name=plan.room.room_name,
        style=plan.style_name,
        room_preset=plan.room_preset_name,
        planned_blend_output=plan.blend_output,
        planned_preview_output=plan.preview_output,
        status=STATUS_PLANNED,
        message=message,
    )


def failed_job(source_svg: Path, message: str, style: str, room_name: str = "") -> BatchJob:
    """Create a failed placeholder job for file-level errors."""

    return BatchJob(
        source_svg=source_svg.resolve(),
        room_name=room_name,
        style=style,
        room_preset=None,
        planned_blend_output=None,
        planned_preview_output=None,
        status=STATUS_FAILED,
        message=message,
    )


def create_jobs_for_svg(
    args: argparse.Namespace,
    source_svg: Path,
) -> tuple[list[BatchJob], int]:
    """Detect rooms in one SVG and create jobs for selected rooms."""

    reports = detect_rooms(source_svg)
    target_rooms = select_target_rooms(reports, args.room, args.all_rooms)
    jobs: list[BatchJob] = []
    for room in target_rooms:
        jobs.append(create_job_from_room(args, source_svg, room))
    return jobs, len(reports)


def load_jobs_from_file(job_file: Path, args: argparse.Namespace) -> list[BatchJob]:
    """Load a saved job list from a prior report or a raw jobs array."""

    resolved = job_file.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy job-file: {resolved}")
    data = json.loads(resolved.read_text(encoding="utf-8"))
    raw_jobs = data.get("jobs", data) if isinstance(data, dict) else data
    if not isinstance(raw_jobs, list):
        raise ValueError("Job-file phải là JSON array hoặc report có trường jobs.")

    jobs: list[BatchJob] = []
    for index, raw in enumerate(raw_jobs, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Job-file có job #{index} không phải object JSON.")
        source_svg = Path(str(raw.get("source_svg", ""))).resolve()
        room_name = str(raw.get("room_name", "")).strip()
        style = str(raw.get("style") or args.style)
        room_preset = raw.get("room_preset")
        planned_blend = raw.get("planned_blend_output")
        planned_preview = raw.get("planned_preview_output")
        jobs.append(
            BatchJob(
                source_svg=source_svg,
                room_name=room_name,
                style=style,
                room_preset=str(room_preset) if room_preset else None,
                planned_blend_output=Path(str(planned_blend)).resolve() if planned_blend else None,
                planned_preview_output=Path(str(planned_preview)).resolve()
                if planned_preview
                else None,
                status=STATUS_PLANNED if room_name else STATUS_FAILED,
                message="Đã tải từ job-file; dry-run sẽ không chạy Blender.",
            )
        )
    return jobs


def discover_jobs(args: argparse.Namespace) -> tuple[str, int, int, list[BatchJob]]:
    """Resolve input mode and create the batch job list."""

    if args.input_dir:
        input_mode = "input-dir"
        svg_files = scan_svg_files(args.input_dir)
    elif args.input_file:
        input_mode = "input-file"
        svg_files = [args.input_file.resolve()]
    else:
        input_mode = "job-file"
        jobs = load_jobs_from_file(args.job_file, args)
        return input_mode, 0, len(jobs), jobs

    jobs: list[BatchJob] = []
    detected_rooms = 0
    for source_svg in svg_files:
        try:
            svg_jobs, room_count = create_jobs_for_svg(args, source_svg)
            detected_rooms += room_count
            jobs.extend(svg_jobs)
        except (OSError, ValueError) as exc:
            jobs.append(failed_job(source_svg, f"Lỗi khi đọc SVG: {exc}", args.style))
            if args.stop_on_error:
                break
    return input_mode, len(svg_files), detected_rooms, jobs


def execute_job(job: BatchJob, args: argparse.Namespace) -> BatchJob:
    """Run one job through Feature 001 and update its status."""

    if job.status == STATUS_FAILED:
        return job
    try:
        plan_args = make_plan_args(args, job.source_svg, job.room_name, dry_run=False)
        plan_args.style = job.style
        plan_args.room_preset = job.room_preset
        plan = builder.build_plan(plan_args)
        print(f"Dang render: {plan.room.room_name} tu {plan.input_path}")
        return_code = builder.run_blender(plan, verbose=args.verbose)
        job.planned_blend_output = plan.blend_output
        job.planned_preview_output = plan.preview_output
        if return_code == 0:
            job.status = STATUS_SUCCEEDED
            job.message = "Đã tạo output và cập nhật manifest."
        else:
            job.status = STATUS_FAILED
            job.message = f"Blender trả về mã lỗi {return_code}."
    except FileNotFoundError as exc:
        job.status = STATUS_FAILED
        job.message = f"Không tìm thấy Blender hoặc file cần thiết: {exc}"
    except (OSError, ValueError) as exc:
        job.status = STATUS_FAILED
        job.message = f"Lỗi khi chạy job: {exc}"
    return job


def mark_remaining_skipped(jobs: list[BatchJob], start_index: int, message: str) -> None:
    """Mark remaining planned jobs as skipped after stop-on-error."""

    for job in jobs[start_index:]:
        if job.status == STATUS_PLANNED:
            job.status = STATUS_SKIPPED
            job.message = message


def report_from_jobs(
    input_mode: str,
    scanned_files: int,
    detected_rooms: int,
    jobs: list[BatchJob],
) -> BatchReport:
    """Build a summary report from current job statuses."""

    return BatchReport(
        input_mode=input_mode,
        scanned_files=scanned_files,
        detected_rooms=detected_rooms,
        planned_jobs=sum(1 for job in jobs if job.room_name and job.planned_blend_output),
        succeeded=sum(1 for job in jobs if job.status == STATUS_SUCCEEDED),
        failed=sum(1 for job in jobs if job.status == STATUS_FAILED),
        skipped=sum(1 for job in jobs if job.status == STATUS_SKIPPED),
        jobs=jobs,
    )


def write_json_report(report: BatchReport, json_report: Path) -> None:
    """Write a UTF-8, pretty-printed JSON batch report."""

    json_report.parent.mkdir(parents=True, exist_ok=True)
    json_report.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_summary(report: BatchReport, report_path: Path) -> None:
    """Print an artist-facing Vietnamese summary."""

    print("TuPhuongVoLo-ArtPipeline - Batch isometric render")
    print(f"Số file SVG đã quét: {report.scanned_files}")
    print(f"Số phòng đã phát hiện: {report.detected_rooms}")
    print(f"Số job đã lập kế hoạch: {report.planned_jobs}")
    print(f"Thành công: {report.succeeded}")
    print(f"Thất bại: {report.failed}")
    print(f"Bỏ qua: {report.skipped}")
    print(f"Báo cáo JSON: {report_path}")


def run_batch(args: argparse.Namespace) -> BatchReport:
    """Create and optionally execute a batch report."""

    input_mode, scanned_files, detected_rooms, jobs = discover_jobs(args)

    if args.dry_run:
        for job in jobs:
            if job.status == STATUS_PLANNED and not job.message:
                job.message = (
                    "Dry-run: chỉ lập kế hoạch, không chạy Blender, "
                    "không cập nhật manifest."
                )
        return report_from_jobs(input_mode, scanned_files, detected_rooms, jobs)

    total = sum(1 for job in jobs if job.status == STATUS_PLANNED)
    rendered = 0
    for index, job in enumerate(jobs):
        if job.status != STATUS_PLANNED:
            if args.stop_on_error and job.status == STATUS_FAILED:
                mark_remaining_skipped(jobs, index + 1, "Dừng theo --stop-on-error.")
                break
            continue
        rendered += 1
        print(f"Rendering {rendered}/{total}: {job.room_name}")
        execute_job(job, args)
        if job.status == STATUS_FAILED and args.stop_on_error:
            mark_remaining_skipped(jobs, index + 1, "Dừng theo --stop-on-error.")
            break

    return report_from_jobs(input_mode, scanned_files, detected_rooms, jobs)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Batch render nhiều phòng isometric từ SVG sạch.",
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input-dir", type=Path, help="Thư mục chứa SVG sạch.")
    input_group.add_argument("--input-file", type=Path, help="Một file SVG sạch.")
    input_group.add_argument(
        "--job-file",
        type=Path,
        help="JSON job list hoặc batch report đã lưu.",
    )
    parser.add_argument("--output-dir", type=Path, default=builder.repo_root() / "outputs")
    parser.add_argument(
        "--room",
        help="Lọc theo tên phòng đã normalize, ví dụ kho hoặc sanh_chinh.",
    )
    parser.add_argument(
        "--all-rooms",
        action="store_true",
        help="Lập job cho mọi phòng dùng được.",
    )
    parser.add_argument("--style", default=DEFAULT_STYLE, help="Style preset dùng cho cả batch.")
    parser.add_argument("--room-preset", help="Room preset tùy chọn.")
    parser.add_argument("--blender-path", type=Path, help="Đường dẫn blender.exe tùy chọn.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ lập kế hoạch, không chạy Blender.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        default=True,
        help="Tiếp tục khi một file/phòng lỗi (mặc định).",
    )
    parser.add_argument("--stop-on-error", action="store_true", help="Dừng sau lỗi đầu tiên.")
    parser.add_argument("--json-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--verbose", action="store_true", help="In log chi tiet.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the batch CLI."""

    configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        report = run_batch(args)
        write_json_report(report, args.json_report)
        print_summary(report, args.json_report)
    except json.JSONDecodeError as exc:
        print(f"ERR_JOB_FILE_INVALID: Job-file không phải JSON hợp lệ: {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2

    if report.failed and (args.stop_on_error or not args.dry_run):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
