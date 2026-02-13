# Full System Answer Audit (New Uploaded Labels)

- Generated: 2026-02-13 18:10:54 UTC
- Retrieval suite: `reports/samples/eval_results_suite_retrieval_20260213_newlabels.json`
- Full suite: `reports/samples/eval_results_suite_full_20260213_newlabels.json`

## 1) High-Level Results

| Dataset | Questions | Full Passed | Full Pass Rate | Retrieval Passed | Retrieval Pass Rate |
|---|---:|---:|---:|---:|---:|
| gold | 42 | 21 | 50.00% | 38 | 90.48% |
| silver | 142 | 81 | 57.04% | 131 | 92.25% |

## 2) Dataset Composition

| Dataset | metadata | procedure | definition | multi_chunk | out_of_scope | other | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| gold | 19 | 10 | 3 | 0 | 8 | 2 | 42 |
| silver | 107 | 14 | 3 | 0 | 15 | 3 | 142 |

## 3) Retrieval vs Full Metrics

| Dataset | Avg Recall@k (retr) | Avg MRR (retr) | Avg nDCG@k (retr) | Avg Ranked Precision (retr) | Avg Recall@k (full) | Avg MRR (full) | Avg nDCG@k (full) | Avg Ranked Precision (full) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gold | 0.8095 | 0.7857 | 0.7919 | 0.7857 | 0.8095 | 0.7976 | 0.8007 | 0.7976 |
| silver | 0.8944 | 0.8908 | 0.8918 | 0.8908 | 0.8944 | 0.8944 | 0.8944 | 0.8944 |

## 4) Behavior Matrix (Full Mode)

| Dataset | Expected Answer -> Actual Answer | Expected Answer -> Actual Refuse | Expected Refuse -> Actual Answer | Expected Refuse -> Actual Refuse |
|---|---:|---:|---:|---:|
| gold | 19 | 15 | 1 | 7 |
| silver | 93 | 34 | 0 | 15 |

## 5) Failure Rule Counts (Full Mode)

### gold

- pass_expected_value_rule: 20
- pass_refusal_rule: 16
- pass_citation_overlap_rule: 15

### silver

- pass_expected_value_rule: 61
- pass_citation_overlap_rule: 42
- pass_refusal_rule: 34

## 6) Example Failed Questions (with exact agent outputs)

### gold (first 10 failures)

- `g003` | `metadata`
  - Question: What is the 'Last updated' month/year for the Data Protection - Employees policy?
  - Expected behavior: answer
  - Expected answer: 03/2024
  - Agent cannot_answer: False
  - Agent answer: The last updated is 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g007` | `metadata`
  - Question: What is the 'Last updated' month/year for the Equality & Diversity Policy?
  - Expected behavior: answer
  - Expected answer: 03/2024
  - Agent cannot_answer: False
  - Agent answer: The last updated is 11.03.2025.[docs/txt/Equality_Diversity.txt:1-100]
  - Agent citations: docs/txt/Equality_Diversity.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g010` | `metadata`
  - Question: What is the 'Last updated' month/year for the Provision of IT Equipment & Acceptable Use policy?
  - Expected behavior: answer
  - Expected answer: 03/2025
  - Agent cannot_answer: False
  - Agent answer: The last updated is 03.04.2025.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
  - Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g014` | `metadata`
  - Question: What is the CURRENT month/year shown for the Recruitment and Selection Policy?
  - Expected behavior: answer
  - Expected answer: 07/2024
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g019` | `procedure`
  - Question: Name two lawful bases for processing personal information listed in the Data Protection - Employees policy.
  - Expected behavior: answer
  - Expected answer: ['consent', 'legal obligation']
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g020` | `definition`
  - Question: According to the Data Protection - Employees policy, what does a 'data breach' mean?
  - Expected behavior: answer
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g021` | `procedure`
  - Question: Before processing any sensitive personal information, who must staff notify (Data Protection - Employees policy)?
  - Expected behavior: answer
  - Expected answer: ['notify', 'Senior Policy and Data Compliance Monitoring Officer']
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g022` | `procedure`
  - Question: After reading and understanding the Data Protection - Employees policy, what must employees do to confirm they have read it?
  - Expected behavior: answer
  - Expected answer: ['sign', 'declaration']
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g023` | `scope`
  - Question: Who does the Data Protection - Employees policy apply to? Provide two groups mentioned in the policy.
  - Expected behavior: answer
  - Expected answer: ['employees', 'job applicants']
  - Agent cannot_answer: False
  - Agent answer: Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `g024` | `procedure`
  - Question: Under the Provision of IT Equipment & Acceptable Use policy, is personal use of STC internet, Teams and email permitted?
  - Expected behavior: answer
  - Expected answer: ['Personal use', 'not permitted']
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

### silver (first 10 failures)

- `s007` | `metadata`
  - Question: When was Data Protection - Employees last updated (MM/YYYY)?
  - Expected behavior: answer
  - Expected answer: 03/2024
  - Agent cannot_answer: False
  - Agent answer: 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s008` | `metadata`
  - Question: What is the 'Last updated' value for Data Protection - Employees?
  - Expected behavior: answer
  - Expected answer: 03/2024
  - Agent cannot_answer: False
  - Agent answer: The last updated is 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s009` | `metadata`
  - Question: Give the last-updated month/year for Data Protection - Employees.
  - Expected behavior: answer
  - Expected answer: 03/2024
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s015` | `metadata`
  - Question: Which committee approved the current version of Data Protection - Employees?
  - Expected behavior: answer
  - Expected answer: P&F
  - Agent cannot_answer: False
  - Agent answer: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s017` | `metadata`
  - Question: What is the approval Date listed in the Current Document Status for Data Protection - Employees?
  - Expected behavior: answer
  - Expected answer: 07.03.2024
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s018` | `metadata`
  - Question: For Data Protection - Employees, what is the Date in the Current Document Status table?
  - Expected behavior: answer
  - Expected answer: 07.03.2024
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s020` | `metadata`
  - Question: For Data Protection - Employees, how long should the document be retained?
  - Expected behavior: answer
  - Expected answer: Until superseded
  - Agent cannot_answer: True
  - Agent answer: I cannot answer from the repository based on the retrieved sources.
  - Agent citations: 
  - Failed rules: pass_refusal_rule, pass_expected_value_rule, pass_citation_overlap_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s021` | `metadata`
  - Question: What is the Version listed in the Current Document Status for Data Protection - Employees?
  - Expected behavior: answer
  - Expected answer: 2024
  - Agent cannot_answer: False
  - Agent answer: The version is 2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s022` | `metadata`
  - Question: For Data Protection - Employees, what Version is shown in the Current Document Status?
  - Expected behavior: answer
  - Expected answer: 2024
  - Agent cannot_answer: False
  - Agent answer: The version is 2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
  - Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

- `s029` | `metadata`
  - Question: When was Equality Diversity last updated (MM/YYYY)?
  - Expected behavior: answer
  - Expected answer: 03/2024
  - Agent cannot_answer: False
  - Agent answer: 11.03.2025.[docs/txt/Equality_Diversity.txt:1-100]
  - Agent citations: docs/txt/Equality_Diversity.txt:1-100
  - Failed rules: pass_expected_value_rule
  - Retrieval recall@k / MRR / nDCG: 1.0 / 1.0 / 1.0

## 7) Full Question-by-Question Output Log

Every item below includes exact question + exact agent answer text + citations from full mode.

### Dataset: gold

#### g001 [PASS] (metadata)

- Question: What is the policy group for the Data Protection - Employees policy?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g002 [PASS] (metadata)

- Question: What is the responsible committee for the Data Protection - Employees policy?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g003 [FAIL] (metadata)

- Question: What is the 'Last updated' month/year for the Data Protection - Employees policy?
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: False
- Agent answer text: The last updated is 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### g004 [PASS] (metadata)

- Question: What is the next review date guidance for the Data Protection - Employees policy?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g005 [PASS] (metadata)

- Question: What is the policy group for the Equality & Diversity Policy?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g006 [PASS] (metadata)

- Question: What is the responsible committee for the Equality & Diversity Policy?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g007 [FAIL] (metadata)

- Question: What is the 'Last updated' month/year for the Equality & Diversity Policy?
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: False
- Agent answer text: The last updated is 11.03.2025.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### g008 [PASS] (metadata)

- Question: What is the next review date guidance for the Equality & Diversity Policy?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g009 [PASS] (metadata)

- Question: What is the policy group for the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: answer
- Expected answer/reference: Employees/Members
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g010 [FAIL] (metadata)

- Question: What is the 'Last updated' month/year for the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: answer
- Expected answer/reference: 03/2025
- Agent cannot_answer: False
- Agent answer text: The last updated is 03.04.2025.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### g011 [PASS] (metadata)

- Question: What is the next review date guidance for the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g012 [PASS] (metadata)

- Question: What is the policy group for the Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g013 [PASS] (metadata)

- Question: What is the responsible committee for the Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g014 [FAIL] (metadata)

- Question: What is the CURRENT month/year shown for the Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: 07/2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g015 [PASS] (metadata)

- Question: What is the next review date guidance for the Recruitment and Selection Policy?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required by legislation.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g016 [PASS] (metadata)

- Question: What is the policy group for the Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g017 [PASS] (metadata)

- Question: What is the responsible committee for the Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g018 [PASS] (metadata)

- Question: What is the next review date guidance for the Employee Handbook?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required by legislation.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g019 [FAIL] (procedure)

- Question: Name two lawful bases for processing personal information listed in the Data Protection - Employees policy.
- Expected behavior: answer
- Expected answer/reference: ['consent', 'legal obligation']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g020 [FAIL] (definition)

- Question: According to the Data Protection - Employees policy, what does a 'data breach' mean?
- Expected behavior: answer
- Expected regex: (?is)(?=.*breach of security)(?=.*unauthori[sz]ed)(?=.*(disclosure|access))(?=.*personal)
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g021 [FAIL] (procedure)

- Question: Before processing any sensitive personal information, who must staff notify (Data Protection - Employees policy)?
- Expected behavior: answer
- Expected answer/reference: ['notify', 'Senior Policy and Data Compliance Monitoring Officer']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g022 [FAIL] (procedure)

- Question: After reading and understanding the Data Protection - Employees policy, what must employees do to confirm they have read it?
- Expected behavior: answer
- Expected answer/reference: ['sign', 'declaration']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g023 [FAIL] (scope)

- Question: Who does the Data Protection - Employees policy apply to? Provide two groups mentioned in the policy.
- Expected behavior: answer
- Expected answer/reference: ['employees', 'job applicants']
- Agent cannot_answer: False
- Agent answer text: Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### g024 [FAIL] (procedure)

- Question: Under the Provision of IT Equipment & Acceptable Use policy, is personal use of STC internet, Teams and email permitted?
- Expected behavior: answer
- Expected answer/reference: ['Personal use', 'not permitted']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g025 [FAIL] (procedure)

- Question: Which two-factor authentication application must remote employees enable under the Provision of IT Equipment & Acceptable Use policy?
- Expected behavior: answer
- Expected answer/reference: Duo Mobile
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g026 [FAIL] (procedure)

- Question: Under the Provision of IT Equipment & Acceptable Use policy, can employees open STC emails on a non-STC device?
- Expected behavior: answer
- Expected regex: (?is)(?=.*\bemail)(?=.*non\s*-?\s*stc)(?=.*device)(?=.*(must\s+not|should\s+not|not\s+permitted|do\s+not))
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g027 [FAIL] (procedure)

- Question: According to the Recruitment and Selection Policy, how long should vacancies be advertised for at minimum?
- Expected behavior: answer
- Expected answer/reference: ['minimum', 'two weeks']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g028 [FAIL] (procedure)

- Question: According to the Recruitment and Selection Policy, which email address should applications be submitted to?
- Expected behavior: answer
- Expected answer/reference: humanresources@saltash.gov.uk
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g029 [FAIL] (scope)

- Question: In the Recruitment and Selection Policy, which role is excluded from the procedure (i.e., has a separate procedure)?
- Expected behavior: answer
- Expected answer/reference: Town Clerk
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g030 [FAIL] (procedure)

- Question: Who has particular responsibility for implementing and monitoring the Equality and Diversity in Employment Policy?
- Expected behavior: answer
- Expected answer/reference: Town Clerk
- Agent cannot_answer: False
- Agent answer text: The senior management team has specific responsibility for eliminating discrimination and providing equality of opportunity, which includes implementing and monitoring the Equality and Diversity in Employment Policy.[docs/txt/Equality_Diversity.txt:101-220]
- Agent citations: docs/txt/Equality_Diversity.txt:101-220
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### g031 [FAIL] (definition)

- Question: What is the aim of the Equality and Diversity Policy (in one sentence)?
- Expected behavior: answer
- Expected regex: (?is)(?=.*less favourable treatment)(?=.*(unfair|unlawful).*(discrimination))
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g032 [FAIL] (metadata)

- Question: How often will the Equality and Diversity Policy be monitored and reviewed?
- Expected behavior: answer
- Expected answer/reference: annually
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g033 [FAIL] (definition)

- Question: Does the Employee Handbook form part of the Contract of Employment?
- Expected behavior: answer
- Expected answer/reference: ['does not form part', 'Contract takes precedence']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g034 [FAIL] (procedure)

- Question: In the Employee Handbook, how long do you have to submit an appeal after receiving the outcome letter for a disciplinary hearing?
- Expected behavior: answer
- Expected regex: (?i)\bwithin\s+five\s+days\b
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### g035 [PASS] (out_of_scope)

- Question: Does this policy pack contain a built-in Kubernetes autoscaler?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g036 [PASS] (out_of_scope)

- Question: What is CrewAI and what is a Crew?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g037 [PASS] (out_of_scope)

- Question: What is the capital of France?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g038 [PASS] (out_of_scope)

- Question: What is the weather forecast for London this weekend?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g039 [PASS] (out_of_scope)

- Question: Explain what a transformer model is in AI.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g040 [PASS] (out_of_scope)

- Question: What is the current EUR to USD exchange rate?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g041 [PASS] (out_of_scope)

- Question: Write a short Python function that reverses a string.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### g042 [FAIL] (out_of_scope)

- Question: What is the latest version of the OpenAI API?
- Expected behavior: refuse
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

### Dataset: silver

#### s001 [PASS] (metadata)

- Question: For Data Protection - Employees, what policy group is listed?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s002 [PASS] (metadata)

- Question: Which policy group does the Data Protection - Employees policy belong to?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s003 [PASS] (metadata)

- Question: What is the Policy Group field for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s004 [PASS] (metadata)

- Question: Which committee is responsible for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s005 [PASS] (metadata)

- Question: What is the RESPONSIBLE COMMITTEE for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s006 [PASS] (metadata)

- Question: For Data Protection - Employees, which committee is listed as responsible?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s007 [FAIL] (metadata)

- Question: When was Data Protection - Employees last updated (MM/YYYY)?
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: False
- Agent answer text: 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s008 [FAIL] (metadata)

- Question: What is the 'Last updated' value for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: False
- Agent answer text: The last updated is 11.03.2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s009 [FAIL] (metadata)

- Question: Give the last-updated month/year for Data Protection - Employees.
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s010 [PASS] (metadata)

- Question: What is the next review date guidance for Data Protection - Employees?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s011 [PASS] (metadata)

- Question: When should Data Protection - Employees be reviewed (next review guidance)?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s012 [PASS] (metadata)

- Question: What does Data Protection - Employees list as the next review date guidance?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or if required by legislation.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s013 [PASS] (metadata)

- Question: Who is the Responsible Officer for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: AJT
- Agent cannot_answer: False
- Agent answer text: AJT.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s014 [PASS] (metadata)

- Question: For Data Protection - Employees, what is listed as the Responsible Officer?
- Expected behavior: answer
- Expected answer/reference: AJT
- Agent cannot_answer: False
- Agent answer text: The responsible officer is AJT.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s015 [FAIL] (metadata)

- Question: Which committee approved the current version of Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s016 [PASS] (metadata)

- Question: For Data Protection - Employees, who is it Approved by?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: P&F.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s017 [FAIL] (metadata)

- Question: What is the approval Date listed in the Current Document Status for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: 07.03.2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s018 [FAIL] (metadata)

- Question: For Data Protection - Employees, what is the Date in the Current Document Status table?
- Expected behavior: answer
- Expected answer/reference: 07.03.2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s019 [PASS] (metadata)

- Question: What is the Document Retention Period for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: False
- Agent answer text: The document retention period is Until superseded 3.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s020 [FAIL] (metadata)

- Question: For Data Protection - Employees, how long should the document be retained?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s021 [FAIL] (metadata)

- Question: What is the Version listed in the Current Document Status for Data Protection - Employees?
- Expected behavior: answer
- Expected answer/reference: 2024
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s022 [FAIL] (metadata)

- Question: For Data Protection - Employees, what Version is shown in the Current Document Status?
- Expected behavior: answer
- Expected answer/reference: 2024
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s023 [PASS] (metadata)

- Question: For Equality Diversity, what policy group is listed?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s024 [PASS] (metadata)

- Question: Which policy group does the Equality Diversity policy belong to?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s025 [PASS] (metadata)

- Question: What is the Policy Group field for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s026 [PASS] (metadata)

- Question: Which committee is responsible for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s027 [PASS] (metadata)

- Question: What is the RESPONSIBLE COMMITTEE for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s028 [PASS] (metadata)

- Question: For Equality Diversity, which committee is listed as responsible?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s029 [FAIL] (metadata)

- Question: When was Equality Diversity last updated (MM/YYYY)?
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: False
- Agent answer text: 11.03.2025.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s030 [FAIL] (metadata)

- Question: What is the 'Last updated' value for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: False
- Agent answer text: The last updated is 11.03.2025.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s031 [FAIL] (metadata)

- Question: Give the last-updated month/year for Equality Diversity.
- Expected behavior: answer
- Expected answer/reference: 03/2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s032 [PASS] (metadata)

- Question: What is the next review date guidance for Equality Diversity?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s033 [PASS] (metadata)

- Question: When should Equality Diversity be reviewed (next review guidance)?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: Annual or as required.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s034 [PASS] (metadata)

- Question: What does Equality Diversity list as the next review date guidance?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s035 [PASS] (metadata)

- Question: Who is the Responsible Officer for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: AJT
- Agent cannot_answer: False
- Agent answer text: AJT.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s036 [PASS] (metadata)

- Question: For Equality Diversity, what is listed as the Responsible Officer?
- Expected behavior: answer
- Expected answer/reference: AJT
- Agent cannot_answer: False
- Agent answer text: The responsible officer is AJT.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s037 [FAIL] (metadata)

- Question: Which committee approved the current version of Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s038 [PASS] (metadata)

- Question: For Equality Diversity, who is it Approved by?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: P&F.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s039 [FAIL] (metadata)

- Question: What is the approval Date listed in the Current Document Status for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: 11.03.2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s040 [FAIL] (metadata)

- Question: For Equality Diversity, what is the Date in the Current Document Status table?
- Expected behavior: answer
- Expected answer/reference: 11.03.2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s041 [PASS] (metadata)

- Question: What is the Document Retention Period for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: False
- Agent answer text: The document retention period is Until superseded 3.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s042 [FAIL] (metadata)

- Question: For Equality Diversity, how long should the document be retained?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s043 [PASS] (metadata)

- Question: What is the Version listed in the Current Document Status for Equality Diversity?
- Expected behavior: answer
- Expected answer/reference: 2025
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s044 [PASS] (metadata)

- Question: For Equality Diversity, what Version is shown in the Current Document Status?
- Expected behavior: answer
- Expected answer/reference: 2025
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s045 [PASS] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, what policy group is listed?
- Expected behavior: answer
- Expected answer/reference: Employees/Members
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s046 [PASS] (metadata)

- Question: Which policy group does the Provision of IT Acceptable Use Policy Employees Members policy belong to?
- Expected behavior: answer
- Expected answer/reference: Employees/Members
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s047 [PASS] (metadata)

- Question: What is the Policy Group field for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: Employees/Members
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees/Members.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s048 [FAIL] (metadata)

- Question: Which committee is responsible for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s049 [FAIL] (metadata)

- Question: What is the RESPONSIBLE COMMITTEE for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s050 [FAIL] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, which committee is listed as responsible?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s051 [FAIL] (metadata)

- Question: When was Provision of IT Acceptable Use Policy Employees Members last updated (MM/YYYY)?
- Expected behavior: answer
- Expected answer/reference: 03/2025
- Agent cannot_answer: False
- Agent answer text: 03.04.2025.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s052 [FAIL] (metadata)

- Question: What is the 'Last updated' value for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: 03/2025
- Agent cannot_answer: False
- Agent answer text: The last updated is 03.04.2025.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s053 [FAIL] (metadata)

- Question: Give the last-updated month/year for Provision of IT Acceptable Use Policy Employees Members.
- Expected behavior: answer
- Expected answer/reference: 03/2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s054 [PASS] (metadata)

- Question: What is the next review date guidance for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s055 [PASS] (metadata)

- Question: When should Provision of IT Acceptable Use Policy Employees Members be reviewed (next review guidance)?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: Annual or as required.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s056 [PASS] (metadata)

- Question: What does Provision of IT Acceptable Use Policy Employees Members list as the next review date guidance?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+as\s+required\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s057 [PASS] (metadata)

- Question: Who is the Responsible Officer for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: AJT
- Agent cannot_answer: False
- Agent answer text: AJT.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s058 [PASS] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, what is listed as the Responsible Officer?
- Expected behavior: answer
- Expected answer/reference: AJT
- Agent cannot_answer: False
- Agent answer text: The responsible officer is AJT.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s059 [FAIL] (metadata)

- Question: Which committee approved the current version of Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: FTC
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s060 [PASS] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, who is it Approved by?
- Expected behavior: answer
- Expected answer/reference: FTC
- Agent cannot_answer: False
- Agent answer text: FTC.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s061 [FAIL] (metadata)

- Question: What is the approval Date listed in the Current Document Status for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: 03.04.2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s062 [FAIL] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, what is the Date in the Current Document Status table?
- Expected behavior: answer
- Expected answer/reference: 03.04.2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s063 [PASS] (metadata)

- Question: What is the Document Retention Period for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: False
- Agent answer text: The document retention period is Until superseded 3.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s064 [FAIL] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, how long should the document be retained?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s065 [PASS] (metadata)

- Question: What is the Version listed in the Current Document Status for Provision of IT Acceptable Use Policy Employees Members?
- Expected behavior: answer
- Expected answer/reference: 2025/26
- Agent cannot_answer: False
- Agent answer text: The version is 2025/26.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s066 [PASS] (metadata)

- Question: For Provision of IT Acceptable Use Policy Employees Members, what Version is shown in the Current Document Status?
- Expected behavior: answer
- Expected answer/reference: 2025/26
- Agent cannot_answer: False
- Agent answer text: The version is 2025/26.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s067 [PASS] (metadata)

- Question: For Recruitment and Selection Policy, what policy group is listed?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s068 [PASS] (metadata)

- Question: Which policy group does the Recruitment and Selection Policy policy belong to?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s069 [PASS] (metadata)

- Question: What is the Policy Group field for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s070 [PASS] (metadata)

- Question: Which committee is responsible for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s071 [PASS] (metadata)

- Question: What is the RESPONSIBLE COMMITTEE for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s072 [PASS] (metadata)

- Question: For Recruitment and Selection Policy, which committee is listed as responsible?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s073 [FAIL] (metadata)

- Question: What is the CURRENT month/year for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: 07/2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s074 [FAIL] (metadata)

- Question: For Recruitment and Selection Policy, what does the CURRENT field say (MM/YYYY)?
- Expected behavior: answer
- Expected answer/reference: 07/2024
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s075 [PASS] (metadata)

- Question: What is the next review date guidance for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required by legislation.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s076 [PASS] (metadata)

- Question: When should Recruitment and Selection Policy be reviewed (next review guidance)?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: Annual or as required by legislation.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s077 [PASS] (metadata)

- Question: What does Recruitment and Selection Policy list as the next review date guidance?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required by legislation.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s078 [FAIL] (metadata)

- Question: Who is the Responsible Officer for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: LM
- Agent cannot_answer: False
- Agent answer text: AJT.[docs/txt/Equality_Diversity.txt:1-100]
- Agent citations: docs/txt/Equality_Diversity.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s079 [FAIL] (metadata)

- Question: For Recruitment and Selection Policy, what is listed as the Responsible Officer?
- Expected behavior: answer
- Expected answer/reference: LM
- Agent cannot_answer: False
- Agent answer text: The responsible officer is AJT.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s080 [FAIL] (metadata)

- Question: Which committee approved the current version of Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: FTC
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s081 [PASS] (metadata)

- Question: For Recruitment and Selection Policy, who is it Approved by?
- Expected behavior: answer
- Expected answer/reference: FTC
- Agent cannot_answer: False
- Agent answer text: FTC.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s082 [FAIL] (metadata)

- Question: What is the approval Date listed in the Current Document Status for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: 07/08/2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s083 [FAIL] (metadata)

- Question: For Recruitment and Selection Policy, what is the Date in the Current Document Status table?
- Expected behavior: answer
- Expected answer/reference: 07/08/2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s084 [PASS] (metadata)

- Question: What is the Document Retention Period for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: False
- Agent answer text: The document retention period is Until superseded 3.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s085 [FAIL] (metadata)

- Question: For Recruitment and Selection Policy, how long should the document be retained?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s086 [PASS] (metadata)

- Question: What is the Version listed in the Current Document Status for Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: 2025
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s087 [PASS] (metadata)

- Question: For Recruitment and Selection Policy, what Version is shown in the Current Document Status?
- Expected behavior: answer
- Expected answer/reference: 2025
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s088 [PASS] (metadata)

- Question: For Employee Handbook, what policy group is listed?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s089 [PASS] (metadata)

- Question: Which policy group does the Employee Handbook policy belong to?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s090 [PASS] (metadata)

- Question: What is the Policy Group field for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: Employees
- Agent cannot_answer: False
- Agent answer text: The policy group is Employees.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s091 [PASS] (metadata)

- Question: Which committee is responsible for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s092 [PASS] (metadata)

- Question: What is the RESPONSIBLE COMMITTEE for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s093 [PASS] (metadata)

- Question: For Employee Handbook, which committee is listed as responsible?
- Expected behavior: answer
- Expected answer/reference: PERSONNEL
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s094 [PASS] (metadata)

- Question: What is the next review date guidance for Employee Handbook?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required by legislation.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s095 [PASS] (metadata)

- Question: When should Employee Handbook be reviewed (next review guidance)?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: Annual or as required by legislation.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s096 [PASS] (metadata)

- Question: What does Employee Handbook list as the next review date guidance?
- Expected behavior: answer
- Expected regex: (?i)\bannual(?:ly)?\b\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?\b
- Agent cannot_answer: False
- Agent answer text: The review frequency is Annual or as required by legislation.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s097 [FAIL] (metadata)

- Question: Who is the Responsible Officer for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: Town Clerk
- Agent cannot_answer: False
- Agent answer text: AJT.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s098 [FAIL] (metadata)

- Question: For Employee Handbook, what is listed as the Responsible Officer?
- Expected behavior: answer
- Expected answer/reference: Town Clerk
- Agent cannot_answer: False
- Agent answer text: The responsible officer is AJT.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s099 [FAIL] (metadata)

- Question: Which committee approved the current version of Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: The responsible committee is PERSONNEL.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s100 [PASS] (metadata)

- Question: For Employee Handbook, who is it Approved by?
- Expected behavior: answer
- Expected answer/reference: P&F
- Agent cannot_answer: False
- Agent answer text: P&F.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s101 [FAIL] (metadata)

- Question: What is the approval Date listed in the Current Document Status for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: 11.03.2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s102 [FAIL] (metadata)

- Question: For Employee Handbook, what is the Date in the Current Document Status table?
- Expected behavior: answer
- Expected answer/reference: 11.03.2025
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s103 [PASS] (metadata)

- Question: What is the Document Retention Period for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: False
- Agent answer text: The document retention period is Until superseded HYNCHB v1.6.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s104 [FAIL] (metadata)

- Question: For Employee Handbook, how long should the document be retained?
- Expected behavior: answer
- Expected answer/reference: Until superseded
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s105 [PASS] (metadata)

- Question: What is the Version listed in the Current Document Status for Employee Handbook?
- Expected behavior: answer
- Expected answer/reference: 2025
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s106 [PASS] (metadata)

- Question: For Employee Handbook, what Version is shown in the Current Document Status?
- Expected behavior: answer
- Expected answer/reference: 2025
- Agent cannot_answer: False
- Agent answer text: The version is 2025.[docs/txt/Employee_Handbook.txt:1-100]
- Agent citations: docs/txt/Employee_Handbook.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s107 [FAIL] (procedure)

- Question: List two examples of lawful bases for processing personal data in the Data Protection - Employees policy.
- Expected behavior: answer
- Expected answer/reference: ['consent', 'legal obligation']
- Agent cannot_answer: False
- Agent answer text: Two examples of lawful bases/conditions for processing personal data (sensitive personal information) in the Data Protection - Employees policy are: (1) where the data subject has given explicit consent, and (2) where the processing is necessary for the establishment, exercise or defence of legal claims.[docs/txt/Data_Protection_-_Employees.txt:301-420]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:301-420
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s108 [FAIL] (procedure)

- Question: In the Data Protection - Employees policy, what are two lawful bases for processing personal information?
- Expected behavior: answer
- Expected answer/reference: ['consent', 'legal obligation']
- Agent cannot_answer: False
- Agent answer text: Two lawful bases for processing personal information in the Data Protection - Employees policy are: (1) where “the data subject has given explicit consent”, and (2) where “the processing is necessary for the establishment, exercise or defence of legal claims.” [docs/txt/Data_Protection_-_Employees.txt:301-420]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:301-420
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s109 [FAIL] (definition)

- Question: What does the Data Protection - Employees policy define a data breach as?
- Expected behavior: answer
- Expected regex: (?is)(?=.*breach of security)(?=.*unauthori[sz]ed)(?=.*(disclosure|access))(?=.*personal)
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s110 [FAIL] (procedure)

- Question: Who is responsible for data protection compliance within Saltash Town Council (as stated in the Data Protection - Employees policy)?
- Expected behavior: answer
- Expected answer/reference: Senior Policy and Data Compliance Monitoring Officer
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s111 [FAIL] (procedure)

- Question: Does the Data Protection - Employees policy form part of an employee’s contract of employment?
- Expected behavior: answer
- Expected answer/reference: ['does not form part', 'contract']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s112 [FAIL] (procedure)

- Question: Is personal use of the STC internet/Teams/email allowed under the IT Acceptable Use policy?
- Expected behavior: answer
- Expected answer/reference: ['personal use', 'not permitted']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s113 [FAIL] (procedure)

- Question: Which app is used for two-factor authentication for remote employees (IT Acceptable Use policy)?
- Expected behavior: answer
- Expected answer/reference: Duo Mobile
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s114 [FAIL] (procedure)

- Question: If a file or document is suspected of being virus infected, what should be done (IT Acceptable Use policy)?
- Expected behavior: answer
- Expected answer/reference: ['immediately referred', 'IT Consultant', 'helpdesk']
- Agent cannot_answer: False
- Agent answer text: If a file or document is suspected of being virus infected, you must not attempt to remove the infected files or remove/disable the anti-virus software, and you should immediately refer the issue to the IT Consultant via the helpdesk.[docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:101-220]
- Agent citations: docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt:101-220
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s115 [FAIL] (procedure)

- Question: When an employee’s contract ends, what must happen to Town Council owned IT property (IT Acceptable Use policy)?
- Expected behavior: answer
- Expected answer/reference: ['Upon termination', 'must be returned']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s116 [FAIL] (procedure)

- Question: In the Recruitment and Selection Policy, what is the minimum advertising period for vacancies?
- Expected behavior: answer
- Expected answer/reference: ['minimum', 'two weeks']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s117 [FAIL] (procedure)

- Question: Where should applicants submit their application according to the Recruitment and Selection Policy?
- Expected behavior: answer
- Expected answer/reference: humanresources@saltash.gov.uk
- Agent cannot_answer: False
- Agent answer text: Applicants should submit their application to the Town Council’s Administration Officer, or on occasion to the Town Council’s appointed Human Resources Consultant.[docs/txt/Recruitment_and_Selection_Policy.txt:201-320]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:201-320
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s118 [FAIL] (procedure)

- Question: According to the Recruitment and Selection Policy, how many referees must candidates provide and what must one of them be?
- Expected behavior: answer
- Expected answer/reference: ['two', 'current or most recent employer']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s119 [FAIL] (procedure)

- Question: According to the Recruitment and Selection Policy, how many working days’ notice must shortlisted candidates be given for an interview?
- Expected behavior: answer
- Expected answer/reference: ['three', 'working days']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s120 [FAIL] (definition)

- Question: In the Equality and Diversity Policy, what is the aim of the policy?
- Expected behavior: answer
- Expected regex: (?is)(?=.*less favourable treatment)(?=.*(unfair|unlawful).*(discrimination))
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s121 [FAIL] (procedure)

- Question: Who has particular responsibility for implementing and monitoring the Equality and Diversity in Employment Policy?
- Expected behavior: answer
- Expected answer/reference: Town Clerk
- Agent cannot_answer: False
- Agent answer text: The senior management team has specific responsibility for eliminating discrimination and providing equality of opportunity, which includes implementing and monitoring the Equality and Diversity in Employment Policy.[docs/txt/Equality_Diversity.txt:101-220]
- Agent citations: docs/txt/Equality_Diversity.txt:101-220
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s122 [FAIL] (metadata)

- Question: How often will the Equality and Diversity Policy be monitored and reviewed?
- Expected behavior: answer
- Expected answer/reference: annually
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s123 [FAIL] (definition)

- Question: According to the Employee Handbook, does the handbook form part of the Contract of Employment?
- Expected behavior: answer
- Expected answer/reference: ['does not form part', 'Contract takes precedence']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s124 [FAIL] (procedure)

- Question: How long do you have to appeal after the outcome of a disciplinary hearing (Employee Handbook)?
- Expected behavior: answer
- Expected regex: (?i)\bwithin\s+five\s+(?:working\s+)?days\b
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s125 [FAIL] (multi)

- Question: For the Data Protection - Employees policy, state the Responsible Committee and the 'Last updated' month/year.
- Expected behavior: answer
- Expected answer/reference: ['PERSONNEL', '03/2024']
- Agent cannot_answer: False
- Agent answer text: PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]
- Agent citations: docs/txt/Data_Protection_-_Employees.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s126 [FAIL] (multi)

- Question: For the Recruitment and Selection Policy, state the Responsible Committee and the minimum advertising period for vacancies.
- Expected behavior: answer
- Expected answer/reference: ['PERSONNEL', 'two weeks']
- Agent cannot_answer: False
- Agent answer text: PERSONNEL.[docs/txt/Recruitment_and_Selection_Policy.txt:1-100]
- Agent citations: docs/txt/Recruitment_and_Selection_Policy.txt:1-100
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: False

#### s127 [FAIL] (multi)

- Question: Under the IT Acceptable Use policy, is personal use permitted and what 2FA app is referenced for remote employees?
- Expected behavior: answer
- Expected answer/reference: ['not permitted', 'Duo Mobile']
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: False
- pass_citation_rule: True
- pass_expected_value_rule: False
- pass_citation_overlap_rule: False
- pass_verification_rule: True
- pass_overall: False

#### s128 [PASS] (out_of_scope)

- Question: Do these council policy documents include Terraform modules for AWS?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s129 [PASS] (out_of_scope)

- Question: What is the SHA256 hash of the Employee Handbook PDF?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s130 [PASS] (out_of_scope)

- Question: Provide the latest Bitcoin price and a prediction for next week.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s131 [PASS] (out_of_scope)

- Question: How do I enable two-factor authentication on my personal Gmail account?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s132 [PASS] (out_of_scope)

- Question: Write a bash script that lists files in a directory.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s133 [PASS] (out_of_scope)

- Question: Explain how to change a car tire.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s134 [PASS] (out_of_scope)

- Question: What is the schedule for the 2026 Premier League season?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s135 [PASS] (out_of_scope)

- Question: Create a simple invoice template (fields and layout).
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s136 [PASS] (out_of_scope)

- Question: Tell me the CEO of OpenAI right now.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s137 [PASS] (out_of_scope)

- Question: How do I bake sourdough bread?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s138 [PASS] (out_of_scope)

- Question: Give me the latest UK immigration law changes this month.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s139 [PASS] (out_of_scope)

- Question: What are the best restaurants near me?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s140 [PASS] (out_of_scope)

- Question: What is the total budget of Saltash Town Council in 2026?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s141 [PASS] (out_of_scope)

- Question: Summarize Saltash Town Council meeting minutes from January 2026.
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True

#### s142 [PASS] (out_of_scope)

- Question: Does the policy pack mention 'CrewAI' anywhere?
- Expected behavior: refuse
- Agent cannot_answer: True
- Agent answer text: I cannot answer from the repository based on the retrieved sources.
- Agent citations: 
- verification_passed: True
- pass_refusal_rule: True
- pass_citation_rule: True
- pass_expected_value_rule: True
- pass_citation_overlap_rule: True
- pass_verification_rule: True
- pass_overall: True
