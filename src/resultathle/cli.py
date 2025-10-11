from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd

from .scraper import CompetitionHeader, scrape_competition
from .site import render_site


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, index=False)


def _write_json(path: Path, header: CompetitionHeader, df: pd.DataFrame) -> None:
    payload = {
        "header": {
            "name": header.name,
            "location": header.location,
            "date": header.date,
            "department": header.department,
            "label": header.label,
        },
        "results": df.to_dict(orient="records"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scrape a Bases Athle competition results table")
    p.add_argument("url", help="Competition results URL (from bases.athle)")
    p.add_argument("pages", type=int, help="Number of result pages to scrape")
    p.add_argument("--out", type=Path, default=Path("output/results.csv"), help="Output CSV path")
    p.add_argument("--json", type=Path, default=None, help="Optional JSON output path")
    p.add_argument("--site-dir", type=Path, default=None, help="Optional directory to render static site")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    header, df = scrape_competition(args.url, args.pages)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(args.out, df)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        _write_json(args.json, header, df)
    if getattr(args, "site_dir", None) is not None:
        args.site_dir.mkdir(parents=True, exist_ok=True)
        render_site(args.site_dir, header, df)
    print(f"Saved {len(df)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
