# Full-sample results summary

Daily N = 5,113 (2010-01-01 → 2023-12-31)

## Main anomaly model (temp_anom)

- total: beta=0.0063, SE=0.0010, p=7.745e-10, approx 0.63% per +1°C
- violent: beta=0.0154, SE=0.0010, p=1.06e-53, approx 1.55% per +1°C
- violent_ucr: beta=0.0158, SE=0.0015, p=3.145e-26, approx 1.60% per +1°C
- property: beta=0.0029, SE=0.0008, p=0.0002807, approx 0.29% per +1°C

## Extreme heat ≥35°C (violent)

- beta=0.0746, SE=0.0154, p=1.195e-06, approx 7.75%

## Placebo lead +7 (violent)

- beta=-0.0025, SE=0.0009, p=0.006454

## ONI first stage

- all_months: partial R²=0.0867; joint F=5.002; N=166
- nov_mar: partial R²=0.1071; joint F=3.223; N=68

**Crime categories use LAPD Crm Cd crosswalk (see crime_classification_audit.csv).**
**ONI results are first-stage diagnostics only; not a causal IV estimate.**