# Full-Sample Findings and Recommended Next Steps
## LA Temperature, Crime, and ENSO Project

**Status:** Full 2010–2023 panel successfully rebuilt and analyzed.
**Daily sample:** 5,113 days.
**Monthly sample:** 168 months.
**Main takeaway:** The full sample substantially changes the pilot story. The strongest and most coherent result is now **heat → violent crime**, while property crime shows little response. The ENSO/ONI route looks weak as a practical LA-only IV strategy.

---

# 1. Data-range issue is resolved

The earlier pilot accidentally used only 2010–2012. That truncation has now been fixed.

Current ranges:

| Source | Range | Status |
|---|---|---|
| LAPD Crime 2010–2019 | 2010-01-01 → 2019-12-31 | OK |
| LAPD Crime 2020–2024 | 2020-01-01 → 2024-12-30 | OK |
| NOAA weather | 1991-01-01 → 2023-12-31 | OK |
| ONI | 1950 → 2026 | OK |
| `daily.csv` | 2010-01-01 → 2023-12-31 | **N = 5,113** |
| `monthly.csv` | 2010–2023 | **N = 168** |

The full-sample results should therefore replace all substantive interpretations from the earlier 2010–2012 debugging run.

---

# 2. Main anomaly model: heat is associated with total and violent crime, not property crime

The main model is:

\[
\log(1+Y_t)
=
\beta_1 TempAnom_t
+
\beta_2 TempAnom_t^2
+
\gamma PRCP_t
+
\lambda_{ym(t)}
+
\delta_{dow(t)}
+
\varepsilon_t
\]

where:

- \(Y_t\) = daily crime count;
- \(TempAnom_t\) = temperature anomaly relative to the 1991–2020 monthly normal;
- \(TempAnom_t^2\) = quadratic temperature-anomaly term;
- \(PRCP_t\) = precipitation;
- \(\lambda_{ym(t)}\) = year-month fixed effects;
- \(\delta_{dow(t)}\) = day-of-week fixed effects;
- \(\varepsilon_t\) = error term.

HAC/Newey–West standard errors are used.

## Linear anomaly term

| Outcome | Coefficient | SE | p-value | Approximate effect per +1°C anomaly |
|---|---:|---:|---:|---:|
| Total crime | 0.006265 | 0.001019 | \(7.7\times10^{-10}\) | **+0.63%** |
| Violent crime proxy | 0.015600 | 0.001024 | \(2.2\times10^{-52}\) | **+1.57%** |
| Property crime proxy | 0.001447 | 0.001155 | 0.210 | +0.14%, not significant |

Approximate percentage effects use:

\[
100(e^\beta-1).
\]

## Interpretation

The clearest heterogeneity is:

\[
Temperature \uparrow
\quad\Rightarrow\quad
\begin{cases}
ViolentCrime & \uparrow\uparrow\\
TotalCrime & \uparrow\\
PropertyCrime & \approx 0
\end{cases}
\]

This is now more compelling than the earlier “extreme heat increases all crime” interpretation.

The violent-crime coefficient is roughly 2.5 times the total-crime coefficient, while property crime is statistically indistinguishable from zero.

---

# 3. Nonlinearity: the temperature-bin results show a strong dose-response for violent crime

The temperature-bin model uses **20–25°C TMAX as the reference category**.

For a log outcome, the approximate percentage effect is:

\[
100(e^{\beta_k}-1).
\]

## Full-sample coefficients

| TMAX bin | Total | Violent | Property |
|---|---:|---:|---:|
| <15°C | -0.0401, p=0.008 | **-0.0868, p<10⁻⁹** | -0.0160, p=0.332 |
| 15–20°C | -0.0050, p=0.305 | **-0.0339, p<10⁻¹¹** | +0.0067, p=0.223 |
| 20–25°C | reference | reference | reference |
| 25–30°C | **+0.0195, p<0.001** | **+0.0386, p<10⁻¹⁵** | +0.0067, p=0.220 |
| 30–35°C | **+0.0256, p=0.006** | **+0.0724, p<10⁻¹⁴** | +0.0006, p=0.958 |
| ≥35°C | **+0.0365, p=0.009** | **+0.0930, p<10⁻¹²** | +0.0069, p=0.668 |

Approximate violent-crime percentage differences relative to 20–25°C are:

- <15°C: about **−8.3%**
- 15–20°C: about **−3.3%**
- 25–30°C: about **+3.9%**
- 30–35°C: about **+7.5%**
- ≥35°C: about **+9.7%**

## Why this matters

The violent-crime response is strikingly ordered:

\[
<15
\rightarrow
15\!-\!20
\rightarrow
20\!-\!25
\rightarrow
25\!-\!30
\rightarrow
30\!-\!35
\rightarrow
\ge35^\circ C
\]

with the coefficient moving monotonically from negative values in cool bins to increasingly positive values in hot bins.

This pattern is more informative than a single arbitrary threshold because it resembles a **dose-response relationship**.

By contrast, property crime is essentially flat across the same temperature bins.

---

# 4. Extreme-heat indicator models tell the same violent-crime story

Separate regressions use indicators for:

\[
Hot30_t = 1(TMAX_t\ge30^\circ C)
\]

\[
Hot32_t = 1(TMAX_t\ge32^\circ C)
\]

\[
Hot35_t = 1(TMAX_t\ge35^\circ C)
\]

## Results

| Outcome | ≥30°C | ≥32°C | ≥35°C |
|---|---:|---:|---:|
| Total | 0.0215, p=0.0055 | 0.0297, p=0.0060 | 0.0279, p=0.064 |
| Violent | **0.0679, p<10⁻¹⁵** | **0.0713, p<10⁻⁶** | **0.0755, p<10⁻⁶** |
| Property | -0.0017, p=0.858 | 0.0102, p=0.362 | 0.0043, p=0.798 |

For violent crime:

\[
100(e^{0.0755}-1)\approx7.8\%.
\]

Thus days with TMAX ≥35°C are associated with roughly **7.8% higher violent-crime counts**, conditional on the current controls.

## Important change from the truncated pilot

The earlier three-year pilot suggested a broad ≥35°C effect across total, violent, and property crime.

That does **not** survive in the full sample.

Instead:

- total-crime ≥35°C effect becomes weaker and borderline;
- violent-crime ≥35°C effect remains large and highly significant;
- property-crime effect disappears.

This shift is substantively useful because it points toward a specific mechanism rather than a generic “heat raises everything” pattern.

---

# 5. Quadratic anomaly model: violent-crime response is positive but mildly concave

For violent crime:

\[
\beta_1 = 0.015600
\]

for the linear anomaly term, and:

\[
\beta_2=-0.000427
\]

for the squared anomaly term.

The quadratic term is significant:

\[
p=0.0169.
\]

The marginal effect of anomaly is:

\[
\frac{\partial \log(1+ViolentCrime_t)}
{\partial TempAnom_t}
=
\beta_1 + 2\beta_2 TempAnom_t.
\]

Substituting the estimates:

\[
\frac{\partial \log(1+ViolentCrime_t)}
{\partial TempAnom_t}
=
0.0156
-
0.000854TempAnom_t.
\]

So the relationship is mildly concave, but across ordinary observed positive anomalies the marginal effect remains positive.

This is not inconsistent with the absolute-TMAX bin results, because the two specifications measure different aspects of heat exposure:

- anomaly model = deviation from seasonal normal;
- TMAX bins = absolute daily heat level.

---

# 6. The placebo result is now much cleaner

The falsification test uses temperature anomaly seven days in the future:

\[
Crime_t
\sim
TempAnom_{t+7}
+
Controls_t.
\]

Full-sample result:

\[
\beta=-0.000257,
\qquad
SE=0.000889,
\qquad
p=0.772.
\]

This is reassuring.

The earlier truncated pilot had:

\[
p\approx0.10.
\]

With the full sample, the future-temperature coefficient is now essentially zero.

This does not by itself prove causality, but it reduces concern that the main result is simply generated by broad unremoved seasonal structure.

---

# 7. ENSO/ONI: the apparent “strong winter IV” disappears in the full sample

The earlier 2010–2012 pilot produced an apparently huge Nov–Mar first-stage F statistic:

\[
F\approx58.8.
\]

That result does not survive.

## Current distributed-lag first stage

| Sample | N | Partial \(R^2\) | Joint F |
|---|---:|---:|---:|
| All months | 166 | 0.0867 | **5.00** |
| Nov–Mar | 68 | 0.1071 | **3.22** |

These are not strong first-stage results for a multi-instrument IV design.

The previous winter \(F=58.8\) should therefore be treated as an artifact of the tiny truncated sample.

---

# 8. ONI is still correlated with LA temperature, but that is not enough for a useful IV

The parsimonious model with contemporaneous ONI alone gives:

### All months

\[
\pi=0.3957,
\qquad
SE=0.1245,
\qquad
p=0.00149.
\]

### November–March

\[
\pi=0.3214,
\qquad
SE=0.1347,
\qquad
p=0.0170.
\]

So there is evidence that:

\[
ONI\uparrow
\Rightarrow
LA\ temperature\ anomaly\uparrow.
\]

However, once contemporaneous and lagged ONI are included together, the individual coefficients are unstable and the joint first stage remains weak.

This is not surprising because ONI itself is a three-month running mean, so:

\[
ONI_t,\quad ONI_{t-1},\quad ONI_{t-2}
\]

are highly correlated.

## Current interpretation

The appropriate conclusion is:

> ENSO has a detectable relationship with Los Angeles temperature, but the current multi-lag LA-only first stage is too weak to motivate a conventional IV strategy.

In addition, the exclusion-restriction problem remains unresolved because ENSO can affect precipitation, storms, economic activity, wildfire conditions, and other channels besides temperature.

Therefore ENSO should currently be **secondary/exploratory**, not the centerpiece of the causal design.

---

# 9. Revised research story

The current evidence supports a cleaner research question:

> **Does short-run heat exposure causally increase violent crime in Los Angeles?**

The empirical pattern is approximately:

\[
Heat
\longrightarrow
\begin{cases}
ViolentCrime & \text{strong positive response}\\
PropertyCrime & \text{little or no response}
\end{cases}
\]

The violent-crime response also increases systematically across hotter TMAX bins.

This is potentially more theoretically meaningful than a generic total-crime effect.

Possible mechanisms include:

- heat stress;
- irritability/aggression;
- interpersonal conflict;
- increased outdoor interaction/exposure;
- changes in routine activities.

The mechanism should not be claimed from these regressions alone, but the violent/property heterogeneity helps distinguish plausible theories.

---

# 10. Highest-priority next analyses

The next stage should focus on validating the violent-crime result rather than adding a complicated IV model.

## Priority 1 — Audit the crime classification

The current `violent` and `property` variables are keyword-based proxies.

This is now the most important outcome-data issue because the main finding depends heavily on the violent/property distinction.

Recommended upgrade:

- build a formal LAPD offense-code crosswalk;
- map offenses into defensible violent/property categories;
- verify overlap and mutually exclusive classification where appropriate;
- report category shares and daily counts.

Preferably align categories with UCR/NIBRS definitions when feasible.

---

## Priority 2 — Count observations in every temperature bin

Report:

\[
N_k = \#\{t:TMAX_t\in Bin_k\}.
\]

Especially inspect:

\[
N_{\ge35}.
\]

Also report:

- number of unique ≥35°C days;
- number of distinct heat-wave episodes;
- years containing ≥35°C days;
- whether one or two extreme episodes dominate the estimate.

A strong coefficient with very sparse support should be interpreted differently from a response observed across many independent heat episodes.

---

## Priority 3 — Test temporal stability

Run the same preferred model on:

1. **2010–2019**
2. **2010–2023**
3. **2010–2023 excluding 2020–2021**
4. optionally 2022–2023 as a post-pandemic check

The most valuable result would be a violent-heat coefficient with the same direction and similar magnitude across these samples.

---

## Priority 4 — Expand placebo leads

Test:

\[
TempAnom_{t+7},
\quad
TempAnom_{t+14},
\quad
TempAnom_{t+21},
\quad
TempAnom_{t+28}.
\]

A useful falsification figure would plot all lead coefficients and confidence intervals.

The desired pattern is:

\[
\beta_{\text{future leads}}\approx0.
\]

---

## Priority 5 — Distributed lags and displacement

Estimate:

\[
\log(1+ViolentCrime_t)
=
\sum_{\ell=0}^{L}
\beta_\ell Heat_{t-\ell}
+
Controls_t
+
\varepsilon_t.
\]

where:

- \(\ell\) = lag in days;
- \(L\) = maximum lag;
- \(\beta_\ell\) = effect associated with heat \(\ell\) days earlier.

This tests whether heat:

- creates additional crime;
- shifts crime forward in time;
- has persistent effects.

If a positive same-day effect is followed by negative lag coefficients, some of the apparent increase may represent temporal displacement.

---

# 11. Highest-priority data improvement: spatially resolved weather

The current pilot assigns one LAX weather station to the entire City of Los Angeles.

This is a major limitation.

Los Angeles has strong coastal–inland temperature gradients. LAX is coastal and often substantially cooler than inland LAPD areas.

The next major data design should therefore move toward:

\[
Crime_{it}
\leftrightarrow
Weather_{it}
\]

where \(i\) is an LAPD area or another spatial unit.

Possible weather sources:

- multiple NOAA stations;
- PRISM;
- Daymet;
- ERA5-Land or another gridded product.

This would:

1. reduce exposure measurement error;
2. capture far more true extreme-heat exposure;
3. create spatial as well as temporal weather variation;
4. permit area fixed effects;
5. support a much stronger city-within-day identification design.

A future model could be:

\[
\log(1+Crime_{it})
=
f(Temperature_{it})
+
\alpha_i
+
\tau_t
+
X_{it}'\gamma
+
\varepsilon_{it}
\]

where:

- \(Crime_{it}\) = crime in area \(i\) on date \(t\);
- \(Temperature_{it}\) = spatially matched local temperature;
- \(f(\cdot)\) = nonlinear temperature response;
- \(\alpha_i\) = area fixed effects;
- \(\tau_t\) = date fixed effects;
- \(X_{it}\) = local time-varying controls;
- \(\varepsilon_{it}\) = error.

This design could compare hotter and cooler parts of Los Angeles **on the same day**, while absorbing citywide daily shocks with \(\tau_t\).

That is potentially much stronger than the current single-city time-series design.

---

# 12. Additional robustness after the core checks

Once the classification and spatial weather are improved, consider:

- 7-, 14-, and 30-day HAC lag choices;
- Poisson or PPML count models;
- holidays;
- major events;
- wildfire smoke / PM2.5;
- precipitation nonlinearities;
- humidity / apparent temperature;
- minimum/nighttime temperature;
- heat-wave duration;
- percentile-based heat definitions;
- multiple-testing adjustments;
- alternative climate normals.

These should come **after** the core result is validated, not before.

---

# 13. Climate-change extension

If the violent-crime temperature-response function remains robust, the climate-change component can be constructed from future changes in temperature-bin exposure.

For bins \(k\):

\[
\Delta Crime
=
\sum_k
\hat{\beta}_k
\left(
FutureDays_k-BaselineDays_k
\right)
\]

where:

- \(\hat{\beta}_k\) = estimated crime response for temperature bin \(k\);
- \(FutureDays_k\) = number of future days in bin \(k\);
- \(BaselineDays_k\) = baseline number of days in bin \(k\);
- \(\Delta Crime\) = predicted climate-driven change in crime.

This would connect the empirical crime response directly to projected warming and changes in the frequency of extreme heat.

A spatial version could apply local climate projections to individual LA areas.

---

# 14. Recommended role of ENSO going forward

At this point, do **not** make ENSO-IV the main paper.

Recommended hierarchy:

### Primary design

\[
Short\text{-}run\ local\ heat
\rightarrow
Violent\ crime
\]

using high-frequency weather variation and increasingly strong spatial/time fixed effects.

### Secondary climate-mechanism analysis

\[
ENSO
\rightarrow
LA\ temperature
\]

to document large-scale climate variability and local weather transmission.

### Optional future IV exploration

Only revisit an ENSO-based IV if a stronger multi-region design becomes feasible, for example:

\[
Z_{it}
=
ONI_t\times PredeterminedSensitivity_i.
\]

This could generate spatial × temporal instrument variation while permitting stronger common time fixed effects.

It would still require a serious exclusion-restriction argument.

---

# 15. Recommended immediate workflow

The next coding round should remain focused and small.

## Step 1

Audit and rebuild violent/property crime categories using offense codes.

## Step 2

Add descriptive support diagnostics:

- days per temperature bin;
- number of extreme-heat episodes;
- category sizes.

## Step 3

Rerun the existing preferred models without changing the core specification.

## Step 4

Run temporal robustness:

- pre-COVID;
- full sample;
- excluding 2020–2021.

## Step 5

Add placebo leads and distributed lags.

## Step 6

Upgrade weather from one LAX station to spatially matched local weather.

Only after these steps should the project add more complex identification or climate-projection modules.

---

# 16. Bottom line for the next agent

The corrected 2010–2023 analysis produces a substantially stronger and more coherent result than the truncated pilot:

\[
\boxed{
\text{Heat is strongly associated with violent crime}
}
\]

while:

\[
\boxed{
\text{Property crime shows little temperature response}
}
\]

The violent-crime response is not limited to a single arbitrary threshold; it rises systematically across hotter temperature bins, reaching roughly **+9.7% relative to the 20–25°C bin at TMAX ≥35°C**.

The +7-day future-temperature placebo is essentially zero, which is encouraging.

The ENSO candidate-IV route becomes much less attractive in the full sample:

\[
F_{\text{all}}\approx5.0,
\qquad
F_{\text{Nov-Mar}}\approx3.2.
\]

Therefore the best current strategy is:

> **Make the short-run heat → violent-crime relationship the main research line, validate it aggressively, improve spatial weather exposure, and keep ENSO as a secondary exploratory climate mechanism rather than forcing it into the main identification strategy.**
