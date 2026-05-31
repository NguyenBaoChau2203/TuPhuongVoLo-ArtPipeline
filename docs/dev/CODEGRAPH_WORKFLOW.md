# CodeGraph Workflow (Development Aid)

> **Document type**: Developer workflow note (English)
> **Phase**: 005.0A — Workflow alignment / architecture cleanup
> **Audience**: AI coding agents and human developers

## What CodeGraph is (and is not)

CodeGraph is a **development aid only**. It builds a queryable graph/index of the
codebase (symbols, references, call relationships) so an agent can locate relevant
files before editing.

- It is **NOT a production dependency** of this pipeline.
- It is **NOT required** to run, test, or ship any feature.
- It MUST NOT be imported by any `scripts/` code.
- It MUST NOT appear in `requirements.txt` or `pyproject.toml` dependencies.

The art pipeline (Illustrator -> Python SVG -> Maya `.ma`) runs identically whether
or not CodeGraph is installed.

## Current availability in this repository

As of Phase 005.0A, CodeGraph is **not installed or configured** on this machine:

- No `codegraph` / `codegraph-mcp` command on `PATH`.
- No `codegraph` Python package installed.
- No `.codegraph/` directory present.

This does **not** block any work. If CodeGraph is unavailable, fall back to the
standard tools below.

## How future AI agents should use it (before editing)

When CodeGraph is available, prefer this order before making code changes:

1. **Initialize / index** the repository so the graph is current.
2. **Query** for the symbols, functions, or files relevant to the task
   (for example: room detection, geometry scaling, manifest writing, Maya command building).
3. **Pull context** for the matched files and read them with the normal Read tool.
4. **Only then edit**, keeping changes scoped to what the task requires.

The goal is to reduce blind searching and avoid editing the wrong layer (for
example, editing the Blender fallback when the Maya-first path was intended).

## Suggested commands (if the installed CodeGraph exposes them)

Exact command names depend on the CodeGraph distribution you install. Typical
shapes look like:

```bash
# Initialize CodeGraph in the repo (one-time)
codegraph init

# Build / refresh the index
codegraph index

# Query for a symbol or concept
codegraph query "detect_rooms"

# Pull surrounding context for a file or symbol
codegraph context scripts/python/build_maya_room.py
```

Confirm the real subcommands with `codegraph --help` after installation. Do not
assume these names; verify first.

## What to do if CodeGraph is unavailable

Do not block the task. Use the standard repository tools instead:

- File discovery: Glob (for example `scripts/**/*.py`).
- Content search: Grep / ripgrep.
- Targeted reads: the Read tool.
- Optionally delegate broad exploration to a sub-agent.

Document in your task notes that CodeGraph was unavailable and that standard tools
were used. Future setup can revisit installing it.

## Hard rule: never commit generated CodeGraph data

Any generated CodeGraph artifacts MUST be treated as local-only and must never be
committed:

- The `.codegraph/` directory and any database/index it produces.
- Any embeddings, vector stores, or caches CodeGraph creates.

These are already covered by `.gitignore`. Verify with `git status` before staging,
and never force-add ignored CodeGraph artifacts.
