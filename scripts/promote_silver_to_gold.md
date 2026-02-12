# Promote Silver To Gold

Use this workflow to convert weak labels into trusted benchmark items.

## 1) Sample candidates
- Run silver eval in full mode.
- Sort by failures with:
  - `retrieval_missed_existing_value=true`
  - `pass_citation_overlap_rule=false`
  - low `evidence_mrr`

## 2) Manually verify evidence
- Open the cited source document.
- Confirm the expected value is explicitly present in the referenced span.
- If evidence is wrong or ambiguous, discard the item.

## 3) Normalize answer target
- Ensure `expected_answer` is canonical.
- Add `acceptable_answers` when multiple phrasings are valid.
- Set `normalization` (`uppercase`, `strip_punct`, `date_iso`) as needed.

## 4) Finalize gold row
- Copy the silver row to `evalset/gold.jsonl`.
- Update:
  - `id` to a stable `gold_*` identifier
  - `gold_evidence` to exact line-range labels
  - `question_type` if needed

## 5) Regression check
- Re-run `run_eval_gold_silver(mode="full")`.
- Confirm gold pass rate does not regress before merging.
