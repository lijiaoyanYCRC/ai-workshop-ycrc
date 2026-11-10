# Research brief (give this to the agent for Exercise 2)

## Scientific question
Have June–August (meteorological summer) temperatures at NOAA Central Park station (`USW00094728`) changed during 1995–2024?

## Required decisions and constraints
1. Treat DATE as a date; use only June, July, August.
2. For this introductory study, calculate a daily midpoint proxy = (TMAX + TMIN)/2 in °C. State clearly that this is **not** a true 24-hour mean.
3. Treat missing or nonnumeric TMAX/TMIN as invalid for that day's midpoint; don't invent temperatures.
4. Explicitly calculate summer coverage = valid summer days / total calendar summer days (92 days/year).
5. Exclude a summer from trend fitting when coverage <90%. Report exclusions; discuss whether missingness may bias estimates even above threshold.
6. Compute one summer mean per eligible year; use those yearly values (not individual days as independent points) for a linear trend, reported in °C per decade.
7. Show a figure with annual summer means and a fitted line; preserve a CSV of yearly summary statistics.
8. Do not make causal attribution claims. Include uncertainty/limitations and say whether conclusions are based on actual NOAA observations or synthetic practice data.
9. Save `PLAN.md`, analysis script, `slurm_analysis.sh`, results, environment/packages, and a `README` explaining how to reproduce. Do not overwrite raw data.

## Deliverables
`PLAN.md`, `summer_analysis.py`, `slurm_analysis.sh`, `results/summer_summary.csv`, `results/summer_trend.png`, `results/report.md`, `environment.txt`.

## Optional extension
Count summer days with TMAX >=32 °C and discuss how the metric differs from summer mean temperature.
