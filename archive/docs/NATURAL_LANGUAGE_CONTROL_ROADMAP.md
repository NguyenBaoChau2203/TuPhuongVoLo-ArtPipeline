# Natural Language Control Roadmap

> Feature 006 — Future Phase | **Tier C: Advanced Agentic**

## Current Sequencing After 007D / 005.5A

Feature 006 remains deferred. The verified Maya artist workflow, desktop app MVP,
packaging workflow, UX/reliability polish, and artist handoff notes are already
documented. Phase 005.5A now records an AI polish preview evaluation only.

Current status:

1. **007A-007D** - Friendly desktop app MVP, packaging, polish, and handoff docs completed.
2. **005.5A** - Optional AI polish preview evaluation completed as documentation only.
3. **Feature 006** - Natural-language control remains deferred and separate.

Do not integrate external AI APIs or production agent memory before API cost,
privacy, secrets handling, and opt-in policy are ready.

## Vision

Enable the artist to control the art pipeline using natural language commands instead of memorizing script names and arguments.

## Example Commands (Future)

```
"Render phòng kho từ file floorplan.svg"
→ Translates to: blender -b -P build_isometric_room.py -- --input floorplan.svg --room kho

"Làm sạch tất cả SVG trong drops/"
→ Translates to: python clean_svg_paths.py --input drops/ --output assets/2d/svg_clean/

"Đổi style sang grayscale cho phòng biệt giam"
→ Translates to: ... --room khu_biet_giam --style grayscale_blockout
```

## Prerequisites

This feature MUST NOT be started until:
- [ ] Feature 001: Floorplan to Isometric Room is functional
- [ ] Feature 002: Illustrator Export & Clean SVG is functional
- [ ] Feature 003: Asset Naming & Manifest is functional
- [ ] Feature 004: Batch Isometric Render is functional
- [ ] **Tier B (Semi-Automated) pipeline is stable in production use**

## MCP Server Implementations (Research-Sourced)

Two existing MCP server implementations for Illustrator were identified in the research:

### jinkeda/Illustrator_MCP (MIT)
- **Architecture**: Python MCP server + CEP WebSocket panel inside Illustrator
- **Capabilities**: Execute ExtendScript, path booleans, annotated previews, checkpoints
- **Transport**: WebSocket between CEP panel and Python server
- **Compatibility**: Illustrator CC 2021 to CC 2026+
- **Key feature**: VLM grounding — AI can capture screenshots, detect overlapping, flag out-of-bounds elements using coordinate rulers
- **Use case**: Full agentic vector path cleanup, layer organization, automated styling

### krVatsal/illustrator-mcp (MIT)
- **Architecture**: Cross-platform MCP server using **COM automation on Windows**, AppleScript on macOS
- **Transport**: stdio (connects AI clients to Illustrator)
- **Compatibility**: Python 3.12+, modern Illustrator versions
- **Use case**: Lightweight Windows-compatible alternative for basic ExtendScript tasks, screenshots, vector primitive generation

## Implementation Options

### Option A: MCP Server (Recommended for AI assistant integration)
- Expose pipeline tools (clean_svg, build_room, batch_render, etc.) as MCP tools
- Compatible with AI assistants (Claude, GPT, etc.) via tool-use protocol
- Can integrate with Illustrator_MCP for direct Illustrator control
- Structured tool calls with parameters and validation

### Option B: Local CLI Agent
- Python CLI that parses natural language
- Maps to existing scripts
- Shows confirmation before execution
- No external AI API dependency

### Option C: Hybrid (Recommended long-term)
- MCP server for AI integration
- CLI agent for local usage
- Both use the same tool registry
- Illustrator_MCP for direct Illustrator automation

## AI Prompt Templates for Illustrator (from Research)

When the NLC layer is implemented, these prompt templates can drive Illustrator automation via MCP:

### Vector Path Cleanup & Layer Organization
```
Using the active document in Adobe Illustrator, perform a systematic preflight
and structural path cleanup on the active selection:
1. Run a preflight scan to identify off-artboard items, empty text frames, locked elements.
2. Group all paths with stroke width ≥3pt → new layer "Layer_Outlines".
3. Group all closed filled paths with no stroke → layer "Layer_Fills".
4. Execute path simplification to reduce redundant anchor points by 20%.
5. Create an annotated canvas preview with bounding boxes and output JSON map.
```

### Isometric Room Draft Generation (for Recraft/Firefly concept art)
```
A highly stylized, isometric interior illustration of an old island motel room,
in the style of hand-drawn vector game art. Perfect 30-degree orthographic isometric
projection with no vanishing points. Clean, isolated composition on a solid pure
magenta background (#FF00FF) for easy background extraction. No text, no signatures.
```

## Safety

- Always show translated command before execution
- Require confirmation for file operations
- Reject destructive operations (delete, overwrite source files)
- Log all commands for audit trail
- No direct file system access outside pipeline scope
- MCP tools must validate inputs against naming convention

## Timeline

This is a **v2+ feature** mapping to **Tier C (Advanced Agentic)** in the three-tier strategy.
No implementation before Tier B (Semi-Automated) pipeline is stable.

Research estimates Tier C adds 55–75% time savings but with medium-to-high risk.
Only proceed when asset volume demands it or when the team has capacity for parallel testing.

## Research Incorporated

This roadmap was updated on 2026-05-29 with findings from:
- **Indie Game Art Workflow Automation Research** — Illustrator_MCP and krVatsal/illustrator-mcp repos with architecture details, VLM grounding framework, contextual prompt engineering suite (3 templates), Tier C positioning in three-tier strategy, Claude Desktop configuration for MCP.
- **Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ** — Explicit warning against implementing NLC before Tier B is stable, prompt templates for Recraft/Illustrator Text to Vector, Illustrator Turntable as exploration tool (not geometry source).
