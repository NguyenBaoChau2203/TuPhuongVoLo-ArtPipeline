# Quickstart: Natural Language Agent Control

> ⚠️ This feature is planned for a future phase. Prerequisites: Features 001–004 must be implemented first.

## Prerequisites

- [ ] Features 001–004 implemented and functional
- [ ] MCP SDK installed (future)
- [ ] LLM access configured (future)

## Quick Verification (Future)

### Step 1: Start the NLC agent

```powershell
python scripts/python/nlc_agent.py
```

### Step 2: Issue a command

```
> Render kho room from floorplan.svg in grayscale
```

Expected: System shows translated command, asks for confirmation, executes.

### Step 3: MCP server (Optional)

```powershell
python scripts/python/mcp_server.py --port 8080
```

## Current Status

This feature is in **specification phase only**. No implementation exists yet.
See `docs/NATURAL_LANGUAGE_CONTROL_ROADMAP.md` for the full roadmap.
