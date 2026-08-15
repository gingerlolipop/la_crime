from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))
RAW, OUT = DATA / "raw", DATA / "processed"
RESULTS = ROOT / "results"

CRIME_START, CRIME_END = "2010-01-01", "2023-12-31"
WEATHER_START, WEATHER_END = "1991-01-01", "2023-12-31"
NORMAL_START, NORMAL_END = "1991-01-01", "2020-12-31"
STATION = "USW00023174"

CRIME_URLS = {
    "crime_2010_2019.csv":
        "https://data.lacity.org/api/views/63jg-8b9z/rows.csv?accessType=DOWNLOAD",
    "crime_2020_2024.csv":
        "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD",
}
ONI_URL = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/"
WEATHER_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
