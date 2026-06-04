"""Maya additive polish template for TuPhuongVoLo sandbox scenes.

Codex should copy and customize this file for one artist prompt.

Run only inside Maya Script Editor on a sandbox working scene:
    .../working/scene_agent_work.ma

Rules:
    - Do not run on original outputs/maya/*.ma scenes.
    - Do not delete or edit source walls, doors, or layout meshes.
    - Put all new objects under one GRP_agent_* group.
    - The artist can hide/delete that group or restore the sandbox backup.
"""

from __future__ import annotations

import maya.cmds as cmds

AGENT_GROUP = "GRP_agent_polish_v001"


def _assert_sandbox_scene() -> None:
    scene = cmds.file(query=True, sceneName=True) or ""
    normalized = scene.replace("\\", "/").lower()
    if "/working/scene_agent_work.ma" not in normalized:
        raise RuntimeError(
            "Safety stop: open the sandbox working/scene_agent_work.ma before running this script."
        )


def _material(name: str, color: tuple[float, float, float]) -> str:
    shader = cmds.shadingNode("lambert", asShader=True, name=name)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{name}SG")
    cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type="double3")
    cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader", force=True)
    return shading_group


def _cube(
    name: str,
    position: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: str,
    parent: str,
) -> str:
    node = cmds.polyCube(name=name, width=1, height=1, depth=1)[0]
    cmds.xform(node, translation=position, scale=scale, worldSpace=True)
    cmds.sets(node, edit=True, forceElement=material)
    cmds.parent(node, parent)
    return node


def _add_note(parent: str) -> None:
    note = cmds.spaceLocator(name="NOTE_agent_polish_review")[0]
    cmds.parent(note, parent)
    text = (
        "Agent polish layer. Artist review: toggle or delete "
        f"{AGENT_GROUP}; rollback with restore_agent_backup.ps1 if needed."
    )
    if not cmds.attributeQuery("artistReviewNote", node=note, exists=True):
        cmds.addAttr(note, longName="artistReviewNote", dataType="string")
    cmds.setAttr(f"{note}.artistReviewNote", text, type="string")


def run() -> None:
    _assert_sandbox_scene()

    if cmds.objExists(AGENT_GROUP):
        raise RuntimeError(f"Safety stop: {AGENT_GROUP} already exists. Use a new version name.")

    root = cmds.group(empty=True, name=AGENT_GROUP)
    wood = _material("mat_agent_warm_wood", (0.47, 0.29, 0.13))
    dark = _material("mat_agent_dark_edge", (0.16, 0.11, 0.08))

    # Example warehouse props. Codex should replace positions/scales from the prompt.
    _cube("agent_shelf_right_01", (4.0, 1.0, 1.8), (0.25, 2.0, 1.0), wood, root)
    _cube("agent_shelf_right_02", (4.0, 1.0, -0.2), (0.25, 2.0, 1.0), wood, root)
    _cube("agent_crate_center_01", (0.2, 0.35, 0.2), (0.7, 0.7, 0.7), wood, root)
    _cube("agent_crate_center_02", (1.0, 0.3, -0.4), (0.6, 0.6, 0.6), dark, root)

    light = cmds.pointLight(name="agent_warm_review_light", intensity=450, rgb=(1.0, 0.78, 0.48))
    light_transform = cmds.listRelatives(light, parent=True)[0]
    cmds.xform(light_transform, translation=(0.0, 4.0, 2.5), worldSpace=True)
    cmds.parent(light_transform, root)

    camera, _shape = cmds.camera(name="cam_agent_polish_review")
    cmds.xform(camera, translation=(5.5, 5.0, 5.5), rotation=(-45.0, 45.0, 0.0), worldSpace=True)
    cmds.parent(camera, root)

    _add_note(root)
    print(f"Created additive polish group: {AGENT_GROUP}")


run()
