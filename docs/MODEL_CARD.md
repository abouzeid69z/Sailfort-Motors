# Model card

## Purpose

Retrospective employee-attrition classification for an educational/portfolio case study. The audience is analysts and HR stakeholders evaluating retention hypotheses. The project is not validated for automated hiring, dismissal, promotion, compensation, or other individual employment decisions.

## Implementation

- Target: `left`, where 1 denotes departure.
- Inputs: nine supplied non-target fields; department and salary are categorical.
- Preprocessing: median imputation and standard scaling for numeric inputs; most-frequent imputation and one-hot encoding for categoricals, ignoring unknown categories.
- Selected classifier: random forest, 200 trees, maximum depth 12, minimum leaf size 3, random seed 42, two parallel workers.
- Baselines: prior-probability dummy classifier, logistic regression, and depth-limited decision tree.
- No fitted model binary is distributed. Rerun the pipeline to train and evaluate it.

## Evaluation protocol

After exact deduplication, stratified splitting produces 7,194 training, 2,398 validation, and 2,399 test records. Preprocessing is fitted on training data. Candidates are selected using validation average precision, with no test-set hyperparameter or threshold tuning. The selected pipeline is refitted on training plus validation before final test evaluation. The threshold is 0.5. Permutation importance is computed on validation before refitting.

The candidate configurations are fixed comparisons, not an exhaustive hyperparameter search.

## Held-out performance

| Measure | Result |
| --- | ---: |
| Accuracy | 0.9829 |
| Precision | 0.9811 |
| Recall | 0.9146 |
| F1 | 0.9467 |
| ROC AUC | 0.9796 |
| Average precision | 0.9639 |
| Test prevalence | 0.1659 |
| AP bootstrap 95% interval | 0.9483–0.9773 |

The 500-resample percentile interval conditions on the fitted model and fixed test predictions. It excludes training uncertainty and future population shifts.

| Actual / predicted | Stayed | Left |
| --- | ---: | ---: |
| Stayed | 1,994 | 7 |
| Left | 34 | 364 |

These scores describe this particular retrospective split. They do not estimate the effect of any retention intervention.

## Limitations and failure modes

- No employee IDs or timestamps support employee-level or temporal validation.
- Deduplication is an assumption; identical records may represent different employees.
- The availability of satisfaction and evaluation scores before a useful prediction date is unknown.
- Random splits can overstate performance on future cohorts; similar profiles remain possible across splits.
- Probability calibration, protected-group fairness, and stability under dataset shift have not been evaluated.
- Permutation importance is predictive, not causal, and correlated features may share importance.
- Data provenance, observation horizon, and license are unverified beyond the supplied archive.

## Before operational use

Confirm data lineage, duplicate policy, feature timing, and target horizon. Evaluate on a later cohort with employee-level separation. Assess calibration and relevant subgroup outcomes, define outreach capacity and error costs, and select a threshold without using the final evaluation set. Any retention pilot should be voluntary, supportive, reviewed by people, and measured against explicit outcomes.

## Reproduction

Follow the repository README. `src/analysis.py` generates the metrics and figures; `src/execute_notebook.py` executes the completed notebook and rebuilds the executive documents. Machine-readable results are in `reports/model_results.json` and `reports/validation_metrics.csv`.
