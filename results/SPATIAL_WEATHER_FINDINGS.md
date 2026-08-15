# Spatial Weather Findings

## Data source
- Weather: NOAA GHCN-Daily multi-station extract (`stations/weather_multi.csv`)
- Matching: nearest station to LAPD area centroid (crime LAT/LON median)
- Crime: offense-code categories from `offense_codes.py`
- Panel: LAPD area × date, 2010–2023

## Support
- Areas: 21
- Area-days: 107,373
- With weather: 106,964
- Missing weather share: 0.0038
- hot30 / hot32 / hot35 area-days: 19,394 / 11,634 / 5,132
- hot35 share: 0.0480 (vs ~0.5% of days in LAX-only design)
- Mean local TMAX − LAX TMAX: 2.77°C

## Preferred spatial model
`log(1+Crime_it) ~ f(Temp_it) + area FE + date FE`, cluster SE by AREA.

### Continuous anomaly (temp_anom)
- violent: beta=0.0006, SE=0.0042, p=0.8795, approx 0.06%
- violent_ucr: beta=0.0011, SE=0.0040, p=0.7871, approx 0.11%
- property: beta=-0.0106, SE=0.0063, p=0.107, approx -1.06%

### Extreme heat (hot35)
- violent: beta=-0.0165, SE=0.0074, p=0.03766, approx -1.64%

## LAX vs spatial (violent)
| Design | temp_anom | hot35 |
|---|---:|---:|
| LAX city-level | 0.0154 (p=1.06e-53) | 0.0746 (p=1.19e-06) |
| Spatial area+date FE | 0.0006 (p=0.88) | -0.0165 (p=0.0377) |

## Interpretation
With full **date fixed effects**, all citywide daily shocks are absorbed. Identification comes from within-day cross-area temperature differences.

The LAX city-level heat → violent crime association **does not survive** this spatial design:
- continuous anomaly ≈ 0
- hot35 flips small negative

This is consistent with the prior city-level result relying mainly on **citywide temporal** heat variation rather than **local cross-sectional** heat exposure.

## Clustering / FE
- Spatial: area + date two-way FE; cluster-robust SE by LAPD AREA
- LAX comparison: year-month + DOW FE; HAC(14)

## Warning
- Station assignment is nearest-neighbor to crime-derived area centroids (approximation to official polygons).
- Several inland areas share Van Nuys / Downtown stations, so local contrast is limited by station density.
- Placebo / ENSO analyses were not re-run in this spatial round.
