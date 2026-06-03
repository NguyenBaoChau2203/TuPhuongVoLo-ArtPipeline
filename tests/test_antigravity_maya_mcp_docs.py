"""Unit tests for Antigravity + Maya MCP sandbox integration documents and scripts.

These tests ensure documentation exists, examples contain only placeholders and localhost
references, the commandPort helper restricts traffic to localhost without exposing wildcard bindings,
and build scripts do not accidentally import the manual commandPort helper.
"""

import json
from pathlib import Path

# Paths relative to repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "antigravity_maya_mcp_sandbox_vi.md"
CONFIG_EXAMPLE_PATH = REPO_ROOT / "docs" / "templates" / "antigravity_maya_mcp_config.example.json"
PROMPT_TEMPLATE_PATH = REPO_ROOT / "docs" / "templates" / "antigravity_maya_agent_prompt_vi.md"
HELPER_SCRIPT_PATH = REPO_ROOT / "scripts" / "maya" / "enable_maya_mcp_command_port.py"


def test_files_exist():
    """Verify that all phase deliverables exist in their designated locations."""
    assert DOC_PATH.is_file(), f"Missing doc: {DOC_PATH}"
    assert CONFIG_EXAMPLE_PATH.is_file(), f"Missing config: {CONFIG_EXAMPLE_PATH}"
    assert PROMPT_TEMPLATE_PATH.is_file(), f"Missing prompt: {PROMPT_TEMPLATE_PATH}"
    assert HELPER_SCRIPT_PATH.is_file(), f"Missing helper script: {HELPER_SCRIPT_PATH}"


def test_config_example_structure_and_placeholders():
    """Verify config example structure, placeholders, and lack of real sandbox paths."""
    with open(CONFIG_EXAMPLE_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert "mcpServers" in config
    assert "maya-sandbox" in config["mcpServers"]
    server_config = config["mcpServers"]["maya-sandbox"]

    assert server_config["command"] == "python"
    assert len(server_config["args"]) > 0
    assert "D:/path/to/external/MayaMCP/server.py" in server_config["args"]

    env = server_config.get("env", {})
    assert env.get("MAYA_MCP_HOST") == "127.0.0.1"
    assert env.get("MAYA_MCP_PORT") == "50007"

    # Ensure no real personal sandbox paths are committed
    raw_content = CONFIG_EXAMPLE_PATH.read_text(encoding="utf-8")
    assert "20260603_211205_phong_kho_v016_agent_test" not in raw_content


def test_command_port_helper_properties():
    """Verify commandPort helper configures localhost, default port, and avoids wildcards."""
    content = HELPER_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "127.0.0.1" in content
    assert "50007" in content

    # STRICT rule: do not include the literal string "0.0.0.0" anywhere
    assert "0.0.0.0" not in content


def test_command_port_helper_not_imported_by_build_pipeline():
    """Ensure the manual commandPort helper is not imported or referenced in python scripts."""
    helper_name = HELPER_SCRIPT_PATH.name
    python_scripts = list((REPO_ROOT / "scripts" / "python").rglob("*.py"))
    maya_scripts = list((REPO_ROOT / "scripts" / "maya").rglob("*.py"))

    for script_path in python_scripts + maya_scripts:
        if script_path.name == helper_name:
            continue

        content = script_path.read_text(encoding="utf-8")
        assert "enable_maya_mcp_command_port" not in content, (
            f"Script {script_path.relative_to(REPO_ROOT)} imports or references the manual helper."
        )


def test_agent_prompt_mentions_work_scene():
    """Verify that the agent prompt explicitly directs the agent to working/scene_agent_work.ma."""
    content = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "working/scene_agent_work.ma" in content


def test_docs_contain_safety_rules_and_forbidden_actions():
    """Verify doc mentions forbidden files and forbidden commits."""
    content = DOC_PATH.read_text(encoding="utf-8")

    # Mention forbidden .ai / .svg / original .ma edits
    assert ".ai" in content
    assert ".svg" in content
    assert ".ma" in content
    assert "outputs/maya/" in content

    # Mention not committing generated files
    assert ".png" in content
    assert ".zip" in content
    assert "commit" in content or "Commit" in content or "tập tin kết quả" in content
