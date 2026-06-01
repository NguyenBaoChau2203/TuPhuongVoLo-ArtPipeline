"""Render an isometric base preview PNG from a saved Maya .ma room blockout.

Feature 005.2 — Maya isometric base render.

Design notes:
    * This script is headless-friendly and meant to be launched with ``mayapy``.
    * It NEVER parses SVG. It only opens an already-built ``.ma`` scene that the
      Python layer produced via ``build_maya_room_scene.py``.
    * It opens the scene read-only (it never re-saves or renames it), so the
      editable ``.ma`` is preserved exactly as written.
    * It avoids viewport/UI-only commands (no ``lookThru``, no ``modelPanel``,
      no ``playblast``); rendering uses the offline ``mayaSoftware`` renderer.
    * It renders through the isometric orthographic camera created by the scene
      builder (``cam_<room>_iso``) or an explicit ``--camera`` when provided.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

# Maya imageFormat enum value for PNG output.
IMAGE_FORMAT_PNG = 32
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
ISO_CAMERA_HINT = "_iso"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args used by mayapy."""

    parser = argparse.ArgumentParser(
        description="Render isometric base PNG preview from a Maya .ma scene.",
    )
    parser.add_argument("--scene", required=True, type=Path, help="Editable .ma scene file.")
    parser.add_argument(
        "--render-output",
        required=True,
        type=Path,
        help="Đường dẫn PNG preview cần tạo.",
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument(
        "--camera",
        help="Tên camera render tùy chọn; mặc định dùng camera iso của scene.",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def initialize_maya() -> Any:
    """Import Maya commands and initialize standalone when running via mayapy."""

    try:
        import maya.cmds as cmds  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Không tìm thấy module Maya Python. "
            "Hãy chạy script bằng mayapy hoặc trong Maya."
        ) from exc

    try:
        import maya.standalone  # type: ignore[import-not-found]

        try:
            maya.standalone.initialize(name="python")
        except Exception as exc:  # Maya raises if already initialized inside Maya.
            if "initialized" not in str(exc).lower():
                raise
    except ModuleNotFoundError:
        pass

    return cmds


def open_scene(cmds: Any, scene_path: Path) -> None:
    """Open the editable .ma scene without modifying it on disk.

    The scene is opened for rendering only; this script intentionally never
    re-saves or renames the scene file, so the artist's editable ``.ma`` is
    preserved exactly as ``build_maya_room_scene.py`` wrote it.
    """

    resolved = scene_path.resolve()
    if not resolved.exists():
        raise ValueError(f"Không tìm thấy Maya scene: {resolved}")
    if resolved.suffix.lower() != ".ma":
        raise ValueError("Scene render phải là file .ma editable.")
    cmds.file(str(resolved), open=True, force=True)


def find_render_camera(cmds: Any, explicit: str | None) -> str:
    """Return a deterministic render camera, preferring the scene's iso camera.

    Selection order:
        1. An explicit ``--camera`` name when it exists in the scene.
        2. The isometric camera created by the scene builder (``cam_*_iso``).
        3. The first orthographic camera in the scene.

    Viewport-only commands (e.g. ``lookThru``) are intentionally avoided; the
    chosen camera is passed straight to the offline renderer.
    """

    if explicit:
        if cmds.objExists(explicit):
            return explicit
        raise ValueError(f"Không tìm thấy camera render: {explicit}")

    camera_shapes = cmds.ls(type="camera", long=True) or []
    iso_transforms: list[str] = []
    ortho_transforms: list[str] = []
    for shape in camera_shapes:
        parents = cmds.listRelatives(shape, parent=True, fullPath=True) or []
        if not parents:
            continue
        transform = parents[0]
        if ISO_CAMERA_HINT in transform.lower():
            iso_transforms.append(transform)
        try:
            if cmds.getAttr(f"{shape}.orthographic"):
                ortho_transforms.append(transform)
        except (RuntimeError, ValueError):
            continue

    if iso_transforms:
        return sorted(iso_transforms)[0]
    if ortho_transforms:
        return sorted(ortho_transforms)[0]
    raise ValueError(
        "Scene không có camera iso/orthographic để render. "
        "Hãy dựng lại scene bằng build_maya_room_scene.py."
    )


def configure_render_camera(cmds: Any, camera_transform: str) -> str:
    """Ensure the selected camera shape is renderable for offline rendering.

    Maya's ``cmds.render()`` silently skips cameras whose shape node has
    ``.renderable`` set to ``False`` — producing the error::

        Warning: Camera is not renderable at this time; skipping image ...

    This helper:
        1. Finds the camera shape under *camera_transform* via ``listRelatives``.
        2. Sets ``.renderable`` to ``True`` on that shape.
        3. Sets ``.renderable`` to ``False`` on **all other** camera shapes so
           the render result is deterministic (only one camera is renderable).

    No viewport/UI commands are used — safe for headless ``mayapy``.
    """

    shapes = cmds.listRelatives(camera_transform, shapes=True, type="camera", fullPath=True) or []
    if not shapes:
        raise ValueError(
            f"Không tìm thấy camera shape dưới transform: {camera_transform}"
        )
    target_shape = shapes[0]

    # Disable renderable on every other camera shape for deterministic output.
    all_camera_shapes = cmds.ls(type="camera", long=True) or []
    for shape in all_camera_shapes:
        cmds.setAttr(f"{shape}.renderable", shape == target_shape)

    return target_shape


def configure_render_settings(cmds: Any, width: int, height: int) -> None:
    """Configure deterministic, headless-safe PNG render settings."""

    if width <= 0 or height <= 0:
        raise ValueError("Kích thước render phải là số dương.")

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware", type="string")
    cmds.setAttr("defaultRenderGlobals.imageFormat", IMAGE_FORMAT_PNG)
    cmds.setAttr("defaultRenderGlobals.animation", 0)
    cmds.setAttr("defaultResolution.width", int(width))
    cmds.setAttr("defaultResolution.height", int(height))
    cmds.setAttr("defaultResolution.deviceAspectRatio", float(width) / float(height))
    cmds.setAttr("defaultResolution.pixelAspect", 1.0)


def render_to_png(
    cmds: Any,
    camera: str,
    width: int,
    height: int,
    render_output: Path,
) -> Path:
    """Render the current scene and copy the image to ``render_output``.

    The offline ``mayaSoftware`` renderer writes into the current workspace
    images directory; the resulting file is copied to the convention-compliant
    output path so the caller controls the final location deterministically.
    """

    render_output.parent.mkdir(parents=True, exist_ok=True)
    rendered = cmds.render(camera, x=int(width), y=int(height))
    if not rendered:
        raise RuntimeError("Maya không trả về đường dẫn ảnh render.")
    rendered_path = Path(str(rendered))
    if not rendered_path.exists():
        raise RuntimeError(f"Không tìm thấy ảnh render Maya: {rendered_path}")
    shutil.copyfile(rendered_path, render_output)
    return render_output


def render_scene(
    scene_path: Path,
    render_output: Path,
    width: int,
    height: int,
    camera: str | None,
) -> Path:
    """Open a saved scene, configure settings, and render an isometric PNG."""

    cmds = initialize_maya()
    open_scene(cmds, scene_path)
    render_camera = find_render_camera(cmds, camera)
    configure_render_camera(cmds, render_camera)
    configure_render_settings(cmds, width, height)
    return render_to_png(cmds, render_camera, width, height, render_output.resolve())


def main(argv: list[str] | None = None) -> int:
    """Run the Maya isometric preview renderer."""

    args = parse_args(argv)
    try:
        print("Feature 005.2 Maya: initializing Maya for render...")
        output = render_scene(
            args.scene,
            args.render_output,
            args.width,
            args.height,
            args.camera,
        )
        print(f"Feature 005.2 Maya: rendered preview {output}")
        return 0
    except Exception as exc:
        print(f"ERR_MAYA_RENDER: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
