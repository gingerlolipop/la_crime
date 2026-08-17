#!/usr/bin/env python3
"""Refresh README 'Latest results' section with links to results/ outputs."""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
RESULTS = ROOT / "results"
START = "<!-- RESULTS-LINKS:START -->"
END = "<!-- RESULTS-LINKS:END -->"

FINDINGS_NAMES = (
    "MECHANISM_FINDINGS_V2.md",
    "SPATIAL_WEATHER_FINDINGS.md",
    "FULL_SAMPLE_FINDINGS.md",
    "PILOT_FINDINGS.md",
    "RESULTS_SUMMARY.md",
)

KEY_TABLES = (
    "crime_mechanism_classification_v2.csv",
    "crime_type_temperature_bins_v2.csv",
    "crime_type_heterogeneity_tests.csv",
    "crime_type_hot_p95_clim.csv",
    "heat_threshold_definitions.csv",
    "spatial_main_models.csv",
    "lax_vs_spatial.csv",
    "main_models.csv",
    "temperature_bins.csv",
    "extreme_heat.csv",
)


def git_short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def build_links_body() -> str:
    """Stable link list (used to detect whether README needs updating)."""
    lines = ["### Findings reports"]
    for name in FINDINGS_NAMES:
        path = RESULTS / name
        if path.exists():
            rel = path.relative_to(ROOT).as_posix()
            label = name.removesuffix(".md").replace("_", " ")
            lines.append(f"- [{label}]({rel})")

    lines += ["", "### Key tables"]
    for name in KEY_TABLES:
        path = RESULTS / name
        if path.exists():
            lines.append(f"- [{name}](results/{name})")

    fig_dir = RESULTS / "figures"
    if fig_dir.is_dir():
        figs = sorted(fig_dir.glob("fig*.png"))
        if figs:
            lines += ["", "### Figures"]
            for path in figs:
                rel = path.relative_to(ROOT).as_posix()
                lines.append(f"- [{path.name}]({rel})")

    return "\n".join(lines)


def build_section(links_body: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = (
        "## Latest results\n\n"
        f"_Auto-updated on push. Snapshot commit `{git_short_sha()}` · {now}_\n"
    )
    return header + "\n" + links_body


def extract_links_body(text: str) -> str | None:
    m = re.search(
        rf"{re.escape(START)}.*?{re.escape(END)}",
        text,
        flags=re.DOTALL,
    )
    if not m:
        return None
    block = m.group(0)
    block = block.replace(START, "").replace(END, "").strip()
    # Drop title + snapshot line
    lines = block.splitlines()
    out = []
    skip = True
    for line in lines:
        if skip:
            if line.startswith("### "):
                skip = False
                out.append(line)
            continue
        out.append(line)
    return "\n".join(out).strip()


def main() -> int:
    if not README.exists():
        print("README.md not found")
        return 1

    links_body = build_links_body()
    text = README.read_text(encoding="utf-8")
    old_links = extract_links_body(text)

    if old_links == links_body:
        print("README results links unchanged")
        return 0

    content = build_section(links_body)
    block = f"{START}\n{content}\n{END}"

    if START in text and END in text:
        new_text = re.sub(
            rf"{re.escape(START)}.*?{re.escape(END)}",
            block,
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        anchor = "Licensed under the [MIT License](LICENSE).\n"
        if anchor not in text:
            print("README anchor not found; append section manually")
            return 1
        new_text = text.replace(anchor, f"{anchor}\n{block}\n")

    README.write_text(new_text, encoding="utf-8")
    print("Updated README.md results section")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
