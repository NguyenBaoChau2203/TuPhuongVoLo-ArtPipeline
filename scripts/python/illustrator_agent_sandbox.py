"""Create a safe Illustrator asset sandbox for agent-controlled experiments.

This utility prepares a timestamped backup session outside generated output
folders. It never opens Illustrator, never connects to MCP, and never reads or
parses Illustrator/SVG/PNG contents.
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


DEFAULT_SESSION_LABEL = "illustrator_agent_session"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


@dataclass(frozen=True)
class CopyPlan:
    """One source-to-sandbox copy operation."""

    source: Path
    destination: Path
    label: str


@dataclass(frozen=True)
class SandboxPlan:
    """Resolved paths and copy operations for one Illustrator sandbox session."""

    timestamp: str
    room: str | None
    session_name: str | None
    label: str
    backup_root: Path
    session_dir: Path
    original_dir: Path
    working_dir: Path
    reports_dir: Path
    restore_script: Path
    copies: list[CopyPlan]
    inputs: dict[str, str | None]
    original_paths: dict[str, str | None]
    working_paths: dict[str, str | None]
    git_commit: str | None


def repo_root() -> Path:
    """Return the repository root from this script location."""

    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Create a timestamped Illustrator agent sandbox backup. "
            "AI/Illustrator MCP may use only files inside working/."
        )
    )
    parser.add_argument("--source-ai", type=Path, help="Optional .ai or .ait source file.")
    parser.add_argument("--source-svg", type=Path, help="Optional .svg source file.")
    parser.add_argument("--source-png", type=Path, help="Optional .png source file.")
    parser.add_argument("--room", help="Optional room name for reports/session naming.")
    parser.add_argument("--session-name", help="Optional session label for the folder name.")
    parser.add_argument(
        "--backup-root",
        type=Path,
        help="Optional backup root. Defaults outside repo outputs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned paths without creating folders or copying files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing direct-child session folder with the same timestamp/name.",
    )
    return parser


def current_timestamp() -> str:
    """Return a filesystem-friendly timestamp."""

    return datetime.now().strftime(TIMESTAMP_FORMAT)


def default_backup_root() -> Path:
    """Return a safe local backup root outside repo outputs."""

    windows_drive = Path("D:/")
    if os.name == "nt" and windows_drive.exists():
        return Path("D:/TuPhuongVoLo_IllustratorAgentBackups")
    return Path.home() / "TuPhuongVoLo_IllustratorAgentBackups"


def sanitize_label(value: str | None) -> str:
    """Return a conservative lowercase ASCII-ish folder-name label."""

    if not value:
        return DEFAULT_SESSION_LABEL
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", ascii_text).strip("._-").lower()
    return safe or DEFAULT_SESSION_LABEL


def session_label(room: str | None, session_name: str | None) -> str:
    """Build the session label from provided room/session names."""

    labels = [sanitize_label(item) for item in (room, session_name) if item]
    return "_".join(labels) if labels else DEFAULT_SESSION_LABEL


def resolve_existing_file(
    path: Path, field_name: str, suffixes: tuple[str, ...]
) -> Path:
    """Resolve and validate an input file without reading or modifying it."""

    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Không tìm thấy {field_name}: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{field_name} phải là file: {resolved}")
    if resolved.suffix.lower() not in suffixes:
        expected = " hoặc ".join(suffixes)
        raise ValueError(f"{field_name} phải có đuôi {expected}: {resolved}")
    return resolved


def ensure_at_least_one_source(args: argparse.Namespace) -> None:
    """Validate that the user provided at least one supported source file."""

    if not (args.source_ai or args.source_svg or args.source_png):
        raise ValueError("Cần cung cấp ít nhất một file: --source-ai, --source-svg, hoặc --source-png.")


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

    ensure_at_least_one_source(args)

    source_ai = (
        resolve_existing_file(args.source_ai, "source AI", (".ai", ".ait"))
        if args.source_ai
        else None
    )
    source_svg = (
        resolve_existing_file(args.source_svg, "source SVG", (".svg",))
        if args.source_svg
        else None
    )
    source_png = (
        resolve_existing_file(args.source_png, "source PNG", (".png",))
        if args.source_png
        else None
    )

    backup_root = (args.backup_root or default_backup_root()).expanduser().resolve()
    resolved_timestamp = timestamp or current_timestamp()
    label = session_label(args.room, args.session_name)
    session_dir = backup_root / f"{resolved_timestamp}_{label}"
    original_dir = session_dir / "original"
    working_dir = session_dir / "working"
    reports_dir = session_dir / "reports"
    restore_script = session_dir / "restore_illustrator_backup.ps1"

    original_paths = {
        "source_ai_before_agent": str(original_dir / "source_ai_before_agent.ai")
        if source_ai
        else None,
        "source_svg_before_agent": str(original_dir / "source_svg_before_agent.svg")
        if source_svg
        else None,
        "source_png_before_agent": str(original_dir / "source_png_before_agent.png")
        if source_png
        else None,
    }
    working_paths = {
        "scene_agent_work_ai": str(working_dir / "scene_agent_work.ai") if source_ai else None,
        "scene_agent_work_svg": str(working_dir / "scene_agent_work.svg") if source_svg else None,
        "scene_agent_work_png": str(working_dir / "scene_agent_work.png") if source_png else None,
    }

    copies: list[CopyPlan] = []
    if source_ai:
        copies.append(
            CopyPlan(source_ai, Path(original_paths["source_ai_before_agent"]), "source_ai_before_agent")
        )
        copies.append(
            CopyPlan(source_ai, Path(working_paths["scene_agent_work_ai"]), "scene_agent_work_ai")
        )
    if source_svg:
        copies.append(
            CopyPlan(
                source_svg,
                Path(original_paths["source_svg_before_agent"]),
                "source_svg_before_agent",
            )
        )
        copies.append(
            CopyPlan(source_svg, Path(working_paths["scene_agent_work_svg"]), "scene_agent_work_svg")
        )
    if source_png:
        copies.append(
            CopyPlan(
                source_png,
                Path(original_paths["source_png_before_agent"]),
                "source_png_before_agent",
            )
        )
        copies.append(
            CopyPlan(source_png, Path(working_paths["scene_agent_work_png"]), "scene_agent_work_png")
        )

    return SandboxPlan(
        timestamp=resolved_timestamp,
        room=args.room,
        session_name=args.session_name,
        label=label,
        backup_root=backup_root,
        session_dir=session_dir,
        original_dir=original_dir,
        working_dir=working_dir,
        reports_dir=reports_dir,
        restore_script=restore_script,
        copies=copies,
        inputs={
            "source_ai": str(source_ai) if source_ai else None,
            "source_svg": str(source_svg) if source_svg else None,
            "source_png": str(source_png) if source_png else None,
        },
        original_paths=original_paths,
        working_paths=working_paths,
        git_commit=git_commit_hash(),
    )


def safety_notes() -> list[str]:
    """Return safety notes included in the JSON report."""

    return [
        "AI/Illustrator MCP may open only working/scene_agent_work.ai if it exists.",
        "Agent may use only working copy files inside the sandbox working folder.",
        "Original .ai/.svg/.png files must never be opened or edited by the agent.",
        "Do not save over original files or export to source folders.",
        "Artist must review before accepting changes.",
        "No Illustrator MCP, Antigravity MCP, AI API, or web connection is configured by this utility.",
    ]


def render_agent_notes() -> str:
    """Return Vietnamese Markdown instructions for the sandbox session."""

    return """# Ghi chú phiên sandbox Illustrator Agent

## Quy tắc bắt buộc

- AI/Illustrator MCP chỉ được mở `working/scene_agent_work.ai` nếu file này tồn tại.
- AI chỉ được dùng các bản sao làm việc bên trong thư mục sandbox `working/`.
- File gốc `.ai`, `.svg`, `.png` tuyệt đối không được mở hoặc chỉnh sửa bởi agent.
- Không save đè lên file gốc.
- Không export vào thư mục nguồn.
- Không xóa, flatten, merge, hoặc đổi tên artwork production nếu chưa được phê duyệt rõ ràng.
- Không commit generated art, backups, outputs, secrets, `.ai`, `.svg`, `.png`, `.ma`, hoặc `.zip`.
- Họa sĩ phải review thủ công trước khi chấp nhận thay đổi.
"""


def render_restore_script() -> str:
    """Return a readable PowerShell restore helper."""

    return r"""[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RestoreTargetFolder,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

# CANH BAO: Script nay khong tu dong chay. Chi restore khi ban da chon ro thu muc dich.
# CANH BAO: Nen restore ra thu muc kiem tra rieng, khong restore truc tiep len artwork production.
$SessionRoot = $PSScriptRoot
$OriginalFolder = Join-Path $SessionRoot "original"

if (-not (Test-Path -LiteralPath $OriginalFolder -PathType Container)) {
    throw "Khong tim thay thu muc original trong sandbox: $OriginalFolder"
}

if (-not (Test-Path -LiteralPath $RestoreTargetFolder -PathType Container)) {
    throw "Thu muc restore khong ton tai. Hay tao thu muc dich truoc: $RestoreTargetFolder"
}

$Snapshots = @(
    "source_ai_before_agent.ai",
    "source_svg_before_agent.svg",
    "source_png_before_agent.png"
)

foreach ($Snapshot in $Snapshots) {
    $Source = Join-Path $OriginalFolder $Snapshot
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        continue
    }

    $Destination = Join-Path $RestoreTargetFolder $Snapshot
    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        throw "File dich da ton tai, khong ghi de neu thieu -Force: $Destination"
    }

    if ($Force) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    } else {
        Copy-Item -LiteralPath $Source -Destination $Destination
    }
    Write-Host "Da restore snapshot vao: $Destination"
}
"""


def session_report(plan: SandboxPlan) -> dict[str, Any]:
    """Return the JSON-serializable session report."""

    return {
        "timestamp": plan.timestamp,
        "room": plan.room,
        "session_name": plan.session_name,
        "label": plan.label,
        "backup_root": str(plan.backup_root),
        "session_dir": str(plan.session_dir),
        "git_commit": plan.git_commit,
        "inputs": plan.inputs,
        "original_paths": plan.original_paths,
        "working_paths": plan.working_paths,
        "safety_notes": safety_notes(),
    }


def write_reports(plan: SandboxPlan) -> None:
    """Write the JSON report, Markdown notes, and restore helper."""

    report_path = plan.reports_dir / "illustrator_agent_session.json"
    notes_path = plan.reports_dir / "agent_notes.md"
    report_path.write_text(
        json.dumps(session_report(plan), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    notes_path.write_text(render_agent_notes(), encoding="utf-8")
    plan.restore_script.write_text(render_restore_script(), encoding="utf-8")


def print_dry_run(plan: SandboxPlan) -> None:
    """Print a human-readable dry-run plan."""

    print("DRY RUN - không tạo thư mục hoặc copy file.")
    print(f"Backup root: {plan.backup_root}")
    print(f"Session folder: {plan.session_dir}")
    print("Source paths:")
    for key, value in plan.inputs.items():
        print(f"  - {key}: {value}")
    print("Original paths:")
    for key, value in plan.original_paths.items():
        print(f"  - {key}: {value}")
    print("Working paths:")
    for key, value in plan.working_paths.items():
        print(f"  - {key}: {value}")
    print("Report paths:")
    print(f"  - illustrator_agent_session: {plan.reports_dir / 'illustrator_agent_session.json'}")
    print(f"  - agent_notes: {plan.reports_dir / 'agent_notes.md'}")
    print(f"  - restore_script: {plan.restore_script}")


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
    print(f"Đã tạo Illustrator agent sandbox: {plan.session_dir}")
    if plan.working_paths["scene_agent_work_ai"]:
        print(f"AI/Illustrator MCP chỉ được mở: {plan.working_paths['scene_agent_work_ai']}")
    else:
        print(f"AI chỉ được dùng file làm việc trong: {plan.working_dir}")
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
