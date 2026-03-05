# Verified Agentic RAG

Reliable, citation-grounded policy Q&A over the Saltash Town Council policy corpus, with strict evaluation for retrieval quality, answer correctness, refusal behavior, and grounding.

## System Snapshot

| Item | Value |
|---|---|
| Primary use case | Policy/document Q&A with evidence citations |
| Corpus | Saltash policy pack (`docs/txt/*.txt`) |
| Retrieval stack | Dense + sparse hybrid + reranker |
| Answering modes | `retrieval` and `full` |
| Safety gate | Refusal + citation validation + grounding verification |
| Test status | `44 passed` (`.venv\Scripts\python.exe -m pytest -q`) |
| Latest benchmark run | `20260302_label_matching_upgrade` |

## What Changed in Latest Upgrade

Targeted reliability upgrade was applied to evaluation label matching:

- Added deterministic canonical alias normalization for policy committee labels.
- Canonicalization now treats `P&F`, `P/F`, and `Personnel and Finance` as equivalent to `PERSONNEL` for evaluation matching.
- This change is implemented in [`src/verified_agentic_rag/evals.py`](src/verified_agentic_rag/evals.py).

## Reliable Label Matching: What Is Used

The evaluator uses deterministic, auditable matching rules (not embedding similarity thresholds):

| Technique | Purpose | Reliability profile |
|---|---|---|
| Normalized exact match (`expected_answer`) | Direct value match in answer/context | High precision for structured metadata |
| Regex match (`expected_answer_regex`) | Format-flexible matching | High recall when values have known textual patterns |
| Required phrase match (`required_phrases`) | Narrative/procedural acceptance | More robust than brittle single-string checks |
| Canonical alias normalization | `P&F` <-> `PERSONNEL` equivalence | Prevents false mismatches from label variants |
| Citation overlap check | Answer citations must overlap gold evidence spans | Strong groundedness guarantee |
| Verification gate | Supported-claims check before pass | Blocks unsupported answered claims |

## Evaluation Rules

Implemented in [`src/verified_agentic_rag/evals.py`](src/verified_agentic_rag/evals.py).

### Retrieval mode `pass_overall`

`pass_expected_doc_rule && pass_evidence_recall_rule && pass_expected_value_rule`

### Full mode `pass_overall`

`pass_refusal_rule && pass_citation_rule && pass_expected_doc_rule && pass_evidence_recall_rule && pass_expected_value_rule && pass_citation_overlap_rule && pass_verification_rule`

## Latest Results

### Aggregate Metrics (Latest Run)

Run artifacts:
- `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_retrieval.json`
- `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_full.json`
- `reports/runs/20260302_label_matching_upgrade/tables/20260302_label_matching_upgrade_question_results.csv`

| Mode | Dataset | Passed | Pass rate |
|---|---|---:|---:|
| Retrieval | Gold | 38 / 42 | 90.48% |
| Retrieval | Silver | 131 / 142 | 92.25% |
| Full | Gold | 26 / 42 | 61.90% |
| Full | Silver | 92 / 142 | 64.79% |

### Delta vs Previous Production Baseline (`20260213_agentic_fixes`)

| Mode | Dataset | Previous | Latest | Delta |
|---|---|---:|---:|---:|
| Retrieval | Gold | 38 / 42 | 38 / 42 | 0 |
| Retrieval | Silver | 131 / 142 | 131 / 142 | 0 |
| Full | Gold | 26 / 42 | 26 / 42 | 0 |
| Full | Silver | 88 / 142 | 92 / 142 | +4 |

### Full-Mode Failure Rule Delta (Previous -> Latest)

| Dataset | `pass_expected_value_rule` fail | `pass_refusal_rule` fail | `pass_citation_overlap_rule` fail |
|---|---:|---:|---:|
| Gold | 15 -> 15 | 10 -> 7 | 10 -> 7 |
| Silver | 54 -> 47 | 26 -> 26 | 32 -> 32 |

## Reproducible Commands

### 1) Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2) Build/refresh index

```bash
.venv\Scripts\python.exe -m verified_agentic_rag.cli ingest --reset --scope docs
```

### 3) Ask a question

```bash
.venv\Scripts\python.exe -m verified_agentic_rag.cli ask "What is the responsible committee for the Data Protection - Employees policy?"
```

### 4) Run evaluation suite

```bash
.venv\Scripts\python.exe -m verified_agentic_rag.cli eval-suite --mode retrieval --output-path reports/runs/<run_id>/suite/<run_id>_suite_retrieval.json
.venv\Scripts\python.exe -m verified_agentic_rag.cli eval-suite --mode full --output-path reports/runs/<run_id>/suite/<run_id>_suite_full.json
```

### 5) Generate report artifacts

```bash
.venv\Scripts\python.exe scripts/generate_evaluation_report.py --retrieval-suite reports/runs/<run_id>/suite/<run_id>_suite_retrieval.json --full-suite reports/runs/<run_id>/suite/<run_id>_suite_full.json --csv-out reports/runs/<run_id>/tables/<run_id>_question_results.csv --md-out reports/runs/<run_id>/analysis/<run_id>_evaluation_summary.md --pdf-out reports/runs/<run_id>/analysis/<run_id>_evaluation_summary.pdf
.venv\Scripts\python.exe scripts/generate_report_figures.py --csv-path reports/runs/<run_id>/tables/<run_id>_question_results.csv --output-dir reports/runs/<run_id>/figures --date-tag <run_id>
```

### 6) Run tests

```bash
.venv\Scripts\python.exe -m pytest -q
```

## FastAPI Fit Assessment (Real-World)

| Deployment context | CLI-only | FastAPI layer |
|---|---|---|
| Single analyst, local workflow | Strong fit | Usually unnecessary overhead |
| Scheduled benchmark runs in CI | Strong fit | Optional |
| Shared internal tool (multi-user) | Limited | Strong fit |
| Integration with web apps, chat UI, or enterprise systems | Limited | Strong fit |
| Governance/audit needs (request logs, auth, rate limiting) | Limited | Strong fit |

Recommendation:
- Keep CLI as the source-of-truth workflow for evaluation and reproducibility.
- Add FastAPI only when you need multi-user access, remote integration, or service-style consumption.

## Repository Layout

```text
src/verified_agentic_rag/
  agentic.py
  evals.py
  retrieve.py
  policy_fields.py
tests/
scripts/
evalset/
reports/
  runs/
data/
```

## Current Limitations and Next Steps

| Area | Current state | Next step |
|---|---|---|
| Narrative/procedure answer quality | Still weakest compared with metadata | Increase `required_phrases` coverage in gold labels |
| Full-mode pass rate (gold) | 61.90% | Improve answer synthesis on definition/procedure items |
| Determinism | LLM generation introduces run variance | Add fixed generation settings and optional replay harness |
| API exposure | CLI-centric | Add FastAPI if multi-user/integration needs arise |

