# Changelog

All notable changes to this project are documented in this file.

## [0.4.0] - 2026-02-13

### Added
- Evidence-based Gold/Silver evaluation architecture (`evalset/gold.jsonl`, `evalset/silver.jsonl`).
- Evaluation schema documentation and legacy archive notes.
- Retrieval trace logging (dense/sparse/fused/reranked/final candidates).
- Console entry points for ingest/chat/eval/report via `pyproject.toml`.
- Report figure generator with committed showcase charts.
- CI workflow for tests + eval with gold pass-rate gate.
- `CHANGELOG.md`, package versioning, and repo structure cleanup.

### Changed
- Migrated package layout from `app/` to `src/verified_agentic_rag/`.
- Updated defaults to Saltash policy corpus naming.
- Updated tests/import paths for `src` layout and added `tests/conftest.py`.
- Refined metadata extraction and PDF table normalization for review guidance variants.

### Fixed
- Refusal items no longer fail due to evidence recall gating.
- nDCG computation no longer inflates with duplicate overlap hits.
- `expected_doc=None` no longer creates false gold evidence labels.

### Archived/Deprecated
- Legacy v1 evalset and old eval output artifacts moved under `docs/legacy/`.
