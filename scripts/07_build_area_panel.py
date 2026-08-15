#!/usr/bin/env python3
"""Build LAPD area × day crime–weather panel with local station matching."""
import numpy as np
import pandas as pd
from config import *
from offense_codes import classify_code, is_violent_ucr

OUT.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)
STAT_DIR = RAW / "stations"


def area_col(df):
    """Normalize trailing-space AREA column names across LAPD extracts."""
    rename = {c: c.strip() for c in df.columns}
    return df.rename(columns=rename)


# ---------------------------------------------------------------------------
# 1) LAPD area centroids from crime LAT/LON medians
# ---------------------------------------------------------------------------
geo_chunks = []
for p in sorted(RAW.glob("crime_*.csv")):
    cols = list(pd.read_csv(p, nrows=0).columns)
    use = [c for c in cols if c.strip() in ("AREA", "AREA NAME", "LAT", "LON")]
    for chunk in pd.read_csv(p, usecols=use, chunksize=400_000, low_memory=False):
        chunk = area_col(chunk)
        chunk = chunk[(chunk["LAT"].abs() > 1) & (chunk["LON"].abs() > 1)]
        geo_chunks.append(chunk[["AREA", "AREA NAME", "LAT", "LON"]])
geo = pd.concat(geo_chunks, ignore_index=True)
areas = (
    geo.groupby(["AREA", "AREA NAME"], as_index=False)
    .agg(latitude=("LAT", "median"), longitude=("LON", "median"), n_geo=("LAT", "size"))
    .sort_values("AREA")
)
areas["AREA"] = areas["AREA"].astype(int)
areas.to_csv(OUT / "lapd_areas.csv", index=False)
print("LAPD areas:", len(areas))
print(areas.to_string(index=False))

# ---------------------------------------------------------------------------
# 2) Area-daily crime counts (offense-code categories)
# ---------------------------------------------------------------------------
crime_parts = []
for p in sorted(RAW.glob("crime_*.csv")):
    cols = list(pd.read_csv(p, nrows=0).columns)
    use = [c for c in cols if c.strip() in ("DATE OCC", "AREA", "AREA NAME", "Crm Cd")]
    for chunk in pd.read_csv(p, usecols=use, chunksize=400_000, low_memory=False):
        chunk = area_col(chunk)
        chunk["date"] = pd.to_datetime(chunk["DATE OCC"], errors="coerce", format="mixed")
        chunk = chunk[chunk["date"].between(CRIME_START, CRIME_END)]
        chunk["Crm Cd"] = pd.to_numeric(chunk["Crm Cd"], errors="coerce")
        chunk["AREA"] = pd.to_numeric(chunk["AREA"], errors="coerce")
        chunk = chunk.dropna(subset=["date", "AREA"])
        chunk["AREA"] = chunk["AREA"].astype(int)
        chunk["category"] = chunk["Crm Cd"].map(classify_code)
        chunk["violent"] = (chunk["category"] == "violent").astype(int)
        chunk["violent_ucr"] = chunk["Crm Cd"].map(is_violent_ucr).astype(int)
        chunk["property"] = (chunk["category"] == "property").astype(int)
        crime_parts.append(chunk[["date", "AREA", "AREA NAME", "violent",
                                  "violent_ucr", "property"]])

crime = pd.concat(crime_parts, ignore_index=True)
# canonical area names
name_map = areas.set_index("AREA")["AREA NAME"].to_dict()
crime["AREA NAME"] = crime["AREA"].map(name_map).fillna(crime["AREA NAME"])

daily_crime = (
    crime.groupby(["date", "AREA", "AREA NAME"], as_index=False)
    .agg(total=("violent", "size"),
         violent=("violent", "sum"),
         violent_ucr=("violent_ucr", "sum"),
         property=("property", "sum"))
)

# Balanced calendar × area panel (zeros for days with no recorded crime)
calendar = pd.DataFrame({"date": pd.date_range(CRIME_START, CRIME_END)})
area_cal = (
    calendar.assign(key=1)
    .merge(areas.assign(key=1), on="key")
    .drop(columns="key")
)
area_crime = area_cal.merge(
    daily_crime, on=["date", "AREA", "AREA NAME"], how="left")
for c in ["total", "violent", "violent_ucr", "property"]:
    area_crime[c] = area_crime[c].fillna(0).astype(int)
area_crime.to_csv(OUT / "area_daily_crime.csv", index=False)
print("area-days crime:", len(area_crime),
      f"({area_crime.date.min().date()} → {area_crime.date.max().date()})")

# ---------------------------------------------------------------------------
# 3) Local weather: nearest NOAA station to each area centroid
# ---------------------------------------------------------------------------
stations = pd.read_csv(STAT_DIR / "la_weather_stations.csv")
w = pd.read_csv(STAT_DIR / "weather_multi.csv")
w["date"] = pd.to_datetime(w["DATE"])
w = w.rename(columns={"STATION": "station"})
for c in ["TMAX", "TMIN", "PRCP"]:
    w[c] = pd.to_numeric(w[c], errors="coerce")
w["tmean"] = (w["TMAX"] + w["TMIN"]) / 2

# Nearest station (haversine-ish Euclidean ok at city scale)
assign = []
for _, a in areas.iterrows():
    d2 = (stations["lat"] - a["latitude"]) ** 2 + (stations["lon"] - a["longitude"]) ** 2
    j = d2.idxmin()
    s = stations.loc[j]
    # rough km
    dist_km = float(np.sqrt(
        ((stations.loc[j, "lat"] - a["latitude"]) * 111) ** 2
        + ((stations.loc[j, "lon"] - a["longitude"]) * 111
           * np.cos(np.radians(a["latitude"]))) ** 2
    ))
    assign.append({
        "AREA": int(a["AREA"]),
        "AREA NAME": a["AREA NAME"],
        "station": s["station"],
        "station_name": s["name"],
        "station_lat": s["lat"],
        "station_lon": s["lon"],
        "dist_km": dist_km,
    })
assign = pd.DataFrame(assign)
assign.to_csv(OUT / "area_station_assignment.csv", index=False)
print("station assignment:")
print(assign.to_string(index=False))

# Area-specific 1991–2020 month normals from assigned station history
hist = w[w["date"].between(NORMAL_START, NORMAL_END)].copy()
hist["month"] = hist["date"].dt.month
normals = (
    hist.groupby(["station", "month"], as_index=False)["tmean"]
    .mean().rename(columns={"tmean": "normal"})
)

# Study-period weather
wx = w[w["date"].between(CRIME_START, CRIME_END)].copy()
wx["month"] = wx["date"].dt.month
wx = wx.merge(normals, on=["station", "month"], how="left")
wx["temp_anom"] = wx["tmean"] - wx["normal"]

# LAX series for comparison diagnostics
lax = wx[wx["station"] == STATION][["date", "TMAX", "tmean", "temp_anom", "PRCP"]].rename(
    columns={"TMAX": "tmax_lax", "tmean": "tmean_lax",
             "temp_anom": "temp_anom_lax", "PRCP": "prcp_lax"})

panel = area_crime.merge(assign[["AREA", "station", "dist_km"]], on="AREA", how="left")
panel = panel.merge(
    wx[["date", "station", "TMAX", "TMIN", "PRCP", "tmean", "temp_anom"]],
    on=["date", "station"], how="left")
panel = panel.merge(lax, on="date", how="left")
panel["tmax_minus_lax"] = panel["TMAX"] - panel["tmax_lax"]
panel["ym"] = panel["date"].dt.to_period("M").astype(str)
panel["dow"] = panel["date"].dt.dayofweek
panel["year"] = panel["date"].dt.year
panel["hot30"] = (panel["TMAX"] >= 30).astype("Int64")
panel["hot32"] = (panel["TMAX"] >= 32).astype("Int64")
panel["hot35"] = (panel["TMAX"] >= 35).astype("Int64")
panel["tmax_bin"] = pd.cut(
    panel["TMAX"], [-np.inf, 15, 20, 25, 30, 35, np.inf],
    labels=["lt15", "15_20", "20_25", "25_30", "30_35", "ge35"], right=False)

panel.to_csv(OUT / "area_daily_crime_weather.csv", index=False)
print("panel rows", len(panel),
      "missing TMAX share", float(panel["TMAX"].isna().mean()))
print("hot35 area-days", int(panel["hot35"].fillna(0).sum()))
print("done ->", OUT)
