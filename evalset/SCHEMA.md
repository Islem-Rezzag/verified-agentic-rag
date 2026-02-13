# Evalset Schema (v2)

Each line in `gold.jsonl` and `silver.jsonl` is one JSON object.

## Required fields
- `id`: Stable unique identifier.
- `question`: User question to evaluate.
- `expected_behavior`: `answer` or `refuse`.
- `question_type`: `metadata`, `procedure`, `definition`, `multi_chunk`, or `out_of_scope`.

## Answer-target fields
- `expected_answer`: Canonical expected answer string, or list of required facts.
- `expected_answer_regex`: Optional regex for flexible matching.
- `required_phrases`: Optional list of phrases (2-5 recommended) that must appear in the answer text **or** in cited evidence text.
- `acceptable_answers`: Optional list of accepted variants.
- `normalization`: Optional normalization rule(s) applied before matching.
  - `uppercase`
  - `strip_punct`
  - `date_iso`

## Evidence fields
- `expected_doc`: Optional legacy doc-level target.
- `gold_evidence`: Evidence spans used for retrieval/citation evaluation.
  - List of objects:
    - `label`: Chunk label in `path:start-end` format
    - `must_contain`: Optional list of anchor strings expected in that evidence span
- `gold_evidence_labels`: Optional alias list of labels in `path:start-end` format.

## Legacy compatibility
The evaluator still supports old fields from `questions.jsonl`:
- `expected` (mapped to `expected_behavior`)
- `expected_value` (mapped to `expected_answer`)
- `expected_value_regex` (mapped to `expected_answer_regex`)

## Gold vs Silver
- `gold.jsonl`: Human-verified labels for reporting and gating.
- `silver.jsonl`: Auto/weak labels for broad regression diagnostics only.
