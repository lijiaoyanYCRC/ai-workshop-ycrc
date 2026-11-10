#!/usr/bin/env python3
"""
Compare the distribution of `response` across experimental conditions.

Input  : experimental_measurements.csv  (read-only; never modified)
Output : condition_comparison.png       (labeled figure)
         summary_stats.csv              (per-condition summary table)

Usage  : module load miniconda && conda activate ex2-2-analysis && \
         python compare_conditions.py

Missing-data handling (flagged for the researcher):
  Rows with a missing `response` are KEPT in the source data and in the
  missing-value audit, but are excluded (complete-case) from all summary
  statistics, tests, and plotting. Alternative choices (e.g. imputation)
  would change the result and are left to the researcher.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
CSV_IN = HERE / "experimental_measurements.csv"
FIG_OUT = HERE / "condition_comparison.png"
TABLE_OUT = HERE / "summary_stats.csv"

CONDITION_ORDER = ["Control", "Treatment_A", "Treatment_B"]

# Categorical palette (dataviz reference palette, light mode, slots 1-3;
# validated all-pairs for CVD and normal vision on the light surface).
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
INK = "#0b0b0b"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def main() -> None:
    # ---- Load (read-only) and audit ------------------------------------
    df = pd.read_csv(CSV_IN)
    print(f"Loaded {CSV_IN.name}: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"Columns: {list(df.columns)}")

    n_missing = df["response"].isna().sum()
    print(f"\nMissing `response` values: {n_missing} of {len(df)} rows "
          f"(kept in source data, excluded from statistics):")
    print(df[df["response"].isna()][["sample_id", "condition", "batch"]]
          .to_string(index=False))

    cond_counts = df["condition"].value_counts()
    print(f"\nRows per condition:\n{cond_counts.to_string()}")

    # ---- Complete-case analysis subset ---------------------------------
    d = df.dropna(subset=["response"]).copy()
    print(f"\nRows used for statistics/plotting (response present): {len(d)}")

    groups = [d.loc[d["condition"] == c, "response"].to_numpy()
              for c in CONDITION_ORDER]
    for c, g in zip(CONDITION_ORDER, groups):
        assert len(g) > 0, f"no observations for condition {c}"

    # ---- Descriptive statistics -----------------------------------------
    summary = (
        d.groupby("condition")["response"]
         .agg(n="count", mean="mean", std="std", median="median",
              min="min", q1=lambda s: s.quantile(0.25),
              q3=lambda s: s.quantile(0.75), max="max")
         .reindex(CONDITION_ORDER)
         .round(3)
    )
    print("\nPer-condition summary (complete cases):")
    print(summary.to_string())
    summary.to_csv(TABLE_OUT)
    print(f"[written] {TABLE_OUT.name}")

    # ---- Distribution tests ---------------------------------------------
    # Two tests reported because the choice depends on assumptions the
    # researcher should check: ANOVA assumes normality/homoscedasticity,
    # Kruskal-Wallis does not (it tests stochastic dominance / rank shifts).
    f_stat, p_anova = stats.f_oneway(*groups)
    h_stat, p_kw = stats.kruskal(*groups)
    print(f"\nOne-way ANOVA:          F = {f_stat:.3f}, p = {p_anova:.3g}")
    print(f"Kruskal-Wallis (H):     H = {h_stat:.3f}, p = {p_kw:.3g}")

    # Pairwise nonparametric comparisons, Holm-corrected across the 3 tests.
    print("\nPairwise Mann-Whitney U (Holm-corrected p):")
    pair_idx = [(i, j) for i in range(3) for j in range(i + 1, 3)]
    pairs = [(CONDITION_ORDER[i], CONDITION_ORDER[j]) for i, j in pair_idx]
    raw = [stats.mannwhitneyu(groups[i], groups[j], alternative="two-sided").pvalue
           for i, j in pair_idx]
    order = np.argsort(raw)
    holm = np.empty(len(raw))
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (len(raw) - rank) * raw[idx])
        holm[idx] = min(running, 1.0)
    for (a, b), p_raw, p_h in zip(pairs, raw, holm):
        print(f"  {a} vs {b}: raw p = {p_raw:.3g}, Holm p = {p_h:.3g}")

    # ---- Figure ----------------------------------------------------------
    rng = np.random.default_rng(42)  # fixed seed -> jitter is reproducible
    fig, ax = plt.subplots(figsize=(8.5, 5.8), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    bp = ax.boxplot(
        groups, positions=[1, 2, 3], widths=0.45, patch_artist=True,
        medianprops={"color": INK, "lw": 1.6},
        whiskerprops={"color": INK_MUTED, "lw": 1.0},
        capprops={"color": INK_MUTED, "lw": 1.0},
        flierprops={"marker": "o", "ms": 4, "mfc": "none",
                    "mec": INK_MUTED, "markeredgewidth": 1.0},
    )
    for patch, col in zip(bp["boxes"], COLORS):
        patch.set(facecolor=col, alpha=0.30, edgecolor=col, lw=1.4)

    # Raw observations, jittered beside each box (n=28-30 per group).
    for k, (c, g) in enumerate(zip(CONDITION_ORDER, groups), start=1):
        x = k + 0.32 + rng.uniform(-0.07, 0.07, size=len(g))
        ax.scatter(x, g, s=16, color=COLORS[k - 1], alpha=0.85,
                   edgecolors=SURFACE, linewidths=0.6, zorder=3,
                   label=f"{c} (n={len(g)})")

    # Direct labels (also the relief for the aqua contrast warning).
    for k, (c, g) in enumerate(zip(CONDITION_ORDER, groups), start=1):
        ax.annotate(f"median {np.median(g):.2f}",
                    xy=(k, np.median(g)), xytext=(k, np.median(g) + 0.35),
                    ha="center", va="bottom", fontsize=8.5, color=INK_MUTED)

    missing_per_cond = df[df["response"].isna()]["condition"].value_counts()
    ax.set_xticks([1, 2, 3],
                  [f"{c}\n(n={len(g)}, {missing_per_cond.get(c, 0)} missing)"
                   for c, g in zip(CONDITION_ORDER, groups)])
    ax.set_ylabel("Response (measurement units)", color=INK)
    ax.set_title("Response distribution by experimental condition",
                 loc="left", color=INK, fontsize=12, fontweight="bold", pad=24)
    ax.text(0.0, 1.015,
            f"Kruskal-Wallis H = {h_stat:.2f}, p = {p_kw:.2g}  |  "
            f"boxes: median/IQR/whiskers; dots: individual observations",
            transform=ax.transAxes, fontsize=8.5, color=INK_MUTED)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(0.4, 3.6)
    ax.legend(loc="upper right", frameon=False, fontsize=9,
              labelcolor=INK, handletextpad=0.4)
    fig.tight_layout()
    fig.savefig(FIG_OUT, dpi=200, facecolor=SURFACE)
    print(f"\n[written] {FIG_OUT.name}")


if __name__ == "__main__":
    main()
