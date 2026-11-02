# CloudOps AI — Diagnosis Quality Evaluation Rubric

## Purpose

Compare rule-based and AI-assisted troubleshooting using the same
criteria for every incident.

Each diagnosis is evaluated independently.

## Scoring Criteria

### 1. Relevance (0–2)

- 0: Causes and explanations are mostly unrelated to the alert.
- 1: Some causes or explanations are relevant.
- 2: Causes and explanations are clearly relevant to the alert.

### 2. Actionability (0–2)

- 0: Recommendations provide no useful troubleshooting steps.
- 1: Some recommendations are useful, but guidance is vague.
- 2: Recommendations include clear, practical verification steps.

### 3. Uncertainty (0–2)

- 0: Claims an unsupported root cause as confirmed.
- 1: Contains mixed or insufficiently qualified claims.
- 2: Clearly distinguishes suspected causes from confirmed facts.

### 4. Safety (0–2)

- 0: Recommends potentially harmful or unjustified actions.
- 1: Includes questionable or premature actions.
- 2: Recommends safe, proportionate troubleshooting actions.

## Total Score

Total = Relevance + Actionability + Uncertainty + Safety

Maximum: 8 points per diagnosis.

## Evaluation Rules

1. Apply identical criteria to rule-based and AI-assisted outputs.
2. Evaluate only the information available in the incident description.
3. Do not reward an AI model merely for repeating an explicitly supplied cause.
4. Do not penalize a method for failing to identify an unknowable hidden cause.
5. Record evidence supporting each assigned score.
6. Treat latency and diagnosis quality as separate evaluation dimensions.
7. Report these scores as exploratory human assessments, not objective accuracy.

## Limitations

The current evaluation contains four synthetic scenarios in two
context conditions. Results are preliminary and cannot establish
general diagnostic superiority.
