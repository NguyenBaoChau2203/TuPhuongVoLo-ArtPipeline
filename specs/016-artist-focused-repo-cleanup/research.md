# Research: Artist-Focused Repo Cleanup

## Decision: Preserve Core Code, Archive The Surface

**Decision**: Do not physically delete or move tested core modules. Hide optional or legacy workflows from the README and daily docs; move old docs/launchers where safe; document retained legacy code in `archive/README.md`.

**Rationale**: The constitution explicitly retains Blender as legacy/fallback. Existing tests cover older modules, and breaking them would reduce confidence. The pain is navigation and artist workflow clarity, not lack of disk space.

**Alternatives considered**:

- Delete Blender/isometric code: rejected because it violates the constitution and breaks tests.
- Move every optional Python script into `archive/`: rejected because app/tests import some optional scripts directly.
- Only rewrite README: rejected because the artist still needs prompt docs and starter templates.

## Decision: Make Codex Script Generation The Assistance Layer

**Decision**: Add reusable JSX and Maya Python templates plus prompt docs instead of implementing direct image-to-JSX automation or direct Maya commandPort integration in Feature 016.

**Rationale**: The immediate workflow can work with Codex generating per-scene scripts from image context and Vietnamese description. Direct Illustrator MCP is currently beta/blocked and direct commandPort operation increases safety risk.

**Alternatives considered**:

- Build full image-to-JSX CLI: rejected as too large for cleanup and likely to overpromise quality.
- Repair Illustrator MCP now: rejected because Feature 016 is cleanup; MCP repair deserves a separate feature.
- Remove all AI preview references everywhere: rejected because optional docs can remain archived for future review.

## Decision: Daily Docs In Vietnamese, README Short And Operator-Oriented

**Decision**: Create `docs/WORKFLOW_FOR_WIFE_VI.md` as the artist daily guide and keep README short enough to route the operator quickly.

**Rationale**: The artist needs Vietnamese, concrete, low-stress steps. README should be an entry point, not a phase history.

**Alternatives considered**:

- Keep all phase status tables in README: rejected because they obscure the daily path.
- Put everything in one giant Vietnamese README: rejected because developers still need concise repo orientation.
