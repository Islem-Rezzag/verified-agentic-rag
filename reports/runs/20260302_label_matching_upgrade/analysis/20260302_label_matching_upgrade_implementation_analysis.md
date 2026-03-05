# Implementation and Results Analysis: 20260302_label_matching_upgrade

Generated: 2026-03-02 UTC

## 1) Scope of this re-analysis

This run re-analyzes the system after a targeted evaluator reliability change:

- Added canonical alias normalization in `evals.py` so label variants like `P&F`, `P/F`, and `Personnel and Finance` are evaluated as equivalent to `PERSONNEL`.

Files changed in implementation:

- `src/verified_agentic_rag/evals.py`
- `tests/test_evals_modes.py`

Validation:

- `44 passed` via `.venv\Scripts\python.exe -m pytest -q`

## 2) Why this change was needed

Prior analysis identified false `pass_expected_value_rule` failures where:

- expected value: `P&F`
- generated answer: `PERSONNEL`

These were semantically equivalent in corpus context but treated as mismatches by strict string matching.

## 3) Evaluation artifacts used

- Retrieval suite:
  - `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_retrieval.json`
- Full suite:
  - `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_full.json`
- Merged question table:
  - `reports/runs/20260302_label_matching_upgrade/tables/20260302_label_matching_upgrade_question_results.csv`
- Summary report:
  - `reports/runs/20260302_label_matching_upgrade/analysis/20260302_label_matching_upgrade_evaluation_summary.md`

## 4) Aggregate result comparison vs baseline (`20260213_agentic_fixes`)

| Mode | Dataset | Baseline | New run | Delta |
|---|---|---:|---:|---:|
| Retrieval | Gold | 38/42 (90.48%) | 38/42 (90.48%) | +0 |
| Retrieval | Silver | 131/142 (92.25%) | 131/142 (92.25%) | +0 |
| Full | Gold | 26/42 (61.90%) | 26/42 (61.90%) | +0 |
| Full | Silver | 88/142 (61.97%) | 92/142 (64.79%) | +4 |

Key interpretation:

- Retrieval quality is unchanged, as expected.
- Full-mode silver improved by +4 passes (about +2.82 percentage points).

## 5) Rule-level comparison (full mode)

### Gold

| Rule | Baseline fails | New fails | Delta |
|---|---:|---:|---:|
| `pass_expected_value_rule` | 15 | 15 | 0 |
| `pass_refusal_rule` | 10 | 7 | -3 |
| `pass_citation_overlap_rule` | 10 | 7 | -3 |
| `pass_citation_rule` | 0 | 0 | 0 |
| `pass_verification_rule` | 0 | 0 | 0 |

### Silver

| Rule | Baseline fails | New fails | Delta |
|---|---:|---:|---:|
| `pass_expected_value_rule` | 54 | 47 | -7 |
| `pass_refusal_rule` | 26 | 26 | 0 |
| `pass_citation_overlap_rule` | 32 | 32 | 0 |
| `pass_citation_rule` | 0 | 0 | 0 |
| `pass_verification_rule` | 0 | 0 | 0 |

## 6) Question-level outcome changes (silver full mode)

Changed `pass_overall` IDs:

- Improved to pass:
  - `s015` (`P&F` expected, `PERSONNEL` answer)
  - `s037` (`P&F` expected, `PERSONNEL` answer)
  - `s099` (`P&F` expected, `PERSONNEL` answer)
  - `s104` (`Until superseded` phrasing variation)
  - `s116` (new run produced grounded answer instead of refusal)
- Regressed:
  - `s042` (answer phrasing changed and no longer satisfied expected-value check)

Net effect: `+4` full-mode passes on silver.

## 7) Reliability assessment after change

- The canonical alias upgrade improved deterministic value-matching reliability for known committee label variants.
- The evaluator remains strict and auditable (no embedding-similarity thresholds were added for matching).
- Full-mode variability still exists because generation is stochastic in end-to-end runs.

## 8) Recommended next steps

1. Add `required_phrases` to targeted narrative/procedural gold items to reduce brittle literal-string failures.
2. Keep alias normalization mappings explicit and versioned for auditability.
3. Consider a replay/evaluation mode that re-scores stored answers to isolate evaluator changes from generation variance.

