# Full Agent System Evaluation Report

- Generated on: 2026-02-12 18:02:46
- Project: verified-agentic-rag
- Retrieval suite file: `reports/samples/eval_results_suite_retrieval_post_upgrade.json`
- Full suite file: `reports/samples/eval_results_suite_full_post_upgrade.json`
- Question-level CSV: `reports/full_system_eval_question_results_20260212.csv`

## 1) Test Execution

The following was executed for this report:
- Retrieval evaluation suite: `run_eval_gold_silver(mode="retrieval")`
- Full end-to-end evaluation suite: `run_eval_gold_silver(mode="full")`
- Full unit/integration tests: `pytest -q` (36/36 passed)

## 2) Gold/Silver Architecture (How Results Are Interpreted)

- `gold.jsonl`: human-verified labels and evidence spans; this is the reliability score used for strict reporting/gating.
- `silver.jsonl`: auto/weakly labeled broader regression set; this is used for coverage and drift detection, not final claims by itself.
- Both datasets share v2 schema (`id`, `question`, `expected_behavior`, `question_type`, `expected_answer`, `gold_evidence`, optional normalization/variants).

## 3) Aggregate Results

### Retrieval mode

| Dataset | Count | Passed | Pass rate | Avg evidence_recall@k | Avg MRR | Avg ranked precision | Avg nDCG@k | Avg evidence coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gold | 4 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| silver | 11 | 11 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Full mode

| Dataset | Count | Passed | Pass rate | Avg evidence_recall@k | Avg MRR | Avg ranked precision | Avg nDCG@k | Avg evidence coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gold | 4 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| silver | 11 | 11 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Full-mode quality indicators (professional-style)

| Dataset | Pass overall | Answer behavior accuracy | Refusal behavior accuracy | Citation validity on answered | Groundedness pass on expected answers | Expected value match on expected answers | Evidence recall on answer items |
|---|---:|---:|---:|---:|---:|---:|---:|
| gold | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| silver | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## 4) Metric Dictionary and How to Read Them

- `pass_overall`: strict gate composed of rule checks below; this is your primary pass/fail signal per question.
- `pass_refusal_rule`: expected refuse must return `cannot_answer=True`; expected answer must return `cannot_answer=False`.
- `pass_citation_rule`: if agent answers, citations must exist and be valid labels; refusals are exempt.
- `pass_expected_doc_rule`: retrieved context should include expected document signal when specified.
- `pass_evidence_recall_rule`: for answer items, retrieved chunks must contain gold evidence overlap; for refuse items, this is intentionally bypassed.
- `pass_expected_value_rule`: answer (full mode) or retrieved context (retrieval mode) matches expected canonical value/regex.
- `pass_citation_overlap_rule`: at least one cited label overlaps gold evidence spans for answer-required questions.
- `pass_verification_rule`: groundedness verification must confirm answer claims are supported by retrieved evidence.
- `evidence_recall_at_k`: binary evidence retrieval hit at top-k (1.0=found, 0.0=miss).
- `evidence_mrr`: reciprocal rank of first evidence hit (1.0 means first ranked chunk is evidential).
- `context_precision_ranked`: ranking-aware precision over evidential hits.
- `evidence_ndcg_at_k`: ranking quality normalized to [0,1] against gold evidence ordering signal.
- `evidence_coverage`: fraction of distinct gold evidence spans covered by retrieved set.
- `retrieval_missed_existing_value`: corpus contains expected value but retrieved context does not (retriever/reranker issue).
- `reranker_dropped_evidence`: evidence was present pre-rerank but absent post-rerank.

## 5) Question-by-question results: GOLD

| ID | Type | Expected behavior | Full pass | Retrieval pass | Received behavior | Answer received |
|---|---|---|---:|---:|---|---|
| gold_q1_responsible_committee_data_protection | metadata | answer | Yes | Yes | answer | The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100] |
| gold_q2_review_guidance_data_protection | metadata | answer | Yes | Yes | answer | The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100] |
| gold_q3_policy_group_it_acceptable_use | metadata | answer | Yes | Yes | answer | The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100] |
| gold_q4_out_of_scope_k8s_autoscaler | out_of_scope | refuse | Yes | Yes | refuse | I cannot answer from the repository based on the retrieved sources. |

### gold_q1_responsible_committee_data_protection

- Question asked: What is the responsible committee for the Data Protection Policy - Employees?
- Expected behavior: `answer`
- Expected answer target: `PERSONNEL`
- Gold evidence labels: `docs/txt/Data_Protection_-_Employees.txt:1-120`
- Agent answer received: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Answer citations (model output): `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Run log file: `20260212-180026_b3bdcc6e20.json` | attempts=1 | final_query=`What is the responsible committee for the Data Protection Policy - Employees?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### gold_q2_review_guidance_data_protection

- Question asked: What is the review frequency (or next review date guidance) for the Data Protection Policy - Employees?
- Expected behavior: `answer`
- Expected answer target: `Annual or if required by legislation`
- Gold evidence labels: `docs/txt/Data_Protection_-_Employees.txt:1-120`
- Agent answer received: The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Answer citations (model output): `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Run log file: `20260212-180028_2615c92cbb.json` | attempts=1 | final_query=`What is the review frequency (or next review date guidance) for the Data Protection Policy - Employees?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### gold_q3_policy_group_it_acceptable_use

- Question asked: What is the policy group for the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: `answer`
- Expected answer target: `Employees/Members`
- Gold evidence labels: `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-120`
- Agent answer received: The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Answer citations (model output): `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100`
- Run log file: `20260212-180054_2aad852dc8.json` | attempts=1 | final_query=`What is the policy group for the Provision of IT Equipment & Acceptable Use policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### gold_q4_out_of_scope_k8s_autoscaler

- Question asked: Does this policy pack contain a built-in Kubernetes autoscaler?
- Expected behavior: `refuse`
- Expected answer target: ``
- Gold evidence labels: ``
- Agent answer received: I cannot answer from the repository based on the retrieved sources.
- Answer citations (model output): ``
- Run log file: `20260212-180043_302b4aab5d.json` | attempts=2 | final_query=`Provide sources from the policy pack that mention Kubernetes components (e.g., autoscaler, HPA, Cluster Autoscaler) or an inventory/manifest listing included Kubernetes tools.`
- Retrieval grade reason: `All sources are HR/IT/data protection policy documents; none mention Kubernetes or an autoscaler, so they do not explicitly answer the question.`
- Top retrieved label: `docs/txt/Employee_Handbook.txt:201-320`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k`: N/A (no gold evidence required for this refusal/out-of-scope item).
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=None` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

## 5) Question-by-question results: SILVER

| ID | Type | Expected behavior | Full pass | Retrieval pass | Received behavior | Answer received |
|---|---|---|---:|---:|---|---|
| silver_q1_data_protection_policy_group | metadata | answer | Yes | Yes | answer | The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100] |
| silver_q2_data_protection_review_guidance | metadata | answer | Yes | Yes | answer | The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100] |
| silver_q3_employee_handbook_responsible_committee | metadata | answer | Yes | Yes | answer | The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100] |
| silver_q4_employee_handbook_review_guidance | metadata | answer | Yes | Yes | answer | The review frequency is Annual or as required by legislation.[docs/txt/Employee_Handbook.txt:1-100] |
| silver_q5_equality_diversity_policy_group | metadata | answer | Yes | Yes | answer | The policy group is Employees.[docs/txt/Equality_Diversity.txt:1-100] |
| silver_q6_equality_diversity_review_guidance | metadata | answer | Yes | Yes | answer | The review frequency is Annual or as required.[docs/txt/Equality_Diversity.txt:1-100] |
| silver_q7_recruitment_responsible_committee | metadata | answer | Yes | Yes | answer | The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100] |
| silver_q8_recruitment_review_guidance | metadata | answer | Yes | Yes | answer | The review frequency is Annual or as required by legislation.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100] |
| silver_q9_it_acceptable_use_policy_group | metadata | answer | Yes | Yes | answer | The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100] |
| silver_q10_it_acceptable_use_review_guidance | metadata | answer | Yes | Yes | answer | The review frequency is Annual or as required.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100] |
| silver_q11_out_of_scope_kubernetes_hpa | out_of_scope | refuse | Yes | Yes | refuse | I cannot answer from the repository based on the retrieved sources. |

### silver_q1_data_protection_policy_group

- Question asked: What is the policy group for the Data Protection Policy - Employees?
- Expected behavior: `answer`
- Expected answer target: `Employees`
- Gold evidence labels: `docs/txt/Data_Protection_-_Employees.txt:1-120`
- Agent answer received: The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Answer citations (model output): `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Run log file: `20260212-180044_2fb02ad436.json` | attempts=1 | final_query=`What is the policy group for the Data Protection Policy - Employees?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q2_data_protection_review_guidance

- Question asked: What is the next review date guidance for the Data Protection Policy - Employees?
- Expected behavior: `answer`
- Expected answer target: `Annual or if required by legislation`
- Gold evidence labels: `docs/txt/Data_Protection_-_Employees.txt:1-120`
- Agent answer received: The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Answer citations (model output): `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Run log file: `20260212-180046_9bf96b206b.json` | attempts=1 | final_query=`What is the next review date guidance for the Data Protection Policy - Employees?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Data_Protection_-_Employees.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q3_employee_handbook_responsible_committee

- Question asked: What is the responsible committee for the Employee Handbook?
- Expected behavior: `answer`
- Expected answer target: `PERSONNEL`
- Gold evidence labels: `docs/txt/Employee_Handbook.txt:1-120`
- Agent answer received: The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100]
- Answer citations (model output): `docs/txt/Employee_Handbook.txt:1-100`
- Run log file: `20260212-180047_cff569b548.json` | attempts=1 | final_query=`What is the responsible committee for the Employee Handbook?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Employee_Handbook.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q4_employee_handbook_review_guidance

- Question asked: What is the next review date guidance for the Employee Handbook?
- Expected behavior: `answer`
- Expected answer target: `Annual or as required by legislation`
- Gold evidence labels: `docs/txt/Employee_Handbook.txt:1-120`
- Agent answer received: The review frequency is Annual or as required by legislation.[docs/txt/Employee_Handbook.txt:1-100]
- Answer citations (model output): `docs/txt/Employee_Handbook.txt:1-100`
- Run log file: `20260212-180048_46937befdd.json` | attempts=1 | final_query=`What is the next review date guidance for the Employee Handbook?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Employee_Handbook.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q5_equality_diversity_policy_group

- Question asked: What is the policy group for the Equality & Diversity Policy?
- Expected behavior: `answer`
- Expected answer target: `Employees`
- Gold evidence labels: `docs/txt/Equality_Diversity.txt:1-120`
- Agent answer received: The policy group is Employees.[docs/txt/Equality_Diversity.txt:1-100]
- Answer citations (model output): `docs/txt/Equality_Diversity.txt:1-100`
- Run log file: `20260212-180049_bf3b85cb0c.json` | attempts=1 | final_query=`What is the policy group for the Equality & Diversity Policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Equality_Diversity.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q6_equality_diversity_review_guidance

- Question asked: What is the next review date guidance for the Equality & Diversity Policy?
- Expected behavior: `answer`
- Expected answer target: `Annual or as required`
- Gold evidence labels: `docs/txt/Equality_Diversity.txt:1-120`
- Agent answer received: The review frequency is Annual or as required.[docs/txt/Equality_Diversity.txt:1-100]
- Answer citations (model output): `docs/txt/Equality_Diversity.txt:1-100`
- Run log file: `20260212-180051_e19b437fcc.json` | attempts=1 | final_query=`What is the next review date guidance for the Equality & Diversity Policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Equality_Diversity.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q7_recruitment_responsible_committee

- Question asked: What is the responsible committee for the Recruitment and Selection Policy?
- Expected behavior: `answer`
- Expected answer target: `PERSONNEL`
- Gold evidence labels: `docs/txt/Recruitment_and_Selection_Policy.txt:1-120`
- Agent answer received: The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Answer citations (model output): `docs/txt/Recruitment_and_Selection_Policy.txt:1-100`
- Run log file: `20260212-180052_da87bc48f6.json` | attempts=1 | final_query=`What is the responsible committee for the Recruitment and Selection Policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Recruitment_and_Selection_Policy.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q8_recruitment_review_guidance

- Question asked: What is the next review date guidance for the Recruitment and Selection Policy?
- Expected behavior: `answer`
- Expected answer target: `Annual or as required by legislation`
- Gold evidence labels: `docs/txt/Recruitment_and_Selection_Policy.txt:1-120`
- Agent answer received: The review frequency is Annual or as required by legislation.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Answer citations (model output): `docs/txt/Recruitment_and_Selection_Policy.txt:1-100`
- Run log file: `20260212-180053_dca0bd179c.json` | attempts=1 | final_query=`What is the next review date guidance for the Recruitment and Selection Policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Recruitment_and_Selection_Policy.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q9_it_acceptable_use_policy_group

- Question asked: What is the policy group for the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: `answer`
- Expected answer target: `Employees/Members`
- Gold evidence labels: `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-120`
- Agent answer received: The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Answer citations (model output): `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100`
- Run log file: `20260212-180054_2aad852dc8.json` | attempts=1 | final_query=`What is the policy group for the Provision of IT Equipment & Acceptable Use policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q10_it_acceptable_use_review_guidance

- Question asked: What is the next review date guidance for the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: `answer`
- Expected answer target: `Annual or as required`
- Gold evidence labels: `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-120`
- Agent answer received: The review frequency is Annual or as required.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Answer citations (model output): `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100`
- Run log file: `20260212-180056_3ffdcdb244.json` | attempts=1 | final_query=`What is the next review date guidance for the Provision of IT Equipment & Acceptable Use policy?`
- Retrieval grade reason: `deterministic metadata extraction matched`
- Top retrieved label: `docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k=1.0`: retriever returned at least one chunk overlapping gold evidence.
  - `evidence_mrr=1.0`: first relevant evidence rank reciprocal (1.0 means rank-1).
  - `evidence_ndcg_at_k=1.0`: ranking quality against gold evidence (bounded [0,1]).
  - `context_precision_ranked=1.0`: relevant evidence appears early with high precision.
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=True` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

### silver_q11_out_of_scope_kubernetes_hpa

- Question asked: Does the policy corpus document Kubernetes HPA configuration values?
- Expected behavior: `refuse`
- Expected answer target: ``
- Gold evidence labels: ``
- Agent answer received: I cannot answer from the repository based on the retrieved sources.
- Answer citations (model output): ``
- Run log file: `20260212-180102_db80c53403.json` | attempts=2 | final_query=`Do any documents in the corpus mention Kubernetes Horizontal Pod Autoscaler (HPA) settings (e.g., minReplicas, maxReplicas, targetCPUUtilizationPercentage)? If so, which file and lines?`
- Retrieval grade reason: `All sources are HR/IT council policy documents; none explicitly mention Kubernetes, HPA, or configuration values.`
- Top retrieved label: `docs/txt/Employee_Handbook.txt:201-320`
- Rule outcomes (full mode): refusal=PASS, citation=PASS, expected_doc=PASS, evidence=PASS, expected_value=PASS, citation_overlap=PASS, verification=PASS, overall=PASS.
- Metric interpretation for this answer:
  - `evidence_recall_at_k`: N/A (no gold evidence required for this refusal/out-of-scope item).
  - `pass_expected_value_rule=True` compares the produced answer (or retrieved text in retrieval mode) to canonical expected value/regex.
  - `pass_citation_rule=True` and `citation_validity=None` enforce that answered outputs carry valid citations.
  - `pass_citation_overlap_rule=True` checks cited labels overlap gold evidence spans.
  - `pass_verification_rule=True` reflects groundedness verifier support for answer claims.

## 6) What Has Been Achieved

- Full-system reliability gate is clean on both tiers: gold 4/4 and silver 11/11 in retrieval and full modes.
- Strict answer controls are active and passing: refusal correctness, citation validity, citation-evidence overlap, and groundedness verification.
- Retrieval ranking stack is behaving correctly for this benchmark: evidence_recall@k, MRR, ranked precision, and nDCG all at ceiling on current sets.
- Diagnostic metrics are healthy: no `retrieval_missed_existing_value` and no `reranker_dropped_evidence` in this run.
- Previously fixed issues are validated in live results:
  - Refusal items are no longer incorrectly failed by evidence-recall gating.
  - Review guidance extraction captures full phrases including `if/as required` variants.
  - nDCG remains within valid bounds [0,1].

## 7) Notes for Professional Accuracy Tables

- Use `gold` as the headline reliability table (release/candidate gating).
- Use `silver` as regression coverage and early-warning table.
- Use the generated CSV for pivoting by dataset, question type, behavior, and each rule/metric.
- Recommended primary columns for executive scorecards: `pass_overall_full`, `pass_refusal_rule`, `pass_citation_rule`, `pass_verification_rule`, `answer_matches_expected_value`, `evidence_recall_at_k_full`, `evidence_mrr_full`, `evidence_ndcg_at_k_full`.
