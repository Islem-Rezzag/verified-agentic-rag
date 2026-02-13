# Run: 20260213_agentic_fixes

This folder contains artifacts from the follow-up run after targeted agent fixes for false refusals and wrong-document metadata citations.

## Contents

- `suite/`
  - `20260213_agentic_fixes_suite_retrieval.json`
  - `20260213_agentic_fixes_suite_full.json`
- `tables/`
  - `20260213_agentic_fixes_question_results.csv`
- `analysis/`
  - `20260213_agentic_fixes_evaluation_summary.md`
  - `20260213_agentic_fixes_evaluation_summary.pdf`
- `figures/`
  - `20260213_agentic_fixes_pass_rate_by_dataset_mode.png`
  - `20260213_agentic_fixes_behavior_confusion_full_mode.png`
  - `20260213_agentic_fixes_rule_pass_breakdown_full_mode.png`
  - `20260213_agentic_fixes_retrieval_ranking_metrics_distribution.png`
  - `20260213_agentic_fixes_context_precision_distribution.png`

## Core Metrics (from this run)

- Retrieval pass:
  - Gold: `38/42` (`90.48%`)
  - Silver: `131/142` (`92.25%`)
- Full pass:
  - Gold: `26/42` (`61.90%`)
  - Silver: `88/142` (`61.97%`)

## Delta vs `20260213_uploaded_labels` (full mode)

- Gold: `+5` pass (`21/42` -> `26/42`)
- Silver: `+7` pass (`81/142` -> `88/142`)
