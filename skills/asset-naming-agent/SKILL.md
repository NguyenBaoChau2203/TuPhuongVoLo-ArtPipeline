---
name: asset-naming-agent
description: Apply naming convention to assets, organize into correct folders, and maintain manifest
---

# Skill: Asset Naming Agent

## When to Use

Use this skill when the task involves:
- Naming assets according to the project convention
- Moving files from `drops/` to the correct asset folder
- Creating or updating the asset manifest
- Querying the manifest for assets by name/stage/version

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Files in drops/ | any | Yes | Files to process |
| naming_convention.yaml | YAML | Yes | Naming pattern config |

## Outputs

| Output | Type | Location | Description |
|--------|------|----------|-------------|
| Named file | any | Correct asset folder | File with convention name |
| Manifest entry | JSON | `outputs/manifest/` | Metadata record |

## Required Workflow

1. **Scan** — Find files in `drops/`
2. **Classify** — Determine asset type and stage from extension/metadata
3. **Name** — Generate filename per convention
4. **Version** — Auto-increment if name already exists
5. **Move** — Copy (not move) to correct folder
6. **Manifest** — Write entry with checksum

## Style & Safety Rules

- NEVER delete files from `drops/` (copy, then artist manually cleans)
- NEVER overwrite existing files — increment version
- Checksum all processed files
- Manifest must be append-only (never truncate)

## Success Criteria

- [ ] File renamed following naming convention
- [ ] File placed in correct folder
- [ ] Manifest entry created with all fields
- [ ] Version auto-incremented correctly
- [ ] No files lost or overwritten

## Common Failure Cases

| Failure | Cause | Fix |
|---------|-------|-----|
| Unknown file type | No extension | Prompt user for asset type |
| Name collision | Same name + version exists | Auto-increment version |
| Corrupt manifest | Invalid JSON | Backup and recreate |
