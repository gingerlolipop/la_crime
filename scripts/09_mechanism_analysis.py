#!/usr/bin/env python3
"""Crime-type temperature response curves (v2 taxonomy).

Same identification as the main temporal model: year-month FE, day-of-week FE,
precipitation, HAC(14). Only the outcome taxonomy changes.

No automated curve-shape labels are produced. The script emits estimates and
mechanical per-bin significance summaries; substantive interpretation lives in
INTERPRETATION below and is written by hand from those estimates.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from config import *
from offense_codes import (
    OPPORTUNITY_OUTCOMES, OPTIONAL_OUTCOMES, VIOLENCE_OUTCOMES,
)

RESULTS.mkdir(exist_ok=True)
FIG = RESULTS / "figures"
FIG.mkdir(exist_ok=True)

d = pd.read_csv(OUT / "daily.csv", parse_dates=["date"])
OUTCOMES = [
    y for y in VIOLENCE_OUTCOMES + OPPORTUNITY_OUTCOMES + OPTIONAL_OUTCOMES
    if y in d.columns
]
BIN_ORDER = ["lt15", "15_20", "20_25", "25_30", "30_35", "ge35"]
BIN_LABELS = {"lt15": "<15", "15_20": "15–20", "20_25": "20–25",
              "25_30": "25–30", "30_35": "30–35", "ge35": "≥35"}
NON_REF = [b for b in BIN_ORDER if b != "20_25"]
BIN_FORMULA = "C(tmax_bin, Treatment(reference='20_25'))"
CONTROLS = "PRCP + C(ym) + C(dow)"

# Planned heterogeneity contrasts (outcome A minus outcome B).
PAIRS = [
    ("interpersonal", "property"),
    ("interpersonal", "motor_vehicle_theft"),
    ("interpersonal", "structure_burglary"),
    ("interpersonal", "robbery"),
]


def hac(formula, data, lag=14):
    return smf.ols(formula, data=data).fit(
        cov_type="HAC", cov_kwds={"maxlags": lag})


def pct(beta):
    return 100 * (np.exp(beta) - 1)


def bin_key(term):
    return term.split("[T.")[1].split("]")[0] if "[T." in term else term


def describe_bins(sub):
    """Mechanical summary of which bins are signed and significant at 5%."""
    parts = []
    for b in NON_REF:
        row = sub[sub.key == b]
        if not len(row):
            continue
        r = row.iloc[0]
        if r.p >= 0.05:
            continue
        parts.append(f"{BIN_LABELS[b]}{'+' if r.coef > 0 else '-'}")
    return "sig@5%: " + (", ".join(parts) if parts else "none")


def fit_bins(series_name, data):
    x = data.copy()
    x["ly"] = np.log1p(x[series_name])
    fit = hac(f"ly ~ {BIN_FORMULA} + {CONTROLS}", x)
    rows = []
    for term in fit.params.index:
        if "tmax_bin" in term:
            rows.append({
                "outcome": series_name,
                "bin": bin_key(term),
                "coef": fit.params[term],
                "se": fit.bse[term],
                "p": fit.pvalues[term],
                "pct": pct(fit.params[term]),
            })
    return pd.DataFrame(rows), fit


# ---------------------------------------------------------------------------
# 1) Temperature bins by crime type
# ---------------------------------------------------------------------------
bin_frames, summaries = [], []
for y in OUTCOMES:
    frame, _ = fit_bins(y, d)
    frame["key"] = frame["bin"]
    bin_frames.append(frame)
    summaries.append({
        "outcome": y,
        "mean_daily_count": float(d[y].mean()),
        "share_of_total": float(d[y].sum() / d["total"].sum()),
        "bin_summary": describe_bins(frame),
    })
bins_df = pd.concat(bin_frames, ignore_index=True)
bins_df[["outcome", "bin", "coef", "se", "p", "pct"]].to_csv(
    RESULTS / "crime_type_temperature_bins_v2.csv", index=False)
summary_df = pd.DataFrame(summaries)

# Supplementary: BH-FDR across all exploratory bin coefficients.
fdr = bins_df[["outcome", "bin", "coef", "se", "p", "pct"]].copy()
fdr["p_fdr_bh"] = multipletests(fdr["p"], method="fdr_bh")[1]
fdr["sig_fdr_05"] = fdr["p_fdr_bh"] < 0.05
fdr.to_csv(RESULTS / "crime_type_temperature_bins_fdr.csv", index=False)

# ---------------------------------------------------------------------------
# 2) Quadratic anomaly model + turning point
# ---------------------------------------------------------------------------
anom_lo, anom_hi = d["temp_anom"].min(), d["temp_anom"].max()
quad = []
for y in OUTCOMES:
    x = d.copy()
    x["ly"] = np.log1p(x[y])
    fit = hac(f"ly ~ temp_anom + I(temp_anom**2) + {CONTROLS}", x)
    b1, b2 = fit.params["temp_anom"], fit.params["I(temp_anom ** 2)"]
    turning = -b1 / (2 * b2) if b2 != 0 else np.nan
    quad.append({
        "outcome": y,
        "b1_linear": b1,
        "b1_se": fit.bse["temp_anom"],
        "b1_p": fit.pvalues["temp_anom"],
        "b1_pct_per_c": pct(b1),
        "b2_quadratic": b2,
        "b2_se": fit.bse["I(temp_anom ** 2)"],
        "b2_p": fit.pvalues["I(temp_anom ** 2)"],
        "turning_point_anom_c": turning,
        "turning_point_in_support": bool(anom_lo <= turning <= anom_hi),
        "anom_min": anom_lo,
        "anom_max": anom_hi,
        "n": fit.nobs,
    })
quad_df = pd.DataFrame(quad)
quad_df.to_csv(RESULTS / "crime_type_quadratic_v2.csv", index=False)

# ---------------------------------------------------------------------------
# 3) Extreme-heat indicators, including climatological P95
# ---------------------------------------------------------------------------
THRESHOLDS = [t for t in ["hot30", "hot32", "hot35", "hot_p95", "hot_p95_clim"]
              if t in d.columns]
hot = []
for y in OUTCOMES:
    for v in THRESHOLDS:
        x = d.copy()
        x["ly"] = np.log1p(x[y])
        fit = hac(f"ly ~ {v} + {CONTROLS}", x)
        hot.append({
            "outcome": y,
            "threshold": v,
            "coef": fit.params[v],
            "se": fit.bse[v],
            "p": fit.pvalues[v],
            "pct": pct(fit.params[v]),
            "n": fit.nobs,
            "n_hot_days": int(x[v].sum()),
        })
hot_df = pd.DataFrame(hot)
hot_df[hot_df.threshold.isin(["hot30", "hot32", "hot35"])].to_csv(
    RESULTS / "crime_type_extreme_heat_v2.csv", index=False)
hot_df[hot_df.threshold.isin(["hot35", "hot_p95", "hot_p95_clim"])].to_csv(
    RESULTS / "crime_type_hot_p95_clim.csv", index=False)

thresholds_meta = pd.read_csv(RESULTS / "heat_threshold_definitions.csv")

# ---------------------------------------------------------------------------
# 4) Planned heterogeneity tests on the log-outcome difference
#    D_t = log(1+A_t) - log(1+B_t), same bin model and HAC(14).
# ---------------------------------------------------------------------------
het = []
for a, b in PAIRS:
    if a not in d.columns or b not in d.columns:
        continue
    x = d.copy()
    x["ly"] = np.log1p(x[a]) - np.log1p(x[b])
    fit = hac(f"ly ~ {BIN_FORMULA} + {CONTROLS}", x)
    for term in fit.params.index:
        if "tmax_bin" not in term:
            continue
        key = bin_key(term)
        coef, p = fit.params[term], fit.pvalues[term]
        if p >= 0.05:
            note = "no detectable difference"
        elif coef > 0:
            note = f"{a} responds more positively than {b}"
        else:
            note = f"{b} responds more positively than {a}"
        het.append({
            "pair": f"{a}_minus_{b}",
            "outcome_a": a,
            "outcome_b": b,
            "bin": key,
            "diff_coef": coef,
            "se": fit.bse[term],
            "p": p,
            "diff_pct": pct(coef),
            "interpretation": note,
        })
het_df = pd.DataFrame(het)
het_df.to_csv(RESULTS / "crime_type_heterogeneity_tests.csv", index=False)

# ---------------------------------------------------------------------------
# 5) Figures
# ---------------------------------------------------------------------------
def bin_series(outcome):
    sub = bins_df[bins_df.outcome == outcome].set_index("key").reindex(NON_REF)
    return np.arange(len(NON_REF)), sub


def style_axis(ax, ylabel=True):
    ax.axhline(0, lw=0.8, color="gray")
    ax.set_xticks(np.arange(len(NON_REF)))
    ax.set_xticklabels([BIN_LABELS[b] for b in NON_REF], rotation=45,
                       ha="right", fontsize=8)
    ax.set_xlabel("Daily TMAX bin (°C)", fontsize=8)
    if ylabel:
        ax.set_ylabel("log-count coef vs 20–25°C", fontsize=8)


# fig12 — every cleaned category, shared y-axis
n = len(OUTCOMES)
ncol = 4
nrow = int(np.ceil(n / ncol))
fig, axes = plt.subplots(nrow, ncol, figsize=(3.4 * ncol, 3.0 * nrow),
                         sharey=True)
axes = np.atleast_1d(axes).flatten()
for ax, y in zip(axes, OUTCOMES):
    x, sub = bin_series(y)
    ax.errorbar(x, sub.coef, yerr=1.96 * sub.se, fmt="o", capsize=3, ms=4)
    ax.set_title(f"{y.replace('_', ' ')}  (mean {d[y].mean():.0f}/day)",
                 fontsize=9)
    style_axis(ax)
for ax in axes[n:]:
    ax.axis("off")
fig.suptitle("Temperature-bin response by crime type, 95% CI "
             "(city-day model, year-month + DOW FE, HAC(14))", fontsize=11)
fig.tight_layout()
fig.savefig(FIG / "fig12_crime_type_temperature_response_v2.png", dpi=200)
plt.close(fig)

# fig13 — interpersonal | robbery | acquisitive offenses | vandalism
panels = [
    ("Interpersonal violence", ["interpersonal"]),
    ("Robbery (violent, instrumental)", ["robbery"]),
    ("Acquisitive property offenses",
     ["theft", "structure_burglary", "vehicle_burglary", "motor_vehicle_theft"]),
    ("Vandalism (property damage, non-acquisitive)", ["vandalism"]),
]
fig, axes = plt.subplots(1, 4, figsize=(16, 4.2), sharey=True)
for ax, (title, cats) in zip(axes, panels):
    for y in cats:
        if y not in OUTCOMES:
            continue
        x, sub = bin_series(y)
        ax.errorbar(x, sub.coef, yerr=1.96 * sub.se, fmt="o-", capsize=3,
                    ms=4, lw=1.2, label=y.replace("_", " "))
    ax.set_title(title, fontsize=10)
    style_axis(ax)
    ax.legend(fontsize=8)
fig.suptitle("Temperature response by offense type: interpersonal violence, "
             "robbery, acquisitive property offenses, and vandalism "
             "(coefficients relative to 20–25°C, 95% CI)", fontsize=11)
fig.tight_layout()
fig.savefig(FIG / "fig13_interpersonal_vs_opportunity_v2.png", dpi=200)
plt.close(fig)

# ---------------------------------------------------------------------------
# 6) MECHANISM_FINDINGS_V2.md
#    Tables are generated; the interpretation below is written by hand.
# ---------------------------------------------------------------------------
INTERPRETATION = """
Heat does not shift all crime uniformly. The divergence between interpersonal
violence and target-dependent property offenses survives the taxonomy cleanup,
and the cleanup changes two of the v1 conclusions.

**Interpersonal violence** shows an ordered positive response: +4.03% at
25–30°C, +8.30% at 30–35°C, and +11.82% at ≥35°C relative to 20–25°C, each
estimated at p<0.001, with the cool bins significantly negative. Every warmer
bin sits above the previous one, so this is an ordered positive response rather
than a single threshold effect. It is the strongest and most precise pattern in
the analysis and is consistent with heat-aggression / negative-affect
mechanisms. The category is defined by offense content — assault, battery, IPV,
threats — not by observed affect, so the mechanism remains an interpretation.

**Robbery** rises through 30–35°C (+4.56%, p=0.018) and then attenuates at ≥35°C
(+2.87%, p=0.48). The defensible description is that robbery rises through
moderate-high heat and then flattens, with the upper tail too imprecise to sign.
Calling this an inverted-U would overstate the evidence. Importantly, the
planned interpersonal-minus-robbery contrast is **not** significant in any warm
bin (p=0.26, 0.07, 0.09), so robbery and interpersonal violence are not
statistically distinguishable here. The apparent difference in their curves
should not be reported as an established contrast between affective and
instrumental violence.

**Acquisitive property offenses are flat to declining in the hot tail.** Clean
theft is flat: no warm bin is significant, and the ≥35°C estimate is −0.18%.
Motor-vehicle theft is the clearest decline (−3.04% at 30–35°C, −8.40% at ≥35°C,
and −2.65% at the climatological P95 threshold, which has 356 supporting days).
Vehicle burglary is negative throughout the warm range and significant at the
percentile thresholds (−3.77% at climatological P95). Structure burglary is
imprecise across bins but significantly negative at both percentile thresholds
(about −2.5%). The aggregate `property` series is flat because these declines
cancel against positive components, so "property crime is inverted-U" is not
supported.

**Two v1 findings do not survive the cleanup.** First, v1 reported theft rising
monotonically with heat. That result was driven by vandalism, which v1 had
folded into `theft`; once separated, clean theft is flat and vandalism carries
the positive response (+2.28%, +4.18%, +8.38% across the warm bins). Second, v1
labelled burglary inverted-U. Splitting it shows structure and vehicle burglary
are each flat-to-declining, and the v1 label was an artifact of the shape
heuristic picking a cool-bin peak.

**Vandalism is the most interesting reclassification.** It is legally a property
offense but its temperature response tracks interpersonal violence rather than
the acquisitive offenses it was grouped with. Vandalism requires no target to
acquire and no completed transaction, so a routine-activity opportunity account
does not obviously predict it to rise while motor-vehicle theft falls. This is
suggestive that the relevant distinction is closer to expressive versus
acquisitive offending than to the conventional violent/property split. We flag
this as a hypothesis generated by the cleanup, not as a tested result.

The planned heterogeneity tests confirm the main divergence is statistical, not
just visual. Interpersonal violence responds significantly more positively than
aggregate property, motor-vehicle theft, and structure burglary in every warm
bin, with the gap widening across bins (for example +0.1995 versus
motor-vehicle theft at ≥35°C, p≈1e-06).

The pattern is not fragile to multiple testing. Under BH-FDR across all 55
exploratory bin coefficients, the warm-bin estimates for interpersonal violence,
violent, violent_ucr, and vandalism remain significant, as do the negative
motor-vehicle-theft estimates at 30–35°C and ≥35°C. The estimates that do not
survive adjustment are the ones already described above as imprecise: robbery at
≥35°C and the single vehicle-burglary result at 25–30°C.

Overall this is consistent with two coexisting pathways: heat-aggression for
interpersonal conflict and expressive offending, and opportunity/target
constraints for offenses requiring vehicles, structures, or sustained outdoor
presence. It does not identify either pathway. Nothing here separates exposure
from behavioural adaptation, reporting behaviour, or policing intensity.

Arson is retained in the tables for completeness but has only 1.2 incidents per
day and no significant bin; it should stay out of the mechanism comparison.
""".strip()

CAVEATS = """
- Single weather station (LAX) for the whole city; the within-day spatial design
  under area + date FE still shows no positive local heat gradient. The
  citywide temporal association and the local spatial null are different
  estimands, so the spatial null does not overturn the temporal result.
- Only 26 crime-period days reach TMAX ≥ 35°C at LAX. Treat hot35 as upper-tail
  supporting evidence; the climatological P95 threshold has far more support.
- 35°C is an intuitive absolute threshold, not a universal extreme-heat
  definition.
- Temperature bins use absolute daily TMAX; the quadratic model uses mean-based
  temperature anomaly. These are different exposure definitions and the two
  specifications should not be read as nested.
- A negative quadratic term means the fitted curve is concave, not that the
  response turns downward inside the observed range. See the turning-point
  column in `crime_type_quadratic_v2.csv`.
- Interpersonal violence is the pre-specified primary mechanism outcome and the
  four contrasts in `crime_type_heterogeneity_tests.csv` are the planned
  comparisons. All remaining crime-type curves are exploratory and uncorrected
  for multiple comparisons; BH-FDR adjusted p-values for the bin coefficients
  are in `crime_type_temperature_bins_fdr.csv` as a supplement.
- The expressive-versus-acquisitive reading of the vandalism result was
  generated by this cleanup rather than specified in advance. It should be
  treated as a hypothesis for a future pre-specified test, not as a finding.
- Curve descriptions in this document are read off the coefficients and
  confidence intervals by hand. No automated shape classifier is used.
""".strip()

classif = pd.read_csv(RESULTS / "crime_mechanism_classification_v2.csv")
lines = [
    "# Mechanism-oriented crime-type findings (v2 taxonomy)",
    "",
    f"City-day sample: N = {len(d):,} "
    f"({d.date.min().date()} → {d.date.max().date()}).",
    "Specification unchanged from the main temporal model: "
    "year-month FE, day-of-week FE, precipitation, HAC(14). "
    "Outcomes are `log(1 + daily count)`; bins are absolute daily TMAX with "
    "20–25°C as the reference.",
    "",
    "## 1. Cleaned category definitions",
    "",
    "v2 changes relative to v1: vandalism and arson are removed from `theft`, "
    "burglary is split into structure vs vehicle, and vehicle theft is "
    "restricted to motor vehicles (bike/boat moved into general theft). "
    "The `violent`, `violent_ucr`, and `property` aggregates are unchanged, so "
    "results remain comparable to `main_models.csv`.",
    "",
    "| Category | Codes | Incidents | Share of all crime | Sibling overlap |",
    "|---|---:|---:|---:|---|",
]
for _, r in classif.iterrows():
    lines.append(
        f"| `{r.category}` | {int(r.n_codes)} | {int(r.incident_count):,} | "
        f"{r.share_of_all:.1%} | {r.overlaps_with_siblings} |"
    )
lines += [
    "",
    "Property subcategories partition the `property` aggregate exactly and are "
    "mutually disjoint (verified in `02_build.py`).",
    "",
    "## 2. Sample counts by outcome",
    "",
    "| Outcome | Mean daily count | Share of all crime | Significant bins |",
    "|---|---:|---:|---|",
]
for _, r in summary_df.iterrows():
    lines.append(
        f"| `{r.outcome}` | {r.mean_daily_count:.1f} | "
        f"{r.share_of_total:.1%} | {r.bin_summary} |"
    )

lines += [
    "",
    "## 3. Temperature-bin coefficients",
    "",
    "Percentage effects are `100(exp(beta) - 1)` relative to the 20–25°C bin.",
    "",
    "| Outcome | " + " | ".join(BIN_LABELS[b] for b in NON_REF) + " |",
    "|---" * (len(NON_REF) + 1) + "|",
]
for y in OUTCOMES:
    cells = []
    sub = bins_df[bins_df.outcome == y].set_index("key")
    for b in NON_REF:
        if b not in sub.index:
            cells.append("—")
            continue
        r = sub.loc[b]
        stars = "***" if r.p < 0.001 else "**" if r.p < 0.01 else "*" if r.p < 0.05 else ""
        cells.append(f"{r.pct:+.2f}%{stars}")
    lines.append(f"| `{y}` | " + " | ".join(cells) + " |")
lines += [
    "",
    "`*` p<0.05, `**` p<0.01, `***` p<0.001. "
    "Full estimates with standard errors: `crime_type_temperature_bins_v2.csv`; "
    "BH-FDR supplement: `crime_type_temperature_bins_fdr.csv`.",
    "",
    "## 4. Extreme-heat thresholds",
    "",
    "| Threshold | Cutoff | Basis | Days in 2010–2023 |",
    "|---|---:|---|---:|",
]
for _, r in thresholds_meta.iterrows():
    lines.append(
        f"| `{r.threshold}` | {r.cutoff_c:.1f}°C | {r.basis} | "
        f"{int(r.n_crime_period_days):,} |"
    )
lines += [
    "",
    "The climatological threshold `hot_p95_clim` is the 95th percentile of LAX "
    f"TMAX over {NORMAL_START[:4]}–{NORMAL_END[:4]}, held fixed and then applied "
    "to the crime period, so the cutoff does not depend on the crime sample.",
    "",
    "| Outcome | hot35 | hot_p95 (sample) | hot_p95_clim |",
    "|---|---:|---:|---:|",
]
for y in OUTCOMES:
    cells = []
    for thr in ["hot35", "hot_p95", "hot_p95_clim"]:
        row = hot_df[(hot_df.outcome == y) & (hot_df.threshold == thr)]
        if not len(row):
            cells.append("—")
            continue
        r = row.iloc[0]
        stars = "***" if r.p < 0.001 else "**" if r.p < 0.01 else "*" if r.p < 0.05 else ""
        cells.append(f"{r.pct:+.2f}%{stars}")
    lines.append(f"| `{y}` | " + " | ".join(cells) + " |")

lines += [
    "",
    "## 5. Planned heterogeneity tests",
    "",
    "Each test regresses the daily log-outcome difference "
    "`D_t = log(1 + A_t) - log(1 + B_t)` on the same bins, controls, and "
    "fixed effects, which preserves same-day covariance between the two "
    "outcomes. A positive coefficient means outcome A responds more positively "
    "than outcome B in that bin.",
    "",
    "| Pair | " + " | ".join(BIN_LABELS[b] for b in NON_REF) + " |",
    "|---" * (len(NON_REF) + 1) + "|",
]
for a, b in PAIRS:
    pair = f"{a}_minus_{b}"
    sub = het_df[het_df.pair == pair].set_index("bin")
    if not len(sub):
        continue
    cells = []
    for bb in NON_REF:
        if bb not in sub.index:
            cells.append("—")
            continue
        r = sub.loc[bb]
        stars = "***" if r.p < 0.001 else "**" if r.p < 0.01 else "*" if r.p < 0.05 else ""
        cells.append(f"{r.diff_coef:+.4f}{stars}")
    lines.append(f"| `{a}` − `{b}` | " + " | ".join(cells) + " |")
lines += [
    "",
    "Full estimates: `crime_type_heterogeneity_tests.csv`.",
    "",
    "## 6. Quadratic summary (compact robustness only)",
    "",
    "The quadratic uses temperature *anomaly*, not absolute TMAX. "
    "`T*` is the implied turning point in anomaly units; "
    "`in support` indicates whether it falls inside the observed anomaly range "
    f"[{anom_lo:.1f}, {anom_hi:.1f}]°C.",
    "",
    "| Outcome | beta1 (%/°C) | p | beta2 | p | T* (°C anom) | In support |",
    "|---|---:|---:|---:|---:|---:|---|",
]
for _, r in quad_df.iterrows():
    lines.append(
        f"| `{r.outcome}` | {r.b1_pct_per_c:+.2f}% | {r.b1_p:.3g} | "
        f"{r.b2_quadratic:+.5f} | {r.b2_p:.3g} | "
        f"{r.turning_point_anom_c:+.1f} | "
        f"{'yes' if r.turning_point_in_support else 'no'} |"
    )

lines += [
    "",
    "## 7. Interpretation",
    "",
    "_Written by hand from the estimates above. No automated curve-shape "
    "classifier is used._",
    "",
    INTERPRETATION,
    "",
    "## 8. Caveats",
    "",
    CAVEATS,
    "",
    "## 9. Figures",
    "",
    "- `figures/fig12_crime_type_temperature_response_v2.png` — all cleaned "
    "categories with 95% CI.",
    "- `figures/fig13_interpersonal_vs_opportunity_v2.png` — interpersonal "
    "violence, robbery, and opportunity-based offenses.",
]

(RESULTS / "MECHANISM_FINDINGS_V2.md").write_text("\n".join(lines) + "\n",
                                                  encoding="utf-8")
print(summary_df.to_string(index=False))
print("\nheterogeneity (warm bins):")
print(het_df[het_df.bin.isin(["25_30", "30_35", "ge35"])]
      [["pair", "bin", "diff_coef", "p"]].to_string(index=False))
print("\ndone ->", RESULTS / "MECHANISM_FINDINGS_V2.md")
