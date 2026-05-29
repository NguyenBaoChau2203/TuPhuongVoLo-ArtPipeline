"""Batch wrapper for Feature 005 Maya room builds.

The batch layer reuses build_maya_room planning/execution so dry-run reports and
actual Maya runs resolve names, rooms, and outputs the same way.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import build_maya_room as builder
from clean_svg_paths import configure_stdio
from detect_rooms_from_svg import RoomReport, detect_rooms, normalize_room_name

DEFAULT_STYLE = "line_art_green_floor"
DEFAULT_REPORT = builder.repo_root() / "outputs" / "reports" / "batch_maya_report.json"
PIPELINE_STEP = "feature_005_maya_bridge_batch"
STATUS_PLANNED = "planned"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"


@dataclass
class BatchMayaJob:
    """One planned or executed Maya room build."""

    source_svg: Path
    room_name: str
    style: str
    room_preset: str | None
    planned_maya_output: Path | None
    status: str = STATUS_PLANNED
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly job representation."""

        return {
            "source_svg": str(self.source_svg),
            "room_name": self.room_name,
            "style": self.style,
            "room_preset": self.room_preset,
            "planned_maya_output": str(self.planned_maya_output)
            if self.planned_maya_output
            else None,
            "status": self.status,
            "message": self.message,
            "feature005_command": build_feature005_command(self, dry_run=True)
            if self.room_name
            else [],
        }


@dataclass
class BatchMayaReport:
    """Summary report for one Maya batch run."""

    input_mode: str
    scanned_files: int
    detected_rooms: int
    planned_jobs: int
    succeeded: int
    failed: int
    skipped: int
    jobs: list[BatchMayaJob]

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


def build_feature005_command(job: BatchMayaJob, dry_run: bool) -> list[str]:
    """Return the equivalent Feature 005 CLI command for this job."""

    command = [
        sys.executable or "python",
        str(builder.repo_root() / "scripts" / "python" / "build_maya_room.py"),
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
        raise ValueError("Không tìm thấy phòng có boundary đóng kín để dựng Maya.")

    if requested_room:
        normalized = normalize_room_name(requested_room)
        selected = [report for report in usable if report.room_name == normalized]
        if not selected:
            available = ", ".join(report.room_name for report in usable)
            raise ValueError(
                f"Không tìm thấy phòng '{normalized}'. Phòng có sẵn: {available}"
            )
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
    """Build Feature 005 args namespace for a single room."""

    return argparse.Namespace(
        input=source_svg,
        room=room_name,
        style=args.style,
        room_preset=args.room_preset,
        output_dir=args.output_dir,
        maya_path=args.maya_path,
        dry_run=dry_run,
        verbose=args.verbose,
    )


def create_job_from_room(
    args: argparse.Namespace,
    source_svg: Path,
    room: RoomReport,
) -> BatchMayaJob:
    """Create one job by reusing Feature 005 dry-run planning."""

    plan = builder.build_plan(make_plan_args(args, source_svg, room.room_name, dry_run=True))
    message = "; ".join(plan.warnings)
    return BatchMayaJob(
        source_svg=plan.input_path,
        room_name=plan.room.room_name,
        style=plan.style_name,
        room_preset=plan.room_preset_name,
        planned_maya_output=plan.maya_output,
        status=STATUS_PLANNED,
        message=message,
    )


def failed_job(source_svg: Path, message: str, style: str, room_name: str = "") -> BatchMayaJob:
    """Create a failed placeholder job for file-level errors."""

    return BatchMayaJob(
        source_svg=source_svg.resolve(),
        room_name=room_name,
        style=style,
        room_preset=None,
        planned_maya_output=None,
        status=STATUS_FAILED,
        message=message,
    )


def create_jobs_for_svg(
    args: argparse.Namespace,
    source_svg: Path,
) -> tuple[list[BatchMayaJob], int]:
    """Detect rooms in one SVG and create jobs for selected rooms."""

    reports = detect_rooms(source_svg)
    target_rooms = select_target_rooms(reports, args.room, args.all_rooms)
    return [create_job_from_room(args, source_svg, room) for room in target_rooms], len(reports)


def load_jobs_from_file(job_file: Path, args: argparse.Namespace) -> list[BatchMayaJob]:
    """Load a saved Maya job list from a prior report or raw jobs array."""

    resolved = job_file.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy job-file: {resolved}")
    data = json.loads(resolved.read_text(encoding="utf-8"))
    raw_jobs = data.get("jobs", data) if isinstance(data, dict) else data
    if not isinstance(raw_jobs, list):
        raise ValueError("Job-file phải là JSON array hoặc report có trường jobs.")

    jobs: list[BatchMayaJob] = []
    for index, raw in enumerate(raw_jobs, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Job-file có job #{index} không phải object JSON.")
        source_svg = Path(str(raw.get("source_svg", ""))).resolve()
        room_name = str(raw.get("room_name", "")).strip()
        style = str(raw.get("style") or args.style)
        room_preset = raw.get("room_preset")
        planned_maya = raw.get("planned_maya_output") or raw.get("maya_output")
        jobs.append(
            BatchMayaJob(
                source_svg=source_svg,
                room_name=room_name,
                style=style,
                room_preset=str(room_preset) if room_preset else None,
                planned_maya_output=Path(str(planned_maya)).resolve() if planned_maya else None,
                status=STATUS_PLANNED if room_name else STATUS_FAILED,
                message="Đã tải từ job-file; dry-run sẽ không chạy Maya.",
            )
        )
    return jobs


def discover_jobs(args: argparse.Namespace) -> tuple[str, int, int, list[BatchMayaJob]]:
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

    jobs: list[BatchMayaJob] = []
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


def execute_job(job: BatchMayaJob, args: argparse.Namespace) -> BatchMayaJob:
    """Run one job through Feature 005 and update its status."""

    if job.status == STATUS_FAILED:
        return job
    try:
        plan_args = make_plan_args(args, job.source_svg, job.room_name, dry_run=False)
        plan_args.style = job.style
        plan_args.room_preset = job.room_preset
        plan = builder.build_plan(plan_args)
        print(f"Đang dựng Maya: {plan.room.room_name} từ {plan.input_path}")
        return_code = builder.run_maya(plan, verbose=args.verbose)
        job.planned_maya_output = plan.maya_output
        if return_code == 0:
            job.status = STATUS_SUCCEEDED
            job.message = "Đã tạo .ma và cập nhật manifest."
        else:
            job.status = STATUS_FAILED
            job.message = f"Maya trả về mã lỗi {return_code}."
    except FileNotFoundError as exc:
        job.status = STATUS_FAILED
        job.message = f"Không tìm thấy Maya/mayapy hoặc file cần thiết: {exc}"
    except (OSError, ValueError) as exc:
        job.status = STATUS_FAILED
        job.message = f"Lỗi khi chạy job: {exc}"
    return job


def mark_remaining_skipped(jobs: list[BatchMayaJob], start_index: int, message: str) -> None:
    """Mark remaining planned jobs as skipped after stop-on-error."""

    for job in jobs[start_index:]:
        if job.status == STATUS_PLANNED:
            job.status = STATUS_SKIPPED
            job.message = message


def report_from_jobs(
    input_mode: str,
    scanned_files: int,
    detected_rooms: int,
    jobs: list[BatchMayaJob],
) -> BatchMayaReport:
    """Build a summary report from current job statuses."""

    return BatchMayaReport(
        input_mode=input_mode,
        scanned_files=scanned_files,
        detected_rooms=detected_rooms,
        planned_jobs=sum(1 for job in jobs if job.room_name and job.planned_maya_output),
        succeeded=sum(1 for job in jobs if job.status == STATUS_SUCCEEDED),
        failed=sum(1 for job in jobs if job.status == STATUS_FAILED),
        skipped=sum(1 for job in jobs if job.status == STATUS_SKIPPED),
        jobs=jobs,
    )


def write_json_report(report: BatchMayaReport, json_report: Path) -> None:
    """Write a UTF-8, pretty-printed JSON batch report."""

    json_report.parent.mkdir(parents=True, exist_ok=True)
    json_report.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_summary(report: BatchMayaReport, report_path: Path) -> None:
    """Print an artist-facing Vietnamese summary."""

    print("TuPhuongVoLo-ArtPipeline - Batch Maya room")
    print(f"Số file SVG đã quét: {report.scanned_files}")
    print(f"Số phòng đã phát hiện: {report.detected_rooms}")
    print(f"Số job đã lập kế hoạch: {report.planned_jobs}")
    print(f"Thành công: {report.succeeded}")
    print(f"Thất bại: {report.failed}")
    print(f"Bỏ qua: {report.skipped}")
    print(f"Báo cáo JSON: {report_path}")


def run_batch(args: argparse.Namespace) -> BatchMayaReport:
    """Create and optionally execute a Maya batch report."""

    input_mode, scanned_files, detected_rooms, jobs = discover_jobs(args)

    if args.dry_run:
        for job in jobs:
            if job.status == STATUS_PLANNED and not job.message:
                job.message = (
                    "Dry-run: chỉ lập kế hoạch, không chạy Maya, "
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
        print(f"Building Maya {rendered}/{total}: {job.room_name}")
        execute_job(job, args)
        if job.status == STATUS_FAILED and args.stop_on_error:
            mark_remaining_skipped(jobs, index + 1, "Dừng theo --stop-on-error.")
            break

    return report_from_jobs(input_mode, scanned_files, detected_rooms, jobs)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Batch dựng nhiều phòng Maya từ SVG sạch."
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
    parser.add_argument("--room", help="Lọc theo tên phòng đã normalize, ví dụ kho.")
    parser.add_argument(
        "--all-rooms",
        action="store_true",
        help="Lập job cho mọi phòng dùng được.",
    )
    parser.add_argument("--style", default=DEFAULT_STYLE, help="Style preset dùng cho cả batch.")
    parser.add_argument("--room-preset", help="Room preset tùy chọn.")
    parser.add_argument(
        "--maya-path",
        type=Path,
        help="Đường dẫn mayapy.exe tùy chọn.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ lập kế hoạch, không chạy Maya.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Dừng sau lỗi đầu tiên.",
    )
    parser.add_argument("--json-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--verbose", action="store_true", help="In log chi tiết.")
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
        print(
            f"ERR_JOB_FILE_INVALID: Job-file không phải JSON hợp lệ: {exc}",
            file=sys.stderr,
        )
        return 2
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2

    if report.failed and (args.stop_on_error or not args.dry_run):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
