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
    """Small maya.cmds stand-in for prop builder tests."""

    def __init__(self) -> None:
        self.cubes: list[dict[str, object]] = []
        self.groups: list[str] = []
        self.parents: list[tuple[str, str]] = []
        self.transforms: dict[str, object] = {}

    def polyCube(self, name: str, width: float, height: float, depth: float):
        self.cubes.append(
            {
                "name": name,
                "size": (width, height, depth),
            }
        )
        return [name]

    def group(self, empty: bool, name: str):
        assert empty is True
        self.groups.append(name)
        return name

    def xform(self, node: str, **kwargs) -> None:
        self.transforms[node] = kwargs

    def sets(self, *args, **kwargs) -> None:
        return None

    def parent(self, node: str, parent: str) -> None:
        self.parents.append((node, parent))


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
        "box": "wooden_crate",
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
        assert scene_builder.has_procedural_prop(alias)


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
