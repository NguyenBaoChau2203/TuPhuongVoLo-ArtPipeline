# Tasks: Asset Naming & Manifest

**Input**: Design documents from `/specs/003-asset-naming-and-manifest/`

## Phase 1: Setup

- [x] T001 Parse `config/naming_convention.yaml` into Python data classes
- [x] T002 [P] Create manifest module skeleton in `scripts/python/manifest.py`

---

## Phase 2: Core Naming

- [x] T003 [US1] Implement filename generator from naming convention pattern
- [x] T004 [US1] Implement version auto-increment (scan existing files)
- [x] T005 [US1] Implement stage detection from file extension/metadata
- [x] T006 [US1] Implement file move/copy (`drops/` to correct asset folder)

---

## Phase 3: Manifest

- [x] T007 [US1] Implement manifest writer (append JSON entry)
- [x] T008 [US1] Implement SHA-256 checksum calculation
- [x] T009 [US2] Implement manifest query (filter by name/stage/version)
- [x] T010 [P] Add unit tests in `tests/test_manifest.py` and `tests/test_naming_convention.py`

---

## Phase 4: Integration

- [x] T011 Implement `asset_agent.py` CLI with argparse per Feature 003 request
- [x] T012 Add Vietnamese error messages
- [x] T013 Write quickstart.md verification steps

---

## Dependencies

- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 1
- Phases 2 and 3 can run in parallel
- Phase 4 depends on Phase 2 + 3
