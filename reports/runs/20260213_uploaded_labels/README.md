# Run: 20260213_uploaded_labels

This folder contains all artifacts generated from the evaluation run after replacing the repo labels with the uploaded `gold.jsonl` and `silver.jsonl`.

## Contents

- `suite/`
  - `20260213_uploaded_labels_suite_retrieval.json`
  - `20260213_uploaded_labels_suite_full.json`
- `tables/`
  - `20260213_uploaded_labels_question_results.csv`
- `analysis/`
  - `20260213_uploaded_labels_evaluation_summary.md`
  - `20260213_uploaded_labels_evaluation_summary.pdf`
  - `20260213_uploaded_labels_answer_audit.md`
  - `20260213_uploaded_labels_answer_audit.pdf`
  - `20260213_uploaded_labels_reliability_analysis.md`
  - `20260213_uploaded_labels_reliability_analysis.pdf`
- `figures/`
  - `20260213_uploaded_labels_pass_rate_by_dataset_mode.png`
  - `20260213_uploaded_labels_behavior_confusion_full_mode.png`
  - `20260213_uploaded_labels_rule_pass_breakdown_full_mode.png`
  - `20260213_uploaded_labels_retrieval_ranking_metrics_distribution.png`
  - `20260213_uploaded_labels_context_precision_distribution.png`

## Core Metrics (from this run)

- Retrieval pass:
  - Gold: `38/42` (`90.48%`)
  - Silver: `131/142` (`92.25%`)
- Full pass:
  - Gold: `21/42` (`50.00%`)
  - Silver: `81/142` (`57.04%`)
- Tests: `39/39` passed
