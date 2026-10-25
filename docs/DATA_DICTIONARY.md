# Data dictionary

## Source and unit of observation

The input is `data/HR_comma_sep.csv`, supplied in `Salifort Motors.zip`. It contains 14,999 rows and ten columns. Each row is treated as an employee record for this case study. The archive does not include an authoritative source citation, employee identifier, collection dates, formal data dictionary, or license. The interpretations below follow the column names and observed values and require confirmation with the data owner.

The CSV and uploaded original notebook are preserved byte-for-byte. Cleaning takes place in memory; the raw CSV is never overwritten.

| Original column | Analysis column | Observed representation | Working interpretation |
| --- | --- | --- | --- |
| `satisfaction_level` | unchanged | Decimal, 0–1 | Employee satisfaction score; survey instrument and timing unknown |
| `last_evaluation` | unchanged | Decimal, 0–1 | Most recent evaluation score; rubric and timing unknown |
| `number_project` | unchanged | Integer | Number of projects associated with the employee |
| `average_montly_hours` | `average_monthly_hours` | Integer | Average monthly working hours; averaging window unknown |
| `time_spend_company` | `tenure` | Integer | Tenure, assumed to be measured in years |
| `Work_accident` | `work_accident` | Binary, 0/1 | Recorded work accident indicator; reference period unknown |
| `left` | unchanged | Binary, 0/1 | Classification target: 1 = left, 0 = stayed; observation horizon unknown |
| `promotion_last_5years` | unchanged | Binary, 0/1 | Promotion in the preceding five years |
| `Department` | `department` | Text category | Department label |
| `salary` | unchanged | `low`, `medium`, `high` | Relative salary category; currency and band boundaries unknown |

## Cleaning policy

- Rename inconsistent column names without altering the input file.
- Remove 3,008 exact duplicate rows before splitting, leaving 11,991 records.
- Report both raw and deduplicated attrition rates: 23.8% and 16.6%, respectively.
- Retain all tenure values rather than assuming extreme values are invalid.
- Fit categorical encoding, scaling, and imputation within model pipelines. No missing cells occur in the supplied dataset.

Removing identical rows reduces direct duplicate leakage, but without employee IDs, identical rows might represent distinct people. Confirm this assumption before using population estimates. Similar employee profiles can still occur across splits.

## Responsible interpretation

These observations cannot identify causal drivers of departure. No demographic fairness assessment or prospective early-warning validation is established. Confirm source attribution and applicable redistribution rights with the owner; this project does not assign a license to the supplied dataset.
