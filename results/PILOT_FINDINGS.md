# Pilot Analysis Findings: LA Temperature, Crime, and ENSO

## Purpose

This note summarizes the main findings from the first pilot run of the Los Angeles temperature–crime project, with particular attention to:

1. the short-run temperature–crime results;
2. the apparent extreme-heat threshold effect;
3. the placebo test;
4. the ENSO/ONI first-stage diagnostics;
5. a critical data-range problem that must be fixed before interpreting the results substantively.

---

## 1. Main temperature-anomaly model: no detectable average effect

The baseline model used a quadratic temperature-anomaly specification:

\[
\log(1 + Crime_t)
=
\beta_1 TempAnom_t
+
\beta_2 TempAnom_t^2
+
Controls_t
+
\varepsilon_t.
\]

For the linear temperature-anomaly term, the estimates were:

| Outcome | Coefficient | SE | p-value |
|---|---:|---:|---:|
| Total crime | -0.0006 | 0.0009 | 0.4965 |
| Violent proxy | -0.0007 | 0.0009 | 0.4695 |
| Property proxy | -0.0006 | 0.0009 | 0.4889 |

### Interpretation

There is no evidence in this pilot that a generic increase in temperature anomaly produces a linear increase in crime.

This does **not** imply that temperature has no effect. The temperature-bin and threshold results suggest that the relationship may instead be concentrated in the extreme upper tail of the temperature distribution.

---

## 2. Temperature bins suggest a threshold-type nonlinear effect

The temperature-bin model used **20–25°C as the reference bin**.

Approximate total-crime coefficients from the plotted/model output were:

| TMAX bin | Coefficient relative to 20–25°C | Interpretation |
|---|---:|---|
| <15°C | about -0.008 | not clearly different from 0 |
| 15–20°C | about -0.010 | CI reaches approximately 0 |
| 25–30°C | approximately 0 | no visible difference |
| 30–35°C | about +0.011 | positive but imprecise |
| ≥35°C | about +0.034 | clearly positive |

The ≥35°C estimate is the most notable result.

Using the log specification,

\[
100\left(e^{0.0342}-1\right)
\approx 3.5\%.
\]

So the pilot estimate implies that days with daily maximum temperature at or above 35°C are associated with approximately **3.5% more recorded crime than days in the 20–25°C reference range**, conditional on the model controls.

The confidence interval in the figure also appears to stay above zero for the ≥35°C bin.

### Substantive implication

The preliminary pattern is not:

\[
Temperature \uparrow
\Rightarrow
Crime \uparrow
\quad \text{at a constant rate}.
\]

It looks more like:

\[
\text{normal/moderately hot temperatures}
\Rightarrow
\text{little change},
\]

followed by:

\[
\boxed{
TMAX \ge 35^\circ C
\Rightarrow
\text{a discrete increase in crime}
}
\]

This is potentially much more interesting for a climate-change application because it points to **tail exposure / extreme heat**, rather than average warming, as the relevant mechanism.

---

## 3. Extreme-heat threshold models reinforce the ≥35°C result

Separate indicator regressions were estimated for days above:

- 30°C;
- 32°C;
- 35°C.

The plotted results show:

- modest positive coefficients at 30°C;
- modest positive coefficients at 32°C;
- a substantially larger coefficient at 35°C.

Approximate ≥35°C estimates were:

| Outcome | Coefficient | Approximate percentage effect |
|---|---:|---:|
| Total crime | 0.03285 | +3.34% |
| Violent proxy | 0.03278 | +3.33% |
| Property proxy | 0.03105 | +3.15% |

Using

\[
100(e^\beta-1),
\]

these all imply an increase of roughly 3–3.5%.

The reported p-values for the ≥35°C coefficients were very small, on the order of \(10^{-5}\) to \(10^{-6}\).

### Important caution

The violent and property coefficients are strikingly similar. Before interpreting this as genuine behavioral heterogeneity, the crime classification should be audited.

The current `violent` and `property` outcomes are keyword-based proxies rather than a formal offense-code crosswalk.

Questions to check:

- Do the two proxy categories overlap?
- What proportion of total crime does each category represent?
- Are broad keywords causing mechanically similar daily series?
- Would an LAPD/UCR/NIBRS offense-code classification change the pattern?

---

## 4. Descriptive temperature–crime relationship is not monotonic

The descriptive binned plot of mean daily crime against mean daily temperature does not show a clean linear increase.

Crime fluctuates through moderate temperatures and rises again at the upper end.

This descriptive pattern is consistent with the regression evidence that a simple linear temperature effect may be inappropriate.

A nonlinear or threshold-based specification appears more suitable.

---

## 5. Future-temperature placebo: not statistically significant, but not fully reassuring

The placebo model used temperature anomaly seven days in the future to predict current crime:

\[
Crime_t
\sim
TempAnom_{t+7}
+
Controls_t.
\]

Result:

\[
\beta = 0.0014,
\qquad
SE = 0.0009,
\qquad
p = 0.1024.
\]

### Interpretation

This placebo is not statistically significant at conventional thresholds, which is encouraging.

However, \(p \approx 0.10\) is not extremely far from significance, and a 7-day lead is not a perfect placebo because weather is serially correlated. Heat waves can persist across multiple days.

A stronger falsification exercise would test several future leads:

\[
Temp_{t+7},
\quad
Temp_{t+14},
\quad
Temp_{t+21},
\quad
Temp_{t+28}.
\]

Ideally, the contemporaneous extreme-heat effect would remain strong while sufficiently distant future temperatures would have coefficients near zero.

---

# 6. ENSO / ONI first-stage results

The pilot reported:

| Sample | Partial \(R^2\) | Joint F |
|---|---:|---:|
| All months | 0.1781 | 3.508 |
| November–March | 0.5853 | 58.818 |

At first sight, the cold-season result looks extremely strong.

However, the effective sample size reveals a major problem.

---

# 7. Critical discovery: the analysis appears to contain only 2010–2012

The daily regression sample size is:

\[
N = 1096.
\]

But:

\[
365 + 365 + 366 = 1096.
\]

That is exactly the number of calendar days in:

- 2010;
- 2011;
- 2012.

The ONI time-series figure also visually stops around the end of 2012.

The all-month ONI distributed-lag first stage has approximately:

\[
N = 34,
\]

which is also consistent with:

\[
36 \text{ months}
-
2 \text{ months lost to lags}
=
34.
\]

Therefore, although the intended research sample was 2010–2023, the actual pilot appears to have analyzed only:

\[
\boxed{2010\text{–}2012}
\]

This is the single most important finding from the debugging stage.

---

## 8. Consequence for the extreme-heat result

The ≥35°C signal is intriguing, but it is currently based on only three years of daily observations.

Therefore, it should be treated as:

> **a promising pilot signal, not yet a substantive empirical result.**

The next run needs the full intended 2010–2023 sample before assessing:

- stability across years;
- sensitivity to COVID years;
- number of ≥35°C days;
- influence of individual heat waves;
- robustness of confidence intervals;
- whether the effect survives more complete controls.

The current result is worth pursuing precisely because it is strong enough to justify fixing the data pipeline and rerunning the full design.

---

# 9. Consequence for the ENSO first stage

The cold-season first stage appears to use only about:

\[
N = 13
\]

observations.

That is far too small for a distributed-lag specification containing:

- contemporaneous ONI;
- ONI lag 1;
- ONI lag 2;
- calendar-month fixed effects;
- time trend.

Therefore:

\[
F = 58.8
\]

should **not** currently be interpreted as evidence of a strong instrument.

With such a small sample and highly autocorrelated ONI lags, the model can become unstable or overfit.

The individual lag coefficients also changed signs, approximately:

\[
\pi_0 < 0,
\qquad
\pi_1 < 0,
\qquad
\pi_2 > 0,
\]

which is another reason to avoid over-interpreting the current distributed-lag result.

The all-month first-stage statistic,

\[
F \approx 3.5,
\]

is weak in the current pilot.

### Current conclusion on ENSO

The correct interpretation is:

> There is a potentially interesting cold-season ENSO–LA temperature signal, but the current three-year sample is much too small to determine whether ONI is a useful instrument.

With the intended 2010–2023 sample, November–March alone should provide roughly:

\[
14 \times 5 \approx 70
\]

monthly observations, which would make the diagnostic considerably more meaningful.

---

# 10. Current empirical picture

The pilot currently suggests three distinct findings.

## A. Average temperature anomaly

No detectable linear effect:

\[
TempAnomaly
\not\Rightarrow
Crime
\]

in the current pilot.

## B. Extreme heat

A potentially strong nonlinear threshold appears around:

\[
\boxed{TMAX \ge 35^\circ C}
\]

with an estimated crime increase of roughly:

\[
3\text{–}3.5\%.
\]

This is currently the most interesting substantive signal.

## C. ENSO

Full-year first stage currently looks weak:

\[
F \approx 3.5.
\]

Cold-season first stage looks superficially very strong:

\[
F \approx 58.8,
\]

but this is based on an extremely small sample and cannot yet be trusted.

---

# 11. Why the extreme-heat result could be more interesting than a linear temperature effect

If the relationship really has a threshold shape, the climate-change interpretation becomes more meaningful.

Instead of assuming:

\[
\Delta Crime
=
\beta \Delta T,
\]

future impacts could be calculated using changes in the number of days falling into high-temperature bins:

\[
\Delta Crime
=
\sum_k
\hat{\beta}_k
\left(
FutureDays_k
-
BaselineDays_k
\right).
\]

Where:

- \(\hat{\beta}_k\) = estimated crime effect for temperature bin \(k\);
- \(FutureDays_k\) = number of future days in temperature bin \(k\);
- \(BaselineDays_k\) = number of baseline days in temperature bin \(k\);
- \(\Delta Crime\) = predicted change in crime associated with the changed temperature distribution.

This would connect the project directly to climate-change exposure rather than only short-run weather.

---

# 12. Immediate next step: debug the truncated sample before changing the econometric model

No further econometric interpretation should be made until the source of the 2010–2012 truncation is identified.

The next diagnostic should inspect the raw data separately:

1. LAPD crime file minimum and maximum dates;
2. NOAA weather file minimum and maximum dates;
3. processed `daily.csv` minimum and maximum dates;
4. monthly ONI minimum and maximum dates.

The main question is:

> Which input or merge step truncates the intended 2010–2023 panel to 2010–2012?

Until that is fixed, it is better **not** to add more models, IV estimators, controls, or robustness specifications.

---

# 13. Bottom line

The pilot contains a genuinely interesting preliminary pattern:

\[
\boxed{
\text{ordinary temperature variation: little evidence}
}
\]

but:

\[
\boxed{
\text{extreme heat around } TMAX\ge35^\circ C:
\text{ crime appears to rise by about 3–3.5\%}
}
\]

At the same time, the analysis unexpectedly contains only **2010–2012**, so the result is not yet publication-quality evidence.

The priority is therefore:

1. fix the date-range/data-download problem;
2. rerun the exact same parsimonious specification on 2010–2023;
3. check whether the ≥35°C threshold survives;
4. only then refine the crime classification and robustness tests;
5. reassess the ENSO cold-season first stage using the full monthly sample.

If the ≥35°C effect remains stable in the full sample, the project may have a stronger research story around **extreme heat and nonlinear crime response** than around average temperature.
