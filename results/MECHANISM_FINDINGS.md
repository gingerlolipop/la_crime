# Mechanism-oriented crime-type findings

Daily sample: N = 5,113 (2010-01-01 → 2023-12-31)
LAX TMAX 95th percentile: 28.9°C (286 days)
LAX hot35 days: 26

## Category definitions

Subcategories use LAPD Crm Cd codes (see `crime_mechanism_classification.csv`).

| Category | Incidents | Share | Overlap check |
|---|---:|---:|---|
| violent | 928,072 | 30.8% | violent_ucr,interpersonal,robbery |
| violent_ucr | 340,555 | 11.3% | violent,interpersonal,robbery |
| interpersonal | 717,198 | 23.8% | violent,violent_ucr |
| robbery | 130,722 | 4.3% | violent,violent_ucr |
| property | 1,602,136 | 53.2% | theft,burglary,vehicle_theft |
| theft | 877,878 | 29.2% | property |
| burglary | 438,963 | 14.6% | property |
| vehicle_theft | 285,295 | 9.5% | property |

## Temperature-bin shapes (vs 20–25°C reference)

### violent
- Shape heuristic: **monotonic increasing**
- Mean daily count: 181.5
  - 15_20: β=-0.0305, SE=0.0048, p=2.238e-10, ~-3.00%
  - 25_30: β=0.0392, SE=0.0045, p=5.888e-18, ~4.00%
  - 30_35: β=0.0706, SE=0.0083, p=1.679e-17, ~7.32%
  - ge35: β=0.0924, SE=0.0129, p=8.089e-13, ~9.68%
  - lt15: β=-0.0897, SE=0.0140, p=1.33e-10, ~-8.58%

### violent_ucr
- Shape heuristic: **noisy**
- Mean daily count: 66.6
  - 15_20: β=-0.0429, SE=0.0071, p=1.519e-09, ~-4.20%
  - 25_30: β=0.0409, SE=0.0067, p=1.274e-09, ~4.18%
  - 30_35: β=0.0611, SE=0.0134, p=5.235e-06, ~6.30%
  - ge35: β=0.0560, SE=0.0249, p=0.02436, ~5.76%
  - lt15: β=-0.0998, SE=0.0179, p=2.309e-08, ~-9.50%

### interpersonal
- Shape heuristic: **monotonic increasing**
- Mean daily count: 140.3
  - 15_20: β=-0.0308, SE=0.0050, p=9.42e-10, ~-3.03%
  - 25_30: β=0.0395, SE=0.0048, p=3.816e-16, ~4.03%
  - 30_35: β=0.0798, SE=0.0089, p=3.33e-19, ~8.30%
  - ge35: β=0.1118, SE=0.0152, p=2.1e-13, ~11.82%
  - lt15: β=-0.0857, SE=0.0144, p=2.48e-09, ~-8.22%

### robbery
- Shape heuristic: **inverted-U**
- Mean daily count: 25.6
  - 15_20: β=-0.0415, SE=0.0091, p=4.748e-06, ~-4.07%
  - 25_30: β=0.0279, SE=0.0090, p=0.001843, ~2.83%
  - 30_35: β=0.0446, SE=0.0188, p=0.01769, ~4.56%
  - ge35: β=0.0283, SE=0.0403, p=0.4833, ~2.87%
  - lt15: β=-0.0984, SE=0.0224, p=1.073e-05, ~-9.38%

### property
- Shape heuristic: **mixed / inconclusive**
- Mean daily count: 313.3
  - 15_20: β=-0.0023, SE=0.0038, p=0.5361, ~-0.23%
  - 25_30: β=0.0085, SE=0.0036, p=0.01827, ~0.85%
  - 30_35: β=-0.0022, SE=0.0075, p=0.7702, ~-0.22%
  - ge35: β=-0.0046, SE=0.0140, p=0.7439, ~-0.45%
  - lt15: β=-0.0227, SE=0.0106, p=0.03192, ~-2.24%

### theft
- Shape heuristic: **monotonic increasing**
- Mean daily count: 171.7
  - 15_20: β=-0.0107, SE=0.0050, p=0.03147, ~-1.06%
  - 25_30: β=0.0119, SE=0.0044, p=0.006648, ~1.20%
  - 30_35: β=0.0194, SE=0.0082, p=0.01739, ~1.96%
  - ge35: β=0.0271, SE=0.0171, p=0.1135, ~2.75%
  - lt15: β=-0.0270, SE=0.0125, p=0.03044, ~-2.67%

### burglary
- Shape heuristic: **inverted-U**
- Mean daily count: 85.9
  - 15_20: β=0.0131, SE=0.0059, p=0.02609, ~1.32%
  - 25_30: β=0.0002, SE=0.0060, p=0.9724, ~0.02%
  - 30_35: β=-0.0230, SE=0.0136, p=0.09218, ~-2.27%
  - ge35: β=-0.0133, SE=0.0189, p=0.482, ~-1.32%
  - lt15: β=-0.0186, SE=0.0165, p=0.2585, ~-1.84%

### vehicle_theft
- Shape heuristic: **mixed / inconclusive**
- Mean daily count: 55.8
  - 15_20: β=-0.0025, SE=0.0059, p=0.6658, ~-0.25%
  - 25_30: β=0.0092, SE=0.0063, p=0.1465, ~0.92%
  - 30_35: β=-0.0340, SE=0.0130, p=0.008659, ~-3.35%
  - ge35: β=-0.0807, SE=0.0347, p=0.01993, ~-7.75%
  - lt15: β=-0.0242, SE=0.0158, p=0.1271, ~-2.39%


## Quadratic temp-anomaly summary (linear term)

- violent: β₁=0.0154, SE=0.0010, p=1.06e-53, ~1.55% per +1°C; β₂=-0.0004 (p=0.01872)
- violent_ucr: β₁=0.0158, SE=0.0015, p=3.145e-26, ~1.60% per +1°C; β₂=-0.0006 (p=0.0162)
- interpersonal: β₁=0.0163, SE=0.0010, p=2.053e-54, ~1.64% per +1°C; β₂=-0.0004 (p=0.05564)
- robbery: β₁=0.0135, SE=0.0017, p=5.841e-16, ~1.36% per +1°C; β₂=-0.0008 (p=0.02102)
- property: β₁=0.0029, SE=0.0008, p=0.0002807, ~0.29% per +1°C; β₂=-0.0004 (p=0.003823)
- theft: β₁=0.0043, SE=0.0010, p=2.17e-05, ~0.43% per +1°C; β₂=-0.0001 (p=0.5547)
- burglary: β₁=0.0000, SE=0.0012, p=0.9917, ~0.00% per +1°C; β₂=-0.0006 (p=0.006056)
- vehicle_theft: β₁=0.0030, SE=0.0012, p=0.01253, ~0.30% per +1°C; β₂=-0.0009 (p=0.0002289)

## Extreme heat indicators

- violent / hot35: β=0.0746, SE=0.0154, p=1.195e-06, ~7.75%, n_hot=26
- violent / hot_p95: β=0.0587, SE=0.0062, p=1.597e-21, ~6.04%, n_hot=286
- interpersonal / hot35: β=0.0927, SE=0.0177, p=1.757e-07, ~9.71%, n_hot=26
- interpersonal / hot_p95: β=0.0657, SE=0.0063, p=1.17e-25, ~6.79%, n_hot=286
- property / hot35: β=-0.0065, SE=0.0141, p=0.6465, ~-0.65%, n_hot=26
- property / hot_p95: β=-0.0063, SE=0.0053, p=0.2301, ~-0.63%, n_hot=286

## Interpretation (do not oversell)

Consistent with **heat-aggression** (interpersonal) and **routine-activity** (property inverted-U) pathways — suggestive, not causal.

Spatial within-day design (area + date FE) still shows no positive local violent-heat effect; this mechanism note applies to the **citywide temporal** specification only.

**Note:** 35°C is an intuitive local tail threshold, not a universal extreme-heat definition. hot_p95 uses LAX TMAX ≥ 28.9°C.