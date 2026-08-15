#!/usr/bin/env python3
"""Build daily/monthly analysis panels with offense-code crime categories."""
import numpy as np
import pandas as pd
from config import *
from offense_codes import VIOLENT, VIOLENT_UCR, PROPERTY, classify_code, is_violent_ucr

OUT.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

use = ["DATE OCC", "Crm Cd", "Crm Cd Desc"]
crime = pd.concat(
    [pd.read_csv(p, usecols=use, low_memory=False) for p in RAW.glob("crime_*.csv")],
    ignore_index=True,
)
crime["date"] = pd.to_datetime(crime["DATE OCC"], errors="coerce", format="mixed")
crime = crime[crime["date"].between(CRIME_START, CRIME_END)].copy()
crime["Crm Cd"] = pd.to_numeric(crime["Crm Cd"], errors="coerce")

# Preferred mutually exclusive classification from Crm Cd
crime["category"] = crime["Crm Cd"].map(classify_code)
crime["violent"] = (crime["category"] == "violent").astype(int)
crime["violent_ucr"] = crime["Crm Cd"].map(is_violent_ucr).astype(int)
crime["property"] = (crime["category"] == "property").astype(int)

# Legacy keyword proxies (for audit only; not mutually exclusive)
desc = crime["Crm Cd Desc"].fillna("").str.upper()
crime["kw_violent"] = desc.str.contains(
    r"HOMICIDE|MURDER|RAPE|ROBBERY|ASSAULT|BATTERY|KIDNAP", regex=True)
crime["kw_property"] = desc.str.contains(
    r"BURGLARY|THEFT|VEHICLE|VANDALISM|SHOPLIFT|STOLEN|ARSON", regex=True)

# --- Classification audit ---
n = len(crime)
audit_rows = []
for label, mask in [
    ("violent_code", crime["violent"] == 1),
    ("violent_ucr", crime["violent_ucr"] == 1),
    ("property_code", crime["property"] == 1),
    ("other", crime["category"] == "other"),
    ("kw_violent", crime["kw_violent"]),
    ("kw_property", crime["kw_property"]),
    ("kw_both", crime["kw_violent"] & crime["kw_property"]),
    ("code_violent_and_property", (crime["violent"] == 1) & (crime["property"] == 1)),
]:
    audit_rows.append({
        "category": label,
        "n": int(mask.sum()),
        "share": float(mask.mean()),
    })
audit = pd.DataFrame(audit_rows)
audit.to_csv(RESULTS / "crime_classification_audit.csv", index=False)

# Top codes in each bucket
code_table = (
    crime.groupby(["Crm Cd", "Crm Cd Desc", "category"], dropna=False)
    .size().reset_index(name="n").sort_values("n", ascending=False)
)
code_table["in_violent_ucr"] = code_table["Crm Cd"].map(is_violent_ucr)
code_table.to_csv(RESULTS / "crime_code_counts.csv", index=False)

print("classification shares:")
print(audit.to_string(index=False))
print(f"code∩ overlap violent&property: "
      f"{((crime.violent==1)&(crime.property==1)).sum()} (should be 0)")
print(f"keyword overlap both: {int((crime.kw_violent & crime.kw_property).sum()):,}")

daily_crime = crime.groupby("date").agg(
    total=("date", "size"),
    violent=("violent", "sum"),
    violent_ucr=("violent_ucr", "sum"),
    property=("property", "sum"),
).reset_index()
calendar = pd.DataFrame({"date": pd.date_range(CRIME_START, CRIME_END)})
daily_crime = calendar.merge(daily_crime, how="left").fillna(0)

# Weather and 1991-2020 normals
w = pd.read_csv(RAW / "weather.csv")
w["date"] = pd.to_datetime(w["DATE"])
for c in ["TMAX", "TMIN", "PRCP"]:
    w[c] = pd.to_numeric(w[c], errors="coerce")
w["tmean"] = (w["TMAX"] + w["TMIN"]) / 2
w["month"] = w["date"].dt.month

normal_mask = w["date"].between(NORMAL_START, NORMAL_END)
normal = w[normal_mask].groupby("month")["tmean"].mean().rename("normal")
w = w.merge(normal, on="month")
w["temp_anom"] = w["tmean"] - w["normal"]

daily = daily_crime.merge(
    w[["date", "TMAX", "TMIN", "PRCP", "tmean", "temp_anom"]], on="date", how="inner")
daily["ym"] = daily["date"].dt.to_period("M").astype(str)
daily["dow"] = daily["date"].dt.dayofweek
daily["year"] = daily["date"].dt.year
daily["hot30"] = (daily["TMAX"] >= 30).astype(int)
daily["hot32"] = (daily["TMAX"] >= 32).astype(int)
daily["hot35"] = (daily["TMAX"] >= 35).astype(int)
daily["tmax_bin"] = pd.cut(
    daily["TMAX"], [-np.inf, 15, 20, 25, 30, 35, np.inf],
    labels=["lt15", "15_20", "20_25", "25_30", "30_35", "ge35"], right=False)
daily.to_csv(OUT / "daily.csv", index=False)

# ONI v6
from bs4 import BeautifulSoup
center = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
          "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
soup = BeautifulSoup((RAW / "oni.html").read_text(errors="ignore"), "lxml")
rows = []
for tr in soup.find_all("tr"):
    cells = [x.get_text(strip=True) for x in tr.find_all(["td", "th"])]
    if len(cells) >= 13 and cells[0].isdigit():
        year = int(cells[0])
        for (season, month), value in zip(center.items(), cells[1:13]):
            rows.append([pd.Timestamp(year, month, 1),
                         pd.to_numeric(value, errors="coerce")])
oni = pd.DataFrame(rows, columns=["date", "oni"]).dropna().sort_values("date")

monthly = (
    daily.assign(date=daily["date"].dt.to_period("M").dt.to_timestamp())
    .groupby("date", as_index=False)
    .agg(total=("total", "sum"), violent=("violent", "sum"),
         violent_ucr=("violent_ucr", "sum"), property=("property", "sum"),
         tmean=("tmean", "mean"), temp_anom=("temp_anom", "mean"),
         prcp=("PRCP", "sum"))
)
monthly["month"] = monthly["date"].dt.month
monthly["trend"] = np.arange(len(monthly))
monthly = monthly.merge(oni, on="date", how="left")
monthly["oni_l1"] = monthly["oni"].shift(1)
monthly["oni_l2"] = monthly["oni"].shift(2)
monthly.to_csv(OUT / "monthly.csv", index=False)

print(f"daily={len(daily):,}  {daily['date'].min().date()} → {daily['date'].max().date()}")
print(f"monthly={len(monthly):,}  {monthly['date'].min().date()} → {monthly['date'].max().date()}")
print(f"mean daily total/violent/property: "
      f"{daily.total.mean():.1f} / {daily.violent.mean():.1f} / {daily.property.mean():.1f}")
if len(daily) == 1096:
    raise SystemExit(
        "ERROR: daily panel has exactly 1096 rows (2010–2012 only). "
        "Likely truncated raw inputs — rerun 01_download after deleting incomplete files."
    )
