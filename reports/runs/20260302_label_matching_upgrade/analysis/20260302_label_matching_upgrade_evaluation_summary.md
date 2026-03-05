# Full Agent System Evaluation Report

- Generated on: 2026-03-02 15:14:09 UTC
- Retrieval suite file: `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_retrieval.json`
- Full suite file: `reports/runs/20260302_label_matching_upgrade/suite/20260302_label_matching_upgrade_suite_full.json`
- Question-level CSV: `reports/runs/20260302_label_matching_upgrade/tables/20260302_label_matching_upgrade_question_results.csv`

## Dataset Composition

| Dataset | Total | Metadata | Procedure | Definition | Multi-chunk | Out-of-scope |
|---|---|---|---|---|---|---|
| gold | 42 | 19 | 10 | 3 | 0 | 8 |
| silver | 142 | 107 | 14 | 3 | 0 | 15 |

## Aggregate Results

### Retrieval mode
| Dataset | Count | Passed | Pass rate | Avg evidence_recall@k | Avg MRR | Avg ranked precision | Avg nDCG@k |
|---|---|---|---|---|---|---|---|
| gold | 42 | 38 | 0.9048 | 1.0000 | 0.9706 | 0.9706 | 0.9783 |
| silver | 142 | 131 | 0.9225 | 1.0000 | 0.9961 | 0.9961 | 0.9971 |

### Full mode
| Dataset | Count | Passed | Pass rate | Avg evidence_recall@k | Avg MRR | Avg ranked precision | Avg nDCG@k |
|---|---|---|---|---|---|---|---|
| gold | 42 | 26 | 0.6190 | 1.0000 | 0.9853 | 0.9853 | 0.9891 |
| silver | 142 | 92 | 0.6479 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Failure Breakdown (Full mode)

- gold:
  - pass_expected_value_rule: 15
  - pass_refusal_rule: 7
  - pass_citation_overlap_rule: 7
- silver:
  - pass_expected_value_rule: 47
  - pass_citation_overlap_rule: 32
  - pass_refusal_rule: 26

## Notes

- `required_phrases` checks are enabled in evaluation and can be satisfied by answer text or cited evidence text.
- Core groundedness requirements remain strict: citation validity, citation overlap with gold evidence, and verification pass.
