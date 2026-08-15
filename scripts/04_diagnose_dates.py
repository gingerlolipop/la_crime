#!/usr/bin/env python3
"""Report min/max dates for each input and the merged analysis files."""
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from config import *

SEP = "-" * 60


def crime_range(path: Path):
    if not path.exists():
        return None, None, 0, "MISSING"
    n = 0
    lo = hi = None
    for chunk in pd.read_csv(path, usecols=["DATE OCC"], chunksize=250_000,
                             low_memory=False):
        d = pd.to_datetime(chunk["DATE OCC"], errors="coerce")
        n += len(chunk)
        lo = d.min() if lo is None else min(lo, d.min())
        hi = d.max() if hi is None else max(hi, d.max())
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 8))
        complete = b"\n" in f.read()
    status = "OK" if complete else "TRUNCATED"
    return lo, hi, n, status


def weather_range(path: Path):
    if not path.exists():
        return None, None, 0, "MISSING"
    w = pd.read_csv(path, usecols=["DATE"])
    d = pd.to_datetime(w["DATE"], errors="coerce")
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 8))
        complete = b"\n" in f.read()
    status = "OK" if complete else "TRUNCATED"
    return d.min(), d.max(), len(w), status


def oni_range(path: Path):
    if not path.exists():
        return None, None, 0, "MISSING"
    soup = BeautifulSoup(path.read_text(errors="ignore"), "lxml")
    years = []
    for tr in soup.find_all("tr"):
        cells = [x.get_text(strip=True) for x in tr.find_all(["td", "th"])]
        if cells and cells[0].isdigit():
            years.append(int(cells[0]))
    if not years:
        return None, None, 0, "EMPTY"
    return min(years), max(years), len(years), "OK"


def csv_date_range(path: Path, col="date"):
    if not path.exists():
        return None, None, 0, "MISSING"
    df = pd.read_csv(path, usecols=[col], parse_dates=[col])
    return df[col].min(), df[col].max(), len(df), "OK"


print(SEP)
print(f"DATA_DIR / RAW = {RAW}")
print(f"OUT            = {OUT}")
print(SEP)

rows = []
for p in sorted(RAW.glob("crime_*.csv")):
    lo, hi, n, st = crime_range(p)
    rows.append(("crime", p.name, lo, hi, n, st, p.stat().st_size))
    print(f"crime {p.name}: {lo} → {hi}  n={n:,}  {st}  {p.stat().st_size/1e6:.1f} MB")

lo, hi, n, st = weather_range(RAW / "weather.csv")
rows.append(("weather", "weather.csv", lo, hi, n, st,
             (RAW / "weather.csv").stat().st_size if (RAW / "weather.csv").exists() else 0))
print(f"weather.csv: {lo} → {hi}  n={n:,}  {st}")

lo, hi, n, st = oni_range(RAW / "oni.html")
print(f"oni.html years: {lo} → {hi}  year-rows={n}  {st}")

print(SEP)
lo, hi, n, st = csv_date_range(OUT / "daily.csv")
print(f"processed daily.csv: {lo} → {hi}  n={n:,}  {st}")
if n and n == 1096:
    print("WARNING: n=1096 matches only 2010–2012 (365+365+366).")
elif n and lo is not None and hi is not None:
    expected = (pd.Timestamp(CRIME_END) - pd.Timestamp(CRIME_START)).days + 1
    print(f"expected full crime calendar length ≈ {expected:,}; got {n:,}")

lo, hi, n, st = csv_date_range(OUT / "monthly.csv")
print(f"processed monthly.csv: {lo} → {hi}  n={n:,}  {st}")
print(SEP)

# Identify bottleneck if daily exists and is short
daily_path = OUT / "daily.csv"
if daily_path.exists():
    daily = pd.read_csv(daily_path, parse_dates=["date"])
    print(f"daily years present: {sorted(daily['date'].dt.year.unique().tolist())}")
print("diagnose_dates done")
