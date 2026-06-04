"""Unit tests for the Illustrator MCP stdio diagnostic helper."""

from __future__ import annotations

import json
from pathlib import Path

import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_PATH = REPO_ROOT / "scripts" / "python"
sys.path.insert(0, str(SCRIPTS_PATH))

import diagnose_illustrator_mcp_stdio as diag  # noqa: E402


def test_build_env_adds_utf8_controls(monkeypatch) -> None:
    monkeypatch.setenv("EXISTING_VALUE", "kept")

    env = diag.build_env(utf8_env=True)

    assert env["EXISTING_VALUE"] == "kept"
    assert env["PYTHONUTF8"] == "1"
    assert env["PYTHONIOENCODING"] == "utf-8"


def test_build_env_can_leave_encoding_unchanged(monkeypatch) -> None:
    monkeypatch.delenv("PYTHONUTF8", raising=False)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    env = diag.build_env(utf8_env=False)

    assert "PYTHONUTF8" not in env
    assert "PYTHONIOENCODING" not in env


def test_json_rpc_request_is_single_utf8_line() -> None:
    payload = diag.json_rpc_request(
        7,
        "tools/call",
        {"name": "help", "arguments": {}},
    )

    assert payload.endswith(b"\n")
    message = json.loads(payload.decode("utf-8"))
    assert message["jsonrpc"] == "2.0"
    assert message["id"] == 7
    assert message["method"] == "tools/call"
    assert message["params"]["name"] == "help"


def test_summarize_tools_extracts_tool_names() -> None:
    response = {
        "ok": True,
        "message": {
            "result": {
                "tools": [
                    {"name": "help"},
                    {"name": "get_system_prompt"},
                ]
            }
        },
    }

    assert diag.summarize_tools(response) == ["help", "get_system_prompt"]
