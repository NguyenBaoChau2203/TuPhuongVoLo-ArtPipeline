# Quickstart: Artist Prompt Control Loop MVP

## What This Phase Delivers

Feature 015A adds the source-of-truth documentation for the real product goal:

```text
Artist prompt
-> Illustrator sandbox when MCP is healthy, otherwise manual SVG export
-> app/CLI Maya build
-> Visual Fidelity pass
-> Maya sandbox
-> Codex prompt polish
-> artist review / rollback
```

No Illustrator MCP, Maya commandPort, DCC launch, or external sandbox edit is required for this phase.

## Stable Daily Workflow

Read:

```text
docs/artist_daily_workflow_vi.md
```

Tomorrow's safe path:

1. Artist opens Illustrator and adjusts the layout/artwork.
2. Artist manually exports a clean SVG if Illustrator MCP is not healthy.
3. Operator runs SVG preflight.
4. Operator runs Maya dry-run.
5. Operator runs actual Maya build with `mayapy.exe` when dry-run passes.
6. Operator runs Visual Fidelity pass if the scene needs clearer readable props.
7. Operator creates or uses a Maya sandbox from the Visual Fidelity `.ma`.
8. Artist opens `working\scene_agent_work.ma`.
9. Artist/operator fills the Maya prompt template and gives it to Codex.
10. Codex verifies scene path before any edit/save and keeps changes under the required agent group.
11. Artist reviews in Maya by toggling agent groups/camera.
12. Rollback uses the sandbox restore script.

Current 014C review sandbox:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\working\scene_agent_work.ma
```

Rollback script:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\restore_agent_backup.ps1
```

## Prompt Templates

Maya prompt loop:

```text
docs/templates/maya_artist_prompt_template_vi.md
```

Illustrator prompt loop:

```text
docs/templates/illustrator_artist_prompt_template_vi.md
```

The Illustrator template is beta/blocked until the Antigravity `illustrator-sandbox` MCP server no longer returns EOF and a path-guard smoke test passes.

## Documentation Validation

Targeted docs test:

```powershell
python -m pytest tests/test_antigravity_maya_mcp_docs.py -v
```

Full suite:

```powershell
python -m pytest tests/ -v
```

Manual doc checks:

- `specs/015-artist-prompt-control-loop/spec.md` states the prompt-control product reset.
- `docs/artist_prompt_control_loop_vi.md` documents both prompt loops and safety checklist.
- `docs/artist_daily_workflow_vi.md` answers the tomorrow handoff questions.
- `docs/templates/maya_artist_prompt_template_vi.md` contains all required placeholders.
- `docs/templates/illustrator_artist_prompt_template_vi.md` contains all required placeholders.
- README and `docs/artist_handoff_desktop_app_vi.md` link to the new daily workflow.

## Stop Conditions

Stop before implementation or commit if:

- The repo is dirty before work starts.
- Commit `4e7079c` is not visible in recent history.
- Any step requires Illustrator MCP.
- Any step requires Maya commandPort.
- Any step requires opening Illustrator or Maya.
- Any step would touch external sandbox files under `D:\TuPhuongVoLo_AgentBackups` or `D:\TuPhuongVoLo_IllustratorAgentBackups`.
- Any generated `.ma`, `.svg`, `.json`, `.png`, `.zip`, report, backup, or output file appears in `git status`.

## Next Phase

Recommended next phase: **015B Maya Prompt Polish Loop smoke test** using:

```text
D:\TuPhuongVoLo_AgentBackups\20260604_203107_phong_kho_v018_014C_visual_fidelity_review\working\scene_agent_work.ma
```

015B should verify the current scene path, perform one additive/guarded polish under a named agent group, save only the sandbox working scene, and confirm rollback.
