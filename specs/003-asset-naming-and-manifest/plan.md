# Implementation Plan: Asset Naming & Manifest

**Branch**: `003-asset-naming-and-manifest` | **Date**: 2026-05-29

## Summary

Python CLI tool that processes files from `drops/`, applies the naming convention, moves them to the correct asset folder, and maintains a JSON manifest.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: PyYAML (config), click (CLI), hashlib (checksums)
**Target Platform**: Windows 10/11
**Project Type**: CLI tool

## Project Structure

```text
scripts/python/
├── asset_agent.py       # Main naming/organizing agent
├── manifest.py          # Manifest read/write utilities
config/
├── naming_convention.yaml
```
