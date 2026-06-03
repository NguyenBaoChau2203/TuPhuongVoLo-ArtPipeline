"""Enable Maya commandPort on localhost only for safe Antigravity/MCP connectivity.

This script should be manually executed inside the Maya Script Editor
within the sandbox working scene. It opens a command port bound only to
127.0.0.1 (localhost) to ensure security.
"""

import sys

try:
    import maya.cmds as cmds
    IN_MAYA = True
except ImportError:
    IN_MAYA = False


def enable_command_port() -> None:
    """Enable the commandPort on localhost if running inside Maya."""
    host = "127.0.0.1"
    port = 50007
    port_name = f"{host}:{port}"

    if not IN_MAYA:
        print(
            "Lỗi: Script này phải được chạy bên trong Autodesk Maya (Script Editor).",
            file=sys.stderr,
        )
        print(
            "Error: This script must be executed inside Autodesk Maya (Script Editor).",
            file=sys.stderr,
        )
        return

    try:
        # Check if port is already active
        if cmds.commandPort(port_name, query=True):
            print(f"Maya commandPort {port_name} đã được bật từ trước và đang hoạt động.")
            print(f"Maya commandPort {port_name} is already active and running.")
            return

        # Open the commandPort for python execution
        cmds.commandPort(name=port_name, sourceType="python")
        print(f"Đã kích hoạt thành công Maya commandPort tại địa chỉ {port_name}.")
        print(f"Successfully enabled Maya commandPort on {port_name}.")
    except Exception as exc:
        print(f"Lỗi khi kích hoạt commandPort: {exc}", file=sys.stderr)
        print(f"Failed to enable commandPort: {exc}", file=sys.stderr)


if __name__ == "__main__":
    enable_command_port()
