# Salifort Motors — Employee Attrition Analysis

## Executive summary

The supplied Salifort Motors dataset contains 14,999 employee records. After removing 3,008 exact duplicate rows, 11,991 records remain, with observed attrition of 16.6%. A random forest provides strong retrospective separation of employees who left and stayed. Use these findings to design and evaluate supportive retention initiatives; prospective performance is not established.

## Plan — business question and success criteria

Which recorded characteristics are associated with employee departure, and can a model identify leavers in a held-out sample? HR leaders are the intended audience. Average precision is the model-selection metric because leavers are a minority. Precision and recall describe the trade-off at a fixed 0.5 threshold. No intervention cost, prediction horizon, or deployment target was supplied.

## Analyze — data quality and assumptions

There are 0 missing cells and ten columns. The raw departure rate is 23.8%; the deduplicated rate is 16.6%. Exact duplicate removal occurs before splitting to avoid identical records appearing across splits. Without employee identifiers, identical rows could represent different employees, so the deduplication assumption requires confirmation. Department and salary are categorical; salary is encoded categorically rather than assuming equally spaced pay levels. Tenure extremes are retained because they can be valid observations.

## Analyze — observed relationships

Salary-group departure rates: high: 4.8% (n=990); low: 20.5% (n=5,740); medium: 14.6% (n=5,261). Workload and satisfaction distributions differ between leavers and stayers; see the accompanying figures. Group associations are descriptive and do not establish that changing pay, hours, or satisfaction will reduce departures.

## Construct — leakage controls and comparison

Records are split 60% training, 20% validation, and 20% test with stratification and random seed 42. Imputation, scaling, and one-hot encoding are fitted within pipelines using training data. A dummy baseline, logistic regression, depth-limited decision tree, and random forest are compared on the validation set. The selected model is refitted on training plus validation, then evaluated on the held-out test set. The threshold remains 0.5; no test-set threshold tuning is performed.

## Execute — held-out results

Selected model: Random forest. Test set: 2,399 records. Accuracy 98.29%; precision 98.11%; recall 91.46%; F1 0.947; ROC AUC 0.980; average precision 0.964, compared with test prevalence 0.166. Confusion matrix: 1,994 true negatives, 7 false positives, 34 false negatives, 364 true positives. The 500-resample percentile bootstrap interval for test average precision is 0.948–0.977; it conditions on the fitted model and does not quantify training or dataset-shift uncertainty.

## Model interpretation

Leading features by validation permutation importance: satisfaction_level, tenure, number_project, average_monthly_hours. Importance measures loss of predictive performance after shuffling a feature. Correlated features can share importance, and these rankings do not identify causal drivers. Feature timing is unknown: satisfaction or evaluation scores collected near departure may not be available at a useful intervention date.

## Recommendations and measurement

1. HR and team leaders should review extreme workloads and project assignments, using confidential employee feedback to understand the context. 2. Pilot voluntary workload and manager-support interventions, with predefined retention and wellbeing measures and a comparison group where feasible. 3. Audit compensation and advancement opportunities before choosing pay interventions. 4. Treat model outputs as research evidence; avoid individual employment decisions until appropriate governance, consent, fairness evaluation, and prospective validation are complete.

## Limitations and next steps

The ZIP provides no authoritative dataset provenance, observation dates, employee IDs, data dictionary, or license. Dataset identity and permission to redistribute must be confirmed before public publication. A random record split cannot verify temporal or employee-level generalization. Similar profiles may remain across splits after exact deduplication. Protected-attribute coverage and subgroup fairness are unknown. No causal effects, deployment readiness, calibrated risk probabilities, or financial savings are established. Next obtain source documentation, confirm deduplication and feature availability, evaluate on a later employee cohort, and choose a threshold using the actual costs of missed and unnecessary outreach.

## Reproduction

Run `python src/analysis.py` followed by `python src/build_deliverables.py` from the repository root. Detailed metrics and group tables are in `reports/`.
