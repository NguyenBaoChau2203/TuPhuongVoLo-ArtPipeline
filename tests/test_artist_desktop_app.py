"""Tests for the Phase 007J artist desktop app helpers.

These tests intentionally avoid creating a Tkinter window.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import artist_desktop_app as app


def _fake_repo(root: Path) -> Path:
    script_path = root / "scripts" / "python" / "build_maya_room.py"
    script_path.parent.mkdir(parents=True)
    script_path.write_text("print('fake pipeline')\n", encoding="utf-8")
    ai_script_path = root / "scripts" / "python" / "ai_polish_preview.py"
    ai_script_path.write_text("print('fake ai preview')\n", encoding="utf-8")
    return root


def test_app_version_metadata_is_display_ready() -> None:
    assert app.APP_VERSION == "0.7.8"
    assert app.APP_PHASE == "007J"
    assert f"v{app.APP_VERSION}" in app.APP_TITLE
    assert app.APP_PHASE in app.APP_TITLE
    assert app.APP_VERSION in app.app_version_display()


def test_theme_palette_constants_are_importable() -> None:
    """Verify theme colour and font constants exist and are non-empty."""
    assert app.THEME_BG and app.THEME_BG.startswith("#")
    assert app.THEME_CARD and app.THEME_CARD.startswith("#")
    assert app.THEME_ACCENT and app.THEME_ACCENT.startswith("#")
    assert app.THEME_TEXT and app.THEME_TEXT.startswith("#")
    assert app.THEME_HINT and app.THEME_HINT.startswith("#")
    assert isinstance(app.THEME_FONT_HEADER, tuple)
    assert isinstance(app.THEME_FONT_HINT, tuple)


def test_style_name_constants_are_importable() -> None:
    """Verify style name constants are non-empty strings."""
    assert isinstance(app.STYLE_PRIMARY_BUTTON, str) and app.STYLE_PRIMARY_BUTTON
    assert isinstance(app.STYLE_ACCENT_BUTTON, str) and app.STYLE_ACCENT_BUTTON
    assert isinstance(app.STYLE_SECONDARY_BUTTON, str) and app.STYLE_SECONDARY_BUTTON
    # Names must be valid ttk style name format (contains ".")
    assert "." in app.STYLE_PRIMARY_BUTTON
    assert "." in app.STYLE_ACCENT_BUTTON
    assert "." in app.STYLE_SECONDARY_BUTTON


def test_configure_artist_theme_is_callable() -> None:
    """Verify configure_artist_theme is importable as a callable without opening a window."""
    assert callable(app.configure_artist_theme)


def test_app_version_cli_exits_before_opening_tkinter(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        app.build_parser().parse_args(["--version"])

    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert app.APP_VERSION in captured.out
    assert app.APP_PHASE in captured.out


def test_dry_run_command_wraps_build_maya_room(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=Path(r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"),
        dry_run=True,
    )

    command = app.build_maya_room_command(
        options,
        python_executable="python",
        root=Path("D:/repo"),
    )

    assert command[0] == "python"
    assert any("build_maya_room.py" in part for part in command)
    assert "--input" in command
    assert str(tmp_path / "room.svg") in command
    assert "--room" in command
    assert "phong_kho" in command
    assert "--output-dir" in command
    assert str(tmp_path / "outputs") in command
    assert "--dry-run" in command
    assert "--maya-path" not in command


def test_default_mayapy_path_detection_when_path_exists(tmp_path: Path) -> None:
    mayapy = tmp_path / "Maya2024" / "bin" / "mayapy.exe"
    mayapy.parent.mkdir(parents=True)
    mayapy.write_text("fake mayapy", encoding="utf-8")

    assert app.default_mayapy_path(mayapy) == str(mayapy)


def test_default_mayapy_path_empty_when_path_missing(tmp_path: Path) -> None:
    assert app.default_mayapy_path(tmp_path / "missing" / "mayapy.exe") == ""


def test_find_repo_root_finds_fake_checkout(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv(app.REPO_ROOT_ENV_VAR, raising=False)
    fake_root = _fake_repo(tmp_path / "repo")
    nested_dir = fake_root / "dist" / "nested"
    nested_dir.mkdir(parents=True)

    detected_root = app.find_repo_root(extra_candidates=[nested_dir])

    assert detected_root == fake_root


def test_packaged_command_does_not_use_app_exe(monkeypatch, tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    fake_app_exe = fake_root / "dist" / "TuPhuongVoLo_MayaArtistApp.exe"
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        dry_run=True,
    )

    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_app_exe))
    monkeypatch.setattr(app.shutil, "which", lambda name: "C:/Python311/python.exe")

    command = app.build_maya_room_command(options, root=fake_root)

    assert command[0] == "C:/Python311/python.exe"
    assert command[0] != str(fake_app_exe)


def test_packaged_python_command_uses_py_launcher_fallback(monkeypatch) -> None:
    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    def fake_which(name: str) -> str | None:
        if name == "py":
            return "C:/Windows/py.exe"
        return None

    monkeypatch.setattr(app.shutil, "which", fake_which)

    assert app.pipeline_python_command_prefix() == ["C:/Windows/py.exe", "-3"]


def test_frozen_mode_without_external_python_returns_validation_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(app.shutil, "which", lambda name: None)

    errors = app.validate_runtime_environment(root=fake_root)

    assert app.PIPELINE_PYTHON_ERROR in errors


def test_missing_repo_root_returns_vietnamese_validation_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(app.REPO_ROOT_ENV_VAR, raising=False)
    monkeypatch.delenv(app.PIPELINE_PYTHON_ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app, "__file__", str(tmp_path / "artist_desktop_app.py"))
    monkeypatch.setattr(sys, "frozen", False, raising=False)

    errors = app.validate_runtime_environment()

    assert app.REPO_ROOT_ERROR in errors


def test_missing_svg_returns_vietnamese_validation_error(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    options = app.ArtistAppOptions(
        svg_path=Path("tests/in/missing.svg"),
        room_name="phong_kho",
        output_dir=Path("outputs"),
        dry_run=True,
    )

    errors = app.validate_run_paths(options, root=fake_root)

    assert app.SVG_NOT_FOUND_ERROR in errors


def test_relative_svg_path_resolves_from_repo_root(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    svg = fake_root / "tests" / "in" / "illustrator_prop_markers.svg"
    svg.parent.mkdir(parents=True)
    svg.write_text("<svg />\n", encoding="utf-8")

    resolved = app.resolve_repo_relative_path(
        Path(r"tests\in\illustrator_prop_markers.svg"),
        fake_root,
    )

    assert resolved == fake_root / r"tests\in\illustrator_prop_markers.svg"
    assert app.validate_run_paths(
        app.ArtistAppOptions(
            svg_path=Path("tests/in/illustrator_prop_markers.svg"),
            room_name="phong_kho",
            output_dir=Path("outputs"),
            dry_run=True,
        ),
        root=fake_root,
    ) == []


def test_empty_room_name_returns_vietnamese_validation_error(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="",
        output_dir=tmp_path / "outputs",
        dry_run=True,
    )

    errors = app.validate_run_options(options)

    assert app.ROOM_EMPTY_ERROR in errors


def test_build_script_path_uses_detected_repo_root(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    assert app.build_script_path(fake_root) == (
        fake_root / "scripts" / "python" / "build_maya_room.py"
    )


def test_frozen_repo_root_uses_exe_location_not_appdata(monkeypatch, tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    appdata_root = _fake_repo(tmp_path / "AppData" / "Local")
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    fake_app_exe = fake_root / "dist" / "TuPhuongVoLo_MayaArtistApp.exe"
    fake_app_exe.parent.mkdir(parents=True)
    fake_app_exe.write_text("fake exe", encoding="utf-8")

    monkeypatch.delenv(app.REPO_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(empty_dir)
    monkeypatch.setattr(app, "__file__", str(appdata_root / "artist_desktop_app.py"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_app_exe))

    assert app.find_repo_root() == fake_root


def test_render_preview_command_includes_size(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        dry_run=True,
        render_preview=True,
        render_width=800,
        render_height=600,
    )

    command = app.build_maya_room_command(options, python_executable="python")

    assert "--render-preview" in command
    assert command[command.index("--render-width") + 1] == "800"
    assert command[command.index("--render-height") + 1] == "600"


def test_actual_run_includes_mayapy_when_provided(tmp_path: Path) -> None:
    mayapy = Path(r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe")
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=mayapy,
        dry_run=False,
    )

    command = app.build_maya_room_command(options, python_executable="python")

    assert "--dry-run" not in command
    assert "--maya-path" in command
    assert command[command.index("--maya-path") + 1] == str(mayapy)


def test_actual_run_without_mayapy_returns_clear_validation_message(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=None,
        dry_run=False,
    )

    errors = app.validate_run_options(options)

    assert app.MAYAPY_REQUIRED_ERROR in errors


def test_actual_run_with_missing_mayapy_returns_validation_error(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    svg = fake_root / "tests" / "in" / "room.svg"
    svg.parent.mkdir(parents=True)
    svg.write_text("<svg />\n", encoding="utf-8")
    options = app.ArtistAppOptions(
        svg_path=Path("tests/in/room.svg"),
        room_name="phong_kho",
        output_dir=Path("outputs"),
        maya_path=tmp_path / "missing" / "mayapy.exe",
        dry_run=False,
    )

    errors = app.validate_run_paths(options, root=fake_root)

    assert app.MAYAPY_NOT_FOUND_ERROR in errors


def test_dry_run_does_not_require_mayapy(tmp_path: Path) -> None:
    options = app.ArtistAppOptions(
        svg_path=tmp_path / "room.svg",
        room_name="phong_kho",
        output_dir=tmp_path / "outputs",
        maya_path=None,
        dry_run=True,
    )

    errors = app.validate_run_options(options)

    assert errors == []


def test_output_folder_helper_only_builds_expected_paths(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"

    assert app.output_subdir_path(output_dir, "maya") == output_dir / "maya"
    assert app.output_subdir_path(output_dir, "preview") == output_dir / "preview"
    assert app.output_subdir_path(output_dir, "reports") == output_dir / "reports"
    assert not output_dir.exists()


def test_output_root_resolves_relative_path_from_repo_root(tmp_path: Path) -> None:
    fake_root = tmp_path / "repo"

    assert app.resolve_output_root(Path("outputs"), fake_root) == fake_root / "outputs"
    assert app.resolve_output_root(tmp_path / "custom_outputs", fake_root) == (
        tmp_path / "custom_outputs"
    )


def test_ai_mock_dry_run_command_wraps_ai_polish_preview(tmp_path: Path) -> None:
    options = app.ArtistAiPreviewOptions(
        input_png_path=tmp_path / "sample_preview.png",
        provider=app.AI_PROVIDER_MOCK,
        dry_run=True,
    )

    command = app.build_ai_preview_command(
        options,
        python_executable="python",
        root=Path("D:/repo"),
    )

    assert command[0] == "python"
    assert any("ai_polish_preview.py" in part for part in command)
    assert command[command.index("--provider") + 1] == "mock"
    assert command[command.index("--input") + 1] == str(tmp_path / "sample_preview.png")
    assert command[command.index("--output-dir") + 1] == str(app.DEFAULT_AI_OUTPUT_DIR)
    assert command[command.index("--prompt-preset") + 1] == app.DEFAULT_AI_PROMPT_PRESET
    assert "--dry-run" in command
    assert "--model" not in command
    assert "--skip-on-missing-config" not in command


def test_ai_fal_command_includes_model_and_skip_on_missing_config(tmp_path: Path) -> None:
    options = app.ArtistAiPreviewOptions(
        input_png_path=tmp_path / "sample_preview.png",
        provider=app.AI_PROVIDER_FAL,
        model="fal-ai/flux-pro/kontext",
        skip_on_missing_config=True,
        dry_run=False,
    )

    command = app.build_ai_preview_command(
        options,
        python_executable="python",
        root=Path("D:/repo"),
    )

    assert command[command.index("--provider") + 1] == "fal"
    assert command[command.index("--model") + 1] == "fal-ai/flux-pro/kontext"
    assert "--skip-on-missing-config" in command
    assert "--dry-run" not in command


def test_ai_prompt_text_is_included_only_when_non_empty(tmp_path: Path) -> None:
    without_prompt = app.build_ai_preview_command(
        app.ArtistAiPreviewOptions(input_png_path=tmp_path / "sample_preview.png"),
        python_executable="python",
        root=Path("D:/repo"),
    )
    with_prompt = app.build_ai_preview_command(
        app.ArtistAiPreviewOptions(
            input_png_path=tmp_path / "sample_preview.png",
            prompt="soft tropical lighting",
        ),
        python_executable="python",
        root=Path("D:/repo"),
    )

    assert "--prompt" not in without_prompt
    assert with_prompt[with_prompt.index("--prompt") + 1] == "soft tropical lighting"


def test_ai_validation_rejects_missing_input_path() -> None:
    errors = app.validate_ai_preview_options(
        app.ArtistAiPreviewOptions(input_png_path=Path(""))
    )

    assert app.AI_INPUT_EMPTY_ERROR in errors


def test_ai_validation_rejects_non_png_input() -> None:
    errors = app.validate_ai_preview_options(
        app.ArtistAiPreviewOptions(input_png_path=Path("preview.jpg"))
    )

    assert app.AI_INPUT_NOT_PNG_ERROR in errors


def test_ai_validation_rejects_missing_png_file(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    errors = app.validate_ai_preview_paths(
        app.ArtistAiPreviewOptions(input_png_path=Path("tests/in/missing_preview.png")),
        root=fake_root,
    )

    assert app.AI_INPUT_NOT_FOUND_ERROR in errors


def test_ai_output_folder_helper_points_to_outputs_ai_preview(tmp_path: Path) -> None:
    root = tmp_path / "repo"

    assert app.output_subdir_path(Path("outputs"), "ai_preview") == (
        Path("outputs") / "ai_preview"
    )
    assert app.ai_output_dir_path(root) == root / "outputs" / "ai_preview"


def test_artist_guide_and_template_paths_use_repo_root(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    assert app.artist_guide_path(fake_root) == (
        fake_root / "docs" / "artist_workflow_cat_guide_vi.html"
    )
    assert app.prop_marker_template_path(fake_root) == (
        fake_root
        / "assets"
        / "2d"
        / "templates"
        / "illustrator_prop_marker_template.svg"
    )
    assert app.prop_marker_template_dir(fake_root) == fake_root / "assets" / "2d" / "templates"


def test_open_artist_guide_uses_mocked_browser_opener(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    guide = app.artist_guide_path(fake_root)
    guide.parent.mkdir(parents=True)
    guide.write_text("<!doctype html><title>guide</title>\n", encoding="utf-8")
    opened: list[str] = []

    returned = app.open_artist_guide(fake_root, opener=opened.append)

    assert returned == guide
    assert opened == [guide.resolve().as_uri()]


def test_open_prop_marker_template_uses_mocked_os_opener(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    template = app.prop_marker_template_path(fake_root)
    template.parent.mkdir(parents=True)
    template.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" />\n", encoding="utf-8")
    opened: list[Path] = []

    returned = app.open_prop_marker_template(fake_root, opener=opened.append)

    assert returned == template
    assert opened == [template]


def test_open_template_folder_uses_mocked_os_opener(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    template_dir = app.prop_marker_template_dir(fake_root)
    template_dir.mkdir(parents=True)
    opened: list[Path] = []

    returned = app.open_prop_marker_template_dir(fake_root, opener=opened.append)

    assert returned == template_dir
    assert opened == [template_dir]


def test_missing_guide_and_template_raise_friendly_errors(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")

    with pytest.raises(FileNotFoundError, match=app.GUIDE_MISSING_ERROR):
        app.open_artist_guide(fake_root, opener=lambda path: None)

    with pytest.raises(FileNotFoundError, match=app.TEMPLATE_MISSING_ERROR):
        app.open_prop_marker_template(fake_root, opener=lambda path: None)

    with pytest.raises(FileNotFoundError, match=app.TEMPLATE_DIR_MISSING_ERROR):
        app.open_prop_marker_template_dir(fake_root, opener=lambda path: None)


def test_os_open_failure_raises_friendly_runtime_error(tmp_path: Path) -> None:
    fake_root = _fake_repo(tmp_path / "repo")
    template = app.prop_marker_template_path(fake_root)
    template.parent.mkdir(parents=True)
    template.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" />\n", encoding="utf-8")

    def fail_open(_path: Path) -> None:
        raise OSError("blocked")

    with pytest.raises(RuntimeError, match=app.OS_OPEN_ERROR):
        app.open_prop_marker_template(fake_root, opener=fail_open)
