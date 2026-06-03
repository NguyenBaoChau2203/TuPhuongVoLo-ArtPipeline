"""Create a safe Maya scene sandbox for agent-controlled experiments.

This utility prepares a timestamped backup session outside generated output
folders. It never opens Maya and never mutates the source scene, source SVG, or
geometry handoff JSON.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_SESSION_LABEL = "maya_agent_session"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


@dataclass(frozen=True)
class CopyPlan:
    """One source-to-sandbox copy operation."""

    source: Path
    destination: Path
    label: str


@dataclass(frozen=True)
class SandboxPlan:
    """Resolved paths and copy operations for one sandbox session."""

    timestamp: str
    room: str | None
    session_name: str | None
    backup_root: Path
    session_dir: Path
    original_dir: Path
    working_dir: Path
    reports_dir: Path
    restore_script: Path
    intended_working_scene: Path
    copies: list[CopyPlan]
    original_input_paths: dict[str, str | None]
    copied_sandbox_paths: dict[str, str | None]
    git_commit: str | None


def repo_root() -> Path:
    """Return the repository root from this script location."""

    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Create a timestamped Maya agent sandbox backup. "
            "Antigravity/MCP should open only working/scene_agent_work.ma."
        )
    )
    parser.add_argument(
        "--maya-scene",
        required=True,
        type=Path,
        help="Path to the generated .ma scene to copy into the sandbox.",
    )
    parser.add_argument(
        "--geometry-json",
        type=Path,
        help="Optional geometry JSON handoff to snapshot in original/.",
    )
    parser.add_argument(
        "--source-svg",
        type=Path,
        help="Optional source SVG snapshot to copy in original/.",
    )
    parser.add_argument(
        "--backup-root",
        type=Path,
        help="Optional backup root. Defaults outside generated outputs.",
    )
    parser.add_argument("--room", help="Optional room name for reports/session naming.")
    parser.add_argument("--session-name", help="Optional session label for the folder name.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned folders and copies without creating or copying files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing session folder with the same timestamp/name.",
    )
    return parser


def current_timestamp() -> str:
    """Return a filesystem-friendly timestamp."""

    return datetime.now().strftime(TIMESTAMP_FORMAT)


def default_backup_root() -> Path:
    """Return a safe local backup root outside repo outputs."""

    windows_drive = Path("D:/")
    if os.name == "nt" and windows_drive.exists():
        return Path("D:/TuPhuongVoLo_AgentBackups")
    return Path.home() / "TuPhuongVoLo_AgentBackups"


def sanitize_label(value: str | None) -> str:
    """Return a conservative folder-name label."""

    if not value:
        return DEFAULT_SESSION_LABEL
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", ascii_text).strip("._-")
    return safe or DEFAULT_SESSION_LABEL


def resolve_existing_file(path: Path, field_name: str, suffix: str | None = None) -> Path:
    """Resolve and validate an input file without modifying it."""

    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy {field_name}: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{field_name} phải là file: {resolved}")
    if suffix and resolved.suffix.lower() != suffix:
        raise ValueError(f"{field_name} phải có đuôi {suffix}: {resolved}")
    return resolved


def ensure_direct_child(child: Path, parent: Path) -> None:
    """Guard force replacement so only the computed session folder is removed."""

    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    if child_resolved.parent != parent_resolved:
        raise ValueError(
            "Session folder không nằm trực tiếp trong backup root; dừng để an toàn."
        )


def git_commit_hash(root: Path | None = None) -> str | None:
    """Return the current git commit hash if git metadata is available."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root or repo_root(),
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def build_plan(args: argparse.Namespace, timestamp: str | None = None) -> SandboxPlan:
    """Resolve a sandbox plan from parsed CLI arguments."""

    maya_scene = resolve_existing_file(args.maya_scene, "Maya scene", ".ma")
    geometry_json = (
        resolve_existing_file(args.geometry_json, "geometry JSON", ".json")
        if args.geometry_json
        else None
    )
    source_svg = (
        resolve_existing_file(args.source_svg, "source SVG", ".svg") if args.source_svg else None
    )

    backup_root = (args.backup_root or default_backup_root()).expanduser().resolve()
    resolved_timestamp = timestamp or current_timestamp()
    label_source = args.session_name or args.room
    session_label = sanitize_label(label_source)
    session_dir = backup_root / f"{resolved_timestamp}_{session_label}"
    original_dir = session_dir / "original"
    working_dir = session_dir / "working"
    reports_dir = session_dir / "reports"
    restore_script = session_dir / "restore_agent_backup.ps1"
    scene_original = original_dir / "scene_before_agent.ma"
    scene_working = working_dir / "scene_agent_work.ma"

    copies = [
        CopyPlan(maya_scene, scene_original, "scene_before_agent"),
        CopyPlan(maya_scene, scene_working, "scene_agent_work"),
    ]
    geometry_copy = None
    if geometry_json:
        geometry_copy = original_dir / "geometry_before_agent.json"
        copies.append(CopyPlan(geometry_json, geometry_copy, "geometry_before_agent"))

    source_svg_copy = None
    if source_svg:
        source_svg_copy = original_dir / "source_svg_snapshot.svg"
        copies.append(CopyPlan(source_svg, source_svg_copy, "source_svg_snapshot"))

    return SandboxPlan(
        timestamp=resolved_timestamp,
        room=args.room,
        session_name=args.session_name,
        backup_root=backup_root,
        session_dir=session_dir,
        original_dir=original_dir,
        working_dir=working_dir,
        reports_dir=reports_dir,
        restore_script=restore_script,
        intended_working_scene=scene_working,
        copies=copies,
        original_input_paths={
            "maya_scene": str(maya_scene),
            "geometry_json": str(geometry_json) if geometry_json else None,
            "source_svg": str(source_svg) if source_svg else None,
        },
        copied_sandbox_paths={
            "scene_before_agent": str(scene_original),
            "scene_agent_work": str(scene_working),
            "geometry_before_agent": str(geometry_copy) if geometry_copy else None,
            "source_svg_snapshot": str(source_svg_copy) if source_svg_copy else None,
        },
        git_commit=git_commit_hash(),
    )


def safety_notes() -> list[str]:
    """Return safety notes included in the JSON report."""

    return [
        "Agent opens only working/scene_agent_work.ma.",
        "Do not open or modify original .ai/.svg/.ma source files.",
        "Save agent results as new files inside working/.",
        "Review agent changes before accepting them into production.",
        "Use restore_agent_backup.ps1 only when a restore target is explicit.",
        "No MCP server, AI API, or web UI is configured by this utility.",
    ]


def render_agent_notes(plan: SandboxPlan) -> str:
    """Return Vietnamese Markdown instructions for the sandbox session."""

    return f"""# Ghi chú phiên sandbox Maya Agent

## Quy tắc bắt buộc

- Agent chỉ được mở file: `{plan.intended_working_scene}`
- Không mở hoặc chỉnh sửa file `.ai`, `.svg`, `.ma` gốc của họa sĩ.
- Không chỉnh sửa file geometry JSON gốc.
- Nếu agent tạo kết quả mới, hãy lưu thành file mới bên trong thư mục `working/`.
- Luôn xem lại file agent tạo ra trước khi chấp nhận vào pipeline chính.
- Nếu cần khôi phục scene ban đầu, dùng script: `{plan.restore_script}`

## Nên làm

1. Mở Maya bằng bản sao trong `working/scene_agent_work.ma`.
2. Cho Antigravity/MCP hoặc agent toàn quyền chỉ trong thư mục `working/`.
3. Lưu kết quả thử nghiệm thành tên mới, ví dụ `scene_agent_result_v001.ma`.
4. Họa sĩ hoặc developer kiểm tra thủ công trước khi đưa vào sản xuất.

## Không được làm

- Không commit file `.ma`, `.png`, `.zip`, hoặc nội dung sinh ra trong `outputs/`.
- Không đưa secrets, `.env`, token, hoặc credential vào báo cáo/session.
- Không trỏ agent vào thư mục `assets/`, `drops/`, hoặc scene gốc.
- Không cài MayaMCP hoặc cấu hình Antigravity trong bước 010A này.
"""


def render_restore_script() -> str:
    """Return a readable PowerShell restore helper."""

    return r"""[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string]$RestoreTarget
)

$ErrorActionPreference = "Stop"

$SessionRoot = $PSScriptRoot
$OriginalScene = Join-Path $SessionRoot "original\scene_before_agent.ma"

if (-not (Test-Path -LiteralPath $OriginalScene -PathType Leaf)) {
    throw "Khong tim thay ban sao scene goc: $OriginalScene"
}

$TargetParent = Split-Path -Parent $RestoreTarget
if ($TargetParent -and -not (Test-Path -LiteralPath $TargetParent -PathType Container)) {
    throw "Thu muc dich khong ton tai: $TargetParent"
}

if ($PSCmdlet.ShouldProcess($RestoreTarget, "Restore Maya scene backup")) {
    Copy-Item -LiteralPath $OriginalScene -Destination $RestoreTarget -Force
    Write-Host "Da restore scene backup vao: $RestoreTarget"
}
"""


def session_report(plan: SandboxPlan) -> dict[str, Any]:
    """Return the JSON-serializable session report."""

    return {
        "timestamp": plan.timestamp,
        "room": plan.room,
        "session_name": plan.session_name,
        "backup_root": str(plan.backup_root),
        "session_folder": str(plan.session_dir),
        "git_commit": plan.git_commit,
        "original_input_paths": plan.original_input_paths,
        "copied_sandbox_paths": plan.copied_sandbox_paths,
        "safety_notes": safety_notes(),
        "intended_working_scene_path": str(plan.intended_working_scene),
        "restore_script_path": str(plan.restore_script),
    }


def write_reports(plan: SandboxPlan) -> None:
    """Write the JSON report, Markdown notes, and restore helper."""

    report_path = plan.reports_dir / "agent_session.json"
    notes_path = plan.reports_dir / "agent_notes.md"
    report_path.write_text(
        json.dumps(session_report(plan), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    notes_path.write_text(render_agent_notes(plan), encoding="utf-8")
    plan.restore_script.write_text(render_restore_script(), encoding="utf-8")


def print_dry_run(plan: SandboxPlan) -> None:
    """Print a human-readable dry-run plan."""

    print("DRY RUN - không tạo thư mục hoặc copy file.")
    print(f"Backup root: {plan.backup_root}")
    print(f"Session folder: {plan.session_dir}")
    print("Planned copies:")
    for copy_plan in plan.copies:
        print(f"  - {copy_plan.source} -> {copy_plan.destination}")
    print(f"Report JSON: {plan.reports_dir / 'agent_session.json'}")
    print(f"Agent notes: {plan.reports_dir / 'agent_notes.md'}")
    print(f"Restore script: {plan.restore_script}")


def create_sandbox(plan: SandboxPlan, force: bool = False) -> SandboxPlan:
    """Create the sandbox session and copy files."""

    if plan.session_dir.exists():
        if not force:
            raise FileExistsError(
                "Session folder đã tồn tại. Dùng --force nếu thật sự muốn thay thế: "
                f"{plan.session_dir}"
            )
        ensure_direct_child(plan.session_dir, plan.backup_root)
        shutil.rmtree(plan.session_dir)

    plan.original_dir.mkdir(parents=True, exist_ok=False)
    plan.working_dir.mkdir(parents=True, exist_ok=False)
    plan.reports_dir.mkdir(parents=True, exist_ok=False)

    for copy_plan in plan.copies:
        shutil.copy2(copy_plan.source, copy_plan.destination)

    write_reports(plan)
    return plan


def run(args: argparse.Namespace) -> SandboxPlan:
    """Execute or dry-run the sandbox workflow."""

    plan = build_plan(args)
    if args.dry_run:
        print_dry_run(plan)
        return plan

    create_sandbox(plan, force=args.force)
    print(f"Đã tạo Maya agent sandbox: {plan.session_dir}")
    print(f"Agent chỉ được mở: {plan.intended_working_scene}")
    return plan


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
