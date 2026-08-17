# Mechanism-oriented crime-type findings (v2 taxonomy)

City-day sample: N = 5,113 (2010-01-01 → 2023-12-31).
Specification unchanged from the main temporal model: year-month FE, day-of-week FE, precipitation, HAC(14). Outcomes are `log(1 + daily count)`; bins are absolute daily TMAX with 20–25°C as the reference.

## 1. Cleaned category definitions

v2 changes relative to v1: vandalism and arson are removed from `theft`, burglary is split into structure vs vehicle, and vehicle theft is restricted to motor vehicles (bike/boat moved into general theft). The `violent`, `violent_ucr`, and `property` aggregates are unchanged, so results remain comparable to `main_models.csv`.

| Category | Codes | Incidents | Share of all crime | Sibling overlap |
|---|---:|---:|---:|---|
| `violent` | 32 | 928,072 | 30.8% | parent aggregate (nests subcategories) |
| `violent_ucr` | 15 | 340,555 | 11.3% | parent aggregate (nests subcategories) |
| `interpersonal` | 13 | 717,198 | 23.8% | none |
| `robbery` | 2 | 130,722 | 4.3% | none |
| `property` | 39 | 1,602,136 | 53.2% | parent aggregate (nests subcategories) |
| `theft` | 29 | 616,869 | 20.5% | none |
| `structure_burglary` | 2 | 218,211 | 7.2% | none |
| `vehicle_burglary` | 2 | 220,752 | 7.3% | none |
| `motor_vehicle_theft` | 3 | 263,188 | 8.7% | none |
| `vandalism` | 2 | 277,136 | 9.2% | none |
| `arson` | 1 | 5,980 | 0.2% | none |

Property subcategories partition the `property` aggregate exactly and are mutually disjoint (verified in `02_build.py`).

## 2. Sample counts by outcome

| Outcome | Mean daily count | Share of all crime | Significant bins |
|---|---:|---:|---|
| `violent` | 181.5 | 30.8% | sig@5%: <15-, 15–20-, 25–30+, 30–35+, ≥35+ |
| `violent_ucr` | 66.6 | 11.3% | sig@5%: <15-, 15–20-, 25–30+, 30–35+, ≥35+ |
| `interpersonal` | 140.3 | 23.8% | sig@5%: <15-, 15–20-, 25–30+, 30–35+, ≥35+ |
| `robbery` | 25.6 | 4.3% | sig@5%: <15-, 15–20-, 25–30+, 30–35+ |
| `property` | 313.3 | 53.2% | sig@5%: <15-, 25–30+ |
| `theft` | 120.6 | 20.5% | sig@5%: <15- |
| `structure_burglary` | 42.7 | 7.2% | sig@5%: none |
| `vehicle_burglary` | 43.2 | 7.3% | sig@5%: 25–30- |
| `motor_vehicle_theft` | 51.5 | 8.7% | sig@5%: 30–35-, ≥35- |
| `vandalism` | 54.2 | 9.2% | sig@5%: 15–20-, 25–30+, 30–35+, ≥35+ |
| `arson` | 1.2 | 0.2% | sig@5%: none |

## 3. Temperature-bin coefficients

Percentage effects are `100(exp(beta) - 1)` relative to the 20–25°C bin.

| Outcome | <15 | 15–20 | 25–30 | 30–35 | ≥35 |
|---|---|---|---|---|---|
| `violent` | -8.58%*** | -3.00%*** | +4.00%*** | +7.32%*** | +9.68%*** |
| `violent_ucr` | -9.50%*** | -4.20%*** | +4.18%*** | +6.30%*** | +5.76%* |
| `interpersonal` | -8.22%*** | -3.03%*** | +4.03%*** | +8.30%*** | +11.82%*** |
| `robbery` | -9.38%*** | -4.07%*** | +2.83%** | +4.56%* | +2.87% |
| `property` | -2.24%* | -0.23% | +0.85%* | -0.22% | -0.45% |
| `theft` | -3.70%* | -0.67% | +0.75% | +0.55% | -0.18% |
| `structure_burglary` | -0.74% | +0.94% | +1.48% | -2.31% | +0.23% |
| `vehicle_burglary` | -2.91% | +1.34% | -1.43%* | -2.14% | -3.85% |
| `motor_vehicle_theft` | -1.50% | -0.15% | +0.80% | -3.04%* | -8.40%* |
| `vandalism` | -1.64% | -1.91%** | +2.28%** | +4.18%** | +8.38%*** |
| `arson` | -5.18% | -2.67% | +1.85% | +5.22% | +11.12% |

`*` p<0.05, `**` p<0.01, `***` p<0.001. Full estimates with standard errors: `crime_type_temperature_bins_v2.csv`; BH-FDR supplement: `crime_type_temperature_bins_fdr.csv`.

## 4. Extreme-heat thresholds

| Threshold | Cutoff | Basis | Days in 2010–2023 |
|---|---:|---|---:|
| `hot35` | 35.0°C | absolute | 26 |
| `hot_p95` | 28.9°C | P95 of TMAX in 2010-2023 crime sample | 286 |
| `hot_p95_clim` | 28.3°C | P95 of TMAX in 1991-2020 normals (10,958 station-days) | 356 |

The climatological threshold `hot_p95_clim` is the 95th percentile of LAX TMAX over 1991–2020, held fixed and then applied to the crime period, so the cutoff does not depend on the crime sample.

| Outcome | hot35 | hot_p95 (sample) | hot_p95_clim |
|---|---:|---:|---:|
| `violent` | +7.75%*** | +6.04%*** | +6.29%*** |
| `violent_ucr` | +4.10% | +5.88%*** | +5.61%*** |
| `interpersonal` | +9.71%*** | +6.79%*** | +6.96%*** |
| `robbery` | +1.85% | +4.85%*** | +5.16%*** |
| `property` | -0.65% | -0.63% | -0.68% |
| `theft` | -0.40% | +0.16% | +0.35% |
| `structure_burglary` | +0.02% | -2.76%* | -2.52%* |
| `vehicle_burglary` | -3.30% | -3.37%** | -3.77%*** |
| `motor_vehicle_theft` | -8.22%* | -2.78%** | -2.65%** |
| `vandalism` | +7.29%** | +3.75%*** | +2.73%** |
| `arson` | +10.08% | +5.87% | +5.93% |

## 5. Planned heterogeneity tests

Each test regresses the daily log-outcome difference `D_t = log(1 + A_t) - log(1 + B_t)` on the same bins, controls, and fixed effects, which preserves same-day covariance between the two outcomes. A positive coefficient means outcome A responds more positively than outcome B in that bin.

| Pair | <15 | 15–20 | 25–30 | 30–35 | ≥35 |
|---|---|---|---|---|---|
| `interpersonal` − `property` | -0.0631*** | -0.0284*** | +0.0310*** | +0.0819*** | +0.1163*** |
| `interpersonal` − `motor_vehicle_theft` | -0.0707** | -0.0293*** | +0.0316*** | +0.1107*** | +0.1995*** |
| `interpersonal` − `structure_burglary` | -0.0783** | -0.0401*** | +0.0248* | +0.1031*** | +0.1095*** |
| `interpersonal` − `robbery` | +0.0127 | +0.0107 | +0.0116 | +0.0352 | +0.0835 |

Full estimates: `crime_type_heterogeneity_tests.csv`.

## 6. Quadratic summary (compact robustness only)

The quadratic uses temperature *anomaly*, not absolute TMAX. `T*` is the implied turning point in anomaly units; `in support` indicates whether it falls inside the observed anomaly range [-7.0, 11.3]°C.

| Outcome | beta1 (%/°C) | p | beta2 | p | T* (°C anom) | In support |
|---|---:|---:|---:|---:|---:|---|
| `violent` | +1.55% | 1.06e-53 | -0.00041 | 0.0187 | +18.5 | no |
| `violent_ucr` | +1.60% | 3.14e-26 | -0.00065 | 0.0162 | +12.3 | no |
| `interpersonal` | +1.64% | 2.05e-54 | -0.00036 | 0.0556 | +22.4 | no |
| `robbery` | +1.36% | 5.84e-16 | -0.00077 | 0.021 | +8.8 | yes |
| `property` | +0.29% | 0.000281 | -0.00040 | 0.00382 | +3.6 | yes |
| `theft` | +0.35% | 0.00518 | -0.00028 | 0.173 | +6.1 | yes |
| `structure_burglary` | +0.10% | 0.505 | -0.00054 | 0.0527 | +0.9 | yes |
| `vehicle_burglary` | -0.08% | 0.63 | -0.00074 | 0.0274 | -0.5 | yes |
| `motor_vehicle_theft` | +0.21% | 0.0808 | -0.00085 | 0.00141 | +1.2 | yes |
| `vandalism` | +0.71% | 3.03e-06 | +0.00005 | 0.851 | -70.6 | no |
| `arson` | +1.03% | 0.0134 | +0.00076 | 0.317 | -6.8 | yes |

## 7. Interpretation

_Written by hand from the estimates above. No automated curve-shape classifier is used._

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

## 8. Caveats

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

## 9. Figures

- `figures/fig12_crime_type_temperature_response_v2.png` — all cleaned categories with 95% CI.
- `figures/fig13_interpersonal_vs_opportunity_v2.png` — interpersonal violence, robbery, and opportunity-based offenses.
