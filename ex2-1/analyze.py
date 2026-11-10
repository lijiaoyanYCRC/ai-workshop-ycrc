"""Exploratory analysis of experimental_measurements.csv.

Reports what each step did (rows in/out, missing values dropped) so problems
are visible in the output. Missing responses are dropped for this EDA pass
(complete-case); imputation is an alternative the researcher may prefer.
"""
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "experimental_measurements.csv"
OUT_PNG = "response_by_condition.png"

# ---------- Load ----------
df = pd.read_csv(CSV)
print(f"Loaded: {df.shape[0]} rows x {df.shape[1]} cols")
print(f"Conditions: {sorted(df['condition'].unique())}")
print(f"Batches:    {sorted(df['batch'].unique())}")
print(f"Design: {df.groupby(['condition', 'batch']).size().unstack().to_dict('index')}")

# ---------- Missing data ----------
n_missing = df["response"].isna().sum()
print(f"\nMissing response values: {n_missing} of {len(df)}")
print(df[df["response"].isna()][["sample_id", "condition", "batch"]].to_string(index=False))
data = df.dropna(subset=["response"]).copy()
print(f"Kept {len(data)} rows, dropped {n_missing} (complete-case for EDA)")

# ---------- Summary stats ----------
print("\nSummary by condition:")
summary = data.groupby("condition")["response"].agg(n="count", mean="mean", sd="std", median="median", min="min", max="max")
print(summary.round(2).to_string())

print("\nMean by condition x batch (batch-effect check):")
print(data.pivot_table(index="condition", columns="batch", values="response", aggfunc="mean").round(2).to_string())

# ---------- Statistics ----------
groups = [g["response"].values for _, g in data.groupby("condition")]
f, p_anova = stats.f_oneway(*groups)
print(f"\nOne-way ANOVA across conditions: F={f:.2f}, p={p_anova:.2e}")

ctrl = data.loc[data["condition"] == "Control", "response"]
for cond in ["Treatment_A", "Treatment_B"]:
    trt = data.loc[data["condition"] == cond, "response"]
    t, p = stats.ttest_ind(trt, ctrl, equal_var=False)  # Welch
    d = (trt.mean() - ctrl.mean()) / np.sqrt((trt.var() + ctrl.var()) / 2)
    print(f"Welch t-test {cond} vs Control: diff={trt.mean()-ctrl.mean():+.2f}, t={t:.2f}, p={p:.2e}, Cohen's d={d:+.2f}")

# Batch effect within Control (simple check; a full model would be two-way ANOVA)
b = [g["response"].values for _, g in data[data["condition"] == "Control"].groupby("batch")]
fb, pb = stats.f_oneway(*b)
print(f"Batch effect within Control (one-way ANOVA): F={fb:.2f}, p={pb:.3f}")

# ---------- Plot ----------
# Palette: dataviz reference slots 1-3 (validated all-pairs, light surface #fcfcfb)
COLORS = {"Control": "#2a78d6", "Treatment_A": "#eb6834", "Treatment_B": "#1baf7a"}
ORDER = ["Control", "Treatment_A", "Treatment_B"]
LABELS = {"Control": "Control", "Treatment_A": "Treatment A", "Treatment_B": "Treatment B"}
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#898781", "#e1e0d9"

fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

rng = np.random.default_rng(42)
positions = np.arange(len(ORDER))
for i, cond in enumerate(ORDER):
    vals = data.loc[data["condition"] == cond, "response"]
    color = COLORS[cond]
    bp = ax.boxplot(
        [vals], positions=[i], widths=0.42, patch_artist=True,
        boxprops=dict(facecolor=color, alpha=0.22, edgecolor=color, linewidth=1.5),
        medianprops=dict(color=color, linewidth=2),
        whiskerprops=dict(color=color, linewidth=1.2),
        capprops=dict(color=color, linewidth=1.2),
        flierprops=dict(marker="none"),
    )
    jitter = rng.uniform(-0.13, 0.13, size=len(vals))
    ax.scatter(i + jitter, vals, s=18, color=color, edgecolors=SURFACE,
               linewidths=0.7, zorder=3, alpha=0.85)
    # Direct labels (relief for the aqua contrast warning): mean +/- SD text
    ax.annotate(f"mean {vals.mean():.2f}\nSD {vals.std():.2f}  n={len(vals)}",
                xy=(i, vals.mean()), xytext=(i + 0.30, vals.mean()),
                fontsize=8, color=MUTED, va="center", ha="left")

ax.set_xticks(positions)
ax.set_xticklabels([LABELS[c] for c in ORDER], fontsize=10, color=INK)
ax.set_ylabel("Response", fontsize=10, color=INK)
ax.set_title("Response by condition", fontsize=12, color=INK, loc="left", pad=10)
ax.tick_params(colors=MUTED, length=0)
ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#c3c2b7")
ax.set_xlim(-0.55, 2.85)
ax.margins(y=0.06)

fig.tight_layout()
fig.savefig(OUT_PNG, facecolor=SURFACE)
print(f"\nSaved plot: {OUT_PNG}")
