#!/usr/bin/env python3
"""Download multi-station NOAA GHCN-Daily weather for the LA basin."""
from pathlib import Path
import requests
import pandas as pd
from config import *

RAW.mkdir(parents=True, exist_ok=True)
STAT_DIR = RAW / "stations"
STAT_DIR.mkdir(parents=True, exist_ok=True)

# Prefer official USW stations inside a tight LA basin box.
STATIONS = [
    "USW00023174",  # LAX
    "USW00093134",  # Downtown / USC
    "USW00023152",  # Burbank
    "USW00023130",  # Van Nuys
    "USW00093197",  # Santa Monica
    "USW00023129",  # Long Beach
    "USW00003167",  # Hawthorne
    "USW00003122",  # Torrance
    "USW00023180",  # Newhall (northern valley)
]


def looks_complete(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1000:
        return False
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 8))
        return b"\n" in f.read()


def download(url, path: Path, params=None):
    if looks_complete(path):
        print("skip", path.name, f"({path.stat().st_size/1e6:.1f} MB)")
        return
    if path.exists():
        path.unlink()
    print("download", path.name)
    tmp = path.with_suffix(path.suffix + ".part")
    with requests.get(url, params=params, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(8 << 20):
                if chunk:
                    f.write(chunk)
    if not looks_complete(tmp):
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"truncated download: {path.name}")
    tmp.replace(path)
    print("saved", path.name, f"({path.stat().st_size/1e6:.1f} MB)")


# Station metadata from GHCN master list
meta_path = STAT_DIR / "ghcnd-stations.txt"
if not meta_path.exists():
    download(
        "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt",
        meta_path,
    )

rows = []
wanted = set(STATIONS)
for line in meta_path.read_text().splitlines():
    sid = line[0:11].strip()
    if sid in wanted:
        rows.append({
            "station": sid,
            "lat": float(line[12:20]),
            "lon": float(line[21:30]),
            "elev_m": float(line[31:37]),
            "name": line[41:71].strip(),
        })
meta = pd.DataFrame(rows).sort_values("station")
meta.to_csv(STAT_DIR / "la_weather_stations.csv", index=False)
print(meta.to_string(index=False))

# One multi-station daily-summaries pull
out = STAT_DIR / "weather_multi.csv"
download(WEATHER_URL, out, {
    "dataset": "daily-summaries",
    "stations": ",".join(STATIONS),
    "startDate": WEATHER_START,
    "endDate": WEATHER_END,
    "dataTypes": "TMAX,TMIN,PRCP",
    "format": "csv",
    "units": "metric",
    "includeAttributes": "false",
})

w = pd.read_csv(out)
print("weather rows", len(w), "stations", sorted(w["STATION"].unique().tolist()))
print("date range", w["DATE"].min(), "→", w["DATE"].max())
print("done ->", STAT_DIR)
