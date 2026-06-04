"""Read-only diagnostics for the external Illustrator MCP stdio server.

The helper launches the configured server under a short timeout and can send a
minimal MCP initialize/tools-list exchange. Optional read-only tool calls are
limited to text helpers such as ``help`` and ``get_system_prompt``.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(r"D:\Tools\illustrator-mcp")
DEFAULT_PYTHON = DEFAULT_ROOT / ".venv" / "Scripts" / "python.exe"
DEFAULT_SERVER = DEFAULT_ROOT / "illustrator" / "server.py"
DEFAULT_PROTOCOL_VERSION = "2024-11-05"
READ_ONLY_TOOLS = ("help", "get_system_prompt")


@dataclass(frozen=True)
class DiagnosticConfig:
    python: Path
    server: Path
    cwd: Path
    startup_seconds: float
    response_seconds: float
    protocol_version: str
    utf8_env: bool
    call_readonly_tools: bool


def build_env(*, utf8_env: bool) -> dict[str, str]:
    """Return a subprocess environment for the MCP server."""
    env = os.environ.copy()
    if utf8_env:
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
    return env


def json_rpc_request(request_id: int, method: str, params: dict[str, Any]) -> bytes:
    """Serialize one JSON-RPC request as a stdio line."""
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8") + b"\n"


def json_rpc_notification(method: str, params: dict[str, Any]) -> bytes:
    """Serialize one JSON-RPC notification as a stdio line."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8") + b"\n"


def reader_thread(pipe: Any, output: queue.Queue[bytes | None]) -> None:
    """Read pipe lines into a queue until EOF."""
    try:
        while True:
            line = pipe.readline()
            if not line:
                break
            output.put(line)
    finally:
        output.put(None)


def launch_server(config: DiagnosticConfig) -> subprocess.Popen[bytes]:
    """Launch the external MCP server with stdio pipes."""
    return subprocess.Popen(
        [str(config.python), str(config.server)],
        cwd=str(config.cwd),
        env=build_env(utf8_env=config.utf8_env),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def startup_probe(config: DiagnosticConfig) -> dict[str, Any]:
    """Launch the server briefly and capture startup stdout/stderr behavior."""
    proc = launch_server(config)
    time.sleep(config.startup_seconds)
    alive = proc.poll() is None
    if alive:
        proc.kill()
    stdout, stderr = proc.communicate(timeout=5)
    return {
        "alive_after_timeout": alive,
        "return_code": proc.returncode,
        "stdout_bytes": len(stdout),
        "stdout_preview": repr(stdout[:300]),
        "stderr_bytes": len(stderr),
        "stderr_preview": stderr[:1600].decode("utf-8", errors="replace"),
    }


def send(proc: subprocess.Popen[bytes], payload: bytes) -> None:
    """Write one stdio payload to the child process."""
    if proc.stdin is None:
        raise RuntimeError("Server stdin is not available.")
    proc.stdin.write(payload)
    proc.stdin.flush()


def wait_for_response(
    stdout_queue: queue.Queue[bytes | None],
    request_id: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    """Wait for one response ID and return a compact diagnostic object."""
    deadline = time.time() + timeout_seconds
    raw_lines: list[str] = []
    while time.time() < deadline:
        try:
            item = stdout_queue.get(timeout=max(0.05, deadline - time.time()))
        except queue.Empty:
            break
        if item is None:
            return {"ok": False, "reason": "stdout_eof", "raw_lines": raw_lines}
        raw = item.decode("utf-8", errors="replace").strip()
        if not raw:
            continue
        raw_lines.append(raw[:500])
        try:
            message = json.loads(raw)
        except json.JSONDecodeError as exc:
            return {
                "ok": False,
                "reason": "json_decode_error",
                "error": str(exc),
                "raw_lines": raw_lines,
            }
        if message.get("id") == request_id:
            return {"ok": "result" in message, "message": message}
    return {"ok": False, "reason": "timeout", "raw_lines": raw_lines}


def drain_stderr(stderr_queue: queue.Queue[bytes | None]) -> list[str]:
    """Collect currently available stderr lines."""
    lines: list[str] = []
    while True:
        try:
            item = stderr_queue.get_nowait()
        except queue.Empty:
            break
        if item is None:
            break
        lines.append(item.decode("utf-8", errors="replace").rstrip("\r\n"))
    return lines


def summarize_tools(tools_response: dict[str, Any]) -> list[str]:
    """Extract tool names from a successful tools/list response."""
    message = tools_response.get("message") or {}
    tools = message.get("result", {}).get("tools", [])
    return [str(tool.get("name")) for tool in tools]


def protocol_probe(config: DiagnosticConfig) -> dict[str, Any]:
    """Run initialize, tools/list, and optional read-only text tool calls."""
    proc = launch_server(config)
    stdout_queue: queue.Queue[bytes | None] = queue.Queue()
    stderr_queue: queue.Queue[bytes | None] = queue.Queue()
    threading.Thread(target=reader_thread, args=(proc.stdout, stdout_queue), daemon=True).start()
    threading.Thread(target=reader_thread, args=(proc.stderr, stderr_queue), daemon=True).start()

    result: dict[str, Any] = {}
    try:
        send(
            proc,
            json_rpc_request(
                1,
                "initialize",
                {
                    "protocolVersion": config.protocol_version,
                    "capabilities": {},
                    "clientInfo": {
                        "name": "tpvl-illustrator-mcp-stdio-diagnostic",
                        "version": "0.1.0",
                    },
                },
            ),
        )
        initialize = wait_for_response(stdout_queue, 1, config.response_seconds)
        result["initialize"] = initialize

        if initialize.get("ok"):
            send(proc, json_rpc_notification("notifications/initialized", {}))
            send(proc, json_rpc_request(2, "tools/list", {}))
            tools_list = wait_for_response(stdout_queue, 2, config.response_seconds)
            result["tools_list"] = tools_list
            result["tool_names"] = summarize_tools(tools_list) if tools_list.get("ok") else []

            if config.call_readonly_tools:
                next_id = 3
                calls: dict[str, Any] = {}
                for tool_name in READ_ONLY_TOOLS:
                    send(
                        proc,
                        json_rpc_request(
                            next_id,
                            "tools/call",
                            {"name": tool_name, "arguments": {}},
                        ),
                    )
                    calls[tool_name] = wait_for_response(
                        stdout_queue,
                        next_id,
                        config.response_seconds,
                    )
                    next_id += 1
                result["readonly_tool_calls"] = calls
    finally:
        if proc.stdin is not None:
            try:
                proc.stdin.close()
            except Exception:
                pass
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)

    stderr_lines = drain_stderr(stderr_queue)
    result["return_code"] = proc.returncode
    result["stderr_line_count"] = len(stderr_lines)
    result["stderr_tail"] = stderr_lines[-50:]
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnose the external Illustrator MCP stdio server without editing artwork.",
    )
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--cwd", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--startup-seconds", type=float, default=2.0)
    parser.add_argument("--response-seconds", type=float, default=6.0)
    parser.add_argument("--protocol-version", default=DEFAULT_PROTOCOL_VERSION)
    parser.add_argument(
        "--utf8-env",
        action="store_true",
        help="Set PYTHONUTF8=1 and PYTHONIOENCODING=utf-8 for the server process.",
    )
    parser.add_argument(
        "--call-readonly-tools",
        action="store_true",
        help="Also call read-only text tools: help and get_system_prompt.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DiagnosticConfig(
        python=args.python,
        server=args.server,
        cwd=args.cwd,
        startup_seconds=args.startup_seconds,
        response_seconds=args.response_seconds,
        protocol_version=args.protocol_version,
        utf8_env=args.utf8_env,
        call_readonly_tools=args.call_readonly_tools,
    )
    report = {
        "config": {
            "python": str(config.python),
            "server": str(config.server),
            "cwd": str(config.cwd),
            "utf8_env": config.utf8_env,
            "call_readonly_tools": config.call_readonly_tools,
        },
        "startup": startup_probe(config),
        "protocol": protocol_probe(config),
    }
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
