"""Static safety tests for the Maya render preview script (Feature 005.2).

These tests run WITHOUT Autodesk Maya installed. They assert that the render
script stays headless-friendly, exposes the expected CLI surface, and preserves
the editable .ma scene it opens for rendering.
"""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root from this test location."""

    return Path(__file__).resolve().parents[1]


def render_script_path() -> Path:
    """Return the Maya render preview script path."""

    return repo_root() / "scripts" / "maya" / "render_maya_room_preview.py"


def render_script_text() -> str:
    """Return the render script source text."""

    return render_script_path().read_text(encoding="utf-8")


def test_render_script_exists() -> None:
    assert render_script_path().exists()


def test_render_script_avoids_viewport_only_commands() -> None:
    """The render script must be headless/UI-free (no viewport-only commands)."""

    script_text = render_script_text()

    for forbidden in ("lookThru(", "playblast(", "modelPanel(", "modelEditor("):
        assert forbidden not in script_text


def test_render_script_accepts_output_and_size_arguments() -> None:
    """The render CLI must expose scene, output, size, and camera arguments."""

    script_text = render_script_text()

    assert "--scene" in script_text
    assert "--render-output" in script_text
    assert "--width" in script_text
    assert "--height" in script_text
    assert "--camera" in script_text


def test_render_script_preserves_editable_scene() -> None:
    """The render script must not save/rename the .ma it opens for rendering."""

    script_text = render_script_text()

    assert "save=True" not in script_text
    assert "rename=" not in script_text
    assert "open=True" in script_text


def test_render_script_uses_deterministic_camera_selection() -> None:
    """Render uses the scene's iso camera (or an explicit/orthographic one)."""

    script_text = render_script_text()

    assert "find_render_camera" in script_text
    assert "_iso" in script_text
    assert "orthographic" in script_text


def test_render_script_uses_offline_renderer() -> None:
    """Render must use an offline renderer, not an interactive viewport capture."""

    script_text = render_script_text()

    assert "mayaSoftware" in script_text
    assert "cmds.render(" in script_text


def test_render_script_imports_only_inside_maya_initializer() -> None:
    """maya.cmds / maya.standalone must be imported lazily so import is safe."""

    script_text = render_script_text()

    # No top-level Maya imports; they live inside initialize_maya().
    assert "\nimport maya" not in script_text
    assert "import maya.cmds" in script_text


def test_render_script_configures_camera_renderable() -> None:
    """The render script must mark the selected camera shape as renderable.

    This is the fix for the 005.2 bug where Maya silently skipped the
    camera with 'Warning: Camera is not renderable at this time'.
    """

    script_text = render_script_text()

    assert "configure_render_camera" in script_text
    assert ".renderable" in script_text
    assert "setAttr" in script_text


def test_render_script_finds_camera_shape_via_list_relatives() -> None:
    """configure_render_camera must use listRelatives to get the camera shape."""

    script_text = render_script_text()

    assert "listRelatives" in script_text
    assert "shapes=True" in script_text


def test_render_script_does_not_save_scene() -> None:
    """The render script must not save/rename the .ma (no cmds.file(save=...))."""

    script_text = render_script_text()

    assert "save=True" not in script_text
    assert "rename=" not in script_text
