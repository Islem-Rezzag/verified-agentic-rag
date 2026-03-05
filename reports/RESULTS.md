# Results Index

This directory stores evaluation outputs in a run-based structure.

## Naming Convention

- Folder per run: `reports/runs/<run_id>/`
- Subfolders:
  - `suite/` for suite JSON outputs
  - `tables/` for question-level CSV
  - `analysis/` for markdown/pdf reports
  - `figures/` for PNG charts
- File prefix: `<run_id>_...`

## Run Folders

### `20260302_label_matching_upgrade`

- Suite outputs:
  - `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_retrieval.json`
  - `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_full.json`
- Question-level table:
  - `reports/runs/20260302_label_matching_upgrade/tables/20260302_label_matching_upgrade_question_results.csv`
- Reports:
  - `reports/runs/20260302_label_matching_upgrade/analysis/20260302_label_matching_upgrade_evaluation_summary.md`
  - `reports/runs/20260302_label_matching_upgrade/analysis/20260302_label_matching_upgrade_evaluation_summary.pdf`
  - `reports/runs/20260302_label_matching_upgrade/analysis/20260302_label_matching_upgrade_implementation_analysis.md`
- Figures:
  - `reports/runs/20260302_label_matching_upgrade/figures/20260302_label_matching_upgrade_pass_rate_by_dataset_mode.png`
  - `reports/runs/20260302_label_matching_upgrade/figures/20260302_label_matching_upgrade_behavior_confusion_full_mode.png`
  - `reports/runs/20260302_label_matching_upgrade/figures/20260302_label_matching_upgrade_rule_pass_breakdown_full_mode.png`
  - `reports/runs/20260302_label_matching_upgrade/figures/20260302_label_matching_upgrade_retrieval_ranking_metrics_distribution.png`
  - `reports/runs/20260302_label_matching_upgrade/figures/20260302_label_matching_upgrade_context_precision_distribution.png`
- Core metrics:
  - Retrieval: Gold `38/42` (`90.48%`), Silver `131/142` (`92.25%`)
  - Full: Gold `26/42` (`61.90%`), Silver `92/142` (`64.79%`)
  - Delta vs `20260213_agentic_fixes` full mode: Gold `+0`, Silver `+4`

### `20260213_agentic_fixes`

- Suite outputs:
  - `reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_retrieval.json`
  - `reports/runs/20260213_agentic_fixes/suite/20260213_agentic_fixes_suite_full.json`
- Question-level table:
  - `reports/runs/20260213_agentic_fixes/tables/20260213_agentic_fixes_question_results.csv`
- Reports:
  - `reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.md`
  - `reports/runs/20260213_agentic_fixes/analysis/20260213_agentic_fixes_evaluation_summary.pdf`
- Figures:
  - `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_pass_rate_by_dataset_mode.png`
  - `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_behavior_confusion_full_mode.png`
  - `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_rule_pass_breakdown_full_mode.png`
  - `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_retrieval_ranking_metrics_distribution.png`
  - `reports/runs/20260213_agentic_fixes/figures/20260213_agentic_fixes_context_precision_distribution.png`
- Core metrics:
  - Retrieval: Gold `38/42` (`90.48%`), Silver `131/142` (`92.25%`)
  - Full: Gold `26/42` (`61.90%`), Silver `88/142` (`61.97%`)
  - Improvement vs `20260213_uploaded_labels` full mode: Gold `+5`, Silver `+7`

### `20260213_uploaded_labels`

- Suite outputs:
  - `reports/runs/20260213_uploaded_labels/suite/20260213_uploaded_labels_suite_retrieval.json`
  - `reports/runs/20260213_uploaded_labels/suite/20260213_uploaded_labels_suite_full.json`
- Question-level table:
  - `reports/runs/20260213_uploaded_labels/tables/20260213_uploaded_labels_question_results.csv`
- Reports:
  - `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_evaluation_summary.md`
  - `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_evaluation_summary.pdf`
  - `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_answer_audit.md`
  - `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_answer_audit.pdf`
  - `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_reliability_analysis.md`
  - `reports/runs/20260213_uploaded_labels/analysis/20260213_uploaded_labels_reliability_analysis.pdf`
- Figures:
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_pass_rate_by_dataset_mode.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_behavior_confusion_full_mode.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_rule_pass_breakdown_full_mode.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_retrieval_ranking_metrics_distribution.png`
  - `reports/runs/20260213_uploaded_labels/figures/20260213_uploaded_labels_context_precision_distribution.png`
- Core metrics:
  - Retrieval: Gold `38/42` (`90.48%`), Silver `131/142` (`92.25%`)
  - Full: Gold `21/42` (`50.00%`), Silver `81/142` (`57.04%`)

## Historical Baseline (kept)

- `reports/full_system_eval_question_results_20260212.csv`
- `reports/full_system_evaluation_report_20260212.md`
- `reports/samples/eval_results_suite_retrieval_post_upgrade.json`
- `reports/samples/eval_results_suite_full_post_upgrade.json`
- `reports/figures/pass_rate_by_dataset_mode.png`
- `reports/figures/behavior_confusion_full_mode.png`
- `reports/figures/rule_pass_breakdown_full_mode.png`
- `reports/figures/context_precision_distribution.png`

## Regenerate Figures for a Run

```bash
python scripts/generate_report_figures.py \
  --csv-path reports/runs/20260213_uploaded_labels/tables/20260213_uploaded_labels_question_results.csv \
  --output-dir reports/runs/20260213_uploaded_labels/figures \
  --date-tag 20260213_uploaded_labels
```
