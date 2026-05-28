# Pipeline Overview — TuPhuongVoLo-ArtPipeline

## Architecture

```
┌──────────────────────┐
│  Adobe Illustrator   │  ← Artist creates 2D vector art
│  (29.8.7 LTS prod)   │     JSX scripts, Actions, Export for Screens
└────────┬─────────────┘
         │ SVG Export / Image Trace / Direct drawing
         ▼
┌──────────────────────┐
│  Vectorization       │  ← Branch by input type
│  (if needed)         │
│  ┌─────────────────┐ │
│  │ B&W line art:   │ │
│  │ mkbitmap+Potrace│ │
│  ├─────────────────┤ │
│  │ Color/noisy:    │ │
│  │ Vectorizer.AI   │ │
│  │ or Image Trace  │ │
│  └─────────────────┘ │
└────────┬─────────────┘
         │ Raw SVG
         ▼
┌──────────────────────┐
│  SVG Cleanup         │  ← vpype 1.15.0 + svgpathtools 1.7.2
│  (Python CLI)        │     linemerge → linesort → reloop → linesimplify
│                      │     Rule-based: filter runt paths, validate bbox,
│                      │     check closed loops, flatten transforms
└────────┬─────────────┘
         │ Clean SVG (source of truth)
         ▼
┌──────────────────┐     ┌──────────────────────┐
│  Blender LTS 4.x │     │  Maya 2024+ (Optional)│
│  (bpy Python)    │     │  (mayapy)             │
│                  │     │                       │
│  SVG → Curves    │     │  Python parser         │
│  → Mesh → Extrude│     │  svgpathtools → cmds  │
│  → Iso Camera    │     │  or Blender → USD →   │
│  → Render PNG    │     │  maya-usd import      │
└────────┬─────────┘     └────────┬──────────────┘
         │                        │
         ▼                        ▼
┌──────────────────────────────────────────┐
│  Outputs                                  │
│  ├─ preview/*.png    (PNG alpha previews) │
│  ├─ blender/*.blend  (editable scenes)    │
│  ├─ maya/*           (Maya scenes)        │
│  ├─ svg/*            (processed SVGs)     │
│  └─ manifest/*.json  (tracking data)      │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  Artist Polish    │  ← Final artistic decisions
│  (Manual)         │     remain with the artist
└──────────────────┘
```

## Data Flow

| Stage | Input | Tool | Version | Output |
|-------|-------|------|---------|--------|
| 1. Author | Creative vision | Illustrator | 29.8.7 LTS | .ai file |
| 2. Export | .ai file | JSX script / Export for Screens | — | Raw SVG |
| 3a. Trace (B&W) | Raster mask/ink | mkbitmap + Potrace | 1.16 | SVG (raw) |
| 3b. Trace (Color) | Raster color | Vectorizer.AI / Image Trace | current | SVG (raw) |
| 4. Clean | Raw SVG | vpype + svgpathtools | 1.15.0 / 1.7.2 | Clean SVG |
| 5. Validate | Clean SVG | Python (svgpathtools rules) | 1.7.2 | Pass/Fail |
| 6. Build | Clean SVG + Presets | Blender | LTS 4.x | .blend scene |
| 7. Render | .blend scene | Blender (EEVEE/CYCLES) | LTS 4.x | PNG alpha |
| 8. Track | All outputs | Python (manifest.py) | 3.11+ | Manifest JSON |
| 9. Polish | All outputs | Artist (manual) | — | Final art |

## Key Design Decisions

1. **Semi-automated**: The pipeline assists but never replaces artistic judgment. Research recommends **Tier B (Semi-Automated)** as the production baseline.
2. **Clean SVG as source of truth**: All downstream tools consume clean SVG. When the artist edits walls in Illustrator or cleanup changes, the 3D scene can be **rebuilt from SVG** rather than edited manually in the DCC.
3. **Blender default, Maya optional**: Blender is free and has confirmed native SVG import. Maya has **no confirmed first-party SVG import** — use Python parser or Blender/USD bridge.
4. **Non-destructive**: Source files are never modified. Outputs are versioned.
5. **Editable outputs**: All outputs can be reopened and modified (.blend, .ma, clean SVG).
6. **Windows-first**: Everything must work on Windows 10/11.
7. **Version-locked toolchain**: Lock specific versions for stability rather than chasing "latest" (see Data Flow table).

## Three-Tier Production Strategy (from Research)

| Tier | Description | Time Savings | Risk |
|------|-------------|:------------:|------|
| **A: Beginner** | Manual Illustrator + Image Trace + manual Blender editing | 15–30% | Low |
| **B: Semi-Automated** ★ | Illustrator + Actions/JSX + Potrace/Vectorizer.AI + vpype + svgpathtools + Blender batch | 40–65% | Low–Medium |
| **C: Advanced Agentic** | Add Maya/USD, MCP servers, manifest agent, CI, auto-rebuild | 55–75% | Medium–High |

★ **Recommended** for Tứ Phương Vô Lộ. Adopt Tier B as the primary workflow; only add Tier C components when asset volume increases.

## Production Risks & Mitigations (from Research)

| Risk | Mitigation |
|------|------------|
| Messy vectors / anchor point bloat from AI tracing | Force all imported AI vectors through vpype + svgpathtools cleanup before manual polish |
| Poor 3D mesh topology from auto-extrude | Keep blockout as non-rendering reference; final art built manually with clean quad topology |
| Style inconsistency in AI-generated drafts | Never use raw AI renders as final sprites; treat as concept drafts only |
| Platform/version instability (Adobe/Autodesk updates) | Lock software versions during production; disable auto-updates; commit all scripts to Git |
| Maya SVG import uncertainty | Use Python parser or Blender/USD bridge instead of unconfirmed first-party SVG import |

## Research Incorporated

This document was updated on 2026-05-29 with findings from:
- **Indie Game Art Workflow Automation Research** — Three-tier production strategy, tool comparison tables, production risk mitigations, GitHub repo registry.
- **Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ** — Three-layer architecture, vectorization branch design, version-locked toolchain, SVG-as-source-of-truth rebuild loop, render settings, Maya SVG import limitations.
