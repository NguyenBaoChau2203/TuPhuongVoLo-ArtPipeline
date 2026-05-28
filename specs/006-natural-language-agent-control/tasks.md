# Tasks: Natural Language Agent Control

**Input**: Design documents from `/specs/006-natural-language-agent-control/`

**Prerequisites**: Features 001–004 must be implemented first.

> ⚠️ Do NOT begin these tasks until the core pipeline is functional.

## Phase 1: Tool Registry

- [ ] T001 Create tool registry mapping pipeline scripts to structured tool definitions
- [ ] T002 [P] Define input/output schemas for each tool

---

## Phase 2: Command Parser

- [ ] T003 [US1] Implement natural language → tool call mapping
- [ ] T004 [US1] Implement confirmation prompt before execution
- [ ] T005 [US3] Implement safety guardrails (reject destructive ops)

---

## Phase 3: MCP Server (Optional)

- [ ] T006 [US2] Implement MCP server skeleton
- [ ] T007 [US2] Register pipeline tools as MCP tools
- [ ] T008 [US2] Test with MCP-compatible client

---

## Phase 4: Integration

- [ ] T009 Write quickstart.md
- [ ] T010 Add Vietnamese usage instructions

---

## Dependencies

- ALL tasks depend on Features 001–004 being implemented
- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 1
