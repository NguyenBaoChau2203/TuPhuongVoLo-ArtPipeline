"""Developer-only packaging helper for the artist desktop app.

This script prepares a PyInstaller command for the Tkinter wrapper. It does not
install PyInstaller, bundle Maya, or change the existing pipeline logic.
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

APP_ENTRY = "scripts/python/artist_desktop_app.py"
EXE_NAME = "TuPhuongVoLo_MayaArtistApp"
PYINSTALLER_MISSING_MESSAGE = (
    "Chưa cài PyInstaller. Hãy cài trong môi trường dev bằng: "
    "python -m pip install pyinstaller"
)
PACKAGING_CLEAN_RELATIVE_PATHS = (
    Path("build"),
    Path("dist"),
)
PROTECTED_OUTPUT_PARTS = {"outputs", "assets", "drops"}


def repo_root() -> Path:
    """Return repository root from this script location."""

    return Path(__file__).resolve().parents[2]


def resolve_pyinstaller_command_prefix() -> list[str] | None:
    """Return a runnable PyInstaller command prefix for the current Python env."""

    pyinstaller_path = shutil.which("pyinstaller")
    if pyinstaller_path is not None:
        return [pyinstaller_path]

    if importlib.util.find_spec("PyInstaller") is not None:
        return [sys.executable, "-m", "PyInstaller"]

    return None


def build_pyinstaller_command(
    *,
    command_prefix: list[str] | None = None,
    app_entry: str = APP_ENTRY,
    exe_name: str = EXE_NAME,
) -> list[str]:
    """Build the PyInstaller command without running it."""

    prefix = command_prefix
    if prefix is None:
        prefix = resolve_pyinstaller_command_prefix() or ["pyinstaller"]

    return [
        *prefix,
        "--onefile",
        "--windowed",
        "--name",
        exe_name,
        "--distpath",
        "dist",
        "--workpath",
        "build/pyinstaller-work",
        "--specpath",
        "build/pyinstaller-spec",
        app_entry,
    ]


def command_to_display(command: list[str]) -> str:
    """Return a Windows-friendly display string."""

    return subprocess.list2cmdline(command)


def configure_stdio() -> None:
    """Prefer UTF-8 console output for Vietnamese messages on Windows."""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _is_safe_clean_target(root: Path, target: Path) -> bool:
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    try:
        relative = resolved_target.relative_to(resolved_root)
    except ValueError:
        return False

    parts = set(relative.parts)
    if parts & PROTECTED_OUTPUT_PARTS:
        return False

    return relative in PACKAGING_CLEAN_RELATIVE_PATHS


def clean_packaging_outputs(root: Path) -> list[str]:
    """Remove only known packaging directories inside the repository."""

    messages: list[str] = []
    for relative_path in PACKAGING_CLEAN_RELATIVE_PATHS:
        target = root / relative_path
        if not _is_safe_clean_target(root, target):
            messages.append(f"Bỏ qua đường dẫn không an toàn: {target}")
            continue
        if not target.exists():
            messages.append(f"Không có gì để xóa: {target}")
            continue
        if target.is_dir():
            shutil.rmtree(target)
            messages.append(f"Đã xóa thư mục package: {target}")
        else:
            target.unlink()
            messages.append(f"Đã xóa file package: {target}")
    return messages


def run_pyinstaller_build(command: list[str], *, root: Path) -> int:
    """Run PyInstaller if it is available in the active dev environment."""

    if resolve_pyinstaller_command_prefix() is None:
        print(PYINSTALLER_MISSING_MESSAGE, file=sys.stderr)
        return 2

    completed = subprocess.run(command, cwd=root, check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Đóng gói desktop app Maya MVP bằng PyInstaller. "
            "PyInstaller là công cụ dev-only và không được cài tự động."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="In lệnh PyInstaller dự kiến mà không chạy build.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Chạy PyInstaller nếu đã được cài trong môi trường dev.",
    )
    parser.add_argument(
        "--clean-output",
        action="store_true",
        help="Xóa build/ và dist/ trong repo trước khi in lệnh hoặc build.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    root = repo_root()
    args = build_parser().parse_args(argv)
    command_prefix = resolve_pyinstaller_command_prefix()
    command = build_pyinstaller_command(command_prefix=command_prefix)

    if args.clean_output:
        for message in clean_packaging_outputs(root):
            print(message)

    if args.build:
        print("Đang chạy PyInstaller:")
        print(command_to_display(command))
        return run_pyinstaller_build(command, root=root)

    if command_prefix is None:
        print(PYINSTALLER_MISSING_MESSAGE, file=sys.stderr)
        return 2

    print("Dry-run: lệnh PyInstaller dự kiến là:")
    print(command_to_display(command))
    print()
    print("Output dự kiến: dist/TuPhuongVoLo_MayaArtistApp.exe")
    print("Lưu ý: .exe này vẫn cần repo/pipeline local, không bundle Maya hoặc mayapy.exe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
