# Run: 20260302_label_matching_upgrade

This run captures post-change evaluation after adding canonical alias normalization for label matching in `evals.py` (notably `P&F` <-> `PERSONNEL`).

## Contents

- `suite/`
  - `20260302_label_matching_upgrade_suite_retrieval.json`
  - `20260302_label_matching_upgrade_suite_full.json`
- `tables/`
  - `20260302_label_matching_upgrade_question_results.csv`
- `analysis/`
  - `20260302_label_matching_upgrade_evaluation_summary.md`
  - `20260302_label_matching_upgrade_evaluation_summary.pdf`
  - `20260302_label_matching_upgrade_implementation_analysis.md`
- `figures/`
  - `20260302_label_matching_upgrade_pass_rate_by_dataset_mode.png`
  - `20260302_label_matching_upgrade_behavior_confusion_full_mode.png`
  - `20260302_label_matching_upgrade_rule_pass_breakdown_full_mode.png`
  - `20260302_label_matching_upgrade_retrieval_ranking_metrics_distribution.png`
  - `20260302_label_matching_upgrade_context_precision_distribution.png`

## Core Metrics

- Retrieval pass:
  - Gold: `38/42` (`90.48%`)
  - Silver: `131/142` (`92.25%`)
- Full pass:
  - Gold: `26/42` (`61.90%`)
  - Silver: `92/142` (`64.79%`)

## Delta vs `20260213_agentic_fixes` (full mode)

- Gold: `+0` pass (`26/42` -> `26/42`)
- Silver: `+4` pass (`88/142` -> `92/142`)
