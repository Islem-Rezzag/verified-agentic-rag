# Full System Reliability Analysis (New Uploaded Labels)

Generated: 2026-02-13 (local run)

## 1) What was executed

1. Replaced eval labels with uploaded files:
- `evalset/gold.jsonl`
- `evalset/silver.jsonl`

2. Rebuilt index:
- `python -m verified_agentic_rag.cli ingest --reset --scope docs`
- Result: 56 chunks indexed

3. Ran evaluation suites:
- Retrieval: `reports/runs/20260213_uploaded_labels/suite/20260213_uploaded_labels_suite_retrieval.json`
- Full: `reports/runs/20260213_uploaded_labels/suite/20260213_uploaded_labels_suite_full.json`

4. Ran tests:
- `pytest -q`
- Result: 39/39 passed

5. Generated artifacts:
- CSV: `reports/runs/20260213_uploaded_labels/tables/20260213_uploaded_labels_question_results.csv`
- Summary report: `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_evaluation_summary.md`
- Summary PDF: `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_evaluation_summary.pdf`
- Full Q&A audit: `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_answer_audit.md`
- Full Q&A audit PDF: `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_answer_audit.pdf`
- Figures:
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_pass_rate_by_dataset_mode.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_behavior_confusion_full_mode.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_rule_pass_breakdown_full_mode.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_retrieval_ranking_metrics_distribution.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_context_precision_distribution.png`

## 2) Evaluation algorithm used

The evaluator runs two modes over both datasets.

### Retrieval mode
- Runs retrieval pipeline without LLM answering.
- Checks:
  - evidence recall at k (did we retrieve required evidence labels?)
  - ranking quality (MRR, nDCG, rank-aware precision)
  - expected value presence in retrieved context (for value-based items)
- `pass_overall` in retrieval mode requires expected doc/evidence/value rules.

### Full mode (strict end-to-end)
- Runs full agent path: retrieve -> decide answer/refuse -> produce citations -> verify grounding.
- Checks:
  - refusal correctness (`pass_refusal_rule`)
  - citation rule (`pass_citation_rule`)
  - expected value/rule matching (`pass_expected_value_rule`)
  - citation overlap with gold evidence (`pass_citation_overlap_rule`)
  - verification gate (`pass_verification_rule`)
- `pass_overall` requires all strict rules to pass.

## 3) Dataset size and composition

| Dataset | Total | metadata | procedure | definition | multi_chunk | out_of_scope | other |
|---|---:|---:|---:|---:|---:|---:|---:|
| gold | 42 | 19 | 10 | 3 | 0 | 8 | 2 (`scope`) |
| silver | 142 | 107 | 14 | 3 | 3 | 15 | 0 |

## 4) Aggregate results

| Dataset | Retrieval pass | Full pass | Retrieval pass rate | Full pass rate |
|---|---:|---:|---:|---:|
| gold | 38/42 | 21/42 | 90.48% | 50.00% |
| silver | 131/142 | 81/142 | 92.25% | 57.04% |

Retrieval metrics (aggregate):
- Gold retrieval: Recall@k 1.0000, MRR 0.9706, nDCG@k 0.9783, ranked precision 0.9706
- Silver retrieval: Recall@k 1.0000, MRR 0.9961, nDCG@k 0.9971, ranked precision 0.9961

Full-mode evidence metrics (aggregate):
- Gold full: Recall@k 1.0000, MRR 0.9853, nDCG@k 0.9891, ranked precision 0.9853
- Silver full: Recall@k 1.0000, MRR 1.0000, nDCG@k 1.0000, ranked precision 1.0000

Interpretation:
- Retrieval quality is very high.
- End-to-end pass drops because strict answer/citation/refusal rules fail on many questions, not because evidence is missing.

## 5) Behavior and reliability findings

### What is strong
- Retriever consistently finds evidence (Recall@k = 1.0 on both sets).
- Out-of-scope behavior is mostly good:
  - gold: 7/8 passed
  - silver: 15/15 passed
- Verification failures are zero in this run.

### Main failure categories (full mode)
- Gold failures (21 total):
  - `pass_expected_value_rule`: 20
  - `pass_refusal_rule`: 16
  - `pass_citation_overlap_rule`: 15
- Silver failures (61 total):
  - `pass_expected_value_rule`: 61
  - `pass_citation_overlap_rule`: 42
  - `pass_refusal_rule`: 34

### Failure pattern analysis
1. False refusals on answerable questions (largest issue)
- Gold: 15 answer-expected questions were refused.
- Silver: 34 answer-expected questions were refused.
- Many of these had perfect retrieval evidence metrics, so failure is in answering/gating stage.

2. Value normalization or label mismatch
- Several expected values are abbreviations or formats not matching corpus phrasing.
- Examples:
  - expected `P&F` vs answer `PERSONNEL`
  - expected `03/2024` vs answer `11.03.2025`
- In retrieval-mode failures, `corpus_contains_expected_value` is often false, indicating label-text mismatch rather than retrieval miss.

3. Cross-policy citation leakage on some metadata prompts
- Example: Provision IT committee question answered with Data Protection citation/answer (`PERSONNEL`) instead of target policy evidence label.
- This causes citation-overlap failure even when text appears plausible.

4. Rare false positive on refusal
- 1 gold out-of-scope question was incorrectly answered:
  - Q: "What is the latest version of the OpenAI API?"
  - A: "The version is 2025.[docs/txt/Equality_Diversity.txt:1-100]"

## 6) Example exact Q&A (from full-mode output)

### Correct examples
- `g001`
  - Q: What is the policy group for the Data Protection - Employees policy?
  - A: The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- `g004`
  - Q: What is the next review date guidance for the Data Protection - Employees policy?
  - A: The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]

### Incorrect examples
- `g003` (value mismatch)
  - Expected: 03/2024
  - A: The last updated is 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- `g019` (false refusal)
  - Q: Name two lawful bases for processing personal information listed in the Data Protection - Employees policy.
  - A: I cannot answer from the repository based on the retrieved sources.
- `s048` (wrong evidence source)
  - Q: Which committee is responsible for Provision of IT Acceptable Use Policy Employees Members?
  - A: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Gold evidence target: Provision IT policy header

## 7) Critical accuracy conclusion

- Retrieval subsystem reliability: high.
- End-to-end strict reliability on this expanded benchmark: moderate (50-57%), not production-ready yet.
- The current agent is strongest on deterministic metadata and refusal safety.
- The weakest area is converting available evidence into accepted full-mode answers for procedure/definition/narrative items.

## 8) What has been achieved

You now have:
- much larger and stricter benchmark coverage than before,
- complete reproducible evaluation artifacts (JSON + CSV + figures + PDF),
- a full question-by-question audit including exact agent answers and citations,
- clear diagnostics separating retrieval quality from full-mode answer reliability.

This is a strong engineering milestone because failures are now measurable and classifiable.

## 9) Immediate next fixes to increase full-mode pass rate

1. Reduce false refusals on answerable narrative/procedure questions (tune retrieval grading/gating thresholds and narrative answer path).
2. Add normalization mappings in eval for known canonical aliases (for example `P&F` <-> `PERSONNEL`, date formats).
3. Strengthen policy-specific routing so metadata extraction/citations stay in the requested document.
4. Add extra gold narrative items with `required_phrases` to avoid brittle literal expected strings.
