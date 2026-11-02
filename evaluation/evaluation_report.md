# CloudOps AI — Troubleshooting Evaluation Report

## 1. Objective

This evaluation compares rule-based troubleshooting with AI-assisted
troubleshooting in the CloudOps AI monitoring dashboard.

The AI-assisted method uses a locally hosted Qwen3 4B model through Ollama.

The evaluation examines:

- Quality of troubleshooting explanations and recommendations.
- Ability to use available incident context.
- Appropriate handling of diagnostic uncertainty.
- Safety of recommended troubleshooting actions.
- Response latency.

## 2. Evaluation Methodology

Four synthetic monitoring incidents were evaluated:

| ID | Incident | Ground-truth cause |
|---|---|---|
| APP-001 | Application unavailable | Application container stopped |
| APP-002 | Application unavailable | Incorrect monitoring target port |
| ERR-001 | High HTTP error rate | Intentional HTTP 500 simulation |
| ERR-002 | High HTTP error rate | Database service unavailable |

Each incident was evaluated under two conditions:

1. Context-rich: The incident description disclosed the underlying cause.
2. Limited-context: The incident description contained symptoms without
   disclosing the underlying cause.

Both troubleshooting methods processed all four scenarios in each condition.

This produced 16 diagnoses: eight rule-based and eight AI-assisted.

The evaluation used saved results from:

- `results/evaluation_20261028T154400Z.json`
- `results/evaluation_20261028T164545Z.json`

## 3. Diagnosis Quality Scoring

Each diagnosis was manually assessed using four criteria:

| Criterion | Maximum score |
|---|---:|
| Relevance | 2 |
| Actionability | 2 |
| Uncertainty | 2 |
| Safety | 2 |
| Total | 8 |

Scores represent preliminary human judgments about the usefulness and
appropriateness of the generated troubleshooting guidance.

They do not measure independently verified root-cause accuracy.

The complete scoring records and evaluation notes are available in
`diagnosis_scores.csv`.

## 4. Quality Results

### 4.1 Context-rich evaluation

| Scenario | Rule-based | AI-assisted |
|---|---:|---:|
| APP-001 | 8/8 | 8/8 |
| APP-002 | 8/8 | 8/8 |
| ERR-001 | 7/8 | 8/8 |
| ERR-002 | 7/8 | 8/8 |
| Average | 7.50/8 | 8.00/8 |

The AI-assisted method provided more targeted recommendations when the
incident descriptions explicitly identified the underlying causes.

However, recognizing causes already disclosed in incident descriptions
does not demonstrate independent root-cause discovery.

### 4.2 Limited-context evaluation

| Scenario | Rule-based | AI-assisted |
|---|---:|---:|
| APP-001 | 8/8 | 7/8 |
| APP-002 | 8/8 | 8/8 |
| ERR-001 | 8/8 | 7/8 |
| ERR-002 | 8/8 | 8/8 |
| Average | 8.00/8 | 7.50/8 |

The rule-based method performed slightly better under limited-context
conditions.

The AI-assisted method received lower safety scores in two scenarios
because it suggested changing the Prometheus scrape interval or
scaling resources without sufficient supporting evidence.

### 4.3 Overall quality

| Method | Average score | Total score |
|---|---:|---:|
| Rule-based | 7.75/8 | 62/64 |
| AI-assisted | 7.75/8 | 62/64 |

Both methods achieved the same overall quality score.

## 5. Response Latency

Latency measurements were collected during the evaluation runs.

| Dataset | Rule-based mean | AI-assisted mean |
|---|---:|---:|
| Context-rich | <0.0001 s | 4.3565 s |
| Limited-context | <0.0001 s | 4.4153 s |
| Overall | <0.0001 s | 4.3859 s |

Overall median AI-assisted latency was 3.9512 seconds.

Rule-based troubleshooting completed substantially faster than local
AI-assisted inference.

These measurements reflect the tested local environment and should not
be generalized to other hardware, models, or deployment configurations.

## 6. Key Findings

1. Both methods achieved an overall average quality score of 7.75/8.
2. AI-assisted troubleshooting provided more context-specific guidance
   when the underlying cause was included in the incident description.
3. Rule-based troubleshooting performed slightly better when only
   limited incident context was available.
4. AI-assisted recommendations occasionally included interventions
   that were not adequately supported by the available evidence.
5. Rule-based troubleshooting had substantially lower response latency.
6. Neither method independently confirmed the underlying causes
   during this evaluation.

## 7. Implications for the Hybrid Architecture

The findings support retaining rule-based troubleshooting as a fast
baseline while using AI assistance to provide additional contextual
explanations and recommendations when appropriate.

AI-generated recommendations should remain subject to validation,
particularly when they propose operational or configuration changes.

The results do not establish that the hybrid architecture itself
outperforms either standalone method.

## 8. Limitations

This evaluation has several limitations:

- Only four synthetic incident scenarios were tested.
- The same scenarios were reused under two context conditions.
- Only one local AI model, Qwen3 4B, was evaluated.
- Quality scores were assigned through a preliminary subjective assessment.
- No independent inter-rater agreement was measured.
- No repeated inference trials were used to quantify response variability.
- Context-rich scenarios disclosed the underlying causes.
- The evaluation did not measure actual incident resolution success.
- Latency measurements are specific to the tested environment.

Consequently, the findings should be interpreted as exploratory rather
than statistically conclusive.

## 9. Conclusion

The evaluation demonstrates that both rule-based and AI-assisted
troubleshooting can provide useful recommendations for common monitoring
incidents.

Qwen3 4B produced more tailored guidance when detailed context was
available, but this benefit came with additional inference latency.

The rule-based method remained fast and consistent, especially under
limited-context conditions.

These findings motivate a hybrid design that combines deterministic
troubleshooting with optional AI-generated explanations, while retaining
appropriate safeguards and diagnostic uncertainty.
