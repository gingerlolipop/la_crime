#!/usr/bin/env python3
"""Spatial area × day FE analysis and LAX comparison."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from config import *

RESULTS.mkdir(exist_ok=True)
FIG = RESULTS / "figures"
FIG.mkdir(exist_ok=True)

panel = pd.read_csv(OUT / "area_daily_crime_weather.csv", parse_dates=["date"])
lax_daily = pd.read_csv(OUT / "daily.csv", parse_dates=["date"])
OUTCOMES = ["violent", "violent_ucr", "property", "total"]


def twoway_demean(df, cols, i="AREA", t="date"):
    out = df[cols].copy()
    for c in cols:
        out[c] = (
            df[c]
            - df.groupby(i)[c].transform("mean")
            - df.groupby(t)[c].transform("mean")
            + df[c].mean()
        )
    return out


def cluster_ols(y, X, groups):
    """OLS with cluster-robust SE by groups (LAPD area)."""
    model = sm.OLS(y, X, hasconst=False).fit()
    return model.get_robustcov_results(cov_type="cluster", groups=groups)


def fit_spatial(df, yname, xnames):
    use = df.dropna(subset=[yname] + xnames).copy()
    use["ly"] = np.log1p(use[yname])
    cols = ["ly"] + xnames
    dem = twoway_demean(use, cols)
    y = dem["ly"].to_numpy()
    X = dem[xnames].to_numpy()
    # drop collinear / zero-variance cols after demeaning
    keep = []
    for j, name in enumerate(xnames):
        if np.nanstd(X[:, j]) > 1e-12:
            keep.append(j)
    X = X[:, keep]
    names = [xnames[j] for j in keep]
    res = cluster_ols(y, X, use["AREA"].to_numpy())
    rows = []
    for j, name in enumerate(names):
        rows.append({
            "outcome": yname,
            "term": name,
            "coef": float(res.params[j]),
            "se": float(res.bse[j]),
            "p": float(res.pvalues[j]),
            "pct": float(100 * (np.exp(res.params[j]) - 1)),
            "n": int(res.nobs),
            "n_areas": int(use["AREA"].nunique()),
            "cluster": "AREA",
            "fe": "area + date",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Support diagnostics
# ---------------------------------------------------------------------------
ok = panel.dropna(subset=["TMAX"]).copy()
support = {
    "n_areas": int(panel["AREA"].nunique()),
    "n_area_days": int(len(panel)),
    "n_area_days_with_weather": int(len(ok)),
    "date_min": str(panel["date"].min().date()),
    "date_max": str(panel["date"].max().date()),
    "missing_weather_share": float(panel["TMAX"].isna().mean()),
    "n_hot30": int(ok["hot30"].sum()),
    "n_hot32": int(ok["hot32"].sum()),
    "n_hot35": int(ok["hot35"].sum()),
    "share_hot30": float(ok["hot30"].mean()),
    "share_hot32": float(ok["hot32"].mean()),
    "share_hot35": float(ok["hot35"].mean()),
    "mean_tmax_minus_lax": float(ok["tmax_minus_lax"].mean()),
    "mean_abs_tmax_minus_lax": float(ok["tmax_minus_lax"].abs().mean()),
}
pd.DataFrame([support]).to_csv(RESULTS / "spatial_support.csv", index=False)

hot_by_area = (
    ok.groupby(["AREA", "AREA NAME"], as_index=False)
    .agg(n_hot35=("hot35", "sum"), mean_tmax=("TMAX", "mean"),
         mean_tmax_minus_lax=("tmax_minus_lax", "mean"),
         mean_violent=("violent", "mean"))
    .sort_values("AREA")
)
hot_by_area.to_csv(RESULTS / "spatial_hot35_by_area.csv", index=False)

hot_by_year = (
    ok.groupby("year", as_index=False)
    .agg(n_hot35=("hot35", "sum"), n_area_days=("date", "size"))
)
hot_by_year.to_csv(RESULTS / "spatial_hot35_by_year.csv", index=False)
print("support:", support)
print(hot_by_area.to_string(index=False))

# ---------------------------------------------------------------------------
# Spatial regressions
# ---------------------------------------------------------------------------
ok = ok.copy()
ok["temp_anom_sq"] = ok["temp_anom"] ** 2
ok["prcp"] = ok["PRCP"].fillna(0)
for v in ["hot30", "hot32", "hot35"]:
    ok[v] = ok[v].astype(float)

main = pd.concat(
    [fit_spatial(ok, y, ["temp_anom", "temp_anom_sq", "prcp"]) for y in OUTCOMES],
    ignore_index=True,
)
main.to_csv(RESULTS / "spatial_main_models.csv", index=False)

# Temperature bins (drop reference 20_25)
bins_out = []
dummies = pd.get_dummies(ok["tmax_bin"], prefix="bin")
# ensure all expected cols
for lab in ["lt15", "15_20", "25_30", "30_35", "ge35"]:
    col = f"bin_{lab}"
    if col not in dummies.columns:
        dummies[col] = 0
xbin = ["bin_lt15", "bin_15_20", "bin_25_30", "bin_30_35", "bin_ge35", "prcp"]
tmp = pd.concat([ok.reset_index(drop=True), dummies.reset_index(drop=True)], axis=1)
for y in OUTCOMES:
    bins_out.append(fit_spatial(tmp, y, xbin))
bins = pd.concat(bins_out, ignore_index=True)
bins.to_csv(RESULTS / "spatial_temperature_bins.csv", index=False)

# Extreme heat
hot = pd.concat(
    [fit_spatial(ok, y, [v, "prcp"]) for y in OUTCOMES for v in ["hot30", "hot32", "hot35"]],
    ignore_index=True,
)
hot.to_csv(RESULTS / "spatial_extreme_heat.csv", index=False)

# ---------------------------------------------------------------------------
# LAX city-level comparison (same outcomes, old FE structure via HAC)
# ---------------------------------------------------------------------------
import statsmodels.formula.api as smf


def hac(formula, data, lag=14):
    return smf.ols(formula, data=data).fit(cov_type="HAC", cov_kwds={"maxlags": lag})


cmp_rows = []
for y in OUTCOMES:
    x = lax_daily.copy()
    x["ly"] = np.log1p(x[y])
    fit_a = hac("ly ~ temp_anom + I(temp_anom**2) + PRCP + C(ym) + C(dow)", x, 14)
    fit_h = hac("ly ~ hot35 + PRCP + C(ym) + C(dow)", x, 14)
    sp_a = main[(main.outcome == y) & (main.term == "temp_anom")].iloc[0]
    sp_h = hot[(hot.outcome == y) & (hot.term == "hot35")].iloc[0]
    cmp_rows += [
        {"design": "LAX city-level", "outcome": y, "term": "temp_anom",
         "coef": float(fit_a.params["temp_anom"]), "se": float(fit_a.bse["temp_anom"]),
         "p": float(fit_a.pvalues["temp_anom"]),
         "pct": float(100 * (np.exp(fit_a.params["temp_anom"]) - 1)),
         "fe": "year-month + DOW", "cluster_or_hac": "HAC-14"},
        {"design": "Spatial area×day", "outcome": y, "term": "temp_anom",
         "coef": sp_a.coef, "se": sp_a.se, "p": sp_a.p, "pct": sp_a.pct,
         "fe": "area + date", "cluster_or_hac": "cluster AREA"},
        {"design": "LAX city-level", "outcome": y, "term": "hot35",
         "coef": float(fit_h.params["hot35"]), "se": float(fit_h.bse["hot35"]),
         "p": float(fit_h.pvalues["hot35"]),
         "pct": float(100 * (np.exp(fit_h.params["hot35"]) - 1)),
         "fe": "year-month + DOW", "cluster_or_hac": "HAC-14"},
        {"design": "Spatial area×day", "outcome": y, "term": "hot35",
         "coef": sp_h.coef, "se": sp_h.se, "p": sp_h.p, "pct": sp_h.pct,
         "fe": "area + date", "cluster_or_hac": "cluster AREA"},
    ]
cmp = pd.DataFrame(cmp_rows)
cmp.to_csv(RESULTS / "lax_vs_spatial.csv", index=False)

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
# Fig 8: local minus LAX TMAX by area
plt.figure(figsize=(9, 4.8))
g = hot_by_area.sort_values("mean_tmax_minus_lax")
plt.barh(g["AREA NAME"], g["mean_tmax_minus_lax"], color="#c45c26")
plt.axvline(0, color="k", lw=1)
plt.xlabel("Mean local TMAX − LAX TMAX (°C)")
plt.tight_layout()
plt.savefig(FIG / "fig8_spatial_temperature_support.png", dpi=200)
plt.close()

# Fig 9: spatial temperature bins for violent
order = ["bin_lt15", "bin_15_20", "bin_25_30", "bin_30_35", "bin_ge35"]
b = bins[(bins.outcome == "violent") & bins.term.isin(order)].copy()
b["term"] = pd.Categorical(b["term"], categories=order, ordered=True)
b = b.sort_values("term")
labels = ["<15", "15–20", "25–30", "30–35", "≥35"]
plt.figure(figsize=(7, 4.5))
x = np.arange(len(b))
plt.errorbar(x, b.coef, yerr=1.96 * b.se, fmt="o", capsize=4, color="#1b4332")
plt.axhline(0, lw=1)
plt.xticks(x, labels)
plt.ylabel("Violent coef vs 20–25°C (area+date FE)")
plt.tight_layout()
plt.savefig(FIG / "fig9_spatial_temperature_bins_violent.png", dpi=200)
plt.close()

# Fig 10: crime-type comparison on temp_anom
c = main[main.term == "temp_anom"].copy()
c["outcome"] = pd.Categorical(c["outcome"], OUTCOMES)
c = c.sort_values("outcome")
plt.figure(figsize=(7, 4.5))
x = np.arange(len(c))
plt.errorbar(x, c.coef, yerr=1.96 * c.se, fmt="o", capsize=4)
plt.axhline(0, lw=1)
plt.xticks(x, c.outcome)
plt.ylabel("Spatial temp_anom coefficient")
plt.tight_layout()
plt.savefig(FIG / "fig10_spatial_crime_type_comparison.png", dpi=200)
plt.close()

# Fig 11: LAX vs spatial for violent
v = cmp[(cmp.outcome == "violent") & (cmp.term.isin(["temp_anom", "hot35"]))]
plt.figure(figsize=(7.5, 4.5))
terms = ["temp_anom", "hot35"]
xpos = np.arange(len(terms))
for i, design in enumerate(["LAX city-level", "Spatial area×day"]):
    g = v[v.design == design].set_index("term").loc[terms]
    plt.errorbar(xpos + (i - 0.5) * 0.2, g.coef, yerr=1.96 * g.se,
                 fmt="o", capsize=4, label=design)
plt.axhline(0, lw=1)
plt.xticks(xpos, ["temp_anom", "hot35"])
plt.ylabel("Violent-crime coefficient")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "fig11_lax_vs_spatial.png", dpi=200)
plt.close()

# ---------------------------------------------------------------------------
# Findings note
# ---------------------------------------------------------------------------
va = main[(main.outcome == "violent") & (main.term == "temp_anom")].iloc[0]
vu = main[(main.outcome == "violent_ucr") & (main.term == "temp_anom")].iloc[0]
pa = main[(main.outcome == "property") & (main.term == "temp_anom")].iloc[0]
vh = hot[(hot.outcome == "violent") & (hot.term == "hot35")].iloc[0]
lax_va = cmp[(cmp.design == "LAX city-level") & (cmp.outcome == "violent")
             & (cmp.term == "temp_anom")].iloc[0]
lax_vh = cmp[(cmp.design == "LAX city-level") & (cmp.outcome == "violent")
             & (cmp.term == "hot35")].iloc[0]

lines = f"""# Spatial Weather Findings

## Data source
- Weather: NOAA GHCN-Daily multi-station extract (`stations/weather_multi.csv`)
- Matching: nearest station to LAPD area centroid (crime LAT/LON median)
- Crime: offense-code categories from `offense_codes.py`
- Panel: LAPD area × date, 2010–2023

## Support
- Areas: {support['n_areas']}
- Area-days: {support['n_area_days']:,}
- With weather: {support['n_area_days_with_weather']:,}
- Missing weather share: {support['missing_weather_share']:.4f}
- hot30 / hot32 / hot35 area-days: {support['n_hot30']:,} / {support['n_hot32']:,} / {support['n_hot35']:,}
- hot35 share: {support['share_hot35']:.4f}
- Mean local TMAX − LAX TMAX: {support['mean_tmax_minus_lax']:.2f}°C

## Preferred spatial model
`log(1+Crime_it) ~ f(Temp_it) + area FE + date FE`, cluster SE by AREA.

### Continuous anomaly (temp_anom)
- violent: beta={va.coef:.4f}, SE={va.se:.4f}, p={va.p:.4g}, approx {va.pct:.2f}%
- violent_ucr: beta={vu.coef:.4f}, SE={vu.se:.4f}, p={vu.p:.4g}, approx {vu.pct:.2f}%
- property: beta={pa.coef:.4f}, SE={pa.se:.4f}, p={pa.p:.4g}, approx {pa.pct:.2f}%

### Extreme heat (hot35)
- violent: beta={vh.coef:.4f}, SE={vh.se:.4f}, p={vh.p:.4g}, approx {vh.pct:.2f}%

## LAX vs spatial (violent)
| Design | temp_anom | hot35 |
|---|---:|---:|
| LAX city-level | {lax_va.coef:.4f} (p={lax_va.p:.3g}) | {lax_vh.coef:.4f} (p={lax_vh.p:.3g}) |
| Spatial area+date FE | {va.coef:.4f} (p={va.p:.3g}) | {vh.coef:.4f} (p={vh.p:.3g}) |

## Clustering / FE
- Spatial: area + date two-way FE; cluster-robust SE by LAPD AREA
- LAX comparison: year-month + DOW FE; HAC(14)

## Warning
- Station assignment is nearest-neighbor to area centroids derived from crime coordinates (approximation to official polygons).
- Extreme-heat support is still sparse relative to continuous anomaly variation; interpret hot35 carefully.
- Placebo / ENSO analyses were not re-run in this spatial round.
"""
(RESULTS / "SPATIAL_WEATHER_FINDINGS.md").write_text(lines, encoding="utf-8")
print(lines)
print("done ->", RESULTS)
