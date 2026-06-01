"""Small Tkinter desktop wrapper for the verified Maya-first pipeline.

The app intentionally delegates all pipeline work to build_maya_room.py. It does
not parse SVG, generate Maya geometry, or update manifests by itself.
"""

from __future__ import annotations

import argparse
import os
import queue
import shutil
import subprocess
import sys
import threading
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

APP_TITLE = "TuPhuongVoLo - Maya Artist App MVP"
DEFAULT_ROOM_NAME = "phong_kho"
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_MAYAPY_PATH = r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
DEFAULT_RENDER_WIDTH = 1280
DEFAULT_RENDER_HEIGHT = 720
STATUS_READY = "Sẵn sàng"
STATUS_RUNNING = "Đang chạy..."
RUN_FINISHED_PREFIX = "__RUN_FINISHED__:"
SVG_EMPTY_ERROR = "Chưa chọn file SVG."
SVG_NOT_FOUND_ERROR = "Không tìm thấy file SVG. Hãy kiểm tra lại đường dẫn."
ROOM_EMPTY_ERROR = "Chưa nhập tên phòng/layer."
OUTPUT_EMPTY_ERROR = "Chưa chọn thư mục output."
BUILD_SCRIPT_MISSING_ERROR = "Không tìm thấy build_maya_room.py trong repo."
MAYAPY_REQUIRED_ERROR = "Chạy thật cần đường dẫn mayapy.exe hợp lệ."
MAYAPY_NOT_FOUND_ERROR = "Không tìm thấy mayapy.exe. Hãy kiểm tra lại đường dẫn."
OUTPUT_SUBDIRS = {
    "maya": "maya",
    "preview": "preview",
    "reports": "reports",
}
BUILD_SCRIPT_RELATIVE_PATH = Path("scripts") / "python" / "build_maya_room.py"
REPO_ROOT_ENV_VAR = "TUPHUONGVOLO_REPO_ROOT"
PIPELINE_PYTHON_ENV_VAR = "TUPHUONGVOLO_PYTHON_EXE"
REPO_ROOT_ERROR = (
    "Không tìm thấy repo root. Hãy chạy app từ thư mục repo hoặc đặt biến môi trường "
    "TUPHUONGVOLO_REPO_ROOT."
)
PIPELINE_PYTHON_ERROR = (
    "Không tìm thấy Python để chạy pipeline. Hãy cài Python hoặc đặt "
    "TUPHUONGVOLO_PYTHON_EXE."
)


@dataclass(frozen=True)
class ArtistAppOptions:
    """User inputs needed to run the Maya room CLI."""

    svg_path: Path
    room_name: str = DEFAULT_ROOM_NAME
    output_dir: Path = Path(DEFAULT_OUTPUT_DIR)
    maya_path: Path | None = None
    dry_run: bool = True
    render_preview: bool = False
    render_width: int = DEFAULT_RENDER_WIDTH
    render_height: int = DEFAULT_RENDER_HEIGHT


def _candidate_with_parents(path: Path) -> list[Path]:
    resolved = path.resolve()
    start = resolved if resolved.is_dir() else resolved.parent
    return [start, *start.parents]


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        try:
            key = str(path.resolve()).lower()
        except OSError:
            key = str(path).lower()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def find_repo_root(extra_candidates: Iterable[Path] | None = None) -> Path | None:
    """Find a repo checkout that contains the source-of-truth pipeline script."""

    candidates: list[Path] = []
    env_root = _clean_text(os.environ.get(REPO_ROOT_ENV_VAR))
    if env_root:
        candidates.extend(_candidate_with_parents(Path(env_root)))

    if extra_candidates is not None:
        for candidate in extra_candidates:
            candidates.extend(_candidate_with_parents(candidate))

    candidates.extend(_candidate_with_parents(Path.cwd()))

    if getattr(sys, "frozen", False):
        candidates.extend(_candidate_with_parents(Path(sys.executable)))
    else:
        candidates.extend(_candidate_with_parents(Path(__file__)))

    for candidate in _unique_paths(candidates):
        if (candidate / BUILD_SCRIPT_RELATIVE_PATH).is_file():
            return candidate

    return None


def repo_root() -> Path:
    """Return repository root or raise a Vietnamese runtime error."""

    root = find_repo_root()
    if root is None:
        raise RuntimeError(REPO_ROOT_ERROR)
    return root


def build_script_path(root: Path | None = None) -> Path:
    """Return the source-of-truth Maya room CLI path."""

    return (root or repo_root()) / BUILD_SCRIPT_RELATIVE_PATH


def default_mayapy_path(candidate: str | Path = DEFAULT_MAYAPY_PATH) -> str:
    """Return the common Maya 2024 mayapy path only when it exists."""

    path = Path(candidate)
    return str(path) if path.is_file() else ""


def _clean_text(value: str | None) -> str:
    return (value or "").strip().strip('"')


def _is_empty_path(path: Path) -> bool:
    return str(path).strip() in {"", "."}


def resolve_repo_relative_path(path: Path, root: Path) -> Path:
    """Resolve artist-entered relative paths from the detected repo root."""

    return path if path.is_absolute() else root / path


def resolve_output_root(output_dir: Path, root: Path) -> Path:
    """Resolve an output root without creating it."""

    return output_dir if output_dir.is_absolute() else root / output_dir


def repo_root_display_value(root: Path | None = None) -> str:
    """Return the repo root path shown in the UI."""

    detected_root = root or find_repo_root()
    if detected_root is not None:
        return str(detected_root)
    return _clean_text(os.environ.get(REPO_ROOT_ENV_VAR))


def pipeline_python_command_prefix(
    *,
    python_executable: str | None = None,
) -> list[str] | None:
    """Return the Python command prefix used to run the CLI pipeline."""

    explicit_python = _clean_text(python_executable)
    if explicit_python:
        return [explicit_python]

    env_python = _clean_text(os.environ.get(PIPELINE_PYTHON_ENV_VAR))
    if env_python:
        return [env_python]

    if not getattr(sys, "frozen", False):
        return [sys.executable or "python"]

    python_path = shutil.which("python")
    if python_path:
        return [python_path]

    py_launcher = shutil.which("py")
    if py_launcher:
        return [py_launcher, "-3"]

    return None


def configure_stdio() -> None:
    """Prefer UTF-8 console output for Vietnamese messages on Windows."""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def options_from_strings(
    *,
    svg_path: str,
    room_name: str,
    output_dir: str,
    maya_path: str,
    dry_run: bool,
    render_preview: bool,
    render_width: str | int,
    render_height: str | int,
) -> ArtistAppOptions:
    """Create validated option values from UI strings."""

    width = int(render_width)
    height = int(render_height)
    mayapy = _clean_text(maya_path)
    return ArtistAppOptions(
        svg_path=Path(_clean_text(svg_path)),
        room_name=_clean_text(room_name),
        output_dir=Path(_clean_text(output_dir)),
        maya_path=Path(mayapy) if mayapy else None,
        dry_run=dry_run,
        render_preview=render_preview,
        render_width=width,
        render_height=height,
    )


def validate_run_options(options: ArtistAppOptions) -> list[str]:
    """Return Vietnamese validation errors without touching the file system."""

    errors: list[str] = []
    if str(options.svg_path).strip() in {"", "."}:
        errors.append(SVG_EMPTY_ERROR)
    elif options.svg_path.suffix.lower() != ".svg":
        errors.append("Input phải là file .svg sạch.")

    if not options.room_name.strip():
        errors.append(ROOM_EMPTY_ERROR)

    if _is_empty_path(options.output_dir):
        errors.append(OUTPUT_EMPTY_ERROR)

    if options.render_width <= 0 or options.render_height <= 0:
        errors.append("Kích thước render phải là số dương.")

    if not options.dry_run and options.maya_path is None:
        errors.append(MAYAPY_REQUIRED_ERROR)

    return errors


def validate_run_paths(options: ArtistAppOptions, *, root: Path) -> list[str]:
    """Return Vietnamese validation errors for files needed before subprocess launch."""

    errors: list[str] = []
    if not _is_empty_path(options.svg_path):
        svg_path = resolve_repo_relative_path(options.svg_path, root)
        if not svg_path.is_file():
            errors.append(SVG_NOT_FOUND_ERROR)

    if not build_script_path(root).is_file():
        errors.append(BUILD_SCRIPT_MISSING_ERROR)

    if (
        not options.dry_run
        and options.maya_path is not None
        and not options.maya_path.is_file()
    ):
        errors.append(MAYAPY_NOT_FOUND_ERROR)

    return errors


def validate_runtime_environment(*, root: Path | None = None) -> list[str]:
    """Return Vietnamese validation errors for repo and Python runtime discovery."""

    errors: list[str] = []
    detected_root = root or find_repo_root()
    if detected_root is None:
        errors.append(REPO_ROOT_ERROR)
    elif not build_script_path(detected_root).is_file():
        errors.append(BUILD_SCRIPT_MISSING_ERROR)

    if getattr(sys, "frozen", False) and pipeline_python_command_prefix() is None:
        errors.append(PIPELINE_PYTHON_ERROR)

    return errors


def build_maya_room_command(
    options: ArtistAppOptions,
    *,
    python_executable: str | None = None,
    python_command_prefix: list[str] | None = None,
    root: Path | None = None,
) -> list[str]:
    """Build the exact CLI command for the existing Maya pipeline."""

    root = root or repo_root()
    prefix = python_command_prefix or pipeline_python_command_prefix(
        python_executable=python_executable
    )
    if prefix is None:
        raise RuntimeError(PIPELINE_PYTHON_ERROR)

    command = [
        *prefix,
        str(build_script_path(root)),
        "--input",
        str(options.svg_path),
        "--room",
        options.room_name,
        "--output-dir",
        str(options.output_dir),
    ]
    if options.dry_run:
        command.append("--dry-run")
    if options.render_preview:
        command.extend(
            [
                "--render-preview",
                "--render-width",
                str(options.render_width),
                "--render-height",
                str(options.render_height),
            ]
        )
    if not options.dry_run and options.maya_path is not None:
        command.extend(["--maya-path", str(options.maya_path)])
    return command


def command_to_display(command: list[str]) -> str:
    """Return a Windows-friendly command string for the log area."""

    return subprocess.list2cmdline(command)


def output_subdir_path(output_dir: Path, subdir_key: str) -> Path:
    """Build an output subfolder path without creating, deleting, or moving files."""

    if subdir_key not in OUTPUT_SUBDIRS:
        raise ValueError(f"Unknown output folder: {subdir_key}")
    return output_dir / OUTPUT_SUBDIRS[subdir_key]


class ArtistDesktopApp:
    """Tkinter UI for the local artist app."""

    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext, ttk

        self.tk = tk
        self.filedialog = filedialog
        self.messagebox = messagebox
        self.ttk = ttk
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("900x680")
        self.root.minsize(780, 560)
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None

        self.svg_var = tk.StringVar()
        self.room_var = tk.StringVar(value=DEFAULT_ROOM_NAME)
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.mayapy_var = tk.StringVar(value=default_mayapy_path())
        self.dry_run_var = tk.BooleanVar(value=True)
        self.render_var = tk.BooleanVar(value=False)
        self.width_var = tk.StringVar(value=str(DEFAULT_RENDER_WIDTH))
        self.height_var = tk.StringVar(value=str(DEFAULT_RENDER_HEIGHT))
        self.repo_root_var = tk.StringVar(value=repo_root_display_value())
        self.status_var = tk.StringVar(value=STATUS_READY)
        self.command_var = tk.StringVar(value="")

        self._build_ui(scrolledtext)
        self.root.after(100, self._drain_log_queue)

    def _build_ui(self, scrolledtext_module) -> None:
        tk = self.tk
        ttk = self.ttk

        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(12, weight=1)

        ttk.Label(outer, text="File SVG sạch").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(outer, textvariable=self.svg_var).grid(row=0, column=1, sticky=tk.EW, pady=4)
        ttk.Button(outer, text="Chọn SVG", command=self._choose_svg).grid(
            row=0, column=2, padx=(8, 0), pady=4
        )

        ttk.Label(outer, text="Tên phòng/layer").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(outer, textvariable=self.room_var).grid(row=1, column=1, sticky=tk.EW, pady=4)

        ttk.Label(outer, text="Thư mục output").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(outer, textvariable=self.output_var).grid(row=2, column=1, sticky=tk.EW, pady=4)
        ttk.Button(outer, text="Chọn thư mục", command=self._choose_output_dir).grid(
            row=2, column=2, padx=(8, 0), pady=4
        )

        ttk.Label(outer, text="mayapy.exe").grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(outer, textvariable=self.mayapy_var).grid(row=3, column=1, sticky=tk.EW, pady=4)
        ttk.Button(outer, text="Chọn mayapy", command=self._choose_mayapy).grid(
            row=3, column=2, padx=(8, 0), pady=4
        )

        ttk.Label(outer, text="Repo root").grid(row=4, column=0, sticky=tk.W, pady=4)
        ttk.Entry(outer, textvariable=self.repo_root_var, state="readonly").grid(
            row=4, column=1, columnspan=2, sticky=tk.EW, pady=4
        )

        checks = ttk.Frame(outer)
        checks.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(8, 2))
        ttk.Checkbutton(checks, text="Dry-run", variable=self.dry_run_var).pack(
            side=tk.LEFT, padx=(0, 18)
        )
        ttk.Checkbutton(checks, text="Render PNG preview", variable=self.render_var).pack(
            side=tk.LEFT
        )

        render_frame = ttk.Frame(outer)
        render_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=4)
        ttk.Label(render_frame, text="Render width").pack(side=tk.LEFT)
        ttk.Entry(render_frame, textvariable=self.width_var, width=8).pack(
            side=tk.LEFT, padx=(6, 16)
        )
        ttk.Label(render_frame, text="Render height").pack(side=tk.LEFT)
        ttk.Entry(render_frame, textvariable=self.height_var, width=8).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        buttons = ttk.Frame(outer)
        buttons.grid(row=7, column=0, columnspan=3, sticky=tk.EW, pady=(10, 4))
        self.run_button = ttk.Button(buttons, text="Chạy pipeline", command=self._run_clicked)
        self.run_button.pack(side=tk.LEFT)
        ttk.Button(buttons, text="Xóa log", command=self._clear_log).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )
        ttk.Button(buttons, text="Copy lệnh", command=self._copy_command).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )
        ttk.Button(
            buttons,
            text="Mở outputs/maya",
            command=lambda: self._open_output("maya"),
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            buttons,
            text="Mở outputs/preview",
            command=lambda: self._open_output("preview"),
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )
        ttk.Button(
            buttons,
            text="Mở outputs/reports",
            command=lambda: self._open_output("reports"),
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(buttons, text="Mở repo", command=self._open_repo).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        ttk.Label(outer, text="Trạng thái").grid(row=8, column=0, sticky=tk.W, pady=(8, 2))
        ttk.Label(outer, textvariable=self.status_var).grid(
            row=8,
            column=1,
            columnspan=2,
            sticky=tk.W,
            pady=(8, 2),
        )

        ttk.Label(outer, text="Lệnh").grid(row=9, column=0, sticky=tk.W, pady=4)
        ttk.Entry(outer, textvariable=self.command_var, state="readonly").grid(
            row=9,
            column=1,
            columnspan=2,
            sticky=tk.EW,
            pady=4,
        )

        ttk.Label(outer, text="Log").grid(row=11, column=0, sticky=tk.W, pady=(10, 2))
        self.log_text = scrolledtext_module.ScrolledText(outer, height=20, wrap=tk.WORD)
        self.log_text.grid(row=12, column=0, columnspan=3, sticky=tk.NSEW)

    def run(self) -> None:
        self.root.mainloop()

    def _choose_svg(self) -> None:
        path = self.filedialog.askopenfilename(
            title="Chọn file SVG sạch",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
        )
        if path:
            self.svg_var.set(path)

    def _choose_output_dir(self) -> None:
        path = self.filedialog.askdirectory(title="Chọn thư mục output")
        if path:
            self.output_var.set(path)

    def _choose_mayapy(self) -> None:
        path = self.filedialog.askopenfilename(
            title="Chọn mayapy.exe",
            filetypes=[("mayapy.exe", "mayapy.exe"), ("Executable", "*.exe"), ("All files", "*.*")],
        )
        if path:
            self.mayapy_var.set(path)

    def _current_options(self) -> ArtistAppOptions:
        return options_from_strings(
            svg_path=self.svg_var.get(),
            room_name=self.room_var.get(),
            output_dir=self.output_var.get(),
            maya_path=self.mayapy_var.get(),
            dry_run=self.dry_run_var.get(),
            render_preview=self.render_var.get(),
            render_width=self.width_var.get(),
            render_height=self.height_var.get(),
        )

    def _run_clicked(self) -> None:
        if self.worker and self.worker.is_alive():
            self.messagebox.showinfo(
                "Đang chạy",
                "Pipeline đang chạy, hãy đợi log kết thúc.",
            )
            return
        try:
            options = self._current_options()
        except ValueError:
            self.messagebox.showerror(
                "Lỗi",
                "Render width/height phải là số nguyên dương.",
            )
            return

        root = find_repo_root()
        self.repo_root_var.set(repo_root_display_value(root))
        errors = validate_run_options(options) + validate_runtime_environment(root=root)
        if root is not None:
            errors.extend(validate_run_paths(options, root=root))
        if errors:
            self.messagebox.showerror("Cần kiểm tra lại", "\n".join(errors))
            return

        try:
            if root is None:
                raise RuntimeError(REPO_ROOT_ERROR)
            command = build_maya_room_command(options, root=root)
        except RuntimeError as exc:
            self.messagebox.showerror("Cần kiểm tra lại", str(exc))
            return
        display_command = command_to_display(command)
        self.command_var.set(display_command)
        self._append_log("\n=== Lệnh sẽ chạy ===\n")
        self._append_log(f"Repo root: {root}\n")
        self._append_log(display_command + "\n\n")
        self.status_var.set(STATUS_RUNNING)
        self.run_button.configure(state=self.tk.DISABLED)
        self.worker = threading.Thread(target=self._run_subprocess, args=(command, root), daemon=True)
        self.worker.start()

    def _run_subprocess(self, command: list[str], root: Path) -> None:
        try:
            process = subprocess.Popen(
                command,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert process.stdout is not None
            for line in process.stdout:
                self.log_queue.put(line)
            return_code = process.wait()
            self.log_queue.put(f"\nExit code: {return_code}\n")
        except OSError as exc:
            return_code = -1
            self.log_queue.put(f"\nLỗi khi chạy pipeline: {exc}\n")
        finally:
            self.log_queue.put(f"{RUN_FINISHED_PREFIX}{return_code}")

    def _drain_log_queue(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if message.startswith(RUN_FINISHED_PREFIX):
                return_code = int(message.removeprefix(RUN_FINISHED_PREFIX))
                self.run_button.configure(state=self.tk.NORMAL)
                if return_code == 0:
                    self.status_var.set("Hoàn tất: mã 0")
                else:
                    self.status_var.set(f"Lỗi: mã {return_code}")
            else:
                self._append_log(message)
        self.root.after(100, self._drain_log_queue)

    def _append_log(self, text: str) -> None:
        self.log_text.insert(self.tk.END, text)
        self.log_text.see(self.tk.END)

    def _clear_log(self) -> None:
        self.log_text.delete("1.0", self.tk.END)

    def _copy_command(self) -> None:
        command = self.command_var.get()
        if not command:
            self.messagebox.showinfo("Chưa có lệnh", "Chưa có lệnh để copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(command)

    def _open_output(self, subdir_key: str) -> None:
        output_root = Path(self.output_var.get() or DEFAULT_OUTPUT_DIR)
        try:
            root = repo_root()
        except RuntimeError as exc:
            self.messagebox.showerror("Cần kiểm tra lại", str(exc))
            return
        output_root = resolve_output_root(output_root, root)
        path = output_subdir_path(output_root, subdir_key)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.messagebox.showerror("Không mở được thư mục", str(exc))
            return
        self._open_folder(path)

    def _open_repo(self) -> None:
        try:
            self._open_folder(repo_root())
        except RuntimeError as exc:
            self.messagebox.showerror("Cần kiểm tra lại", str(exc))

    def _open_folder(self, path: Path) -> None:
        resolved = path.resolve()
        if not resolved.exists():
            self.messagebox.showwarning("Chưa có thư mục", f"Không tìm thấy:\n{resolved}")
            return
        os.startfile(str(resolved))  # type: ignore[attr-defined]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mở desktop app MVP để chạy Maya-first pipeline cho họa sĩ."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    build_parser().parse_args(argv)
    try:
        ArtistDesktopApp().run()
    except ImportError as exc:
        print(f"Lỗi: Không mở được Tkinter desktop app: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
