from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from src.resultathle.scraper import CompetitionHeader, scrape_competition
from src.resultathle.site import render_site


def main() -> int:
    url = os.getenv(
        "COMP_URL",
        # Example competition URL; replace via repository variables for real deployments
        "https://bases.athle.fr/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=282742",
    )
    pages_str = os.getenv("COMP_PAGES", "1")
    try:
        pages = int(pages_str)
    except ValueError:
        pages = 1

    header: CompetitionHeader
    results: pd.DataFrame
    try:
        header, results = scrape_competition(url, pages)
    except Exception:
        # Fallback to an empty site if scraping fails (e.g., network/CORS restrictions in CI)
        header = CompetitionHeader(
            name="ResultAthle",
            location="",
            date="",
            department=None,
            label=None,
        )
        results = pd.DataFrame(
            {
                "Athlete": [],
                "FirstName": [],
                "LastName": [],
                "Category": [],
                "League": [],
                "BirthYear": [],
                "Performance": [],
                "DurationHMS": [],
            }
        )

    output_dir = Path("site")
    output_dir.mkdir(parents=True, exist_ok=True)
    render_site(output_dir, header, results)

    # Also write JSON for convenience
    (output_dir / "results.json").write_text(
        results.to_json(orient="records", force_ascii=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
