from __future__ import annotations

import dataclasses
import re
from typing import Iterable, List, Optional, Tuple
from urllib import request

import bs4
import pandas as pd


@dataclasses.dataclass(frozen=True)
class CompetitionHeader:
    name: str
    location: str
    date: str
    department: Optional[str]
    label: Optional[str]


@dataclasses.dataclass(frozen=True)
class CompetitionResult:
    athlete: str
    league: Optional[str]
    performance_band: Optional[str]
    birth_year: Optional[int]
    category: Optional[str]
    duration_seconds: float
    duration_hms: str


ATHLETE_REGEX = re.compile(r"[A-Z]{2,} ?-?[A-Z]* ?-?[A-Z]* ?-?[A-Z]*[A-Z]{1}[a-z]+ ?-?[A-Z]?[a-z]*")
TIME_BOLD_REGEX = re.compile(r"<b>(?=\d).*(?=</b>)")
LEAGUE_REGEX = re.compile(r"[A-Z]{3,}(?=<)|[A-Z]-[A-Z](?=<)")
PERF_REGEX = re.compile(r"[A-Z]{1,2}[1-8](?=<)|I[A,B](?=<)")
CATEGORY_REGEX = re.compile(r"[A-Z]{3}(?=<)|[A-Z]{1}\d[A-Z]{1}")
YEAR_REGEX = re.compile(r"/[0-9]{2}<")


def _get(url: str) -> str:
    with request.urlopen(url) as resp:
        return resp.read().decode("utf-8")


def fetch_page(url: str, page_index: int) -> bs4.BeautifulSoup:
    html = _get(f"{url}&frmposition={page_index}")
    return bs4.BeautifulSoup(html, "lxml")


def extract_rows(page: bs4.BeautifulSoup) -> List[bs4.element.Tag]:
    rows: List[bs4.element.Tag] = []
    for tr in page.find_all("tr"):
        s = str(tr)
        if not any(k in s for k in ("groups", "headers", "mainheaders", "barButtons", "subheaderscom")):
            rows.append(tr)
    return rows


def parse_header(page: bs4.BeautifulSoup) -> CompetitionHeader:
    header = page.find("div", {"class": "mainheaders"})
    if header is None:
        return CompetitionHeader(name="", location="", date="", department=None, label=None)
    s = str(header)
    name_and_sub = re.compile(r"(?<=\- )(.*?)(?=<)").findall(s)
    name = name_and_sub[0] if name_and_sub else ""
    subtitle = name_and_sub[1] if len(name_and_sub) > 1 else ""
    location_match = re.compile(r"(?<=>)(\D*?)(?= \-)").findall(s)
    location = location_match[0] if location_match else ""
    date_match = re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{2}").findall(s)
    date = date_match[0] if date_match else ""
    dept_match = re.compile(r"[0-9]{3}").findall(subtitle)
    department = dept_match[0] if dept_match else None
    try:
        label = re.compile(r"(?<=Label ).*(?<!')").findall(subtitle)[0]
    except IndexError:
        label = None
    return CompetitionHeader(name=name, location=location, date=date, department=department, label=label)


def _parse_times_from_cells(cells: Iterable[bs4.element.Tag]) -> List[pd.Timestamp]:
    times: List[pd.Timestamp] = []
    for cell in cells:
        bold_matches = TIME_BOLD_REGEX.findall(str(cell))
        if not bold_matches:
            continue
        raw = bold_matches[0].replace("<b>", "")
        parsed: Optional[pd.Timestamp] = None
        for fmt in ("%Hh%M'%S''", "%M'%S''", "%S''"):
            try:
                parsed = pd.to_datetime(raw, format=fmt)
                break
            except ValueError:
                continue
        if parsed is not None:
            times.append(parsed)
    return times


def _extract_with_regex(cells: Iterable[bs4.element.Tag], pattern: re.Pattern[str]) -> List[str]:
    out: List[str] = []
    for cell in cells:
        match = pattern.search(str(cell))
        out.append(match.group() if match else "")
    return out


def _extract_leagues(cells: Iterable[bs4.element.Tag], valid_categories: List[str]) -> List[str]:
    leagues: List[str] = []
    for cell in cells:
        match = LEAGUE_REGEX.search(str(cell))
        if match is None or match.group() in valid_categories:
            leagues.append("")
        else:
            leagues.append(match.group())
    return leagues


def _extract_performance_bands(cells: Iterable[bs4.element.Tag], valid: List[str]) -> List[str]:
    bands: List[str] = []
    for cell in cells:
        match = PERF_REGEX.search(str(cell))
        found = match.group() if match else ""
        bands.append(found if found in valid else "")
    return bands


def _extract_categories(cells: Iterable[bs4.element.Tag], valid_categories: List[str]) -> List[Optional[str]]:
    categories: List[Optional[str]] = []
    for cell in cells:
        matches = CATEGORY_REGEX.findall(str(cell))
        if not matches:
            categories.append(None)
        elif len(matches) > 1 and matches[1] in valid_categories:
            categories.append(matches[1])
        else:
            categories.append(matches[0] if matches[0] in valid_categories else None)
    return categories


def _extract_birth_years(cells: Iterable[bs4.element.Tag], valid_categories: List[str]) -> List[Optional[int]]:
    years: List[Optional[int]] = []
    for cell in cells:
        match = YEAR_REGEX.search(str(cell))
        if match is None or match.group() in valid_categories:
            years.append(None)
            continue
        yy = int(str(match.group()).replace("/", "").replace("<", ""))
        years.append(yy + 2000 if yy <= 20 else yy + 1900)
    return years


def _performance_bands() -> dict[str, int]:
    return {
        "IA": 40,
        "IB": 35,
        "N1": 30,
        "N2": 28,
        "N3": 26,
        "N4": 24,
        "IR1": 21,
        "IR2": 20,
        "IR3": 19,
        "IR4": 18,
        "R1": 15,
        "R2": 14,
        "R3": 13,
        "R4": 12,
        "R5": 11,
        "R6": 10,
        "D1": 8,
        "D2": 7,
        "D3": 6,
        "D4": 5,
        "D5": 4,
        "D6": 3,
        "D7": 2,
    }


def _age_categories_fr() -> dict[str, str]:
    return {
        "M10": "Masters 10",
        "M9": "Masters 9",
        "M8": "Masters 8",
        "M7": "Masters 7",
        "M6": "Masters 6",
        "M5": "Masters 5",
        "M4": "Masters 4",
        "M3": "Masters 3",
        "M2": "Masters 2",
        "M1": "Masters 1",
        "M0": "Masters 0",
        "SE": "Seniors",
        "ES": "Espoirs",
        "JU": "Juniors",
        "CA": "Cadets",
        "MI": "Minimes",
        "BE": "Benjamins",
        "PO": "Poussins",
        "EA": "Ecole d'Athlétisme",
        "BB": "Baby Athlé",
    }


def _expand_categories_with_gender(cat: dict[str, str]) -> List[str]:
    with_gender: List[str] = []
    for key in cat.keys():
        with_gender.append(f"{key}F")
    for key in cat.keys():
        with_gender.append(f"{key}M")
    return with_gender


def parse_results_from_rows(rows: Iterable[bs4.element.Tag]) -> Tuple[List[str], List[pd.Timestamp], List[str], List[str], List[Optional[str]], List[Optional[int]]]:
    categories = _expand_categories_with_gender(_age_categories_fr())
    times = _parse_times_from_cells(rows)
    leagues = _extract_leagues(rows, categories)
    perf_bands = _extract_performance_bands(rows, list(_performance_bands().keys()))
    categories_found = _extract_categories(rows, categories)
    years = _extract_birth_years(rows, categories)
    # Athletes use pattern by cell list
    athletes_nested: List[List[str]] = []
    for cell in rows:
        found = ATHLETE_REGEX.findall(str(cell))
        if found:
            athletes_nested.append(found)
    athletes = [x[0] for x in athletes_nested]
    return athletes, times, leagues, perf_bands, categories_found, years


def build_results_dataframe(
    athletes: List[str],
    times: List[pd.Timestamp],
    leagues: List[str],
    perf_bands: List[str],
    categories: List[Optional[str]],
    years: List[Optional[int]],
) -> pd.DataFrame:
    # find offset where categories is not None
    offset = 0
    while offset < len(categories) and categories[offset] is None:
        offset += 1

    rows: List[List[object]] = []
    for i, athlete in enumerate(athletes):
        row: List[object] = [
            athlete,
            leagues[i + offset] if i + offset < len(leagues) else "",
            times[i],
            perf_bands[i + offset] if i + offset < len(perf_bands) else "",
            years[i + offset] if i + offset < len(years) else None,
            categories[i + offset] if i + offset < len(categories) else None,
        ]
        rows.append(row)

    df = pd.DataFrame(
        rows,
        columns=[
            "Athlete",
            "League",
            "FinishTime",
            "Performance",
            "BirthYear",
            "Category",
        ],
    )

    df["hours"] = df["FinishTime"].dt.hour
    df["minutes"] = df["FinishTime"].dt.minute
    df["seconds"] = df["FinishTime"].dt.second

    df["time_delta"] = df["FinishTime"] - pd.to_datetime('1900-01-01')
    df = df.sort_values("time_delta").reset_index(drop=True)
    df["time_gap"] = df["FinishTime"] - df["FinishTime"][0]
    df["duration"] = df["time_delta"].dt.total_seconds()

    # Split names into FirstName / LastName
    df["FirstName"] = df["Athlete"].str.extract("[A-Z]+(?:[- ]?[A-Z]+)? (.+)")
    df["LastName"] = df["Athlete"].str.replace(df["FirstName"].astype(str), "", regex=False)

    # Duration as HH:MM:SS string
    df["DurationHMS"] = pd.to_timedelta(df["duration"], unit="s").apply(
        lambda x: f"{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}"
    )

    # Final columns
    return df[[
        "Athlete",
        "LastName",
        "FirstName",
        "League",
        "Performance",
        "BirthYear",
        "Category",
        "duration",
        "DurationHMS",
        "time_gap",
    ]].rename(columns={"duration": "DurationSeconds"})


def scrape_competition(url: str, num_pages: int) -> Tuple[CompetitionHeader, pd.DataFrame]:
    if num_pages <= 0:
        raise ValueError("num_pages must be greater than 0")

    all_rows: List[bs4.element.Tag] = []
    header: Optional[CompetitionHeader] = None
    for i in range(num_pages):
        page = fetch_page(url, i)
        all_rows.extend(extract_rows(page))
        header = parse_header(page)
    if header is None:
        header = CompetitionHeader(name="", location="", date="", department=None, label=None)

    athletes, times, leagues, perf_bands, categories, years = parse_results_from_rows(all_rows)
    df = build_results_dataframe(athletes, times, leagues, perf_bands, categories, years)
    return header, df


def scrape_latest_competitions(limit: int) -> List[dict]:
    index_url = "https://bases.athle.fr/asp.net/accueil.aspx?frmbase=resultats"
    html = _get(index_url)
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="ctnResultats")
    comps: List[dict] = []
    if table:
        rows = table.find_all("tr")[1:]
        for row in rows[:limit]:
            cols = row.find_all("td")
            if len(cols) >= 9:
                date = cols[4].text.strip()
                family = cols[6].text.strip()
                label = cols[8].text.strip()
                location = cols[10].text.strip()
                rel = cols[0].find("a")["href"] if cols[0].find("a") else None
                full = f"https://bases.athle.fr{rel}" if rel else None
                comps.append({
                    "Date": date,
                    "Family": family,
                    "Label": label,
                    "Location": location,
                    "URL": full,
                })
    return comps
