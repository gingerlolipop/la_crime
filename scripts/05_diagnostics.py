#!/usr/bin/env python3
"""Support diagnostics: temperature-bin counts and extreme-heat episodes."""
import numpy as np
import pandas as pd
from config import *

RESULTS.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(OUT / "daily.csv", parse_dates=["date"])

# Days per TMAX bin
bin_counts = (
    d.groupby("tmax_bin", observed=False)
    .agg(n_days=("date", "size"),
         mean_tmax=("TMAX", "mean"),
         mean_total=("total", "mean"),
         mean_violent=("violent", "mean"),
         mean_property=("property", "mean"))
    .reset_index()
)
bin_counts["share_days"] = bin_counts["n_days"] / len(d)
bin_counts.to_csv(RESULTS / "temperature_bin_counts.csv", index=False)
print("temperature bin support:")
print(bin_counts.to_string(index=False))

# Extreme-heat day summary
hot = d[d["hot35"] == 1].copy()
years = sorted(hot["date"].dt.year.unique().tolist()) if len(hot) else []

# Episodes: consecutive hot35 days (gap resets episode)
episodes = []
if len(hot):
    dates = hot["date"].sort_values().tolist()
    start = prev = dates[0]
    length = 1
    for cur in dates[1:]:
        if (cur - prev).days == 1:
            length += 1
        else:
            episodes.append({"start": start, "end": prev, "n_days": length})
            start = cur
            length = 1
        prev = cur
    episodes.append({"start": start, "end": prev, "n_days": length})

ep = pd.DataFrame(episodes)
ep.to_csv(RESULTS / "heat_episodes_ge35.csv", index=False)

summary = {
    "n_days_total": len(d),
    "n_hot30": int(d["hot30"].sum()),
    "n_hot32": int(d["hot32"].sum()),
    "n_hot35": int(d["hot35"].sum()),
    "n_heat_episodes_ge35": len(ep),
    "longest_episode_days": int(ep["n_days"].max()) if len(ep) else 0,
    "years_with_ge35": ",".join(map(str, years)),
    "mean_daily_total": float(d["total"].mean()),
    "mean_daily_violent": float(d["violent"].mean()),
    "mean_daily_violent_ucr": float(d["violent_ucr"].mean()),
    "mean_daily_property": float(d["property"].mean()),
    "share_violent": float(d["violent"].sum() / d["total"].sum()),
    "share_violent_ucr": float(d["violent_ucr"].sum() / d["total"].sum()),
    "share_property": float(d["property"].sum() / d["total"].sum()),
}
pd.DataFrame([summary]).to_csv(RESULTS / "support_summary.csv", index=False)
print("\nsupport summary:")
for k, v in summary.items():
    print(f"  {k}: {v}")
if len(ep):
    print(f"\nheat episodes ≥35°C (n={len(ep)}), longest={ep['n_days'].max()} days")
    print(ep.sort_values("n_days", ascending=False).head(10).to_string(index=False))
