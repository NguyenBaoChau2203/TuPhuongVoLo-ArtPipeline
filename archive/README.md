# Archive And Legacy Notes

This folder keeps reference material that is not part of the daily artist workflow.

Daily work starts in:

- `README.md`
- `docs/WORKFLOW_FOR_WIFE_VI.md`
- `docs/CODEX_PROMPTS_VI.md`
- `launchers/09_artist_desktop_app.bat`

## What Is Out Of The Daily Path

- Blender/isometric pipeline: retained as legacy/fallback code because the project constitution says it must not be removed or broken. It is not the primary production path.
- AI polish preview mock/fal: reference-only experiments; not needed for daily Illustrator -> Maya work. Docs moved to `archive/docs/`.
- Natural-language/MCP roadmap: future/beta layer, not production daily workflow. Roadmap moved to `archive/docs/NATURAL_LANGUAGE_CONTROL_ROADMAP.md`.
- Old verification notes: useful history, not operator instructions. Moved to `archive/verification/`.
- Long research docs: useful architecture background, not daily steps for the artist. Moved to `archive/research/`.
- Old architecture/dev audits: moved to `archive/architecture/` and `archive/dev/`.
- Batch/package/legacy launchers: developer or bulk-processing tools, not the normal one-scene artist loop. Moved to `archive/launchers/`.

## Retained Legacy Code Still In Place

These paths remain in their original locations so existing tests and fallback behavior do not break:

```text
scripts\blender\
scripts\python\build_isometric_room.py
scripts\python\batch_isometric_render.py
scripts\python\ai_polish_preview.py
scripts\python\batch_maya_room.py
scripts\python\package_artist_app.py
```

Use them only when a future task explicitly asks for legacy/fallback, batch, packaging, or optional AI preview work.

## Archived Launchers

These were moved out of `launchers/` so the artist-facing folder shows only daily actions:

```text
archive\launchers\01_install_tools.bat
archive\launchers\02_clean_svg.bat
archive\launchers\03_build_isometric_room.bat
archive\launchers\04_batch_isometric_render.bat
archive\launchers\04_batch_render.bat
archive\launchers\05_open_outputs.bat
archive\launchers\06_ingest_assets.bat
archive\launchers\08_batch_maya_room.bat
archive\launchers\10_package_artist_app.bat
```

They are not deleted; they are just no longer daily artist entry points.
