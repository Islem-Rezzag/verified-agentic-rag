# Results and Figures

This folder contains committed showcase outputs for the post-upgrade evaluation architecture.

## Inputs

- Question-level CSV:
  - `reports/full_system_eval_question_results_20260212.csv`
- Suite JSON snapshots:
  - `reports/samples/eval_results_suite_retrieval_post_upgrade.json`
  - `reports/samples/eval_results_suite_full_post_upgrade.json`

## Figures

- `reports/figures/pass_rate_by_dataset_mode.png`
  - Compares pass rate for Gold/Silver in retrieval vs full modes.
- `reports/figures/behavior_confusion_full_mode.png`
  - Shows expected behavior (`answer`/`refuse`) versus actual `cannot_answer`.
- `reports/figures/rule_pass_breakdown_full_mode.png`
  - Pass/fail breakdown for core strict rules in full mode:
    - refusal
    - citation
    - verification
    - expected value
- `reports/figures/context_precision_distribution.png`
  - Distribution of document-level context precision, revealing residual retrieval noise.

## Regenerate

```bash
python scripts/generate_report_figures.py \
  --csv-path reports/full_system_eval_question_results_20260212.csv \
  --output-dir reports/figures
```
