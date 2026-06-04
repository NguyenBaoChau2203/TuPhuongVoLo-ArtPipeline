"""Tests for Feature 005 Maya build CLI wrapper that do not require Maya."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import build_maya_room as builder


class _FakeProcess:
    """Minimal subprocess.CompletedProcess stand-in for monkeypatched runs."""

    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _FakeMayaCmds:
    """Small maya.cmds stand-in for prop builder and build_scene tests."""

    def __init__(self) -> None:
        self.cubes: list[dict[str, object]] = []
        self.groups: list[str] = []
        self.parents: list[tuple[str, str]] = []
        self.transforms: dict[str, object] = {}
        self.materials: list[str] = []
        self.shading_groups: list[str] = []
        self.attrs: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self.connections: list[tuple[str, str]] = []
        self.assignments: list[tuple[str, str]] = []
        self.display_layers: list[str] = []
        self.display_layer_members: list[tuple[str, str]] = []
        self.locators: list[str] = []
        self.annotations: list[dict[str, str]] = []
        self.renames: list[tuple[str, str]] = []
        self.cameras: list[str] = []
        self.lights: list[str] = []
        self.facets: list[str] = []
        self.files: list[dict[str, object]] = []
        self.deleted: list[str] = []
        self.constraints: list[str] = []

    def polyCube(self, name: str, width: float, height: float, depth: float):
        self.cubes.append(
            {
                "name": name,
                "size": (width, height, depth),
            }
        )
        return [name]

    def polyCreateFacet(self, point: list, name: str):
        self.facets.append(name)
        return [name]

    def group(self, empty: bool, name: str):
        assert empty is True
        self.groups.append(name)
        return name

    def xform(self, node: str, **kwargs) -> None:
        self.transforms[node] = kwargs

    def shadingNode(self, _node_type: str, asShader: bool, name: str):
        assert asShader is True
        self.materials.append(name)
        return name

    def sets(self, *args, **kwargs):
        if kwargs.get("renderable") and kwargs.get("empty"):
            name = kwargs["name"]
            self.shading_groups.append(name)
            return name
        if kwargs.get("edit") and "forceElement" in kwargs:
            self.assignments.append((str(args[0]), str(kwargs["forceElement"])))
        return None

    def setAttr(self, attr: str, *args, **kwargs) -> None:
        self.attrs.append((attr, args, kwargs))

    def connectAttr(self, source: str, target: str, **_kwargs) -> None:
        self.connections.append((source, target))

    def parent(self, node: str, parent: str) -> None:
        self.parents.append((node, parent))

    def createDisplayLayer(self, name: str, empty: bool = True):
        self.display_layers.append(name)
        return name

    def editDisplayLayerMembers(self, layer: str, obj: str, **_kwargs) -> None:
        self.display_layer_members.append((layer, obj))

    def spaceLocator(self, name: str):
        self.locators.append(name)
        return [name]

    def annotate(self, node: str, text: str):
        shape_name = f"{node}_annotationShape"
        self.annotations.append({"node": node, "text": text, "shape": shape_name})
        return shape_name

    def listRelatives(self, node: str, parent: bool = False, **_kwargs):
        # Return a fake parent transform for annotation shapes and lights.
        return [f"{node}_transform"]

    def rename(self, old_name: str, new_name: str):
        self.renames.append((old_name, new_name))
        return new_name

    def camera(self, name: str):
        self.cameras.append(name)
        return [name, f"{name}Shape"]

    def directionalLight(self, name: str):
        self.lights.append(name)
        return name

    def ambientLight(self, name: str, intensity: float = 1.0):
        self.lights.append(name)
        return name

    def aimConstraint(self, *args, **kwargs):
        self.constraints.append("aimConstraint")
        return ["aimConstraint1"]

    def delete(self, *args) -> None:
        self.deleted.extend(args)

    def file(self, *args, **kwargs) -> None:
        self.files.append(kwargs)

    def currentUnit(self, **kwargs) -> None:
        pass


def write_svg(path: Path) -> Path:
    """Write a clean SVG with two room groups."""

    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="100" height="100">
  <g id="room_kho"><path d="M0 0 L10 0 L10 10 L0 10 Z"/></g>
  <g id="g2" inkscape:label="Sảnh chính"><path d="M20 0 L40 0 L40 10 L20 10 Z"/></g>
</svg>
""",
        encoding="utf-8",
    )
    return path


def write_prop_rotation_svg(path: Path) -> Path:
    """Write a clean SVG with one unrotated and one rotated prop marker."""

    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <g id="room_kho">
    <path d="M0 0 L100 0 L100 100 L0 100 Z"/>
    <g id="prop_shelf_unit"><rect x="10" y="10" width="20" height="8"/></g>
    <g id="prop_table_rot90"><rect x="40" y="40" width="16" height="12"/></g>
  </g>
</svg>
""",
        encoding="utf-8",
    )
    return path


def write_illustrator_x5f_svg(path: Path) -> Path:
    """Write an Illustrator-style SVG whose IDs encode underscores as x5F."""

    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">
  <g id="room_x5F_phong_x5F_kho">
    <path d="M0 0 L120 0 L120 80 L0 80 Z"/>
    <g id="prop_x5F_wooden_x5F_crate_x5F_01">
      <rect x="20" y="20" width="16" height="12"/>
    </g>
  </g>
</svg>
""",
        encoding="utf-8",
    )
    return path


def isolated_manifest(monkeypatch, tmp_path: Path) -> Path:
    """Redirect manifest lookups to a temp file."""

    manifest_path = tmp_path / "manifest" / "asset_manifest.json"
    monkeypatch.setattr(
        builder.asset_manifest,
        "resolve_manifest_path",
        lambda *args, **kwargs: manifest_path,
    )
    return manifest_path


def test_maya_scene_script_does_not_switch_viewports() -> None:
    """mayapy headless mode has no active viewport for cmds.lookThru."""

    script_path = builder.repo_root() / "scripts" / "maya" / "build_maya_room_scene.py"
    script_text = script_path.read_text(encoding="utf-8")

    for forbidden in ("lookThru(", "playblast(", "modelPanel(", "modelEditor("):
        assert forbidden not in script_text


def load_maya_scene_builder():
    """Load the Maya scene script as a plain Python module without Maya."""

    script_path = builder.repo_root() / "scripts" / "maya" / "build_maya_room_scene.py"
    spec = importlib.util.spec_from_file_location("build_maya_room_scene", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_maya_camera_framing_uses_room_bounds_and_padding() -> None:
    """Camera framing should scale from room bounds instead of a close span."""

    scene_builder = load_maya_scene_builder()

    framing = scene_builder.camera_framing_from_bounds((0.0, 0.0, 4.0, 2.0), 3.0)

    assert framing["center_x"] == 2.0
    assert framing["center_z"] == 1.0
    assert framing["target_y"] == 1.5
    assert framing["max_dimension"] == 4.0
    assert framing["camera_distance"] >= 4.0 * scene_builder.ISO_CAMERA_DISTANCE_FACTOR
    assert framing["orthographic_width"] >= (
        3.0 * 2.0 * scene_builder.ORTHOGRAPHIC_PADDING_FACTOR
    )


def test_maya_camera_framing_handles_wide_deep_and_tiny_rooms() -> None:
    """Framing must be deterministic for common aspect extremes and tiny input."""

    scene_builder = load_maya_scene_builder()

    wide = scene_builder.camera_framing_from_bounds((0.0, 0.0, 8.0, 2.0), 3.0)
    deep = scene_builder.camera_framing_from_bounds((0.0, 0.0, 2.0, 8.0), 3.0)
    tiny = scene_builder.camera_framing_from_bounds((0.0, 0.0, 0.1, 0.1), 3.0)

    assert wide["camera_distance"] >= 8.0 * scene_builder.ISO_CAMERA_DISTANCE_FACTOR
    assert deep["camera_distance"] >= 8.0 * scene_builder.ISO_CAMERA_DISTANCE_FACTOR
    assert wide["orthographic_width"] >= 8.0 * scene_builder.ORTHOGRAPHIC_PADDING_FACTOR
    assert deep["orthographic_width"] >= 8.0 * scene_builder.ORTHOGRAPHIC_PADDING_FACTOR
    assert tiny["max_dimension"] == 1.0
    assert tiny["orthographic_width"] >= scene_builder.MIN_ORTHOGRAPHIC_WIDTH


def test_maya_camera_framing_accounts_for_wall_height() -> None:
    """Taller walls need a wider orthographic frame in a 16:9 render."""

    scene_builder = load_maya_scene_builder()

    low_walls = scene_builder.camera_framing_from_bounds((0.0, 0.0, 4.0, 4.0), 1.0)
    tall_walls = scene_builder.camera_framing_from_bounds((0.0, 0.0, 4.0, 4.0), 4.0)

    assert tall_walls["orthographic_width"] > low_walls["orthographic_width"]
    assert tall_walls["target_y"] > low_walls["target_y"]


def test_maya_scene_bounds_include_svg_prop_marker_extents() -> None:
    """Camera bounds should include explicit prop centers and footprints."""

    scene_builder = load_maya_scene_builder()

    bounds, max_prop_height = scene_builder.scene_bounds_with_props(
        (0.0, 0.0, 1.0, 1.0),
        [
            {
                "prop_type": "prop_shelf_unit",
                "center_maya": [1.8, -0.6],
                "bbox_maya": [0.0, 0.0, 1.2, 0.6],
            }
        ],
        units_scale=0.01,
    )

    assert bounds[0] == 0.0
    assert bounds[1] < 0.0
    assert bounds[2] > 1.0
    assert bounds[3] == 1.0
    assert max_prop_height == scene_builder.PROCEDURAL_PROP_SIZES["shelf_unit"][1]


def test_maya_scene_bounds_ignore_invalid_prop_marker_data() -> None:
    """Malformed marker data must not crash camera planning."""

    scene_builder = load_maya_scene_builder()

    room_bounds = (0.0, 0.0, 1.0, 1.0)
    bounds, max_prop_height = scene_builder.scene_bounds_with_props(
        room_bounds,
        [
            {"prop_type": "prop_bed", "center_maya": ["bad", None]},
            {"prop_type": "prop_table", "bbox_maya": [0.0, 0.0, 10.0, 10.0]},
            "not-a-marker",
        ],
    )

    assert bounds == room_bounds
    assert max_prop_height == 0.0


def test_maya_preview_floor_color_falls_back_when_too_pale() -> None:
    """A near-white floor should get a visible preview fallback."""

    scene_builder = load_maya_scene_builder()

    assert scene_builder.preview_floor_color("#FFFFFF") == scene_builder.PREVIEW_FLOOR_COLOR_FALLBACK
    assert scene_builder.preview_floor_color("#E8E4DF") == scene_builder.PREVIEW_FLOOR_COLOR_FALLBACK
    assert scene_builder.preview_floor_color("#4A7C59") != scene_builder.PREVIEW_FLOOR_COLOR_FALLBACK


def test_maya_camera_framing_is_more_conservative_than_previous_polish() -> None:
    """005.2P2 prefers extra whitespace over any remaining top-edge crop."""

    scene_builder = load_maya_scene_builder()

    framing = scene_builder.camera_framing_from_bounds((0.0, 0.0, 4.0, 2.0), 3.0)
    previous_width = 4.0 * 2.0

    assert scene_builder.ORTHOGRAPHIC_PADDING_FACTOR >= 2.8
    assert framing["orthographic_width"] > previous_width * 2.0


def test_maya_scene_camera_uses_orthographic_room_framing() -> None:
    """The scene builder should create one room-aware orthographic iso camera."""

    script_path = builder.repo_root() / "scripts" / "maya" / "build_maya_room_scene.py"
    script_text = script_path.read_text(encoding="utf-8")

    assert "camera_framing_from_bounds" in script_text
    assert "orthographicWidth" in script_text
    assert "wall_height" in script_text
    assert "aimConstraint" in script_text
    assert "target_y" in script_text


def test_dry_run_builds_expected_ma_output_path(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.maya_output.name == "tu_phuong_vo_lo_kho_main_maya_v001.ma"
    assert plan.geometry_json.name == "tu_phuong_vo_lo_kho_main_blockout_v001.json"


def test_missing_svg_returns_error(tmp_path: Path, capsys) -> None:
    exit_code = builder.main(["--input", str(tmp_path / "missing.svg"), "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Không tìm thấy file SVG" in captured.err


def test_room_selection_by_normalized_vietnamese_name(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "Sảnh chính",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "sanh_chinh"


def test_room_selection_accepts_artist_name_for_illustrator_x5f_ids(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_illustrator_x5f_svg(tmp_path / "x5f_floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "phong_kho"
    assert plan.room.original_label == "room_x5F_phong_x5F_kho"
    assert plan.maya_output.name == "tu_phuong_vo_lo_phong_kho_main_maya_v001.ma"


def test_room_selection_still_accepts_legacy_encoded_x5f_room_name(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_illustrator_x5f_svg(tmp_path / "x5f_floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "x5f_phong_x5f_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "phong_kho"


def test_missing_room_error_lists_raw_decoded_and_internal_room_names(
    tmp_path: Path,
    capsys,
) -> None:
    svg = write_illustrator_x5f_svg(tmp_path / "x5f_floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "sanh_chinh",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "room_x5F_phong_x5F_kho -> room_phong_kho -> phong_kho" in captured.err


def test_missing_style_returns_clear_error(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(["--input", str(svg), "--style", "missing_style", "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Style preset không tồn tại" in captured.err


def test_missing_maya_executable_is_handled_gracefully(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--maya-path",
            str(tmp_path / "missing_mayapy.exe"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Maya" in captured.err or "mayapy" in captured.err


def test_actual_run_rejects_maya_or_mayabatch_path(tmp_path: Path, capsys) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    for executable_name in ("maya.exe", "mayabatch.exe"):
        fake_executable = tmp_path / executable_name
        fake_executable.write_text("not a real executable", encoding="utf-8")

        exit_code = builder.main(
            [
                "--input",
                str(svg),
                "--room",
                "kho",
                "--maya-path",
                str(fake_executable),
            ]
        )
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Feature 005 MVP chỉ hỗ trợ mayapy.exe cho actual run" in captured.err
        assert "maya.exe/mayabatch.exe chưa được hỗ trợ" in captured.err


def test_dry_run_allows_non_mayapy_path_for_planning(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    fake_maya = tmp_path / "maya.exe"
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--maya-path",
            str(fake_maya),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.maya_command[0] == str(fake_maya)


def test_dry_run_does_not_update_manifest(tmp_path: Path, monkeypatch) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not manifest_path.exists()


def test_generated_maya_command_includes_scene_script(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    command = builder.build_plan(args).maya_command

    assert command[0]
    assert any("build_maya_room_scene.py" in part for part in command)
    assert "--geometry-json" in command
    assert "--maya-output" in command


def test_geometry_json_payload_contains_boundary_and_walls(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    assert payload["room_name"] == "kho"
    assert len(payload["boundary_points"]) == 4
    assert len(payload["wall_segments"]) == 4
    assert payload["units"]["maya_linear"] == "meter"
    assert payload["opening_markers"] == []
    assert "floor_material_hint" not in payload
    assert "wall_material_hint" not in payload


def test_geometry_json_payload_contains_svg_prop_markers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_prop_markers.svg"),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    markers = payload["prop_markers"]
    assert [marker["prop_type"] for marker in markers] == ["shelf_unit", "wooden_crate"]
    assert markers[0]["original_label"] == "prop_shelf_unit"
    assert markers[0]["group_path"] == ["Layer 1", "Phòng Kho", "prop_shelf_unit"]
    assert markers[0]["center_svg"] == [45.0, 39.0]
    assert markers[0]["bbox_svg"] == [35.0, 35.0, 55.0, 43.0]
    assert markers[0]["center_local"] == [30.0, 14.0]
    assert markers[0]["center_maya"] == [0.3, -0.14]
    assert markers[1]["center_maya"][0] == 0.65
    assert round(markers[1]["center_maya"][1], 2) == -0.35


def test_geometry_json_payload_contains_prop_rotation_metadata(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_prop_rotation_svg(tmp_path / "prop_rotation.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    markers = payload["prop_markers"]
    assert [marker["prop_type"] for marker in markers] == ["shelf_unit", "table"]
    assert [marker["rotation_y_degrees"] for marker in markers] == [0, 90]


def test_geometry_json_payload_contains_material_color_hints(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = tmp_path / "material_tags.svg"
    svg.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <g id="room_kho">
    <g id="floor_material_wood"><path d="M0 0 L100 0 L100 100 L0 100 Z"/></g>
    <g id="wall_mat_stone"></g>
    <g id="prop_wooden_crate_01_mat_wood"><rect x="20" y="30" width="10" height="8"/></g>
    <g id="prop_table_material_metal"><rect x="40" y="30" width="10" height="8"/></g>
    <g id="prop_box_color_red"><rect x="60" y="30" width="10" height="8"/></g>
    <g id="prop_chair_mat_mystery"><rect x="80" y="30" width="10" height="8"/></g>
  </g>
</svg>
""",
        encoding="utf-8",
    )
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    assert payload["floor_material_hint"] == "wood"
    assert payload["wall_material_hint"] == "stone"
    markers = {marker["prop_type"]: marker for marker in payload["prop_markers"]}
    assert markers["wooden_crate"]["material_hint"] == "wood"
    assert markers["table"]["material_hint"] == "metal"
    assert markers["box"]["color_hint"] == "red"
    assert markers["chair"]["material_hint"] == "mystery"


def test_geometry_json_payload_contains_opening_markers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_opening_markers.svg"),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    markers = payload["opening_markers"]
    assert [(marker["marker_type"], marker["marker_name"]) for marker in markers] == [
        ("door", "main"),
        ("window", "back_01"),
    ]
    assert markers[0]["source_name"] == "door_main"
    assert markers[0]["group_path"] == ["Layer 1", "room_kho", "door_main"]
    assert markers[0]["center_svg"] == [16.0, 74.0]
    assert markers[0]["bbox_svg"] == [8.0, 72.0, 24.0, 76.0]
    assert markers[0]["center_local"] == [16.0, 74.0]
    assert markers[0]["center_maya"] == [0.16, -0.74]
    assert markers[1]["source_name"] == "window_back_01"
    assert markers[1]["center_maya"] == [0.9, -0.02]
    assert [marker["prop_type"] for marker in payload["prop_markers"]] == ["shelf_unit"]


def test_geometry_json_payload_contains_curved_barrel_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = tmp_path / "curved_barrel.svg"
    svg.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="240" height="460">\n'
        '  <g id="room_phong_kho"><polygon points="0,0 220,0 220,440 0,440"/></g>\n'
        '  <g id="prop_barrel_01">\n'
        '    <path d="M183.44,406.93c-16,0-28.9,2.43-28.9,5.44s12.94,5.45,28.9,5.45"/>\n'
        "  </g>\n"
        "</svg>\n",
        encoding="utf-8",
    )
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    markers = payload["prop_markers"]
    assert [marker["original_label"] for marker in markers] == ["prop_barrel_01"]
    assert markers[0]["prop_type"] == "barrel"
    assert markers[0]["bbox_svg"]
    assert markers[0]["center_svg"]
    assert markers[0]["center_maya"]
    assert any("fallback approximate path bbox" in warning for warning in markers[0]["warnings"])


def test_geometry_json_payload_contains_real_illustrator_sibling_props(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_real_grouped_room_props.svg"),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    assert payload["room_name"] == "phong_kho"
    markers = payload["prop_markers"]
    assert len(markers) == 5
    assert [marker["original_label"] for marker in markers] == [
        "prop_wooden_crate_01",
        "prop_shelf_unit_01",
        "prop_barrel_01",
        "prop_electrical_cabinet_01_mat_metal",
        "prop_floor_grate_01_mat_metal",
    ]
    assert [marker["prop_type"] for marker in markers] == [
        "wooden_crate",
        "shelf_unit",
        "barrel",
        "electrical_cabinet",
        "floor_grate",
    ]
    assert payload["opening_markers"][0]["source_name"] == "door_main"
    assert markers[3]["material_hint"] == "metal"
    assert markers[4]["material_hint"] == "metal"


def test_output_naming_follows_convention(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.maya_output.parent.name == "maya"
    assert plan.maya_output.name == "tu_phuong_vo_lo_kho_main_maya_v001.ma"


FIXTURE_DIR = Path(__file__).parent / "in"
PROP_TEMPLATE_SVG = (
    builder.repo_root()
    / "assets"
    / "2d"
    / "templates"
    / "illustrator_prop_marker_template.svg"
)
CANONICAL_PROP_MARKER_NAMES = [
    "prop_bed",
    "prop_table",
    "prop_chair",
    "prop_sofa",
    "prop_fridge",
    "prop_sink",
    "prop_kitchen_counter",
    "prop_cabinet",
    "prop_locker",
    "prop_plant",
    "prop_shelf_unit",
    "prop_wooden_crate",
]


def test_dry_run_reports_candidate_and_usable_room_counts(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        ["--input", str(svg), "--room", "kho", "--output-dir", str(tmp_path / "o"), "--dry-run"]
    )

    plan = builder.build_plan(args)

    assert plan.candidate_rooms == 2
    assert plan.usable_rooms == 2


def test_dry_run_with_illustrator_transform_fixture(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_transforms_shapes.svg"),
            "--room",
            "phong_ngu",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "phong_ngu"
    assert plan.transform_applied is True
    assert "rect" in plan.room.shape_kinds


def test_dry_run_reports_unsupported_elements(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_style_class.svg"),
            "--room",
            "bep",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert any("circle" in item for item in plan.unsupported_elements)


def test_dry_run_reports_svg_prop_markers(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_prop_markers.svg"),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert [marker.prop_type for marker in plan.room.prop_markers] == [
        "shelf_unit",
        "wooden_crate",
    ]


def test_dry_run_lists_prop_labels_and_zero_opening_diagnostic(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = tmp_path / "curved_barrel.svg"
    svg.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="240" height="460">\n'
        '  <g id="room_phong_kho"><polygon points="0,0 220,0 220,440 0,440"/></g>\n'
        '  <g id="prop_barrel_01">\n'
        '    <path d="M183.44,406.93c-16,0-28.9,2.43-28.9,5.44s12.94,5.45,28.9,5.45"/>\n'
        "  </g>\n"
        "</svg>\n",
        encoding="utf-8",
    )

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "prop_barrel_01 (barrel)" in captured.out
    assert "Loại prop: barrel=1" in captured.out
    assert "Opening marker SVG (0)" in captured.out
    assert "Không tìm thấy door_/window_ marker" in captured.out
    assert "Cảnh báo bbox xấp xỉ:" in captured.out
    assert "prop_barrel_01: dùng approximate path bbox cho 1 curved path shape(s)" in captured.out


def test_build_plan_warns_when_preflight_marker_count_exceeds_geometry(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "empty_marker.svg")
    svg.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <g id="room_kho">
    <path d="M0 0 L100 0 L100 100 L0 100 Z"/>
    <g id="prop_empty_01"></g>
  </g>
</svg>
""",
        encoding="utf-8",
    )
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.preflight_prop_marker_candidates == 1
    assert plan.room.prop_markers == []
    assert any("geometry chỉ emit 0" in warning for warning in plan.warnings)


def test_prop_showcase_fixture_dry_run_detects_supported_markers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_prop_showcase.svg"),
            "--room",
            "phong_showcase",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "phong_showcase"
    assert [marker.prop_type for marker in plan.room.prop_markers] == [
        "bed",
        "table",
        "chair",
        "sofa",
        "fridge",
        "sink",
        "kitchen_counter",
        "cabinet",
        "locker",
        "plant",
        "shelf_unit",
        "wooden_crate",
    ]


def test_prop_marker_template_dry_run_detects_all_canonical_markers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(PROP_TEMPLATE_SVG),
            "--room",
            "phong_marker_template",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.room.room_name == "phong_marker_template"
    assert [marker.original_label for marker in plan.room.prop_markers] == (
        CANONICAL_PROP_MARKER_NAMES
    )
    assert [marker.prop_type for marker in plan.room.prop_markers] == [
        name.removeprefix("prop_") for name in CANONICAL_PROP_MARKER_NAMES
    ]


def test_prop_marker_template_dry_run_does_not_update_manifest(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)

    exit_code = builder.main(
        [
            "--input",
            str(PROP_TEMPLATE_SVG),
            "--room",
            "phong_marker_template",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert not manifest_path.exists()
    assert "Prop marker SVG (12):" in captured.out
    assert "ghi manifest" in captured.out


def test_prop_showcase_dry_run_does_not_update_manifest(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)

    exit_code = builder.main(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_prop_showcase.svg"),
            "--room",
            "phong_showcase",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert not manifest_path.exists()
    assert "Prop marker SVG (12):" in captured.out
    assert "tu_phuong_vo_lo_phong_showcase_main_preview_v001.png" in captured.out
    assert "ghi manifest" in captured.out


def test_prop_showcase_render_preview_planning_still_works(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_prop_showcase.svg"),
            "--room",
            "phong_showcase",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.render_preview is True
    assert plan.render_output is not None
    assert plan.render_output.name == "tu_phuong_vo_lo_phong_showcase_main_preview_v001.png"
    assert any("render_maya_room_preview.py" in part for part in plan.render_command)


def test_maya_scene_builder_has_marker_placeholder_helpers() -> None:
    scene_builder = load_maya_scene_builder()

    assert scene_builder.prop_placeholder_size("shelf_unit") == (0.8, 1.8, 0.35)
    assert scene_builder.prop_placeholder_size(
        "single_bed"
    ) == scene_builder.prop_placeholder_size("bed")
    assert scene_builder.prop_placeholder_size("unknown_type") == scene_builder.GENERIC_PROP_SIZE
    assert scene_builder.safe_maya_name("wooden crate") == "wooden_crate"
    assert scene_builder.normalize_prop_type("prop_couch") == "sofa"
    assert scene_builder.normalize_prop_type("refrigerator") == "fridge"
    assert scene_builder.marker_center_maya({"center_maya": [0.3, -0.14]}) == (0.3, -0.14)
    assert scene_builder.opening_marker_center_maya({"center_maya": [0.16, -0.74]}) == (
        0.16,
        -0.74,
    )
    assert scene_builder.opening_marker_size("door") == (0.7, 2.0, 0.06)


def test_maya_scene_builder_uses_known_prop_definition_dimensions() -> None:
    scene_builder = load_maya_scene_builder()

    expected_sizes = {
        "shelf_unit": (0.8, 1.8, 0.35),
        "wooden_crate": (0.45, 0.45, 0.45),
        "table": (1.0, 0.75, 0.65),
        "chair": (0.45, 0.85, 0.45),
        "bed": (0.9, 0.55, 1.6),
        "cabinet": (0.8, 1.3, 0.45),
        "barrel": (0.45, 0.7, 0.45),
        "box": (0.35, 0.35, 0.35),
    }

    assert scene_builder.PROP_DEFINITION_SIZES == expected_sizes
    for prop_type, size in expected_sizes.items():
        assert scene_builder.has_prop_definition(prop_type)
        assert scene_builder.prop_placeholder_size(prop_type) == size


def test_maya_scene_builder_maps_supported_prop_types_to_procedural_builders() -> None:
    scene_builder = load_maya_scene_builder()

    expected = {
        "bed",
        "table",
        "chair",
        "sofa",
        "fridge",
        "sink",
        "kitchen_counter",
        "cabinet",
        "locker",
        "plant",
        "shelf_unit",
        "wooden_crate",
    }

    assert expected <= set(scene_builder.PROP_BLOCKOUT_BUILDERS)
    for prop_type in expected:
        assert scene_builder.has_procedural_prop(prop_type)
        assert scene_builder.prop_placeholder_size(prop_type) != scene_builder.GENERIC_PROP_SIZE


def test_maya_scene_builder_normalizes_required_prop_aliases() -> None:
    scene_builder = load_maya_scene_builder()

    aliases = {
        "shelf": "shelf_unit",
        "shelving": "shelf_unit",
        "crate": "wooden_crate",
        "box": "box",
        "cardboard_box": "box",
        "wooden_barrel": "barrel",
        "single_bed": "bed",
        "desk": "table",
        "couch": "sofa",
        "refrigerator": "fridge",
        "counter": "kitchen_counter",
        "cupboard": "cabinet",
        "potted_plant": "plant",
    }

    for alias, canonical in aliases.items():
        assert scene_builder.normalize_prop_type(alias) == canonical
        assert scene_builder.has_procedural_prop(alias) or scene_builder.has_prop_definition(alias)


def test_maya_scene_builder_uses_maya_safe_part_suffix_helpers() -> None:
    scene_builder = load_maya_scene_builder()

    assert scene_builder.side_token(-1) == "left"
    assert scene_builder.side_token(1) == "right"
    assert scene_builder.depth_token(-1) == "front"
    assert scene_builder.depth_token(1) == "back"
    assert scene_builder.corner_token(-1, -1) == "left_front"
    assert scene_builder.corner_token(1, 1) == "right_back"


def test_maya_scene_builder_creates_deterministic_opening_placeholders() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_opening_markers(
        cmds,
        [
            {
                "marker_type": "door",
                "marker_name": "main",
                "source_name": "door_main",
                "center_maya": [0.16, -0.74],
            },
            {
                "marker_type": "window",
                "marker_name": "back_01",
                "source_name": "window_back_01",
                "center_maya": [0.9, -0.02],
            },
        ],
        "openings",
    )

    assert created == 2
    assert [cube["name"] for cube in cmds.cubes] == ["door_main_01", "window_back_01"]
    assert cmds.transforms["door_main_01"]["translation"] == (0.16, 1.0, -0.74)
    assert cmds.transforms["window_back_01"]["translation"] == (0.9, 1.35, -0.02)
    assert ("door_main_01", "openings") in cmds.parents
    assert ("window_back_01", "openings") in cmds.parents


def test_maya_scene_builder_names_duplicate_opening_placeholders() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_opening_markers(
        cmds,
        [
            {"marker_type": "window", "marker_name": "back_01", "center_maya": [0.9, -0.02]},
            {"marker_type": "window", "marker_name": "back_01", "center_maya": [1.1, -0.02]},
            {"marker_type": "door", "marker_name": "main", "center_maya": [0.16, -0.74]},
            {"marker_type": "door", "marker_name": "main", "center_maya": [0.4, -0.74]},
        ],
        "openings",
    )

    assert created == 4
    assert [cube["name"] for cube in cmds.cubes] == [
        "window_back_01",
        "window_back_01_02",
        "door_main_01",
        "door_main_02",
    ]


def test_maya_scene_builder_wires_openings_group() -> None:
    script_path = builder.repo_root() / "scripts" / "maya" / "build_maya_room_scene.py"
    script_text = script_path.read_text(encoding="utf-8")

    assert "opening_markers" in script_text
    assert "create_svg_opening_markers" in script_text
    assert 'name="openings"' in script_text


def test_procedural_prop_child_names_do_not_use_signed_suffixes() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    for prop_type in ("table", "chair", "sofa", "shelf_unit"):
        scene_builder.create_procedural_prop(
            cmds,
            f"prop_{prop_type}_01",
            prop_type,
            (1.0, -2.0),
            None,
            "MAT_props",
            "MAT_prop_details",
            "props",
        )

    cube_names = {str(cube["name"]) for cube in cmds.cubes}
    assert not any("-" in name for name in cube_names)
    assert "prop_table_01_leg_left_front" in cube_names
    assert "prop_table_01_leg_right_back" in cube_names
    assert "prop_chair_01_leg_left_back" in cube_names
    assert "prop_chair_01_leg_right_front" in cube_names
    assert "prop_sofa_01_arm_left" in cube_names
    assert "prop_sofa_01_arm_right" in cube_names
    assert "prop_shelf_unit_01_side_left" in cube_names
    assert "prop_shelf_unit_01_side_right" in cube_names


def test_maya_scene_builder_uses_procedural_group_and_generic_fallback() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_prop_markers(
        cmds,
        [
            {
                "prop_type": "couch",
                "center_maya": [1.0, -2.0],
                "bbox_svg": [0.0, 0.0, 80.0, 40.0],
            },
            {
                "prop_type": "unknown_totem",
                "center_maya": [2.0, -3.0],
                "bbox_svg": [0.0, 0.0, 50.0, 50.0],
            },
        ],
        "MAT_props",
        "MAT_prop_details",
        "props",
        units_scale=0.01,
    )

    assert created == 2
    assert "prop_sofa_01" in cmds.groups
    assert any(cube["name"] == "prop_sofa_01_seat" for cube in cmds.cubes)
    fallback = next(cube for cube in cmds.cubes if cube["name"] == "prop_unknown_totem_01")
    assert fallback["size"] == scene_builder.GENERIC_PROP_SIZE
    assert ("prop_unknown_totem_01", "props") in cmds.parents


def test_maya_scene_builder_uses_known_cube_dimensions_for_simple_props() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_prop_markers(
        cmds,
        [
            {"prop_type": "barrel", "center_maya": [1.0, -2.0]},
            {"name": "box", "center_maya": [2.0, -3.0]},
            {"prop_type": "unknown_totem", "center_maya": [3.0, -4.0]},
        ],
        "MAT_props",
        "MAT_prop_details",
        "props",
    )

    assert created == 3
    cubes_by_name = {cube["name"]: cube for cube in cmds.cubes}
    assert cubes_by_name["prop_barrel_01"]["size"] == scene_builder.prop_placeholder_size("barrel")
    assert cubes_by_name["prop_box_01"]["size"] == scene_builder.prop_placeholder_size("box")
    assert cubes_by_name["prop_unknown_totem_01"]["size"] == scene_builder.GENERIC_PROP_SIZE


def test_maya_scene_builder_creates_real_illustrator_props_under_props_group() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_prop_markers(
        cmds,
        [
            {"prop_type": "wooden_crate", "center_maya": [0.25, -0.84]},
            {"prop_type": "shelf_unit", "center_maya": [1.21, -0.36]},
            {"prop_type": "barrel", "center_maya": [0.66, -0.64]},
            {
                "prop_type": "electrical_cabinet",
                "center_maya": [0.15, -0.32],
                "material_hint": "metal",
            },
            {
                "prop_type": "floor_grate",
                "center_maya": [1.38, -0.93],
                "material_hint": "metal",
            },
        ],
        "MAT_props",
        "MAT_prop_details",
        "props",
        material_overrides={},
    )

    assert created == 5
    assert ("prop_wooden_crate_01", "props") in cmds.parents
    assert ("prop_shelf_unit_01", "props") in cmds.parents
    assert ("prop_barrel_01", "props") in cmds.parents
    assert ("prop_electrical_cabinet_01", "props") in cmds.parents
    assert ("prop_floor_grate_01", "props") in cmds.parents
    cubes_by_name = {cube["name"]: cube for cube in cmds.cubes}
    assert cubes_by_name["prop_electrical_cabinet_01"]["size"] == scene_builder.GENERIC_PROP_SIZE
    assert cubes_by_name["prop_floor_grate_01"]["size"] == scene_builder.GENERIC_PROP_SIZE


def test_maya_scene_builder_creates_deterministic_material_for_supported_prop_hint() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_prop_markers(
        cmds,
        [
            {"prop_type": "table", "center_maya": [1.0, -2.0], "material_hint": "metal"},
            {"prop_type": "box", "center_maya": [2.0, -3.0], "color_hint": "red"},
            {"prop_type": "chair", "center_maya": [3.0, -4.0], "material_hint": "mystery"},
        ],
        "MAT_props",
        "MAT_prop_details",
        "props",
        material_overrides={},
    )

    assert created == 3
    assert "mat_tpv_metal" in cmds.materials
    assert "mat_tpv_red" in cmds.materials
    assert "mat_tpv_mystery" not in cmds.materials
    assert ("mat_tpv_metal.outColor", "mat_tpv_metalSG.surfaceShader") in cmds.connections
    assert ("mat_tpv_red.outColor", "mat_tpv_redSG.surfaceShader") in cmds.connections
    assert ("prop_box_01", "mat_tpv_redSG") in cmds.assignments
    assert any(node.startswith("prop_table_01_") and sg == "mat_tpv_metalSG" for node, sg in cmds.assignments)


def test_maya_scene_builder_reuses_material_hint_nodes() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    cache: dict[str, str] = {}

    first = scene_builder.material_from_hints(cmds, "wood", None, cache)
    second = scene_builder.material_from_hints(cmds, "wood", None, cache)

    assert first == "mat_tpv_woodSG"
    assert second == "mat_tpv_woodSG"
    assert cmds.materials.count("mat_tpv_wood") == 1


def test_maya_scene_builder_prop_marker_output_is_deterministic() -> None:
    scene_builder = load_maya_scene_builder()
    markers = [
        {"prop_type": "shelf_unit", "center_maya": [1.0, -2.0]},
        {"prop_type": "wooden_crate", "center_maya": [2.0, -3.0]},
        {"prop_type": "table", "center_maya": [3.0, -4.0]},
        {"prop_type": "chair", "center_maya": [4.0, -5.0]},
        {"prop_type": "unknown_totem", "center_maya": [5.0, -6.0]},
    ]

    def snapshot() -> tuple[object, ...]:
        cmds = _FakeMayaCmds()
        created = scene_builder.create_svg_prop_markers(
            cmds,
            markers,
            "MAT_props",
            "MAT_prop_details",
            "props",
        )
        return created, cmds.groups, cmds.cubes, cmds.parents, cmds.transforms

    assert snapshot() == snapshot()


def test_maya_scene_builder_applies_marker_y_rotation_to_props() -> None:
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()

    created = scene_builder.create_svg_prop_markers(
        cmds,
        [
            {
                "prop_type": "shelf_unit",
                "center_maya": [1.0, -2.0],
                "rotation_y_degrees": 90,
                "bbox_svg": [0.0, 0.0, 80.0, 40.0],
            },
            {
                "prop_type": "unknown_totem",
                "center_maya": [2.0, -3.0],
                "rotation_y_degrees": 270,
                "bbox_svg": [0.0, 0.0, 50.0, 50.0],
            },
        ],
        "MAT_props",
        "MAT_prop_details",
        "props",
        units_scale=0.01,
    )

    assert created == 2
    assert cmds.transforms["prop_shelf_unit_01"]["rotation"] == (0.0, 90.0, 0.0)
    assert cmds.transforms["prop_shelf_unit_01"]["pivots"] == (1.0, 0.0, -2.0)
    assert cmds.transforms["prop_unknown_totem_01"]["rotation"] == (0.0, 270.0, 0.0)


def test_maya_scene_builder_prefers_svg_markers_over_preset_props() -> None:
    script_path = builder.repo_root() / "scripts" / "maya" / "build_maya_room_scene.py"
    script_text = script_path.read_text(encoding="utf-8")

    assert "prop_markers" in script_text
    assert "create_svg_prop_markers" in script_text
    assert 'name="props"' in script_text
    assert "prop_{name_type}_" in script_text
    assert "replace" in script_text or "room-preset auto props" in script_text


def test_dry_run_on_illustrator_fixture_leaves_manifest_untouched(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)

    exit_code = builder.main(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_nested_groups.svg"),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert not manifest_path.exists()
    assert "không ghi manifest" in captured.out


# --- Feature 005.2: Maya isometric PNG preview render ---


def fake_mayapy(tmp_path: Path) -> Path:
    """Create a fake mayapy.exe accepted by actual-run validation."""

    path = tmp_path / "mayapy.exe"
    path.write_text("fake mayapy", encoding="utf-8")
    return path


def test_build_plan_includes_render_settings_when_enabled(
    tmp_path: Path, monkeypatch
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--render-width",
            "800",
            "--render-height",
            "600",
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.render_preview is True
    assert plan.render_width == 800
    assert plan.render_height == 600
    assert plan.render_output is not None
    assert any("render_maya_room_preview.py" in part for part in plan.render_command)
    assert "--scene" in plan.render_command
    assert "--render-output" in plan.render_command


def test_build_plan_render_disabled_by_default(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.render_preview is False
    assert plan.render_output is None
    assert plan.render_command == []


def test_render_output_follows_naming_convention(tmp_path: Path, monkeypatch) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--dry-run",
        ]
    )

    plan = builder.build_plan(args)

    assert plan.render_output is not None
    assert plan.render_output.parent.name == "preview"
    assert plan.render_output.name == "tu_phuong_vo_lo_kho_main_preview_v001.png"


def test_dry_run_render_preview_prints_png_path_and_size(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "tu_phuong_vo_lo_kho_main_preview_v001.png" in captured.out
    assert "1280x720" in captured.out
    assert "không render" in captured.out


def test_dry_run_render_preview_does_not_update_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not manifest_path.exists()


def test_dry_run_render_preview_does_not_create_files(
    tmp_path: Path, monkeypatch
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")

    builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--render-preview",
            "--dry-run",
        ]
    )

    preview_dir = tmp_path / "outputs" / "preview"
    pngs = list(preview_dir.glob("*.png")) if preview_dir.exists() else []
    assert pngs == []


def test_actual_run_renders_png_and_updates_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    mayapy = fake_mayapy(tmp_path)

    def fake_run(command, **kwargs):
        if any("build_maya_room_scene.py" in part for part in command):
            output = Path(command[command.index("--maya-output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("//Maya ASCII", encoding="utf-8")
        elif any("render_maya_room_preview.py" in part for part in command):
            output = Path(command[command.index("--render-output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"\x89PNG\r\n")
        return _FakeProcess(0)

    monkeypatch.setattr(builder.subprocess, "run", fake_run)

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--maya-path",
            str(mayapy),
            "--render-preview",
        ]
    )

    assert exit_code == 0
    png = tmp_path / "outputs" / "preview" / "tu_phuong_vo_lo_kho_main_preview_v001.png"
    assert png.exists()
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    stages = {entry["stage"] for entry in entries}
    assert "maya" in stages
    assert "preview" in stages


def test_actual_run_missing_png_is_error(tmp_path: Path, monkeypatch, capsys) -> None:
    manifest_path = isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    mayapy = fake_mayapy(tmp_path)

    def fake_run(command, **kwargs):
        if any("build_maya_room_scene.py" in part for part in command):
            output = Path(command[command.index("--maya-output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("//Maya ASCII", encoding="utf-8")
        # Render command intentionally produces no PNG.
        return _FakeProcess(0)

    monkeypatch.setattr(builder.subprocess, "run", fake_run)

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--maya-path",
            str(mayapy),
            "--render-preview",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ERR_RENDER_MISSING" in captured.err
    # The .ma manifest entry exists, but no preview entry was added.
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    stages = [entry["stage"] for entry in entries]
    assert "preview" not in stages


def test_actual_run_render_failure_returns_error(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg = write_svg(tmp_path / "floorplan.svg")
    mayapy = fake_mayapy(tmp_path)

    def fake_run(command, **kwargs):
        if any("build_maya_room_scene.py" in part for part in command):
            output = Path(command[command.index("--maya-output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("//Maya ASCII", encoding="utf-8")
            return _FakeProcess(0)
        return _FakeProcess(2)

    monkeypatch.setattr(builder.subprocess, "run", fake_run)

    exit_code = builder.main(
        [
            "--input",
            str(svg),
            "--room",
            "kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--maya-path",
            str(mayapy),
            "--render-preview",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "ERR_RENDER_FAILED" in captured.err


def test_render_preview_still_rejects_maya_or_mayabatch(
    tmp_path: Path, capsys
) -> None:
    svg = write_svg(tmp_path / "floorplan.svg")

    for executable_name in ("maya.exe", "mayabatch.exe"):
        fake_executable = tmp_path / executable_name
        fake_executable.write_text("not a real executable", encoding="utf-8")

        exit_code = builder.main(
            [
                "--input",
                str(svg),
                "--room",
                "kho",
                "--maya-path",
                str(fake_executable),
                "--render-preview",
            ]
        )
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Feature 005 MVP chỉ hỗ trợ mayapy.exe cho actual run" in captured.err


# --- Feature 008B: Root-level Illustrator SVG room fixture in Maya build ---


def test_geometry_json_payload_contains_root_level_room_props(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """build_maya_room geometry JSON must include props from root svg id phong_kho."""
    isolated_manifest(monkeypatch, tmp_path)
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(FIXTURE_DIR / "illustrator_root_level_room.svg"),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    assert payload["room_name"] == "phong_kho"
    markers = payload["prop_markers"]
    assert len(markers) == 2
    prop_types = [marker["prop_type"] for marker in markers]
    assert "shelf_unit" in prop_types
    assert "wooden_crate" in prop_types

    opening_markers = payload["opening_markers"]
    assert len(opening_markers) == 1
    assert opening_markers[0]["marker_type"] == "door"
    assert opening_markers[0]["marker_name"] == "main"


def test_geometry_json_payload_contains_opening_from_data_name_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    isolated_manifest(monkeypatch, tmp_path)
    svg_path = tmp_path / "door_data_name.svg"
    svg_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" id="phong_kho" width="120" height="80">\n'
        '  <g id="room_phong_kho"><polygon points="0,0 120,0 120,80 0,80"/></g>\n'
        '  <g id="some_exported_id" data-name="door_main"><rect x="8" y="72" width="16" height="4"/></g>\n'
        "</svg>\n",
        encoding="utf-8",
    )
    args = builder.build_parser().parse_args(
        [
            "--input",
            str(svg_path),
            "--room",
            "phong_kho",
            "--output-dir",
            str(tmp_path / "outputs"),
            "--dry-run",
        ]
    )
    plan = builder.build_plan(args)

    builder.write_geometry_json(plan)
    payload = json.loads(plan.geometry_json.read_text(encoding="utf-8"))

    opening_markers = payload["opening_markers"]
    assert len(opening_markers) == 1
    assert opening_markers[0]["marker_type"] == "door"
    assert opening_markers[0]["marker_name"] == "main"
    assert opening_markers[0]["source_name"] == "door_main"


# --- Feature 008D Phase 2: Maya scene layout polish ---


def _minimal_geometry_data(
    room_name: str = "phong_kho",
    prop_markers: list | None = None,
    opening_markers: list | None = None,
) -> dict:
    """Return a minimal geometry JSON dict for build_scene tests."""
    return {
        "room_name": room_name,
        "style_preset": {
            "floor_color": "#A2B296",
            "wall_color": "#D0D0D0",
        },
        "room_preset": {},
        "units": {"scale": 0.01},
        "boundary_points": [[0, 0], [2.2, 0], [2.2, 4.4], [0, 4.4]],
        "wall_segments": [
            {"start": [0, 0], "end": [2.2, 0]},
            {"start": [2.2, 0], "end": [2.2, 4.4]},
            {"start": [2.2, 4.4], "end": [0, 4.4]},
            {"start": [0, 4.4], "end": [0, 0]},
        ],
        "prop_markers": prop_markers or [],
        "opening_markers": opening_markers or [],
    }


def test_build_scene_creates_display_layers(tmp_path: Path) -> None:
    """build_scene must create LYR_walls, LYR_props, LYR_floor, LYR_lights."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data()
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    assert "LYR_walls" in cmds.display_layers
    assert "LYR_props" in cmds.display_layers
    assert "LYR_floor" in cmds.display_layers
    assert "LYR_lights" in cmds.display_layers


def test_build_scene_assigns_objects_to_display_layers(tmp_path: Path) -> None:
    """Groups must be assigned to correct display layers."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data()
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    layer_map = {obj: layer for layer, obj in cmds.display_layer_members}
    assert layer_map.get("walls") == "LYR_walls"
    assert layer_map.get("props") == "LYR_props"
    assert layer_map.get("lights") == "LYR_lights"
    assert layer_map.get("floor_blockout") == "LYR_floor"


def test_build_scene_wall_material_has_transparency(tmp_path: Path) -> None:
    """Wall material must have transparency set for blockout readability."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data()
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    # Find the transparency setAttr call for MAT_wall
    wall_transparency_set = [
        (attr, args, kwargs)
        for attr, args, kwargs in cmds.attrs
        if "MAT_wall" in attr and "transparency" in attr
    ]
    assert len(wall_transparency_set) > 0, "Wall material must have transparency"
    # Transparency values must be > 0
    transparency_args = wall_transparency_set[0][1]
    assert all(v > 0.0 for v in transparency_args)


def test_build_scene_uses_reduced_wall_height(tmp_path: Path) -> None:
    """Walls must use blockout height (<=1.8m) instead of full 3m default."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data()
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    wall_cubes = [c for c in cmds.cubes if str(c["name"]).startswith("wall_")]
    assert len(wall_cubes) >= 4
    for wall in wall_cubes:
        # height is the second element of size tuple
        assert wall["size"][1] <= scene_builder.BLOCKOUT_WALL_HEIGHT


def test_build_scene_creates_prop_type_materials(tmp_path: Path) -> None:
    """Different prop types must get distinct materials."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data(
        prop_markers=[
            {"prop_type": "wooden_crate", "center_maya": [0.5, 1.0]},
            {"prop_type": "barrel", "center_maya": [1.0, 1.0]},
            {"prop_type": "shelf_unit", "center_maya": [1.5, 1.0]},
        ]
    )
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    # Check that type-specific materials were created
    assert "MAT_prop_wooden_crate" in cmds.materials
    assert "MAT_prop_barrel" in cmds.materials
    assert "MAT_prop_shelf_unit" in cmds.materials


def test_build_scene_material_hint_overrides_prop_type(tmp_path: Path) -> None:
    """material_hint=metal must produce a metal material regardless of prop type."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data(
        prop_markers=[
            {
                "prop_type": "electrical_cabinet",
                "center_maya": [0.5, 1.0],
                "material_hint": "metal",
            },
        ]
    )
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    assert "MAT_prop_metal" in cmds.materials


def test_build_scene_creates_scene_notes(tmp_path: Path) -> None:
    """build_scene must create ARTIST_NOTES group with annotation."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data(
        prop_markers=[
            {"prop_type": "barrel", "center_maya": [0.5, 1.0]},
        ]
    )
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    assert "ARTIST_NOTES" in cmds.groups
    assert any("NOTE_phong_kho_info" in loc for loc in cmds.locators)
    assert len(cmds.annotations) > 0
    annotation_text = cmds.annotations[0]["text"]
    assert "phong_kho" in annotation_text
    assert "Props: 1" in annotation_text
    assert "Openings: 0" in annotation_text


def test_build_scene_notes_include_approx_bbox_warning(tmp_path: Path) -> None:
    """Scene notes must mention approximate bbox when fallback warnings exist."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data(
        prop_markers=[
            {
                "prop_type": "barrel",
                "center_maya": [0.5, 1.0],
                "warnings": ["fallback approximate path bbox used"],
            },
        ]
    )
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    assert len(cmds.annotations) > 0
    annotation_text = cmds.annotations[0]["text"]
    assert "approximate" in annotation_text.lower()


def test_build_scene_camera_naming_is_deterministic(tmp_path: Path) -> None:
    """Camera must follow cam_{room}_iso naming convention."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data(room_name="phong_kho")
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    assert "cam_phong_kho_iso" in cmds.cameras


def test_build_scene_group_hierarchy(tmp_path: Path) -> None:
    """Scene must have correct group hierarchy under GRP_{room}_blockout."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    data = _minimal_geometry_data()
    output = tmp_path / "test.ma"

    scene_builder.build_scene(cmds, data, output)

    assert "GRP_phong_kho_blockout" in cmds.groups
    assert "walls" in cmds.groups
    assert "props" in cmds.groups
    assert "lights" in cmds.groups
    assert "ARTIST_NOTES" in cmds.groups

    parent_map = {child: parent for child, parent in cmds.parents}
    assert parent_map.get("walls") == "GRP_phong_kho_blockout"
    assert parent_map.get("props") == "GRP_phong_kho_blockout"
    assert parent_map.get("lights") == "GRP_phong_kho_blockout"
    assert parent_map.get("ARTIST_NOTES") == "GRP_phong_kho_blockout"


def test_build_scene_display_layer_constants_are_correct() -> None:
    """Display layer constant names must match expectations."""
    scene_builder = load_maya_scene_builder()
    assert scene_builder.DISPLAY_LAYER_WALLS == "LYR_walls"
    assert scene_builder.DISPLAY_LAYER_PROPS == "LYR_props"
    assert scene_builder.DISPLAY_LAYER_FLOOR == "LYR_floor"
    assert scene_builder.DISPLAY_LAYER_LIGHTS == "LYR_lights"


def test_build_scene_blockout_wall_height_constant() -> None:
    """BLOCKOUT_WALL_HEIGHT must be less than DEFAULT_WALL_HEIGHT."""
    scene_builder = load_maya_scene_builder()
    assert scene_builder.BLOCKOUT_WALL_HEIGHT < scene_builder.DEFAULT_WALL_HEIGHT
    assert scene_builder.BLOCKOUT_WALL_HEIGHT == 1.8


def test_resolve_prop_material_returns_distinct_materials() -> None:
    """resolve_prop_material must return different materials for different types."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    cache: dict[str, str] = {}

    crate_mat = scene_builder.resolve_prop_material(cmds, "wooden_crate", None, cache)
    barrel_mat = scene_builder.resolve_prop_material(cmds, "barrel", None, cache)
    unknown_mat = scene_builder.resolve_prop_material(cmds, "unknown_thing", None, cache)

    assert crate_mat is not None
    assert barrel_mat is not None
    assert crate_mat != barrel_mat
    assert unknown_mat is None  # Unknown types get default


def test_resolve_prop_material_metal_hint_priority() -> None:
    """material_hint=metal must override prop type."""
    scene_builder = load_maya_scene_builder()
    cmds = _FakeMayaCmds()
    cache: dict[str, str] = {}

    metal_mat = scene_builder.resolve_prop_material(cmds, "barrel", "metal", cache)
    assert metal_mat is not None
    assert "MAT_prop_metal" in cmds.materials


def test_build_scene_prop_type_material_colors_exist() -> None:
    """PROP_TYPE_MATERIAL_COLORS must have entries for common prop types."""
    scene_builder = load_maya_scene_builder()
    required_types = [
        "wooden_crate", "barrel", "shelf_unit", "electrical_cabinet", "floor_grate",
    ]
    for prop_type in required_types:
        assert prop_type in scene_builder.PROP_TYPE_MATERIAL_COLORS, (
            f"Missing material color for {prop_type}"
        )
