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
import webbrowser
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

APP_VERSION = "0.7.10"
APP_PHASE = "007L"
APP_TITLE_BASE = "TuPhuongVoLo - Maya Artist App"
APP_TITLE = f"{APP_TITLE_BASE} v{APP_VERSION} ({APP_PHASE})"

# ── Artist theme palette ─────────────────────────────────────────────────────
THEME_BG = "#FFF8F0"          # warm cream / very light peach
THEME_CARD = "#FFFCF8"        # soft off-white section background
THEME_ACCENT = "#E8845A"      # warm terracotta-orange accent
THEME_ACCENT_DARK = "#C0623A" # pressed accent
THEME_SECONDARY = "#D4A0C0"   # soft dusty rose for secondary buttons
THEME_SECONDARY_DARK = "#B5809E"
THEME_TEXT = "#3D2B1F"        # dark warm brown
THEME_HINT = "#7A8C6A"        # muted sage green for helper labels
THEME_BORDER = "#D9C4B5"      # warm border
THEME_FONT_BODY = ("Segoe UI", 9)
THEME_FONT_LABEL = ("Segoe UI", 9)
THEME_FONT_HINT = ("Segoe UI", 8)
THEME_FONT_HEADER = ("Segoe UI", 14, "bold")
THEME_FONT_SUBTITLE = ("Segoe UI", 9)
THEME_FONT_TIP = ("Segoe UI", 8, "italic")
# ── Style name constants (importable for tests) ──────────────────────────────
STYLE_PRIMARY_BUTTON = "Primary.TButton"
STYLE_ACCENT_BUTTON = "Accent.TButton"
STYLE_SECONDARY_BUTTON = "Secondary.TButton"
STYLE_UTILITY_BUTTON = "Utility.TButton"
STYLE_GUIDE_BUTTON = "Guide.TButton"
DEFAULT_ROOM_NAME = "phong_kho"
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_AI_OUTPUT_DIR = Path("outputs") / "ai_preview"
DEFAULT_MAYAPY_PATH = r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
DEFAULT_RENDER_WIDTH = 1280
DEFAULT_RENDER_HEIGHT = 720
DEFAULT_AI_PROVIDER = "mock"
AI_PROVIDER_MOCK = "mock"
AI_PROVIDER_FAL = "fal"
AI_PROVIDERS = (AI_PROVIDER_MOCK, AI_PROVIDER_FAL)
DEFAULT_AI_MODEL = "fal-ai/flux-pro/kontext"
DEFAULT_AI_PROMPT_PRESET = "tropical-island-room"
STATUS_READY = "Sẵn sàng"
STATUS_RUNNING = "Đang chạy..."
RUN_FINISHED_PREFIX = "__RUN_FINISHED__:"
AI_RUN_FINISHED_PREFIX = "__AI_RUN_FINISHED__:"
PREFLIGHT_RUN_FINISHED_PREFIX = "__PREFLIGHT_RUN_FINISHED__:"
SVG_EMPTY_ERROR = "Chưa chọn file SVG."
SVG_NOT_FOUND_ERROR = "Không tìm thấy file SVG. Hãy kiểm tra lại đường dẫn."
ROOM_EMPTY_ERROR = "Chưa nhập tên phòng/layer."
OUTPUT_EMPTY_ERROR = "Chưa chọn thư mục output."
BUILD_SCRIPT_MISSING_ERROR = "Không tìm thấy build_maya_room.py trong repo."
AI_INPUT_EMPTY_ERROR = "Chưa chọn file PNG preview cho AI."
AI_INPUT_NOT_FOUND_ERROR = "Không tìm thấy file PNG preview. Hãy kiểm tra lại đường dẫn."
AI_INPUT_NOT_PNG_ERROR = "Input AI phải là file .png preview."
AI_SCRIPT_MISSING_ERROR = "Không tìm thấy ai_polish_preview.py trong repo."
PREFLIGHT_SCRIPT_MISSING_ERROR = "Không tìm thấy svg_preflight_check.py trong repo."
AI_PROVIDER_ERROR = "Provider AI phải là mock hoặc fal."
MAYAPY_REQUIRED_ERROR = "Chạy thật cần đường dẫn mayapy.exe hợp lệ."
MAYAPY_NOT_FOUND_ERROR = "Không tìm thấy mayapy.exe. Hãy kiểm tra lại đường dẫn."
DRY_RUN_REQUIRED_ERROR = (
    "Chưa chạy thử an toàn thành công cho SVG/phòng/output/render hiện tại. "
    "Hãy bấm 'Chạy thử an toàn' trước khi dựng Maya thật."
)
OUTPUT_SUBDIRS = {
    "maya": "maya",
    "preview": "preview",
    "reports": "reports",
    "ai_preview": "ai_preview",
}
BUILD_SCRIPT_RELATIVE_PATH = Path("scripts") / "python" / "build_maya_room.py"
AI_SCRIPT_RELATIVE_PATH = Path("scripts") / "python" / "ai_polish_preview.py"
PREFLIGHT_SCRIPT_RELATIVE_PATH = Path("scripts") / "python" / "svg_preflight_check.py"
ARTIST_GUIDE_RELATIVE_PATH = Path("docs") / "artist_workflow_cat_guide_vi.html"
PROP_MARKER_TEMPLATE_RELATIVE_PATH = (
    Path("assets") / "2d" / "templates" / "illustrator_prop_marker_template.svg"
)
PROP_MARKER_TEMPLATE_DIR_RELATIVE_PATH = Path("assets") / "2d" / "templates"
REPO_MARKER_RELATIVE_PATHS = (
    BUILD_SCRIPT_RELATIVE_PATH,
    AI_SCRIPT_RELATIVE_PATH,
    PREFLIGHT_SCRIPT_RELATIVE_PATH,
)
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
GUIDE_MISSING_ERROR = "Không tìm thấy hướng dẫn HTML cho họa sĩ."
TEMPLATE_MISSING_ERROR = "Không tìm thấy SVG mẫu marker prop."
TEMPLATE_DIR_MISSING_ERROR = "Không tìm thấy thư mục template SVG."
OS_OPEN_ERROR = "Hệ điều hành không mở được file hoặc thư mục này."


def app_version_display() -> str:
    """Return the version label shown in CLI output and the desktop UI."""

    return f"TuPhuongVoLo Maya Artist App v{APP_VERSION} ({APP_PHASE})"


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


@dataclass(frozen=True)
class ArtistAiPreviewOptions:
    """User inputs needed to run the optional AI polish preview CLI."""

    input_png_path: Path
    provider: str = DEFAULT_AI_PROVIDER
    output_dir: Path = DEFAULT_AI_OUTPUT_DIR
    model: str = DEFAULT_AI_MODEL
    prompt_preset: str = DEFAULT_AI_PROMPT_PRESET
    prompt: str = ""
    skip_on_missing_config: bool = True
    dry_run: bool = True


@dataclass(frozen=True)
class ArtistPreflightOptions:
    """User inputs needed to run the SVG preflight CLI."""

    svg_path: Path
    json_output: Path | None = None


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
        if any((candidate / marker).is_file() for marker in REPO_MARKER_RELATIVE_PATHS):
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


def ai_script_path(root: Path | None = None) -> Path:
    """Return the optional AI polish preview CLI path."""

    return (root or repo_root()) / AI_SCRIPT_RELATIVE_PATH


def preflight_script_path(root: Path | None = None) -> Path:
    """Return the SVG preflight CLI path."""

    return (root or repo_root()) / PREFLIGHT_SCRIPT_RELATIVE_PATH


def artist_guide_path(root: Path | None = None) -> Path:
    """Return the main artist-facing HTML guide path."""

    return (root or repo_root()) / ARTIST_GUIDE_RELATIVE_PATH


def prop_marker_template_path(root: Path | None = None) -> Path:
    """Return the Illustrator prop marker template SVG path."""

    return (root or repo_root()) / PROP_MARKER_TEMPLATE_RELATIVE_PATH


def prop_marker_template_dir(root: Path | None = None) -> Path:
    """Return the Illustrator template folder path."""

    return (root or repo_root()) / PROP_MARKER_TEMPLATE_DIR_RELATIVE_PATH


def _open_with_startfile(path: Path) -> None:
    os.startfile(str(path.resolve()))  # type: ignore[attr-defined]


def open_artist_guide(
    root: Path | None = None,
    *,
    opener=None,
) -> Path:
    """Open the HTML guide in the default browser and return the target path."""

    path = artist_guide_path(root)
    if not path.is_file():
        raise FileNotFoundError(GUIDE_MISSING_ERROR)
    selected_opener = opener or webbrowser.open
    try:
        selected_opener(path.resolve().as_uri())
    except OSError as exc:
        raise RuntimeError(f"{OS_OPEN_ERROR} {path}") from exc
    return path


def open_prop_marker_template(
    root: Path | None = None,
    *,
    opener=None,
) -> Path:
    """Open the SVG marker template with the OS default app."""

    path = prop_marker_template_path(root)
    if not path.is_file():
        raise FileNotFoundError(TEMPLATE_MISSING_ERROR)
    selected_opener = opener or _open_with_startfile
    try:
        selected_opener(path)
    except OSError as exc:
        raise RuntimeError(f"{OS_OPEN_ERROR} {path}") from exc
    return path


def open_prop_marker_template_dir(
    root: Path | None = None,
    *,
    opener=None,
) -> Path:
    """Open the folder that contains Illustrator SVG marker templates."""

    path = prop_marker_template_dir(root)
    if not path.is_dir():
        raise FileNotFoundError(TEMPLATE_DIR_MISSING_ERROR)
    selected_opener = opener or _open_with_startfile
    try:
        selected_opener(path)
    except OSError as exc:
        raise RuntimeError(f"{OS_OPEN_ERROR} {path}") from exc
    return path


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


def configure_artist_theme(style) -> None:
    """Apply the cat-themed pastel ttk.Style to the desktop app.

    Uses only built-in Tkinter/ttk; no external assets, fonts, or CDN.
    Must be called after the Tk root and ttk.Style are initialised.
    """
    style.theme_use("clam")

    # Base widget colours
    style.configure(
        ".",
        background=THEME_BG,
        foreground=THEME_TEXT,
        font=THEME_FONT_BODY,
        fieldbackground=THEME_CARD,
        bordercolor=THEME_BORDER,
        troughcolor=THEME_BORDER,
    )

    # Frames
    style.configure("TFrame", background=THEME_BG)
    style.configure("TLabelframe", background=THEME_BG, bordercolor=THEME_BORDER)
    style.configure(
        "TLabelframe.Label",
        background=THEME_BG,
        foreground=THEME_ACCENT,
        font=("Segoe UI", 9, "bold"),
    )

    # Labels
    style.configure("TLabel", background=THEME_BG, foreground=THEME_TEXT)
    style.configure(
        "Hint.TLabel",
        background=THEME_BG,
        foreground=THEME_HINT,
        font=THEME_FONT_HINT,
    )
    style.configure(
        "Header.TLabel",
        background=THEME_BG,
        foreground=THEME_TEXT,
        font=THEME_FONT_HEADER,
    )
    style.configure(
        "Subtitle.TLabel",
        background=THEME_BG,
        foreground=THEME_TEXT,
        font=THEME_FONT_SUBTITLE,
    )
    style.configure(
        "Tip.TLabel",
        background=THEME_BG,
        foreground=THEME_HINT,
        font=THEME_FONT_TIP,
    )

    # Checkbutton / Combobox
    style.configure("TCheckbutton", background=THEME_BG, foreground=THEME_TEXT)
    style.configure("TCombobox", fieldbackground=THEME_CARD, foreground=THEME_TEXT)

    # Entry
    style.configure("TEntry", fieldbackground=THEME_CARD, foreground=THEME_TEXT)

    # Primary button — Chạy pipeline / Tạo AI polish preview
    # Most visible: terracotta/orange, bold, white text.
    style.configure(
        STYLE_PRIMARY_BUTTON,
        background=THEME_ACCENT,
        foreground="#FFFFFF",
        font=("Segoe UI", 9, "bold"),
        padding=(10, 5),
        relief="raised",
        borderwidth=2,
    )
    style.map(
        STYLE_PRIMARY_BUTTON,
        background=[
            ("active", THEME_ACCENT_DARK),
            ("pressed", THEME_ACCENT_DARK),
            ("disabled", THEME_BORDER),
        ],
        foreground=[
            ("disabled", "#AAAAAA"),
        ],
        relief=[
            ("pressed", "sunken"),
        ],
    )

    # Guide button — Mở hướng dẫn / Mở SVG mẫu marker
    # Friendly dusty rose; used for guide/template shortcuts.
    THEME_GUIDE = "#D4879A"       # deeper rose for guide buttons
    THEME_GUIDE_DARK = "#B86878"  # pressed guide
    style.configure(
        STYLE_GUIDE_BUTTON,
        background="#E8A0B0",
        foreground=THEME_TEXT,
        font=("Segoe UI", 9, "bold"),
        padding=(8, 4),
        relief="raised",
        borderwidth=2,
    )
    style.map(
        STYLE_GUIDE_BUTTON,
        background=[
            ("active", THEME_GUIDE),
            ("pressed", THEME_GUIDE_DARK),
        ],
        relief=[
            ("pressed", "sunken"),
        ],
    )

    # Accent button — alias for Guide.TButton for backwards compat
    style.configure(
        STYLE_ACCENT_BUTTON,
        background="#E8A0B0",
        foreground=THEME_TEXT,
        font=("Segoe UI", 9, "bold"),
        padding=(8, 4),
        relief="raised",
        borderwidth=2,
    )
    style.map(
        STYLE_ACCENT_BUTTON,
        background=[
            ("active", THEME_GUIDE),
            ("pressed", THEME_GUIDE_DARK),
        ],
        relief=[
            ("pressed", "sunken"),
        ],
    )

    # Utility button — small helper actions (Xóa log, Copy lệnh, Mở outputs/…)
    # Warm peach/beige so it is clearly NOT plain white.
    style.configure(
        STYLE_UTILITY_BUTTON,
        background="#F5C8A0",
        foreground=THEME_TEXT,
        font=THEME_FONT_BODY,
        padding=(6, 3),
        relief="raised",
        borderwidth=1,
    )
    style.map(
        STYLE_UTILITY_BUTTON,
        background=[
            ("active", "#E0A870"),
            ("pressed", "#C88050"),
        ],
        foreground=[
            ("pressed", "#FFFFFF"),
        ],
        relief=[
            ("pressed", "sunken"),
        ],
    )

    # Secondary button — kept for backwards compat; same appearance as Utility
    style.configure(
        STYLE_SECONDARY_BUTTON,
        background="#F5C8A0",
        foreground=THEME_TEXT,
        font=THEME_FONT_BODY,
        padding=(6, 3),
        relief="raised",
        borderwidth=1,
    )
    style.map(
        STYLE_SECONDARY_BUTTON,
        background=[
            ("active", "#E0A870"),
            ("pressed", "#C88050"),
        ],
        foreground=[
            ("pressed", "#FFFFFF"),
        ],
        relief=[
            ("pressed", "sunken"),
        ],
    )


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


def ai_options_from_strings(
    *,
    input_png_path: str,
    provider: str,
    model: str,
    prompt_preset: str,
    prompt: str,
    skip_on_missing_config: bool,
    dry_run: bool,
    output_dir: str | Path = DEFAULT_AI_OUTPUT_DIR,
) -> ArtistAiPreviewOptions:
    """Create AI preview option values from UI strings."""

    selected_output_dir = (
        output_dir if isinstance(output_dir, Path) else Path(_clean_text(output_dir))
    )
    return ArtistAiPreviewOptions(
        input_png_path=Path(_clean_text(input_png_path)),
        provider=_clean_text(provider) or DEFAULT_AI_PROVIDER,
        output_dir=selected_output_dir,
        model=_clean_text(model) or DEFAULT_AI_MODEL,
        prompt_preset=_clean_text(prompt_preset) or DEFAULT_AI_PROMPT_PRESET,
        prompt=_clean_text(prompt),
        skip_on_missing_config=skip_on_missing_config,
        dry_run=dry_run,
    )


def default_preflight_report_path(output_dir: Path) -> Path:
    """Return the default JSON report path for guided SVG preflight."""

    return output_dir / OUTPUT_SUBDIRS["reports"] / "svg_preflight_report.json"


def preflight_options_from_strings(
    *,
    svg_path: str,
    output_dir: str,
) -> ArtistPreflightOptions:
    """Create SVG preflight option values from UI strings."""

    selected_output_dir = Path(_clean_text(output_dir) or DEFAULT_OUTPUT_DIR)
    return ArtistPreflightOptions(
        svg_path=Path(_clean_text(svg_path)),
        json_output=default_preflight_report_path(selected_output_dir),
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


def validate_ai_preview_options(options: ArtistAiPreviewOptions) -> list[str]:
    """Return Vietnamese validation errors for AI preview inputs."""

    errors: list[str] = []
    if _is_empty_path(options.input_png_path):
        errors.append(AI_INPUT_EMPTY_ERROR)
    elif options.input_png_path.suffix.lower() != ".png":
        errors.append(AI_INPUT_NOT_PNG_ERROR)

    if options.provider not in AI_PROVIDERS:
        errors.append(AI_PROVIDER_ERROR)

    if _is_empty_path(options.output_dir):
        errors.append(OUTPUT_EMPTY_ERROR)

    return errors


def validate_ai_preview_paths(options: ArtistAiPreviewOptions, *, root: Path) -> list[str]:
    """Return Vietnamese validation errors for files needed by the AI subprocess."""

    errors: list[str] = []
    if not _is_empty_path(options.input_png_path):
        input_path = resolve_repo_relative_path(options.input_png_path, root)
        if not input_path.is_file():
            errors.append(AI_INPUT_NOT_FOUND_ERROR)

    if not ai_script_path(root).is_file():
        errors.append(AI_SCRIPT_MISSING_ERROR)

    return errors


def validate_preflight_options(options: ArtistPreflightOptions) -> list[str]:
    """Return Vietnamese validation errors for SVG preflight inputs."""

    errors: list[str] = []
    if _is_empty_path(options.svg_path):
        errors.append(SVG_EMPTY_ERROR)
    elif options.svg_path.suffix.lower() != ".svg":
        errors.append("Input phải là file .svg sạch.")
    return errors


def validate_preflight_paths(options: ArtistPreflightOptions, *, root: Path) -> list[str]:
    """Return Vietnamese validation errors for files needed by preflight."""

    errors: list[str] = []
    if not _is_empty_path(options.svg_path):
        svg_path = resolve_repo_relative_path(options.svg_path, root)
        if not svg_path.is_file():
            errors.append(SVG_NOT_FOUND_ERROR)

    if not preflight_script_path(root).is_file():
        errors.append(PREFLIGHT_SCRIPT_MISSING_ERROR)

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


def validate_ai_runtime_environment(*, root: Path | None = None) -> list[str]:
    """Return Vietnamese validation errors for repo and Python runtime discovery for AI."""

    errors: list[str] = []
    detected_root = root or find_repo_root()
    if detected_root is None:
        errors.append(REPO_ROOT_ERROR)
    elif not ai_script_path(detected_root).is_file():
        errors.append(AI_SCRIPT_MISSING_ERROR)

    if getattr(sys, "frozen", False) and pipeline_python_command_prefix() is None:
        errors.append(PIPELINE_PYTHON_ERROR)

    return errors


def validate_preflight_runtime_environment(*, root: Path | None = None) -> list[str]:
    """Return Vietnamese validation errors for SVG preflight runtime discovery."""

    errors: list[str] = []
    detected_root = root or find_repo_root()
    if detected_root is None:
        errors.append(REPO_ROOT_ERROR)
    elif not preflight_script_path(detected_root).is_file():
        errors.append(PREFLIGHT_SCRIPT_MISSING_ERROR)

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


def build_ai_preview_command(
    options: ArtistAiPreviewOptions,
    *,
    python_executable: str | None = None,
    python_command_prefix: list[str] | None = None,
    root: Path | None = None,
) -> list[str]:
    """Build the exact CLI command for the optional AI polish preview."""

    root = root or repo_root()
    prefix = python_command_prefix or pipeline_python_command_prefix(
        python_executable=python_executable
    )
    if prefix is None:
        raise RuntimeError(PIPELINE_PYTHON_ERROR)

    command = [
        *prefix,
        str(ai_script_path(root)),
        "--provider",
        options.provider,
        "--input",
        str(options.input_png_path),
        "--output-dir",
        str(options.output_dir),
        "--prompt-preset",
        options.prompt_preset,
    ]
    if options.provider == AI_PROVIDER_FAL:
        command.extend(["--model", options.model])
        if options.skip_on_missing_config:
            command.append("--skip-on-missing-config")
    if options.prompt:
        command.extend(["--prompt", options.prompt])
    if options.dry_run:
        command.append("--dry-run")
    return command


def build_svg_preflight_command(
    options: ArtistPreflightOptions,
    *,
    python_executable: str | None = None,
    python_command_prefix: list[str] | None = None,
    root: Path | None = None,
) -> list[str]:
    """Build the exact CLI command for the SVG preflight checker."""

    root = root or repo_root()
    prefix = python_command_prefix or pipeline_python_command_prefix(
        python_executable=python_executable
    )
    if prefix is None:
        raise RuntimeError(PIPELINE_PYTHON_ERROR)

    command = [
        *prefix,
        str(preflight_script_path(root)),
        "--input",
        str(options.svg_path),
    ]
    if options.json_output is not None:
        command.extend(["--json-output", str(options.json_output)])
    return command


def dry_run_settings_key(options: ArtistAppOptions, *, root: Path) -> tuple[str, str, str, bool, int, int]:
    """Return the settings fingerprint that must match before actual Maya run."""

    svg_path = resolve_repo_relative_path(options.svg_path, root).resolve()
    output_root = resolve_output_root(options.output_dir, root).resolve()
    return (
        str(svg_path).lower(),
        options.room_name.strip().lower(),
        str(output_root).lower(),
        options.render_preview,
        options.render_width,
        options.render_height,
    )


def dry_run_matches_current_settings(
    successful_dry_run_key: tuple[str, str, str, bool, int, int] | None,
    options: ArtistAppOptions,
    *,
    root: Path,
) -> bool:
    """Return whether the current actual run is covered by a successful dry-run."""

    if successful_dry_run_key is None:
        return False
    return successful_dry_run_key == dry_run_settings_key(options, root=root)


def command_to_display(command: list[str]) -> str:
    """Return a Windows-friendly command string for the log area."""

    return subprocess.list2cmdline(command)


def output_subdir_path(output_dir: Path, subdir_key: str) -> Path:
    """Build an output subfolder path without creating, deleting, or moving files."""

    if subdir_key not in OUTPUT_SUBDIRS:
        raise ValueError(f"Unknown output folder: {subdir_key}")
    return output_dir / OUTPUT_SUBDIRS[subdir_key]


def ai_output_dir_path(root: Path) -> Path:
    """Return the default AI preview output folder under the repository."""

    return root / DEFAULT_AI_OUTPUT_DIR


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
        self.root.configure(bg=THEME_BG)
        self.root.geometry("980x860")
        self.root.minsize(860, 700)

        # Apply cat-themed artist style
        style = ttk.Style(self.root)
        configure_artist_theme(style)
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.ai_worker: threading.Thread | None = None
        self.preflight_worker: threading.Thread | None = None
        self.active_maya_options: ArtistAppOptions | None = None
        self.active_maya_root: Path | None = None
        self.successful_dry_run_key: tuple[str, str, str, bool, int, int] | None = None

        self.svg_var = tk.StringVar()
        self.room_var = tk.StringVar(value=DEFAULT_ROOM_NAME)
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.mayapy_var = tk.StringVar(value=default_mayapy_path())
        self.dry_run_var = tk.BooleanVar(value=True)
        self.render_var = tk.BooleanVar(value=False)
        self.width_var = tk.StringVar(value=str(DEFAULT_RENDER_WIDTH))
        self.height_var = tk.StringVar(value=str(DEFAULT_RENDER_HEIGHT))
        self.repo_root_var = tk.StringVar(value=repo_root_display_value())
        self.svg_status_var = tk.StringVar(value="Chưa kiểm tra")
        self.status_var = tk.StringVar(value=STATUS_READY)
        self.workflow_status_var = tk.StringVar(
            value="Luồng khuyến nghị: Chọn SVG (1) → Kiểm tra SVG (2) → Chạy thử an toàn (3) → Dựng Maya thật (4) → Mở kết quả (5)."
        )
        self.command_var = tk.StringVar(value="")
        self.ai_png_var = tk.StringVar()
        self.ai_provider_var = tk.StringVar(value=DEFAULT_AI_PROVIDER)
        self.ai_model_var = tk.StringVar(value=DEFAULT_AI_MODEL)
        self.ai_prompt_preset_var = tk.StringVar(value=DEFAULT_AI_PROMPT_PRESET)
        self.ai_prompt_var = tk.StringVar()
        self.ai_skip_missing_var = tk.BooleanVar(value=True)
        self.ai_dry_run_var = tk.BooleanVar(value=True)
        self.ai_status_var = tk.StringVar(value=STATUS_READY)
        self.ai_command_var = tk.StringVar(value="")

        self._build_ui(scrolledtext)
        self.root.after(100, self._drain_log_queue)

    def _build_ui(self, scrolledtext_module) -> None:  # noqa: PLR0915
        tk = self.tk
        ttk = self.ttk

        # ── Scrollable Container Setup ────────────────────────────────────────
        canvas = tk.Canvas(self.root, bg=THEME_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=12)
        scrollable_frame.columnconfigure(0, weight=1)

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollable_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _configure_canvas)

        def _on_mousewheel(event):
            if hasattr(self, "log_text"):
                w = event.widget
                while w:
                    if w == self.log_text:
                        return
                    try:
                        w = w.master
                    except AttributeError:
                        break
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── Cat-themed header ────────────────────────────────────────────────
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, 6))
        ttk.Label(
            header_frame,
            text="🐱 Tứ Phương Vô Lộ — Maya Artist App",
            style="Header.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(
            header_frame,
            text="Vẽ SVG trong Illustrator → kiểm tra dry-run → dựng blockout Maya",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W, pady=(1, 0))
        ttk.Label(
            header_frame,
            text=(
                "🐾 Gợi ý: Chọn SVG → Dry-run → Chạy Maya → Mở .ma trong Maya"
                "   |   Không sửa/xóa file gốc của artist."
            ),
            style="Tip.TLabel",
        ).pack(anchor=tk.W, pady=(2, 0))
        ttk.Label(
            header_frame,
            text=app_version_display(),
            style="Hint.TLabel",
        ).pack(anchor=tk.W, pady=(2, 0))

        # ── Hướng dẫn & SVG mẫu ──────────────────────────────────────────
        doc_section = ttk.LabelFrame(
            scrollable_frame, text="📖 Tài liệu & SVG mẫu", padding=8
        )
        doc_section.grid(row=1, column=0, sticky=tk.EW, pady=(0, 6))
        doc_buttons = ttk.Frame(doc_section)
        doc_buttons.pack(fill=tk.X)
        ttk.Button(
            doc_buttons,
            text="Mở hướng dẫn",
            command=self._open_artist_guide,
            style=STYLE_GUIDE_BUTTON,
        ).pack(side=tk.LEFT)
        ttk.Button(
            doc_buttons,
            text="Mở SVG mẫu marker",
            command=self._open_prop_marker_template,
            style=STYLE_GUIDE_BUTTON,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            doc_buttons,
            text="Mở thư mục template",
            command=self._open_prop_marker_template_dir,
            style=STYLE_UTILITY_BUTTON,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            doc_buttons,
            text="Copy đường dẫn SVG mẫu",
            command=self._copy_template_path,
            style=STYLE_UTILITY_BUTTON,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(
            doc_section,
            text=(
                "💡 Sổ tay mèo HTML là hướng dẫn chính. "
                "SVG mẫu marker dùng để copy/paste prop vào Illustrator."
            ),
            style="Hint.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        # ── Step 1: Chọn SVG sạch ─────────────────────────────────────────
        step1_section = ttk.LabelFrame(
            scrollable_frame, text="🐾 Step 1: Chọn SVG sạch", padding=8
        )
        step1_section.grid(row=2, column=0, sticky=tk.EW, pady=(0, 6))
        step1_section.columnconfigure(1, weight=1)

        ttk.Label(step1_section, text="Chọn SVG sạch").grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Entry(step1_section, textvariable=self.svg_var).grid(
            row=0, column=1, sticky=tk.EW, pady=3
        )
        ttk.Button(
            step1_section, text="Chọn SVG", command=self._choose_svg, style=STYLE_UTILITY_BUTTON
        ).grid(row=0, column=2, padx=(8, 0), pady=3)

        ttk.Label(step1_section, text="Tên phòng/layer").grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Entry(step1_section, textvariable=self.room_var).grid(
            row=1, column=1, columnspan=2, sticky=tk.EW, pady=3
        )

        ttk.Label(step1_section, text="Repo root").grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Entry(step1_section, textvariable=self.repo_root_var, state="readonly").grid(
            row=2, column=1, columnspan=2, sticky=tk.EW, pady=3
        )

        ttk.Label(
            step1_section,
            text="💡 Chọn file SVG sạch đã xuất từ Illustrator (không phải .ai gốc).",
            style="Hint.TLabel",
        ).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 2))

        # ── Step 2: Kiểm tra SVG ─────────────────────────────────────────
        step2_section = ttk.LabelFrame(
            scrollable_frame, text="🔍 Step 2: Kiểm tra SVG", padding=8
        )
        step2_section.grid(row=3, column=0, sticky=tk.EW, pady=(0, 6))

        self.preflight_button = ttk.Button(
            step2_section,
            text="Kiểm tra SVG",
            command=self._run_preflight_clicked,
            style=STYLE_GUIDE_BUTTON,
        )
        self.preflight_button.pack(side=tk.LEFT)
        ttk.Label(
            step2_section,
            text="💡 Kiểm tra cấu trúc SVG xem có lỗi đặt tên/marker/layer trước khi dựng hình.",
            style="Hint.TLabel",
        ).pack(side=tk.LEFT, padx=(10, 0))

        # ── Step 3: Chạy dry-run ──────────────────────────────────────────
        step3_section = ttk.LabelFrame(
            scrollable_frame, text="🛡️ Step 3: Chạy thử an toàn (Chạy dry-run)", padding=8
        )
        step3_section.grid(row=4, column=0, sticky=tk.EW, pady=(0, 6))
        step3_section.columnconfigure(1, weight=1)

        ttk.Label(step3_section, text="Thư mục output").grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Entry(step3_section, textvariable=self.output_var).grid(
            row=0, column=1, sticky=tk.EW, pady=3
        )
        ttk.Button(
            step3_section,
            text="Chọn thư mục",
            command=self._choose_output_dir,
            style=STYLE_UTILITY_BUTTON,
        ).grid(row=0, column=2, padx=(8, 0), pady=3)

        checks = ttk.Frame(step3_section)
        checks.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(6, 2))

        ttk.Checkbutton(
            checks,
            text="Render PNG preview sau khi build Maya",
            variable=self.render_var,
        ).pack(side=tk.LEFT)

        render_frame = ttk.Frame(step3_section)
        render_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=3)
        ttk.Label(render_frame, text="Render width").pack(side=tk.LEFT)
        ttk.Entry(render_frame, textvariable=self.width_var, width=8).pack(
            side=tk.LEFT, padx=(6, 16)
        )
        ttk.Label(render_frame, text="Render height").pack(side=tk.LEFT)
        ttk.Entry(render_frame, textvariable=self.height_var, width=8).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        dry_run_buttons_frame = ttk.Frame(step3_section)
        dry_run_buttons_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(6, 4))

        self.dry_run_button = ttk.Button(
            dry_run_buttons_frame,
            text="Chạy thử an toàn",
            command=self._run_dry_run_clicked,
            style=STYLE_GUIDE_BUTTON,
        )
        self.dry_run_button.pack(side=tk.LEFT)
        ttk.Label(
            dry_run_buttons_frame,
            text="💡 Chạy thử không cần cài Maya để tạo cấu trúc dữ liệu JSON kiểm nghiệm.",
            style="Hint.TLabel",
        ).pack(side=tk.LEFT, padx=(10, 0))

        # ── Step 4: Chạy Maya thật ─────────────────────────────────────────
        step4_section = ttk.LabelFrame(
            scrollable_frame, text="⚡ Step 4: Dựng Maya thật", padding=8
        )
        step4_section.grid(row=5, column=0, sticky=tk.EW, pady=(0, 6))
        step4_section.columnconfigure(1, weight=1)

        ttk.Label(step4_section, text="mayapy.exe").grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Entry(step4_section, textvariable=self.mayapy_var).grid(
            row=0, column=1, sticky=tk.EW, pady=3
        )
        ttk.Button(
            step4_section,
            text="Chọn mayapy",
            command=self._choose_mayapy,
            style=STYLE_UTILITY_BUTTON,
        ).grid(row=0, column=2, padx=(8, 0), pady=3)

        actual_run_buttons_frame = ttk.Frame(step4_section)
        actual_run_buttons_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(6, 4))

        self.actual_run_button = ttk.Button(
            actual_run_buttons_frame,
            text="Dựng Maya thật",
            command=self._run_actual_clicked,
            style=STYLE_PRIMARY_BUTTON,
        )
        self.actual_run_button.pack(side=tk.LEFT)
        ttk.Label(
            actual_run_buttons_frame,
            text="💡 Chỉ khả dụng sau khi chạy dry-run thành công cho cùng SVG và thiết lập.",
            style="Hint.TLabel",
        ).pack(side=tk.LEFT, padx=(10, 0))

        # ── Tính năng AI (AI preview) ───────────────────────────────────────
        ai_section = ttk.LabelFrame(
            scrollable_frame, text="✨ Tính năng AI (Xem trước)", padding=8
        )
        ai_section.grid(row=6, column=0, sticky=tk.EW, pady=(0, 6))
        ttk.Label(
            ai_section,
            text="AI preview: chưa bật trong workflow hiện tại. Tính năng này có thể được cập nhật sau.",
            style="Hint.TLabel",
        ).pack(anchor=tk.W)

        # Hidden elements for backwards compatibility
        self.run_button = ttk.Button(step3_section)
        self.ai_run_button = ttk.Button(ai_section)

        # ── Step 5: Mở output / xem log ──────────────────────────────────────
        step5_section = ttk.LabelFrame(
            scrollable_frame, text="📋 Step 5: Mở thư mục kết quả & Xem log", padding=8
        )
        step5_section.grid(row=7, column=0, sticky=tk.NSEW)
        step5_section.columnconfigure(1, weight=1)

        ttk.Label(step5_section, text="Trạng thái SVG").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2)
        )
        ttk.Label(step5_section, textvariable=self.svg_status_var).grid(
            row=0, column=1, sticky=tk.W, pady=(0, 2)
        )

        ttk.Label(step5_section, text="Trạng thái Maya").grid(
            row=1, column=0, sticky=tk.W, pady=3
        )
        ttk.Label(step5_section, textvariable=self.status_var).grid(
            row=1, column=1, sticky=tk.W, pady=3
        )

        ttk.Label(step5_section, text="Lệnh gần nhất").grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Entry(step5_section, textvariable=self.command_var, state="readonly").grid(
            row=2, column=1, sticky=tk.EW, pady=3
        )

        ttk.Label(step5_section, text="Kết quả gần nhất").grid(
            row=3, column=0, sticky=tk.W, pady=3
        )
        ttk.Label(step5_section, textvariable=self.workflow_status_var).grid(
            row=3, column=1, sticky=tk.W, pady=3
        )

        buttons = ttk.Frame(step5_section)
        buttons.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(6, 4))

        ttk.Button(
            buttons,
            text="Mở outputs/maya",
            command=lambda: self._open_output("maya"),
            style=STYLE_UTILITY_BUTTON,
        ).pack(side=tk.LEFT)
        ttk.Button(
            buttons,
            text="Mở outputs/preview",
            command=lambda: self._open_output("preview"),
            style=STYLE_UTILITY_BUTTON,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            buttons,
            text="Mở outputs/reports",
            command=lambda: self._open_output("reports"),
            style=STYLE_UTILITY_BUTTON,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            buttons, text="Xóa log", command=self._clear_log, style=STYLE_UTILITY_BUTTON
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            buttons, text="Copy lệnh", command=self._copy_command, style=STYLE_UTILITY_BUTTON
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            buttons, text="Mở repo", command=self._open_repo, style=STYLE_UTILITY_BUTTON
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.log_text = scrolledtext_module.ScrolledText(
            step5_section,
            height=12,
            wrap=tk.WORD,
            bg=THEME_CARD,
            fg=THEME_TEXT,
            font=("Consolas", 9),
            relief="flat",
            borderwidth=1,
        )
        self.log_text.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, pady=(6, 0))

    def run(self) -> None:
        self.root.mainloop()

    def _choose_svg(self) -> None:
        path = self.filedialog.askopenfilename(
            title="Chọn file SVG sạch",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
        )
        if path:
            self.svg_var.set(path)
            self.successful_dry_run_key = None
            self.workflow_status_var.set("Đã chọn SVG mới. Hãy kiểm tra SVG rồi chạy dry-run.")

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

    def _choose_ai_png(self) -> None:
        path = self.filedialog.askopenfilename(
            title="Chọn PNG preview cho AI",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.ai_png_var.set(path)

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

    def _current_ai_options(self) -> ArtistAiPreviewOptions:
        return ai_options_from_strings(
            input_png_path=self.ai_png_var.get(),
            provider=self.ai_provider_var.get(),
            model=self.ai_model_var.get(),
            prompt_preset=self.ai_prompt_preset_var.get(),
            prompt=self.ai_prompt_var.get(),
            skip_on_missing_config=self.ai_skip_missing_var.get(),
            dry_run=self.ai_dry_run_var.get(),
        )

    def _current_preflight_options(self) -> ArtistPreflightOptions:
        return preflight_options_from_strings(
            svg_path=self.svg_var.get(),
            output_dir=self.output_var.get(),
        )

    def _run_preflight_clicked(self) -> None:
        if self.preflight_worker and self.preflight_worker.is_alive():
            self.messagebox.showinfo(
                "Đang kiểm tra SVG",
                "Preflight SVG đang chạy, hãy đợi log kết thúc.",
            )
            return

        options = self._current_preflight_options()
        root = find_repo_root()
        self.repo_root_var.set(repo_root_display_value(root))
        errors = validate_preflight_options(options) + validate_preflight_runtime_environment(
            root=root
        )
        if root is not None:
            errors.extend(validate_preflight_paths(options, root=root))
        if errors:
            self.messagebox.showerror("Cần kiểm tra lại", "\n".join(errors))
            return

        try:
            if root is None:
                raise RuntimeError(REPO_ROOT_ERROR)
            assert options.json_output is not None
            resolved_output = resolve_output_root(options.json_output.parent.parent, root)
            preflight_options = ArtistPreflightOptions(
                svg_path=options.svg_path,
                json_output=default_preflight_report_path(resolved_output),
            )
            command = build_svg_preflight_command(preflight_options, root=root)
        except RuntimeError as exc:
            self.messagebox.showerror("Cần kiểm tra lại", str(exc))
            return

        display_command = command_to_display(command)
        self.command_var.set(display_command)
        self._append_log("\n=== Kiểm tra SVG preflight ===\n")
        self._append_log(f"Repo root: {root}\n")
        self._append_log(display_command + "\n\n")
        self.svg_status_var.set("Đang kiểm tra SVG...")
        self.workflow_status_var.set("Bước 2/5: Đang chạy kiểm tra SVG...")
        self.preflight_button.configure(state=self.tk.DISABLED)
        self.preflight_worker = threading.Thread(
            target=self._run_subprocess,
            args=(
                command,
                root,
                PREFLIGHT_RUN_FINISHED_PREFIX,
                "Lỗi khi kiểm tra SVG",
            ),
            daemon=True,
        )
        self.preflight_worker.start()

    def _run_dry_run_clicked(self) -> None:
        self.dry_run_var.set(True)
        self._run_clicked()

    def _run_actual_clicked(self) -> None:
        self.dry_run_var.set(False)
        self._run_clicked()

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

        if root is not None and not options.dry_run:
            if not dry_run_matches_current_settings(
                self.successful_dry_run_key,
                options,
                root=root,
            ):
                self.workflow_status_var.set("Chưa thể dựng thật: cần chạy thử an toàn (Bước 3) trước.")
                self.messagebox.showwarning("Cần chạy thử an toàn trước", DRY_RUN_REQUIRED_ERROR)
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
        
        if options.dry_run:
            self.status_var.set("Đang chạy thử an toàn...")
            self.workflow_status_var.set("Bước 3/5: Đang chạy thử an toàn (dry-run) Maya...")
        else:
            self.status_var.set("Đang dựng Maya thật...")
            self.workflow_status_var.set("Bước 4/5: Đang dựng Maya thật...")

        self.run_button.configure(state=self.tk.DISABLED)
        self.dry_run_button.configure(state=self.tk.DISABLED)
        self.actual_run_button.configure(state=self.tk.DISABLED)
        self.active_maya_options = options
        self.active_maya_root = root
        self.worker = threading.Thread(
            target=self._run_subprocess,
            args=(command, root, RUN_FINISHED_PREFIX, "Lỗi khi chạy pipeline"),
            daemon=True,
        )
        self.worker.start()

    def _run_ai_clicked(self) -> None:
        if self.ai_worker and self.ai_worker.is_alive():
            self.messagebox.showinfo(
                "AI đang chạy",
                "AI polish preview đang chạy, hãy đợi log kết thúc.",
            )
            return

        options = self._current_ai_options()
        root = find_repo_root()
        self.repo_root_var.set(repo_root_display_value(root))
        errors = validate_ai_preview_options(options) + validate_ai_runtime_environment(
            root=root
        )
        if root is not None:
            errors.extend(validate_ai_preview_paths(options, root=root))
        if errors:
            self.messagebox.showerror("Cần kiểm tra lại", "\n".join(errors))
            return

        try:
            if root is None:
                raise RuntimeError(REPO_ROOT_ERROR)
            command = build_ai_preview_command(options, root=root)
        except RuntimeError as exc:
            self.messagebox.showerror("Cần kiểm tra lại", str(exc))
            return

        display_command = command_to_display(command)
        self.ai_command_var.set(display_command)
        self._append_log("\n=== Lệnh AI sẽ chạy ===\n")
        self._append_log(f"Repo root: {root}\n")
        self._append_log(display_command + "\n\n")
        self.ai_status_var.set(STATUS_RUNNING)
        self.ai_run_button.configure(state=self.tk.DISABLED)
        self.ai_worker = threading.Thread(
            target=self._run_subprocess,
            args=(
                command,
                root,
                AI_RUN_FINISHED_PREFIX,
                "Lỗi khi chạy AI polish preview",
            ),
            daemon=True,
        )
        self.ai_worker.start()

    def _run_subprocess(
        self,
        command: list[str],
        root: Path,
        finish_prefix: str,
        error_label: str,
    ) -> None:
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
            self.log_queue.put(f"\n{error_label}: {exc}\n")
        finally:
            self.log_queue.put(f"{finish_prefix}{return_code}")

    def _drain_log_queue(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if message.startswith(RUN_FINISHED_PREFIX):
                return_code = int(message.removeprefix(RUN_FINISHED_PREFIX))
                self.run_button.configure(state=self.tk.NORMAL)
                self.dry_run_button.configure(state=self.tk.NORMAL)
                self.actual_run_button.configure(state=self.tk.NORMAL)
                if return_code == 0:
                    if (
                        self.active_maya_options is not None
                        and self.active_maya_root is not None
                        and self.active_maya_options.dry_run
                    ):
                        self.status_var.set("Chạy thử xong: mã 0")
                        self.successful_dry_run_key = dry_run_settings_key(
                            self.active_maya_options,
                            root=self.active_maya_root,
                        )
                        self.workflow_status_var.set(
                            "Bước 3/5 hoàn tất: Chạy thử an toàn thành công. Bây giờ có thể dựng Maya thật (Bước 4)."
                        )
                    elif (
                        self.active_maya_options is not None
                        and not self.active_maya_options.dry_run
                    ):
                        self.status_var.set("Dựng thật xong: mã 0")
                        self.workflow_status_var.set(
                            "Bước 4/5 hoàn tất: Dựng Maya thành công! Hãy mở thư mục kết quả (Bước 5)."
                        )
                else:
                    if self.active_maya_options is not None and self.active_maya_options.dry_run:
                        self.status_var.set(f"Chạy thử lỗi: mã {return_code}")
                        self.workflow_status_var.set("Bước 3/5: Chạy thử an toàn thất bại. Hãy xem log để sửa lỗi trước khi chạy Maya thật.")
                    else:
                        self.status_var.set(f"Dựng thật lỗi: mã {return_code}")
                        self.workflow_status_var.set("Bước 4/5: Dựng Maya thật thất bại. Hãy xem log để kiểm tra chi tiết lỗi.")
                self.active_maya_options = None
                self.active_maya_root = None
            elif message.startswith(PREFLIGHT_RUN_FINISHED_PREFIX):
                return_code = int(message.removeprefix(PREFLIGHT_RUN_FINISHED_PREFIX))
                self.preflight_button.configure(state=self.tk.NORMAL)
                if return_code == 0:
                    self.svg_status_var.set("Kiểm tra xong: mã 0")
                    self.workflow_status_var.set(
                        "Bước 2/5 hoàn tất: Kiểm tra SVG OK. Hãy chạy thử an toàn (Bước 3)."
                    )
                else:
                    self.svg_status_var.set(f"Kiểm tra lỗi: mã {return_code}")
                    self.workflow_status_var.set(
                        "Kiểm tra SVG thất bại/cảnh báo. Hãy sửa file SVG trước khi chạy thử."
                    )
            elif message.startswith(AI_RUN_FINISHED_PREFIX):
                return_code = int(message.removeprefix(AI_RUN_FINISHED_PREFIX))
                self.ai_run_button.configure(state=self.tk.NORMAL)
                if return_code == 0:
                    self.ai_status_var.set("Hoàn tất: mã 0")
                else:
                    self.ai_status_var.set(f"Lỗi: mã {return_code}")
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

    def _open_ai_output(self) -> None:
        try:
            root = repo_root()
        except RuntimeError as exc:
            self.messagebox.showerror("Cần kiểm tra lại", str(exc))
            return
        path = ai_output_dir_path(root)
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

    def _show_open_problem(self, title: str, exc: Exception) -> None:
        message = str(exc)
        self._append_log(f"\n{title}: {message}\n")
        self.messagebox.showwarning(title, message)

    def _open_artist_guide(self) -> None:
        try:
            path = open_artist_guide(repo_root())
        except (FileNotFoundError, RuntimeError) as exc:
            self._show_open_problem("Không mở được hướng dẫn", exc)
            return
        self._append_log(f"\nĐã mở hướng dẫn: {path}\n")

    def _open_prop_marker_template(self) -> None:
        try:
            path = open_prop_marker_template(repo_root())
        except (FileNotFoundError, RuntimeError) as exc:
            self._show_open_problem("Không mở được SVG mẫu marker", exc)
            return
        self._append_log(f"\nĐã mở SVG mẫu marker: {path}\n")

    def _open_prop_marker_template_dir(self) -> None:
        try:
            path = open_prop_marker_template_dir(repo_root())
        except (FileNotFoundError, RuntimeError) as exc:
            self._show_open_problem("Không mở được thư mục template", exc)
            return
        self._append_log(f"\nĐã mở thư mục template: {path}\n")

    def _copy_template_path(self) -> None:
        try:
            path = prop_marker_template_path(repo_root())
        except RuntimeError as exc:
            self._show_open_problem("Không copy được đường dẫn template", exc)
            return
        if not path.is_file():
            self._show_open_problem(
                "Không copy được đường dẫn template",
                FileNotFoundError(TEMPLATE_MISSING_ERROR),
            )
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(str(path))
        self._append_log(f"\nĐã copy đường dẫn SVG mẫu marker: {path}\n")

    def _open_folder(self, path: Path) -> None:
        resolved = path.resolve()
        if not resolved.exists():
            self.messagebox.showwarning("Chưa có thư mục", f"Không tìm thấy:\n{resolved}")
            return
        try:
            os.startfile(str(resolved))  # type: ignore[attr-defined]
        except OSError as exc:
            self._show_open_problem("Không mở được thư mục", exc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mở desktop app MVP để chạy Maya-first pipeline cho họa sĩ."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=app_version_display(),
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
