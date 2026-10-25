# Contributing

Use Python 3.12 and follow the installation commands in the README. Keep the supplied CSV and original notebook unchanged.

For analysis changes:

1. Document the business question and any new assumptions.
2. Keep preprocessing inside training pipelines and reserve the held-out test set for final evaluation.
3. Run `python src/execute_notebook.py` using the prepared virtual environment.
4. Review regenerated metrics, notebook outputs, report, presentation, and figures together for consistency.
5. Describe methodology changes and limitations in the README and model card.

Do not commit virtual environments, credentials, cache directories, or employee-identifying data. Do not add a data license or source attribution without verifying it.
