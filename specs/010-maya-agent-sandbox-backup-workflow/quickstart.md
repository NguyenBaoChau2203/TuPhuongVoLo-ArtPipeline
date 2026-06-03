# Quickstart: Maya Agent Sandbox Backup Workflow

## Create a Sandbox Session

```powershell
python scripts/python/maya_agent_sandbox.py `
  --maya-scene outputs\maya\tu_phuong_vo_lo_phong_kho_main_maya_v017.ma `
  --geometry-json outputs\tmp\tu_phuong_vo_lo_phong_kho_main_blockout_v017.json `
  --source-svg D:\TuPhuongVoLo_ArtistTests\real_svg_test_01\phong_kho.svg `
  --room phong_kho `
  --backup-root D:\TuPhuongVoLo_AgentBackups
```

## Dry Run

```powershell
python scripts/python/maya_agent_sandbox.py `
  --maya-scene outputs\maya\example.ma `
  --room phong_kho `
  --dry-run
```

## Validation

```powershell
python scripts/python/maya_agent_sandbox.py --help
pytest tests/test_maya_agent_sandbox.py -v
pytest tests/ -v --ignore=tests/tmp
```
