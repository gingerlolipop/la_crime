#!/usr/bin/env python3
"""Preferred models + temporal robustness + placebos + distributed lags."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from config import *

RESULTS.mkdir(exist_ok=True)
FIG = RESULTS / "figures"
FIG.mkdir(exist_ok=True)
d = pd.read_csv(OUT / "daily.csv", parse_dates=["date"])
m = pd.read_csv(OUT / "monthly.csv", parse_dates=["date"])
OUTCOMES = ["total", "violent", "violent_ucr", "property"]


def hac(formula, data, lag=14):
    return smf.ols(formula, data=data).fit(
        cov_type="HAC", cov_kwds={"maxlags": lag})


def pct(beta):
    return 100 * (np.exp(beta) - 1)


# ---------------------------------------------------------------------------
# 1) Main anomaly model
# ---------------------------------------------------------------------------
rows = []
for y in OUTCOMES:
    x = d.copy()
    x["ly"] = np.log1p(x[y])
    fit = hac("ly ~ temp_anom + I(temp_anom**2) + PRCP + C(ym) + C(dow)", x, 14)
    for term in ["temp_anom", "I(temp_anom ** 2)"]:
        rows.append([y, term, fit.params[term], fit.bse[term],
                     fit.pvalues[term], fit.nobs, pct(fit.params[term])])
pd.DataFrame(rows, columns=["outcome", "term", "coef", "se", "p", "n", "pct"]).to_csv(
    RESULTS / "main_models.csv", index=False)

# ---------------------------------------------------------------------------
# 2) Temperature bins
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
bins = pd.DataFrame(bins, columns=["outcome", "bin", "coef", "se", "p", "pct"])
bins.to_csv(RESULTS / "temperature_bins.csv", index=False)

# ---------------------------------------------------------------------------
# 3) Extreme heat indicators
# ---------------------------------------------------------------------------
hot = []
for y in OUTCOMES:
    for v in ["hot30", "hot32", "hot35"]:
        x = d.copy()
        x["ly"] = np.log1p(x[y])
        fit = hac(f"ly ~ {v} + PRCP + C(ym) + C(dow)", x, 14)
        hot.append([y, v, fit.params[v], fit.bse[v], fit.pvalues[v],
                    pct(fit.params[v]), fit.nobs])
hot = pd.DataFrame(hot, columns=["outcome", "threshold", "coef", "se", "p", "pct", "n"])
hot.to_csv(RESULTS / "extreme_heat.csv", index=False)

# ---------------------------------------------------------------------------
# 4) Multi-lead placebos (total + violent)
# ---------------------------------------------------------------------------
placebo_rows = []
for y in ["total", "violent"]:
    x = d.copy()
    x["ly"] = np.log1p(x[y])
    for lead in [7, 14, 21, 28]:
        col = f"future_temp{lead}"
        x[col] = x["temp_anom"].shift(-lead)
        fit = hac(f"ly ~ {col} + PRCP + C(ym) + C(dow)", x.dropna(subset=[col]), 14)
        placebo_rows.append([y, lead, fit.params[col], fit.bse[col],
                             fit.pvalues[col], fit.nobs])
placebo = pd.DataFrame(placebo_rows, columns=["outcome", "lead_days", "coef", "se", "p", "n"])
placebo.to_csv(RESULTS / "placebo.csv", index=False)

# ---------------------------------------------------------------------------
# 5) Temporal robustness for violent ~ hot35 and violent ~ temp_anom
# ---------------------------------------------------------------------------
samples = {
    "2010_2019": d["year"].between(2010, 2019),
    "2010_2023": d["year"].between(2010, 2023),
    "excl_2020_2021": ~d["year"].isin([2020, 2021]),
    "2022_2023": d["year"].between(2022, 2023),
}
rob = []
for name, mask in samples.items():
    sub = d.loc[mask].copy()
    if len(sub) < 100:
        continue
    for y in ["violent", "violent_ucr", "total", "property"]:
        sub["ly"] = np.log1p(sub[y])
        fit_h = hac("ly ~ hot35 + PRCP + C(ym) + C(dow)", sub, 14)
        fit_a = hac("ly ~ temp_anom + I(temp_anom**2) + PRCP + C(ym) + C(dow)", sub, 14)
        rob.append([name, y, "hot35", fit_h.params["hot35"], fit_h.bse["hot35"],
                    fit_h.pvalues["hot35"], pct(fit_h.params["hot35"]), fit_h.nobs,
                    int(sub["hot35"].sum())])
        rob.append([name, y, "temp_anom", fit_a.params["temp_anom"], fit_a.bse["temp_anom"],
                    fit_a.pvalues["temp_anom"], pct(fit_a.params["temp_anom"]),
                    fit_a.nobs, np.nan])
rob = pd.DataFrame(rob, columns=[
    "sample", "outcome", "term", "coef", "se", "p", "pct", "n", "n_hot35_days"])
rob.to_csv(RESULTS / "temporal_robustness.csv", index=False)

# ---------------------------------------------------------------------------
# 6) Distributed lags of hot35 on violent (L=7)
# ---------------------------------------------------------------------------
x = d.copy()
x["ly"] = np.log1p(x["violent"])
parts = []
for ell in range(0, 8):
    x[f"hot35_l{ell}"] = x["hot35"].shift(ell)
    parts.append(f"hot35_l{ell}")
fit = hac(
    "ly ~ " + " + ".join(parts) + " + PRCP + C(ym) + C(dow)",
    x.dropna(subset=parts), 14)
lag_rows = [[ell, fit.params[f"hot35_l{ell}"], fit.bse[f"hot35_l{ell}"],
             fit.pvalues[f"hot35_l{ell}"], pct(fit.params[f"hot35_l{ell}"])]
            for ell in range(0, 8)]
lags = pd.DataFrame(lag_rows, columns=["lag", "coef", "se", "p", "pct"])
lags.to_csv(RESULTS / "distributed_lags_hot35_violent.csv", index=False)

# ---------------------------------------------------------------------------
# 7) ONI first stage (secondary)
# ---------------------------------------------------------------------------
def first_stage(data, sample):
    data = data.dropna(subset=["oni", "oni_l1", "oni_l2", "temp_anom"]).copy()
    short = hac("temp_anom ~ oni + C(month) + trend", data, 6)
    full = hac("temp_anom ~ oni + oni_l1 + oni_l2 + C(month) + trend", data, 6)
    restricted = smf.ols("temp_anom ~ C(month) + trend", data=data).fit()
    unrobust = smf.ols(
        "temp_anom ~ oni + oni_l1 + oni_l2 + C(month) + trend", data=data).fit()
    partial_r2 = 1 - unrobust.ssr / restricted.ssr
    terms = ["oni", "oni_l1", "oni_l2"]
    R = np.zeros((3, len(full.params)))
    for i, term in enumerate(terms):
        R[i, list(full.params.index).index(term)] = 1
    test = full.wald_test(R, use_f=True, scalar=True)
    out = [[sample, "oni_only", "oni", short.params["oni"], short.bse["oni"],
            short.pvalues["oni"], np.nan, np.nan, len(data)]]
    out += [[sample, "distributed", term, full.params[term], full.bse[term],
             full.pvalues[term], partial_r2, float(test.statistic), len(data)]
            for term in terms]
    return out


fs = first_stage(m, "all_months")
fs += first_stage(m[m["month"].isin([11, 12, 1, 2, 3])], "nov_mar")
fs = pd.DataFrame(fs, columns=[
    "sample", "model", "term", "coef", "se", "p", "partial_r2", "joint_F", "n"])
fs.to_csv(RESULTS / "oni_first_stage.csv", index=False)

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
q = d.assign(temp_q=pd.qcut(d["tmean"], 20, duplicates="drop")).groupby(
    "temp_q", observed=True).agg(temp=("tmean", "mean"), crime=("violent", "mean")).reset_index()
plt.figure(figsize=(7, 4.5))
plt.plot(q["temp"], q["crime"], marker="o")
plt.xlabel("Daily mean temperature (°C)")
plt.ylabel("Mean daily violent crime")
plt.tight_layout()
plt.savefig(FIG / "fig1_temperature_crime.png", dpi=200)
plt.close()

b = bins[bins.outcome == "violent"].copy()
b["label"] = b["bin"].str.extract(r"\[T\.(.*)\]")[0]
plt.figure(figsize=(7, 4.5))
x = np.arange(len(b))
plt.errorbar(x, b.coef, yerr=1.96 * b.se, fmt="o", capsize=4)
plt.axhline(0, lw=1)
plt.xticks(x, b.label, rotation=30)
plt.ylabel("Violent-crime coef vs 20–25°C")
plt.tight_layout()
plt.savefig(FIG / "fig2_temperature_bins.png", dpi=200)
plt.close()

h = hot[hot.outcome.isin(["violent", "property", "total"])]
plt.figure(figsize=(7, 4.5))
for y, g in h.groupby("outcome"):
    xx = g["threshold"].str.extract(r"(\d+)")[0].astype(int)
    plt.plot(xx, g["coef"], marker="o", label=y)
plt.axhline(0, lw=1)
plt.xlabel("TMAX threshold (°C)")
plt.ylabel("log(1+crime) coefficient")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "fig3_extreme_heat.png", dpi=200)
plt.close()

# Placebo leads figure (violent)
pv = placebo[placebo.outcome == "violent"]
plt.figure(figsize=(7, 4.5))
plt.errorbar(pv.lead_days, pv.coef, yerr=1.96 * pv.se, fmt="o", capsize=4)
plt.axhline(0, lw=1)
plt.xlabel("Lead (days)")
plt.ylabel("Violent-crime coef on future temp anomaly")
plt.tight_layout()
plt.savefig(FIG / "fig6_placebo_leads.png", dpi=200)
plt.close()

# Distributed lags figure
plt.figure(figsize=(7, 4.5))
plt.errorbar(lags.lag, lags.coef, yerr=1.96 * lags.se, fmt="o", capsize=4)
plt.axhline(0, lw=1)
plt.xlabel("Lag of hot35 (days)")
plt.ylabel("Violent-crime coefficient")
plt.tight_layout()
plt.savefig(FIG / "fig7_distributed_lags.png", dpi=200)
plt.close()

z = m.dropna(subset=["oni", "temp_anom"])
plt.figure(figsize=(9, 4.5))
plt.plot(z.date, (z.oni - z.oni.mean()) / z.oni.std(), label="ONI")
plt.plot(z.date, (z.temp_anom - z.temp_anom.mean()) / z.temp_anom.std(),
         label="LA temp anomaly")
plt.axhline(0, lw=1)
plt.ylabel("Standard deviations")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "fig4_oni_temperature.png", dpi=200)
plt.close()

plt.figure(figsize=(7, 4.5))
plt.scatter(z.oni, z.temp_anom, s=18, alpha=.6)
coef = np.polyfit(z.oni, z.temp_anom, 1)
xx = np.linspace(z.oni.min(), z.oni.max(), 100)
plt.plot(xx, coef[0] * xx + coef[1])
plt.xlabel("ONI")
plt.ylabel("Monthly temp anomaly (°C)")
plt.tight_layout()
plt.savefig(FIG / "fig5_oni_first_stage.png", dpi=200)
plt.close()

# ---------------------------------------------------------------------------
# Summary markdown
# ---------------------------------------------------------------------------
main = pd.read_csv(RESULTS / "main_models.csv")
pl = placebo[(placebo.outcome == "violent") & (placebo.lead_days == 7)].iloc[0]
eh = hot[(hot.outcome == "violent") & (hot.threshold == "hot35")].iloc[0]
lines = [
    "# Full-sample results summary",
    "",
    f"Daily N = {len(d):,} ({d.date.min().date()} → {d.date.max().date()})",
    "",
    "## Main anomaly model (temp_anom)",
    "",
]
for _, r in main[main.term == "temp_anom"].iterrows():
    lines.append(
        f"- {r.outcome}: beta={r.coef:.4f}, SE={r.se:.4f}, p={r.p:.4g}, "
        f"approx {r.pct:.2f}% per +1°C"
    )
lines += [
    "",
    "## Extreme heat ≥35°C (violent)",
    "",
    f"- beta={eh.coef:.4f}, SE={eh.se:.4f}, p={eh.p:.4g}, approx {eh.pct:.2f}%",
    "",
    "## Placebo lead +7 (violent)",
    "",
    f"- beta={pl.coef:.4f}, SE={pl.se:.4f}, p={pl.p:.4g}",
    "",
    "## ONI first stage",
    "",
]
for sample in ["all_months", "nov_mar"]:
    g = fs[(fs["sample"] == sample) & (fs["model"] == "distributed")]
    if len(g):
        r = g.iloc[0]
        lines.append(
            f"- {sample}: partial R²={r.partial_r2:.4f}; joint F={r.joint_F:.3f}; N={int(r.n)}"
        )
lines += [
    "",
    "**Crime categories use LAPD Crm Cd crosswalk (see crime_classification_audit.csv).**",
    "**ONI results are first-stage diagnostics only; not a causal IV estimate.**",
]
(RESULTS / "RESULTS_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
print("done ->", RESULTS)
