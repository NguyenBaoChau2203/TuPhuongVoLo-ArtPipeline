# TuPhuongVoLo-ArtPipeline

> Semi-automated art pipeline for the indie game **Tứ Phương Vô Lộ**

---

## 🎯 Project Purpose

This repository provides **semi-automated tooling** for an indie game art pipeline. It bridges the gap between hand-drawn/vector art in Adobe Illustrator and isometric 3D draft renders in Blender (with an optional Maya advanced branch).

**Current Phase**: 📋 SDD Bootstrap / Planning Only — no production logic implemented yet.

All files are documentation, specs, placeholder scripts, config templates, and AI agent instructions. This is preparation for future coding work.

---

## 🏗️ Pipeline Flow

```
Illustrator authoring / export
    → clean SVG export (JSX / ExtendScript)
    → optional vectorization (Potrace / Vectorizer.AI / Image Trace)
    → vpype cleanup
    → svgpathtools rule-based validation
    → Blender SVG import / extrude / isometric camera / render
    → optional Maya advanced branch
    → editable outputs for artist polish
```

---

## 📌 Recommended Implementation Order

| Order | Feature | Spec | Status |
|-------|---------|------|--------|
| 1 | Illustrator Export & Clean SVG | `specs/002-illustrator-export-clean-svg/` | 📋 Spec only |
| 2 | Asset Naming & Manifest | `specs/003-asset-naming-and-manifest/` | 📋 Spec only |
| 3 | Floorplan to Isometric Room | `specs/001-floorplan-to-isometric-room/` | 📋 Spec only |
| 4 | Batch Isometric Render | `specs/004-batch-isometric-render/` | 📋 Spec only |
| 5 | Maya Bridge (optional) | `specs/005-maya-bridge/` | 📋 Spec only |
| 6 | Natural Language Agent Control | `specs/006-natural-language-agent-control/` | 📋 Spec only |

> Feature 002 should be implemented first because it produces clean SVGs that all other features consume.

---

## 🚀 Quickstart for Developers

### Prerequisites
- Python 3.11+
- Git
- (Optional) Blender 4.x — only needed for features 001, 004
- (Optional) Adobe Illustrator — only needed for feature 002
- (Optional) Autodesk Maya — only needed for feature 005

### Setup
```powershell
# Clone the repository
git clone <repo-url>
cd TuPhuongVoLo-ArtPipeline

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies declared for Feature 002/003 planning
pip install -r requirements.txt

# Run tests (placeholder — tests are stubs)
pytest tests/ -v
```

### Read the specs
Start with `specs/002-illustrator-export-clean-svg/spec.md` and work through the implementation order above.

---

## 🎨 Quickstart for Artist (Dành cho họa sĩ)

Xem hướng dẫn chi tiết bằng tiếng Việt tại:
- 📖 [Hướng dẫn cài đặt](docs/INSTALL_VI.md)
- 🎨 [Hướng dẫn sử dụng](docs/HOW_TO_USE_FOR_ARTIST_VI.md)
- 🔧 [Xử lý sự cố](docs/TROUBLESHOOTING_VI.md)
- 🚀 [Launchers](launchers/README_LAUNCHERS_VI.md)

**Quy trình cơ bản:**
1. Bỏ file SVG vào thư mục `drops/`
2. Chạy file `.bat` phù hợp trong `launchers/`
3. Lấy kết quả từ `outputs/`

---

## 📁 Repository Structure

```
TuPhuongVoLo-ArtPipeline/
├─ AGENTS.md                    # AI agent instructions
├─ README.md                    # This file
├─ pyproject.toml               # Python project config
├─ requirements.txt             # Python dependencies
├─ .gitignore                   # Git ignore rules
├─ .editorconfig                # Editor settings
│
├─ .specify/                    # Spec Kit configuration
│  ├─ constitution.md           # Project constitution
│  └─ templates/                # SDD templates
│
├─ specs/                       # Feature specifications (SDD)
│  ├─ 001-floorplan-to-isometric-room/
│  ├─ 002-illustrator-export-clean-svg/
│  ├─ 003-asset-naming-and-manifest/
│  ├─ 004-batch-isometric-render/
│  ├─ 005-maya-bridge/
│  └─ 006-natural-language-agent-control/
│
├─ .cursor/rules/               # Cursor IDE rules
├─ skills/                      # Reusable AI agent skills
├─ scripts/                     # Automation scripts
│  ├─ illustrator/              # JSX/ExtendScript
│  ├─ python/                   # Python CLI tools
│  ├─ blender/                  # Blender Python
│  └─ maya/                     # Maya Python/MEL
│
├─ launchers/                   # Windows .bat launchers
├─ config/                      # YAML configuration
├─ assets/                      # Source art assets
├─ drops/                       # Artist drops files here
├─ outputs/                     # Generated outputs
├─ examples/                    # Example inputs/outputs
├─ tests/                       # Test files
└─ docs/                        # Documentation
```

---

## 🗺️ Feature Roadmap

### Phase 1: Foundation (Current)
- [x] Repository skeleton
- [x] SDD artifacts and specs
- [x] AI agent rules and skills
- [x] Config templates
- [x] Vietnamese documentation placeholders

### Phase 2: Core Pipeline
- [ ] Feature 002: Illustrator Export & Clean SVG
- [ ] Feature 003: Asset Naming & Manifest
- [ ] Feature 001: Floorplan to Isometric Room

### Phase 3: Batch & Integration
- [ ] Feature 004: Batch Isometric Render
- [ ] Feature 005: Maya Bridge (optional)

### Phase 4: Intelligence Layer
- [ ] Feature 006: Natural Language Agent Control

---

## ⚠️ What Is Intentionally NOT Implemented Yet

| Item | Reason |
|------|--------|
| SVG parsing/cleaning logic | Placeholder scripts only — implement via Feature 002 |
| Blender scene generation | Placeholder scripts only — implement via Feature 001 |
| Maya integration | Optional advanced branch — implement via Feature 005 |
| Natural language control | Future layer — implement via Feature 006 |
| Production Python implementations | Dependencies are declared for Feature 002/003, but production logic remains unimplemented |
| CI/CD pipeline | Not needed until production code exists |
| AI/ML models | This is rule-based semi-automation, not ML |

---

## 📜 License

Internal project — not for public distribution.

---

## 🤝 Contributing

Follow the Spec-Driven Development workflow:
1. Read `AGENTS.md` and `.specify/constitution.md`
2. Pick a feature from `specs/`
3. Follow the spec → plan → tasks → implement cycle
4. Run tests before committing
5. Update manifest for any generated outputs
