import sys
import re
from urllib import request
import bs4
import pandas as pd


def read_input():
    """
    Read command line arguments.

    Returns
    -------
    tuple
        A tuple containing the URL and the number of pages to scrape.
        If the URL or number of pages is not provided, returns an error message and None.
    """

    if len(sys.argv) < 2:
        return ("No URL provided", None)
    elif len(sys.argv[1:]) < 2:
        return ("Number of pages not provided", None)
    elif len(sys.argv[1:]) == 2:
        url = sys.argv[1:][0]
        nb_pages = sys.argv[1:][1]
        return (url, int(nb_pages))
    else:
        return ("Bad parameter value", None)


# bareme et table de cotation
# source: https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=125


def get_perf():
    """
    Return performance levels.

    Returns
    -------
    dict
        A dictionary mapping performance levels to their corresponding values.
    """

    return {
        "IA": 40,
        "IB": 35,  # international
        "N1": 30,
        "N2": 28,
        "N3": 26,
        "N4": 24,  # national
        "IR1": 21,
        "IR2": 20,
        "IR3": 19,
        "IR4": 18,  # inter-regional
        "R1": 15,
        "R2": 14,
        "R3": 13,
        "R4": 12,
        "R5": 11,
        "R6": 10,  # regional
        "D1": 8,
        "D2": 7,
        "D3": 6,
        "D4": 5,
        "D5": 4,
        "D6": 3,
        "D7": 2,
    }  # departemental


# categories d'âge en 2023
# source: https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=25


def get_cat():
    """
    Return age categories.

    Returns
    -------
    dict
        A dictionary mapping age categories to their corresponding labels.
    """

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
        "CA": "Cadet.te.s",
        "MI": "Minimes",
        "BE": "Benjamin.e.s",
        "PO": "Poussins",
        "EA": "École d'Athlétisme",
        "BB": "Baby Athlé",
    }


def get_categories(cat):
    """
    Add gender (F/M) to categories.

    Parameters
    ----------
    cat : dict
        A dictionary containing the categories.

    Returns
    -------
    list
        A list of categories with appended gender labels.
    """

    categoriesF = list(cat.keys())
    for i in range(len(categoriesF)):
        categoriesF[i] += "F"

    categoriesM = list(cat.keys())
    for i in range(len(categoriesM)):
        categoriesM[i] += "M"

    return categoriesF + categoriesM


def get_page(url, i):
    """
    Get page content from URL.

    Parameters
    ----------
    url : str
        The URL of the page.
    i : int
        The page number.

    Returns
    -------
    bs4.BeautifulSoup or None
        The BeautifulSoup object containing the page content, or None if an error occurs.
    """

    url_i = url + "&frmposition=" + str(i)
    try:
        with request.urlopen(url_i) as response:
            request_text = response.read().decode("utf-8")
    except request.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None
    else:
        return bs4.BeautifulSoup(request_text, "lxml")


def get_rows(page):
    """
    Get all rows from the page.

    Parameters
    ----------
    page : bs4.BeautifulSoup
        The BeautifulSoup object representing the page.

    Returns
    -------
    list
        A list of rows extracted from the page.
    """

    rows = []
    for i in page.find_all("tr"):
        if (
            "groups" not in str(i)
            and "headers" not in str(i)
            and "mainheaders" not in str(i)
            and "barButtons" not in str(i)
            and "subheaderscom" not in str(i)
        ):
            rows.append(i)
    return rows


def read_header(page):
    """
    Read header information from the page.

    Parameters
    ----------
    page : bs4.BeautifulSoup
        The BeautifulSoup object representing the page.

    Returns
    -------
    dict
        A dictionary containing header information such as competition name, location, date,
        department, and label.
    """

    header = page.find("div", {"class": "mainheaders"})
    header = str(header)

    re_nom = re.compile(r"(?<=\- )(.*?)(?=\<)")
    text = re_nom.findall(header)
    nom = text[0]
    sous_titre = text[1]

    re_lieu = re.compile(r"(?<=\>)(\D*?)(?=\ -)")
    lieu = re_lieu.findall(header)[0]

    re_date = re.compile("[0-9]{2}/[0-9]{2}/[0-9]{2}")
    date = re_date.findall(header)[0]

    re_dept = re.compile("[0-9]{3}")
    dept = re_dept.findall(sous_titre)[0]

    re_label = re.compile("(?<=Label ).*(?<!')")
    try:
        label = re_label.findall(sous_titre)[0]
    except IndexError:
        print("Pas de label pour cette compétition")
        label = None

    compet = {"nom": nom, "lieu": lieu, "date": date, "dept": dept, "label": label}

    return compet


def get_athletes(L):
    """
    Get athletes' names.

    Parameters
    ----------
    L : list
        A list of items from which to extract athletes' names.

    Returns
    -------
    list
        A list of athletes' names.
    """

    re_athlete = re.compile(
        "[A-Z]{2,} ?-?[A-Z]* ?-?[A-Z]* ?-?[A-Z]*[A-Z]{1}[a-z]+ ?-?[A-Z]?[a-z]*"
    )
    athletes = []
    for i in L:
        athletes.append(re_athlete.findall(str(i)))
    athletes = [x for x in athletes if x != []]
    return athletes


def get_temps(L):
    """
    Get finish times.

    Parameters
    ----------
    L : list
        A list of items from which to extract finish times.

    Returns
    -------
    list
        A list of finish times.
    """

    re_temps = re.compile(r"<b>(?=\d).*(?=<\/b>)")
    temps = []
    for i in L:
        temps.append(re_temps.findall(str(i)))
    temps = [x for x in temps if x != []]
    for i in range(len(temps)):
        temps[i] = temps[i][0].replace("<b>", "")
        try:
            temps[i] = pd.to_datetime(temps[i], format="%Hh%M'%S''")
        except ValueError:
            pass  # ignore error and try next datetime format
        try:
            temps[i] = pd.to_datetime(temps[i], format="%M'%S''")
        except ValueError:
            pass  # ignore error and try next datetime format
        try:
            temps[i] = pd.to_datetime(temps[i], format="%S''")
        except ValueError:
            pass  # ignore error and try next datetime format
    return temps


def get_ligue(L, categories):
    """
    Get league names.

    Parameters
    ----------
    L : list
        A list of items from which to extract league names.
    categories : list
        A list of categories.

    Returns
    -------
    list
        A list of league names.
    """

    re_ligue = re.compile("[A-Z]{3,}(?=<)|[A-Z]-[A-Z](?=<)")
    ligue = []
    for i in L:
        match = re_ligue.search(str(i))
        if (match is None) or (match.group() in categories):
            ligue.append("0")
        else:
            ligue.append(match.group())
    return ligue


def get_perfs(L, perf):
    """
    Get performance levels.

    Parameters
    ----------
    L : list
        A list of items from which to extract performance levels.
    perf : dict
        A dictionary containing performance levels.

    Returns
    -------
    list
        A list of performance levels.
    """

    re_perf = re.compile("[A-Z]{1,2}[1-8](?=<)|I[A,B](?=<)")
    perfs = []
    for i in L:
        match = (
            str(re_perf.findall(str(i)))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        if match in list(perf.keys()):
            perfs.append(match)
        else:
            perfs.append("")
    return perfs


def get_categorie(L, categories):
    """
    Get age categories.

    Parameters
    ----------
    L : list
        A list of items from which to extract age categories.
    categories : list
        A list of categories.

    Returns
    -------
    list
        A list of age categories.
    """

    re_cat = re.compile(r"[A-Z]{3}(?=<)|[A-Z]{1}\d[A-Z]{1}")
    categorie = []
    for i in L:
        match = re_cat.search(str(i))
        if match is None:
            categorie.append(None)
        else:
            match = re_cat.findall(str(i))
            if len(match) > 1 and (match[1] in categories):
                categorie.append(match[1])
            else:
                if match[0] in categories:
                    categorie.append(match[0])
    return categorie


def get_annee(L, categories):
    """
    Get birth years.

    Parameters
    ----------
    L : list
        A list of items from which to extract birth years.
    categories : list
        A list of categories.

    Returns
    -------
    list
        A list of birth years.
    """

    re_annee = re.compile(r"\/[0-9]{2}<")
    annee = []
    for i in L:
        match = re_annee.search(str(i))
        if (match is None) or (match.group() in categories):
            annee.append("0")
        else:
            year = int(str(match.group()).replace("/", "").replace("<", ""))
            if year <= 20:
                annee.append(year + 2000)
            else:
                annee.append(year + 1900)
    return annee


def get_liste(L, categories, perf):
    """
    Get all data from the page.

    Parameters
    ----------
    L : list
        A list of items from which to extract data.
    categories : list
        A list of categories.
    perf : dict
        A dictionary containing performance levels.

    Returns
    -------
    tuple
        A tuple containing lists of athletes, finish times, league names, performance levels,
        age categories, and birth years.
    """

    athletes = get_athletes(L)
    temps = get_temps(L)
    ligue = get_ligue(L, categories)
    perfs = get_perfs(L, perf)
    categorie = get_categorie(L, categories)
    annee = get_annee(L, categories)
    return athletes, temps, ligue, perfs, categorie, annee


def get_data(liste):
    """
    Create a dataframe from the data.

    Parameters
    ----------
    liste : tuple
        A tuple containing lists of athletes, finish times, league names, performance levels,
        age categories, and birth years.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the extracted data.
    """

    athletes = liste[0]
    temps = liste[1]
    ligue = liste[2]
    perfs = liste[3]
    categorie = liste[4]
    annee = liste[5]

    debut = 0
    while categorie[debut] is None:
        debut += 1

    liste = []
    for i in range(len(athletes)):
        ligne = []
        ligne.append(athletes[i][0])
        ligne.append(ligue[i + debut])
        # ligne.append(str(clubs[i+debut]))
        ligne.append(temps[i])
        ligne.append(perfs[i + debut])
        ligne.append(annee[i + debut])
        ligne.append(categorie[i + debut])
        liste.append(ligne)

    data = pd.DataFrame(
        liste,
        columns=["Athlète", "Ligue", "Chrono", "Performance", "Naissance", "Catégorie"],
    )

    data["hours"] = data["Chrono"].dt.hour
    data["minutes"] = data["Chrono"].dt.minute
    data["seconds"] = data["Chrono"].dt.second

    data["time_delta"] = data["Chrono"] - pd.to_datetime("'1900-01-01")
    data = data.sort_values("time_delta")
    data = data.reset_index(drop=True)

    data["time_gap"] = data["Chrono"] - data["Chrono"][0]
    data["duration"] = data["time_delta"].dt.total_seconds()

    data = data.drop("Chrono", axis=1)

    # Add columns for first name and last name
    data['Prénom'] = data['Athlète'].str.extract('[A-Z]+(?:[- ]?[A-Z]+)? (.+)')
    data['Nom'] = data.apply(lambda row: row['Athlète'].replace(row['Prénom'], ''), axis=1)

    # Add column for duration in hours
    data['h_duration'] = data['duration'].apply(
                                    lambda x: pd.to_datetime(x, unit="s").strftime('%H:%M:%S')
                                    )

    return data


def get_results(url, nb_pages):
    """
    Main scraping function.

    Parameters
    ----------
    url : str
        The URL to scrape.
    nb_pages : int
        The number of pages to scrape.

    Returns
    -------
    tuple
        A tuple containing header information and a DataFrame of extracted data.
    """

    try:
        if nb_pages is None:
            print(url)  # url contains the error message in this case
            sys.exit()
    except ValueError:
        print("Bad parameter value")
        sys.exit()

    perf = get_perf()
    cat = get_cat()
    categories = get_categories(cat)
    rows = []
    if nb_pages > 0:
        for i in range(nb_pages):
            page = get_page(url, i)
            rows += get_rows(page)
        header = read_header(page)
    else:
        print("Error: nb_pages must be greater than 0")
        return
    athletes, temps, ligue, perfs, categorie, annee = get_liste(rows, categories, perf)
    liste = [athletes, temps, ligue, perfs, categorie, annee]
    data = get_data(liste)
    return header, data

def scrape_last_competitions(num_competitions):
    """
    Scrapes the last `num_competitions` competitions from the website https://bases.athle.fr/asp.net/accueil.aspx?frmbase=resultats.

    Args:
        num_competitions (int): The number of competitions to scrape.

    Returns:
        list: A list of dictionaries containing information about the competitions. Each dictionary contains the following keys:
            - 'Date': The date of the competition.
            - 'Famille': The category of the competition.
            - 'Libellé': The label of the competition.
            - 'Lieu': The location of the competition.
            - 'URL': The URL of the competition.

    """
    url = "https://bases.athle.fr/asp.net/accueil.aspx?frmbase=resultats"
    try:
        with request.urlopen(url) as response:
            request_text = response.read().decode("utf-8")
    except request.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return
    else:
        soup = bs4.BeautifulSoup(request_text, 'html.parser')
        table = soup.find('table', id='ctnResultats')

    competitions = []
    if table:
        rows = table.find_all('tr')[1:]
        for row in rows[:num_competitions]:
            cols = row.find_all('td')
            if len(cols) >= 9:  
                date = cols[4].text.strip()
                famille = cols[6].text.strip()
                libelle = cols[8].text.strip()
                lieu = cols[10].text.strip()
                url_competition = cols[0].find('a')['href'] if cols[0].find('a') else None
                if url_competition:
                    url_competition = "https://bases.athle.fr" + url_competition # add prefix
                competitions.append({'Date': date, 'Famille': famille, 'Libellé': libelle, 'Lieu': lieu, 'URL': url_competition})
                
    return competitions
