"""
props_library.py — TuPhuongVoLo-ArtPipeline (Blender Script)

Purpose:
    Library of placeholder prop generators for isometric room scenes.
    Creates basic geometry for furniture and objects defined in room presets.

Status: PLACEHOLDER — TODO: Implement prop generators

See: specs/001-floorplan-to-isometric-room/spec.md
"""


def create_prop(prop_name: str, position: tuple = (0, 0, 0)) -> None:
    """Create a placeholder prop at the given position.

    Args:
        prop_name: Name from room_presets.yaml (e.g., 'shelf_unit', 'wooden_crate')
        position: (x, y, z) world position
    """
    # TODO: Implement prop generators for each type:
    # - shelf_unit: tall rectangular box
    # - wooden_crate: cube with slight variation
    # - cardboard_box: smaller cube
    # - console_desk: L-shaped box
    # - office_chair: cylinder + box
    # - monitor_screen: thin tall rectangle
    # - dining_table: slab on legs
    # - metal_bed_frame: low rectangle
    # - reception_desk: curved front box
    # - glass_cabinet: transparent box
    # - lab_table: simple slab
    print(f"TODO: Create prop '{prop_name}' at {position}")


def place_props_for_room(room_preset: dict, room_bounds: tuple) -> None:
    """Place all props for a room based on its preset and boundaries.

    Args:
        room_preset: Preset dict from config/room_presets.yaml
        room_bounds: (min_x, min_y, max_x, max_y) room bounding box
    """
    # TODO: Implement placement strategies:
    # - along_wall: distribute evenly along specified wall
    # - center: place at room center
    # - corner: place in room corner
    # - at_desk: offset from desk position
    # - on_shelf: stack on shelf
    # - entrance: place at room entrance
    print(f"TODO: Place props for room preset")
