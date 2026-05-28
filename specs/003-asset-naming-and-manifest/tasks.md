# Tasks: Asset Naming & Manifest

**Input**: Design documents from `/specs/003-asset-naming-and-manifest/`

## Phase 1: Setup

- [ ] T001 Parse `config/naming_convention.yaml` into Python data classes
- [ ] T002 [P] Create manifest module skeleton in `scripts/python/manifest.py`

---

## Phase 2: Core Naming

- [ ] T003 [US1] Implement filename generator from naming convention pattern
- [ ] T004 [US1] Implement version auto-increment (scan existing files)
- [ ] T005 [US1] Implement stage detection from file extension/metadata
- [ ] T006 [US1] Implement file move (drops/ → correct asset folder)

---

## Phase 3: Manifest

- [ ] T007 [US1] Implement manifest writer (append JSON entry)
- [ ] T008 [US1] Implement SHA-256 checksum calculation
- [ ] T009 [US2] Implement manifest query (filter by name/stage/version)
- [ ] T010 [P] Add unit tests in `tests/test_manifest.py` and `tests/test_naming_convention.py`

---

## Phase 4: Integration

- [ ] T011 Implement `asset_agent.py` CLI with click
- [ ] T012 Add Vietnamese error messages
- [ ] T013 Write quickstart.md verification steps

---

## Dependencies

- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 1
- Phases 2 and 3 can run in parallel
- Phase 4 depends on Phase 2 + 3
