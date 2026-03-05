# Mandatory Analysis Inputs (Copy-Paste Pack)

Use this file as the single source of required inputs for external analysis of the `20260213_agentic_fixes` run.

## 1) Run Identity and Artifact Paths

- `run_id`: `20260213_agentic_fixes`
- `generated_on`: `2026-02-13 21:54:03 UTC`
- `retrieval_suite_json`: `reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_retrieval.json`
- `full_suite_json`: `reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_full.json`
- `question_results_csv`: `reports/runs/20260213_agentic_fixes/tables/20260213_agentic_fixes_question_results.csv`
- `summary_report_md`: `reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.md`
- `summary_report_pdf`: `reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.pdf`
- `results_index`: `reports/RESULTS.md`

Figures:
- `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_pass_rate_by_dataset_mode.png`
- `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_behavior_confusion_full_mode.png`
- `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_rule_pass_breakdown_full_mode.png`
- `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_retrieval_ranking_metrics_distribution.png`
- `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_context_precision_distribution.png`

## 2) Mandatory Evaluation Algorithm Inputs

Evaluator implementation:
- `src/verified_agentic_rag/evals.py`

Pass rules (must be used exactly):

Retrieval mode:
- `pass_expected_doc_rule`
- `pass_evidence_recall_rule`
- `pass_expected_value_rule`
- `pass_overall = pass_expected_doc_rule AND pass_evidence_recall_rule AND pass_expected_value_rule`

Full mode:
- `pass_refusal_rule`
- `pass_citation_rule`
- `pass_expected_doc_rule`
- `pass_evidence_recall_rule`
- `pass_expected_value_rule`
- `pass_citation_overlap_rule`
- `pass_verification_rule`
- `pass_overall = AND(all rules above)`

Answer matching signals:
- `expected_answer` and/or `expected_answer_regex`
- `required_phrases` (can match either answer text or cited evidence text)
- `gold_evidence_labels` used for overlap checks

Strict groundedness:
- answered items must have valid citations
- citations must overlap gold evidence
- verification gate must pass for answer-expected items

## 3) Dataset Composition (This Run)

Gold (`n=42`):
- `metadata=19`
- `procedure=10`
- `definition=3`
- `out_of_scope=8`
- `multi_chunk=0`
- `other(scope)=2` (from suite type key)

Silver (`n=142`):
- `metadata=107`
- `procedure=14`
- `definition=3`
- `out_of_scope=15`
- `multi=3` (suite type key)

## 4) Aggregate Metrics

Retrieval mode:
- Gold: `38/42`, pass rate `0.9048`
  - `avg_evidence_recall@k=1.0000`
  - `avg_MRR=0.9706`
  - `avg_ranked_context_precision=0.9706`
  - `avg_nDCG@k=0.9783`
  - `avg_context_precision_doc=0.5931`
  - `avg_context_recall_doc=1.0000`
- Silver: `131/142`, pass rate `0.9225`
  - `avg_evidence_recall@k=1.0000`
  - `avg_MRR=0.9961`
  - `avg_ranked_context_precision=0.9961`
  - `avg_nDCG@k=0.9971`
  - `avg_context_precision_doc=0.4528`
  - `avg_context_recall_doc=1.0000`

Full mode:
- Gold: `26/42`, pass rate `0.6190`
  - `avg_evidence_recall@k=1.0000`
  - `avg_MRR=0.9853`
  - `avg_ranked_context_precision=0.9853`
  - `avg_nDCG@k=0.9891`
  - `avg_context_precision_doc=0.6176`
  - `avg_context_recall_doc=1.0000`
- Silver: `88/142`, pass rate `0.6197`
  - `avg_evidence_recall@k=1.0000`
  - `avg_MRR=1.0000`
  - `avg_ranked_context_precision=1.0000`
  - `avg_nDCG@k=1.0000`
  - `avg_context_precision_doc=0.5262`
  - `avg_context_recall_doc=1.0000`

## 5) Full-Mode Mandatory Behavior and Rule Breakdown

Behavior confusion (expected_behavior vs cannot_answer):

Gold (`n=42`):
- expected `answer`, actual answered (`cannot_answer=false`): `24`
- expected `answer`, false refusal (`cannot_answer=true`): `10`
- expected `refuse`, correct refusal (`cannot_answer=true`): `8`

Silver (`n=142`):
- expected `answer`, actual answered (`cannot_answer=false`): `101`
- expected `answer`, false refusal (`cannot_answer=true`): `26`
- expected `refuse`, correct refusal (`cannot_answer=true`): `15`

Rule pass/fail counts:

Gold:
- `pass_refusal_rule`: pass `32`, fail `10`
- `pass_citation_rule`: pass `42`, fail `0`
- `pass_citation_overlap_rule`: pass `32`, fail `10`
- `pass_expected_value_rule`: pass `27`, fail `15`
- `pass_verification_rule`: pass `42`, fail `0`

Silver:
- `pass_refusal_rule`: pass `116`, fail `26`
- `pass_citation_rule`: pass `142`, fail `0`
- `pass_citation_overlap_rule`: pass `110`, fail `32`
- `pass_expected_value_rule`: pass `88`, fail `54`
- `pass_verification_rule`: pass `142`, fail `0`

## 6) Full-Mode Pass Rate by Question Type

Gold:
- `metadata`: `15/19` (`0.7895`)
- `procedure`: `3/10` (`0.3000`)
- `definition`: `0/3` (`0.0000`)
- `out_of_scope`: `8/8` (`1.0000`)
- `scope`: `0/2` (`0.0000`)

Silver:
- `metadata`: `71/107` (`0.6636`)
- `procedure`: `2/14` (`0.1429`)
- `definition`: `0/3` (`0.0000`)
- `multi`: `0/3` (`0.0000`)
- `out_of_scope`: `15/15` (`1.0000`)

## 7) Delta vs Prior Run (`20260213_uploaded_labels`)

Full mode:
- Gold: `21/42 -> 26/42` (`+5`, from `50.00%` to `61.90%`)
- Silver: `81/142 -> 88/142` (`+7`, from `57.04%` to `61.97%`)

Retrieval mode:
- unchanged
  - Gold: `38/42` (`90.48%`)
  - Silver: `131/142` (`92.25%`)

## 8) Repro Commands (Exact)

```bash
python -m verified_agentic_rag.cli ingest --reset --scope docs
python -m verified_agentic_rag.cli eval-suite --output reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_retrieval.json --mode retrieval
python -m verified_agentic_rag.cli eval-suite --output reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_full.json --mode full
python scripts/generate_evaluation_report.py --retrieval-suite reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_retrieval.json --full-suite reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_full.json --csv-out reports/runs/20260213_agentic_fixes/tables/20260213_agentic_fixes_question_results.csv --md-out reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.md --pdf-out reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.pdf
python scripts/generate_report_figures.py --csv-path reports/runs/20260213_agentic_fixes/tables/20260213_agentic_fixes_question_results.csv --output-dir reports/runs/20260213_agentic_fixes/figures --date-tag 20260213_agentic_fixes
python -m pytest -q
```

## 9) Copy-Paste JSON Input Block

```json
{
  "run_id": "20260213_agentic_fixes",
  "artifacts": {
    "retrieval_suite_json": "reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_retrieval.json",
    "full_suite_json": "reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_full.json",
    "question_results_csv": "reports/runs/20260213_agentic_fixes/tables/20260213_agentic_fixes_question_results.csv",
    "summary_report_md": "reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.md",
    "results_index": "reports/RESULTS.md"
  },
  "dataset_composition": {
    "gold": {"total": 42, "metadata": 19, "procedure": 10, "definition": 3, "out_of_scope": 8, "multi_chunk": 0, "scope": 2},
    "silver": {"total": 142, "metadata": 107, "procedure": 14, "definition": 3, "out_of_scope": 15, "multi": 3}
  },
  "aggregate_metrics": {
    "retrieval": {
      "gold": {"passed": 38, "count": 42, "pass_rate": 0.9048, "avg_evidence_recall_at_k": 1.0, "avg_mrr": 0.9706, "avg_ranked_context_precision": 0.9706, "avg_ndcg_at_k": 0.9783},
      "silver": {"passed": 131, "count": 142, "pass_rate": 0.9225, "avg_evidence_recall_at_k": 1.0, "avg_mrr": 0.9961, "avg_ranked_context_precision": 0.9961, "avg_ndcg_at_k": 0.9971}
    },
    "full": {
      "gold": {"passed": 26, "count": 42, "pass_rate": 0.6190, "avg_evidence_recall_at_k": 1.0, "avg_mrr": 0.9853, "avg_ranked_context_precision": 0.9853, "avg_ndcg_at_k": 0.9891},
      "silver": {"passed": 88, "count": 142, "pass_rate": 0.6197, "avg_evidence_recall_at_k": 1.0, "avg_mrr": 1.0, "avg_ranked_context_precision": 1.0, "avg_ndcg_at_k": 1.0}
    }
  },
  "full_mode_behavior_confusion": {
    "gold": {"expected_answer_actual_answer": 24, "expected_answer_actual_refuse": 10, "expected_refuse_actual_refuse": 8},
    "silver": {"expected_answer_actual_answer": 101, "expected_answer_actual_refuse": 26, "expected_refuse_actual_refuse": 15}
  },
  "full_mode_rule_failures": {
    "gold": {"pass_expected_value_rule_fail": 15, "pass_refusal_rule_fail": 10, "pass_citation_overlap_rule_fail": 10},
    "silver": {"pass_expected_value_rule_fail": 54, "pass_citation_overlap_rule_fail": 32, "pass_refusal_rule_fail": 26}
  },
  "algorithm_mandatory_rules": {
    "retrieval_pass_overall": "pass_expected_doc_rule && pass_evidence_recall_rule && pass_expected_value_rule",
    "full_pass_overall": "pass_refusal_rule && pass_citation_rule && pass_expected_doc_rule && pass_evidence_recall_rule && pass_expected_value_rule && pass_citation_overlap_rule && pass_verification_rule",
    "required_phrases_logic": "required_phrases may be satisfied by answer text or cited evidence text"
  },
  "delta_vs_previous_run": {
    "reference_run": "20260213_uploaded_labels",
    "full_gold": {"from": "21/42", "to": "26/42", "delta_passed": 5},
    "full_silver": {"from": "81/142", "to": "88/142", "delta_passed": 7},
    "retrieval_gold": "38/42",
    "retrieval_silver": "131/142"
  }
}
```
