# Continuous Meta Analysis

Use this skill when the user asks for a continuous-outcome meta-analysis with means, standard deviations, and sample sizes for treatment and control groups.

## Workflow

1. Check the input table has `First_author`, `Year`, `n.e`, `mean.e`, `sd.e`, `n.c`, `mean.c`, and `sd.c`.
2. Create a task directory with `create_analysis_project.py`.
3. Copy or adapt `templates/continuous_meta_analysis.R`.
4. Run the task with `run_r_task.py`.
5. Archive outputs with `archive_result.py`.
6. Ask the user before promoting the result back into the knowledge base.

## Guardrails

- Do not overwrite user source data.
- Do not commit real study data to the framework repository.
- Prefer random-effects interpretation when heterogeneity is high.

