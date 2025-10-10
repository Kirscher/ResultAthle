from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Optional

import jinja2
import pandas as pd

from .scraper import CompetitionHeader


def render_site(dest_dir: Path, header: CompetitionHeader, results: pd.DataFrame) -> Path:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(Path(__file__).parent / "templates")))
    template = env.get_template("index.html.j2")
    dest_dir.mkdir(parents=True, exist_ok=True)
    html = template.render(header=asdict(header), results=results.to_dict(orient="records"))
    out = dest_dir / "index.html"
    out.write_text(html)
    return out
