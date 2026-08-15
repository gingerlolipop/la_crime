#!/usr/bin/env python3
"""Download raw inputs. Never keep truncated files."""
from pathlib import Path
import requests
from config import *

RAW.mkdir(parents=True, exist_ok=True)


def looks_complete(path: Path) -> bool:
    """Reject empty/tiny files and CSVs cut mid-row (no trailing newline)."""
    if not path.exists() or path.stat().st_size < 1000:
        return False
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 8))
        tail = f.read()
    if path.suffix.lower() == ".csv":
        return b"\n" in tail
    return True


def download(url, path: Path, params=None):
    if looks_complete(path):
        print("skip", path.name, f"({path.stat().st_size/1e6:.1f} MB)")
        return
    if path.exists():
        print("remove incomplete", path.name)
        path.unlink()

    print("download", path.name)
    tmp = path.with_suffix(path.suffix + ".part")
    try:
        with requests.get(url, params=params, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(8 << 20):
                    if chunk:
                        f.write(chunk)
        if not looks_complete(tmp):
            raise RuntimeError(f"download looks truncated: {path.name}")
        tmp.replace(path)
        print("saved", path.name, f"({path.stat().st_size/1e6:.1f} MB)")
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


for name, url in CRIME_URLS.items():
    download(url, RAW / name)

download(WEATHER_URL, RAW / "weather.csv", {
    "dataset": "daily-summaries", "stations": STATION,
    "startDate": WEATHER_START, "endDate": WEATHER_END,
    "dataTypes": "TMAX,TMIN,PRCP", "format": "csv",
    "units": "metric", "includeAttributes": "false"
})

download(ONI_URL, RAW / "oni.html")
print("downloads complete under", RAW)
