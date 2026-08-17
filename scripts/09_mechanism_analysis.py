#!/usr/bin/env python3
"""Crime-type temperature response curves for mechanism hypotheses."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from config import *
from offense_codes import MECHANISM_OUTCOMES

RESULTS.mkdir(exist_ok=True)
FIG = RESULTS / "figures"
FIG.mkdir(exist_ok=True)

d = pd.read_csv(OUT / "daily.csv", parse_dates=["date"])
OUTCOMES = [y for y in MECHANISM_OUTCOMES if y in d.columns]
BIN_ORDER = ["lt15", "15_20", "20_25", "25_30", "30_35", "ge35"]
BIN_LABELS = ["<15", "15–20", "20–25", "25–30", "30–35", "≥35"]


def hac(formula, data, lag=14):
    return smf.ols(formula, data=data).fit(
        cov_type="HAC", cov_kwds={"maxlags": lag})


def pct(beta):
    return 100 * (np.exp(beta) - 1)


def classify_shape(coefs, ref_idx=2):
    """Heuristic label: monotonic increasing, inverted-U, flat, noisy."""
    vals = np.array(coefs)
    if len(vals) < 4:
        return "too sparse"
    hot = vals[ref_idx + 1:]
    cool = vals[:ref_idx]
    hot_rising = np.all(np.diff(hot) >= -0.005)
    hot_monotone_up = hot_rising and vals[-1] > vals[ref_idx] + 0.01
    peak_mid = np.argmax(vals) in range(1, len(vals) - 1)
    tail_down = vals[-1] < vals[np.argmax(vals)] - 0.01
    inverted = peak_mid and tail_down and vals[ref_idx] < vals[np.argmax(vals)] - 0.01
    all_small = np.all(np.abs(vals - vals[ref_idx]) < 0.01)
    se_proxy = np.std(vals)
    if all_small:
        return "flat"
    if inverted:
        return "inverted-U"
    if hot_monotone_up and vals[-1] > vals[ref_idx] + 0.02:
        return "monotonic increasing"
    if se_proxy > 0.04:
        return "noisy"
    return "mixed / inconclusive"


# ---------------------------------------------------------------------------
# Temperature bins
# ---------------------------------------------------------------------------
bins = []
for y in OUTCOMES:
    x = d.copy()
    x["ly"] = np.log1p(x[y])
    fit = hac(
        "ly ~ C(tmax_bin, Treatment(reference='20_25')) + PRCP + C(ym) + C(dow)",
        x, 14)
    for term in fit.params.index:
        if "tmax_bin" in term:
            bins.append([y, term, fit.params[term], fit.bse[term],
                         fit.pvalues[term], pct(fit.params[term])])
bins_df = pd.DataFrame(bins, columns=["outcome", "bin", "coef", "se", "p", "pct"])
bins_df.to_csv(RESULTS / "crime_type_temperature_bins.csv", index=False)

# ---------------------------------------------------------------------------
# Quadratic anomaly model
# ---------------------------------------------------------------------------
quad = []
for y in OUTCOMES:
    x = d.copy()
    x["ly"] = np.log1p(x[y])
    fit = hac("ly ~ temp_anom + I(temp_anom**2) + PRCP + C(ym) + C(dow)", x, 14)
    for term in ["temp_anom", "I(temp_anom ** 2)"]:
        quad.append([y, term, fit.params[term], fit.bse[term],
                     fit.pvalues[term], pct(fit.params[term]), fit.nobs])
quad_df = pd.DataFrame(quad, columns=["outcome", "term", "coef", "se", "p", "pct", "n"])
quad_df.to_csv(RESULTS / "crime_type_quadratic.csv", index=False)

# ---------------------------------------------------------------------------
# Extreme heat: hot35 (reuse thresholds from build)
# ---------------------------------------------------------------------------
hot = []
for y in OUTCOMES:
    for v in ["hot30", "hot32", "hot35"]:
        if v not in d.columns:
            continue
        x = d.copy()
        x["ly"] = np.log1p(x[y])
        fit = hac(f"ly ~ {v} + PRCP + C(ym) + C(dow)", x, 14)
        hot.append([y, v, fit.params[v], fit.bse[v], fit.pvalues[v],
                    pct(fit.params[v]), fit.nobs, int(x[v].sum())])
hot_df = pd.DataFrame(hot, columns=[
    "outcome", "threshold", "coef", "se", "p", "pct", "n", "n_hot_days"])
hot_df.to_csv(RESULTS / "crime_type_extreme_heat.csv", index=False)

# ---------------------------------------------------------------------------
# Percentile-based extreme heat (hot_p95)
# ---------------------------------------------------------------------------
tmax_p95 = d["TMAX"].quantile(0.95)
p95 = []
focus = ["violent", "interpersonal", "property"]
for y in focus:
    if y not in d.columns:
        continue
    x = d.copy()
    x["ly"] = np.log1p(x[y])
    for v in ["hot35", "hot_p95"]:
        fit = hac(f"ly ~ {v} + PRCP + C(ym) + C(dow)", x, 14)
        p95.append([y, v, tmax_p95, fit.params[v], fit.bse[v], fit.pvalues[v],
                    pct(fit.params[v]), fit.nobs, int(x[v].sum())])
p95_df = pd.DataFrame(p95, columns=[
    "outcome", "threshold", "tmax_cutoff", "coef", "se", "p", "pct", "n", "n_hot_days"])
p95_df.to_csv(RESULTS / "crime_type_hot_p95.csv", index=False)

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def extract_bin_label(term):
    return term.split("[T.")[1].split("]")[0] if "[T." in term else term


plot_outcomes = [y for y in OUTCOMES if y in [
    "violent", "violent_ucr", "interpersonal", "robbery",
    "property", "theft", "burglary", "vehicle_theft"]]

# fig12 — all crime types
fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharey=True)
axes = axes.flatten()
for i, y in enumerate(plot_outcomes):
    sub = bins_df[bins_df.outcome == y].copy()
    sub["key"] = sub.bin.map(extract_bin_label)
    sub = sub.set_index("key").reindex([b for b in BIN_ORDER if b != "20_25"])
    x = np.arange(len(sub))
    ax = axes[i]
    ax.errorbar(x, sub.coef, yerr=1.96 * sub.se, fmt="o", capsize=3)
    ax.axhline(0, lw=0.8, color="gray")
    ax.set_title(y.replace("_", " "))
    ax.set_xticks(x)
    ax.set_xticklabels([l for l, b in zip(BIN_LABELS, BIN_ORDER) if b != "20_25"],
                       rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("coef vs 20–25°C")
plt.suptitle("Temperature-bin response by crime type (temporal FE model)")
plt.tight_layout()
plt.savefig(FIG / "fig12_crime_type_temperature_response.png", dpi=200)
plt.close()

# fig13 — interpersonal vs property opportunity crimes
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
groups = {
    "Interpersonal / affective violence": ["interpersonal", "violent"],
    "Property / opportunity crime": ["theft", "burglary", "vehicle_theft", "property"],
}
for ax, (title, cats) in zip(axes, groups.items()):
    for y in cats:
        if y not in plot_outcomes:
            continue
        sub = bins_df[bins_df.outcome == y].copy()
        sub["key"] = sub.bin.map(extract_bin_label)
        sub = sub.set_index("key").reindex([b for b in BIN_ORDER if b != "20_25"])
        x = np.arange(len(sub))
        ax.errorbar(x, sub.coef, yerr=1.96 * sub.se, fmt="o-", capsize=3,
                    label=y.replace("_", " "))
    ax.axhline(0, lw=0.8, color="gray")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels([l for l, b in zip(BIN_LABELS, BIN_ORDER) if b != "20_25"],
                       rotation=30, ha="right")
    ax.set_ylabel("coef vs 20–25°C")
    ax.legend(fontsize=8)
plt.suptitle("Interpersonal violence vs property/opportunity crime")
plt.tight_layout()
plt.savefig(FIG / "fig13_interpersonal_vs_property_heat.png", dpi=200)
plt.close()

# ---------------------------------------------------------------------------
# MECHANISM_FINDINGS.md
# ---------------------------------------------------------------------------
classif = pd.read_csv(RESULTS / "crime_mechanism_classification.csv")
shapes = {}
for y in OUTCOMES:
    sub = bins_df[bins_df.outcome == y].copy()
    sub["key"] = sub.bin.map(extract_bin_label)
    coefs = []
    for b in BIN_ORDER:
        if b == "20_25":
            coefs.append(0.0)
        else:
            row = sub[sub.key == b]
            coefs.append(float(row.coef.iloc[0]) if len(row) else 0.0)
    shapes[y] = classify_shape(coefs)

lines = [
    "# Mechanism-oriented crime-type findings",
    "",
    f"Daily sample: N = {len(d):,} ({d.date.min().date()} → {d.date.max().date()})",
    f"LAX TMAX 95th percentile: {tmax_p95:.1f}°C ({int(d.hot_p95.sum())} days)",
    f"LAX hot35 days: {int(d.hot35.sum())}",
    "",
    "## Category definitions",
    "",
    "Subcategories use LAPD Crm Cd codes (see `crime_mechanism_classification.csv`).",
    "",
    "| Category | Incidents | Share | Overlap check |",
    "|---|---:|---:|---|",
]
for _, r in classif.iterrows():
    overlap = r.overlaps_with if pd.notna(r.overlaps_with) and r.overlaps_with else "none"
    lines.append(
        f"| {r.category} | {int(r.incident_count):,} | {r.share_of_all:.1%} | {overlap} |"
    )

lines += ["", "## Temperature-bin shapes (vs 20–25°C reference)", ""]
for y in OUTCOMES:
    sub = bins_df[bins_df.outcome == y]
    lines.append(f"### {y}")
    lines.append(f"- Shape heuristic: **{shapes[y]}**")
    lines.append(f"- Mean daily count: {d[y].mean():.1f}")
    for _, r in sub.iterrows():
        key = extract_bin_label(r.bin)
        lines.append(
            f"  - {key}: β={r.coef:.4f}, SE={r.se:.4f}, p={r.p:.4g}, ~{r.pct:.2f}%"
        )
    lines.append("")

lines += ["", "## Quadratic temp-anomaly summary (linear term)", ""]
for y in OUTCOMES:
    r = quad_df[(quad_df.outcome == y) & (quad_df.term == "temp_anom")].iloc[0]
    b2 = quad_df[(quad_df.outcome == y) & (quad_df.term == "I(temp_anom ** 2)")]
    b2_txt = ""
    if len(b2):
        b2_txt = f"; β₂={b2.iloc[0].coef:.4f} (p={b2.iloc[0].p:.4g})"
    lines.append(
        f"- {y}: β₁={r.coef:.4f}, SE={r.se:.4f}, p={r.p:.4g}, "
        f"~{r.pct:.2f}% per +1°C{b2_txt}"
    )

lines += ["", "## Extreme heat indicators", ""]
for y in ["violent", "interpersonal", "property"]:
    for thr in ["hot35", "hot_p95"]:
        row = p95_df[(p95_df.outcome == y) & (p95_df.threshold == thr)]
        if len(row):
            r = row.iloc[0]
            lines.append(
                f"- {y} / {thr}: β={r.coef:.4f}, SE={r.se:.4f}, p={r.p:.4g}, "
                f"~{r.pct:.2f}%, n_hot={int(r.n_hot_days)}"
            )

lines += ["", "## Interpretation (do not oversell)", ""]
interp = shapes.get("interpersonal", "unknown")
prop_shapes = [shapes.get(x, "") for x in ["theft", "burglary", "vehicle_theft", "property"]]
prop_inverted = any("inverted" in s for s in prop_shapes)
inter_mono = "monotonic" in interp

if inter_mono and prop_inverted:
    mechanism = "Consistent with **heat-aggression** (interpersonal) and **routine-activity** (property inverted-U) pathways — suggestive, not causal."
elif inter_mono:
    mechanism = "Interpersonal violence rises with heat; property response is flat or mixed. Partial support for aggression pathway; routine-activity inverted-U not clear."
elif prop_inverted:
    mechanism = "Property crime shows inverted-U; interpersonal pattern is weaker. Mixed evidence."
else:
    mechanism = "**Inconclusive** — differential pathway patterns are not clearly supported."

lines.append(mechanism)
lines += [
    "",
    "Spatial within-day design (area + date FE) still shows no positive local violent-heat effect; "
    "this mechanism note applies to the **citywide temporal** specification only.",
    "",
    "**Note:** 35°C is an intuitive local tail threshold, not a universal extreme-heat definition. "
    f"hot_p95 uses LAX TMAX ≥ {tmax_p95:.1f}°C.",
]

(RESULTS / "MECHANISM_FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")
print("done ->", RESULTS / "MECHANISM_FINDINGS.md")
