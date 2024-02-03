import sys
import os
import bs4
import pandas as pd
import numpy as np
import re
from urllib import request

def install_lxml():
    """Install lxml if not already installed."""
    os.system('pip install lxml')

def read_input():
    """Read command line arguments."""
    if len(sys.argv[1:])<=2:
        url=sys.argv[1:][0]
        nb_pages=sys.argv[1:][1]
        return(url, int(nb_pages))
    else: 
        return("Bad parameter value", None)

#bareme et table de cotation
#source: https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=125

def get_perf():
    """Return performance levels."""
    return {'IA': 40, 'IB': 35, #international
            'N1': 30, 'N2': 28, 'N3': 26, 'N4': 24, #national
            'IR1': 21, 'IR2': 20, 'IR3': 19, 'IR4': 18, #inter-regional
            'R1': 15, 'R2': 14, 'R3': 13, 'R4': 12, 'R5': 11, 'R6': 10, #regional
            'D1': 8, 'D2': 7, 'D3': 6, 'D4': 5, 'D5': 4, 'D6': 3, 'D7': 2} #departemental

#categories d'âge en 2023
#source: https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=25

def get_cat():
    """Return age categories."""
    return {'M10': 'Masters 10', 'M9': 'Masters 9', 'M8': 'Masters 8', 'M7': 'Masters 7', 'M6': 'Masters 6',
           'M5': 'Masters 5', 'M4': 'Masters 4', 'M3': 'Masters 3', 'M2': 'Masters 2', 'M1': 'Masters 1', 'M0': 'Masters 0',
           'SE': 'Seniors',
           'ES': 'Espoirs',
           'JU': 'Juniors',
           'CA': 'Cadet.te.s',
           'MI': 'Minimes',
           'BE': 'Benjamin.e.s',
           'PO': 'Poussins',
           'EA': 'École d\'Athlétisme',
           'BB': 'Baby Athlé'}

def get_categories(cat):
    """Add gender (F/M) to categories."""
    categoriesF=list(cat.keys())
    for i in range(len(categoriesF)):
        categoriesF[i]+='F'

    categoriesM=list(cat.keys())
    for i in range(len(categoriesM)):
        categoriesM[i]+='M'

    return categoriesF+categoriesM

def get_page(url, i):
    """Get page content from url."""
    url_i=url+"&frmposition="+str(i)
    request_text = request.urlopen(url_i).read()
    return bs4.BeautifulSoup(request_text, "lxml")

def get_rows(page, nb_pages):
    """Get all rows from the page."""
    rows=[]
    for i in range(nb_pages):
        for i in page.find_all('tr'):
            if "groups" not in str(i) and "mainheaders" not in str(i) and "barButtons" not in str(i) and "subheaderscom" not in str(i):
                rows.append(i)
    return rows

def read_header(page):
    """Read header information from the page."""
    header = page.find('div', {'class' : "mainheaders"})
    header=str(header)

    re_nom = re.compile("(?<=\- )(.*?)(?=\<)")
    text = re_nom.findall(header)
    nom = text[0]
    sous_titre = text[1]

    re_lieu = re.compile("(?<=\>)(\D*?)(?=\ -)")
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
        label=None

    compet= {'nom': nom,
    'lieu': lieu,
    'date': date,
    'dept': dept,
    'label': label}

    return compet

def get_athletes(L):
    """Get athletes names."""
    re_athlete = re.compile("[A-Z]{2,} ?-?[A-Z]* ?-?[A-Z]* ?-?[A-Z]*[A-Z]{1}[a-z]+ ?-?[A-Z]?[a-z]*")
    athletes=[]
    for i in L:
        athletes.append(re_athlete.findall(str(i)))
    athletes=[x for x in athletes if x!=[]]
    return athletes

def get_temps(L):
    """Get finish time."""
    re_temps = re.compile("<b>(?=\d).*(?=<\/b>)")
    temps=[]
    for i in L:
        temps.append(re_temps.findall(str(i)))
    temps=[x for x in temps if x!=[]]
    for i in range(len(temps)):
        temps[i]=temps[i][0].replace("<b>","")
        try:
            temps[i]=pd.to_datetime(temps[i], format='%Hh%M\'%S\'\'')
        except ValueError as e:
            pass #ignore error and try next datetime format
        try:
            temps[i]=pd.to_datetime(temps[i], format='%M\'%S\'\'')
        except ValueError as e:
            pass #ignore error and try next datetime format
        try:
            temps[i]=pd.to_datetime(temps[i], format='%S\'\'')
        except ValueError as e:
            pass #ignore error and try next datetime format
    return temps

def get_ligue(L, categories):
    """Get league name."""
    re_ligue = re.compile("[A-Z]{3,}(?=<)|[A-Z]-[A-Z](?=<)")
    ligue=[]
    for i in L:
        match = re_ligue.search(str(i))
        if (match==None) or (match.group() in categories):
            ligue.append('0')
        else:
            ligue.append(match.group())
    return ligue

def get_perfs(L, perf):
    """Get performance level."""
    re_perf = re.compile("[A-Z]{1,2}[1-8](?=<)|I[A,B](?=<)")
    perfs=[]
    for i in L:
        match= str(re_perf.findall(str(i))).replace('[','').replace(']','').replace('\'','')
        if match in list(perf.keys()):
            perfs.append(match)
        else:
            perfs.append('')
    return perfs

def get_categorie(L, categories):
    """Get age category."""
    re_cat = re.compile("[A-Z]{3}(?=<)|[A-Z]{1}\d[A-Z]{1}")
    categorie=[]
    for i in L:
        match = re_cat.search(str(i))
        if (match==None):
            categorie.append(None)
        else:
            match = re_cat.findall(str(i))
            if len(match)>1 and (match[1] in categories):
                categorie.append(match[1])
            else:
                if (match[0] in categories):
                    categorie.append(match[0])
    return categorie

def get_annee(L, categories):
    """Get birth year."""
    re_annee = re.compile("\/[0-9]{2}<")
    annee=[]
    for i in L:
        match = re_annee.search(str(i))
        if (match==None) or (match.group() in categories):
            annee.append('0')
        else:
            year = int(str(match.group()).replace('/','').replace('<',''))
            if year <=20:
                annee.append(year+2000)
            else:
                annee.append(year+1900)
    return annee

def get_liste(L, categories, perf):
    """Get all data from the page."""
    athletes=get_athletes(L)
    temps=get_temps(L)
    ligue=get_ligue(L, categories)
    perfs=get_perfs(L, perf)
    categorie=get_categorie(L, categories)
    annee=get_annee(L, categories)
    return athletes, temps, ligue, perfs, categorie, annee

def get_data(liste):
    """Create a dataframe from the data."""
    athletes=liste[0]
    temps=liste[1]
    ligue=liste[2]
    perfs=liste[3]
    categorie=liste[4]
    annee=liste[5]

    debut=0
    while categorie[debut]==None:
        debut+=1

    liste=[]
    for i in range(len(athletes)):
        ligne=[]
        ligne.append(athletes[i][0])
        ligne.append(ligue[i+debut])
        #ligne.append(str(clubs[i+debut]))
        ligne.append(temps[i])
        ligne.append(perfs[i+debut])
        ligne.append(annee[i+debut])
        ligne.append(categorie[i+debut])
        liste.append(ligne)

    data=pd.DataFrame(liste, columns=["Athlète", "Ligue", "Chrono", "Performance", "Naissance", "Catégorie"])

    data['hours']=data['Chrono'].dt.hour
    data['minutes']=data['Chrono'].dt.minute
    data['seconds']=data['Chrono'].dt.second

    data['time_delta']=data['Chrono']-pd.to_datetime("'1900-01-01")
    data=data.sort_values('time_delta')
    data=data.reset_index(drop=True)

    data['time_gap']=data["Chrono"]-data['Chrono'][0]
    data['duration']=data['time_delta'].dt.total_seconds()

    data=data.drop("Chrono", axis=1)

    return data
    
def main():
    """Main function."""
    install_lxml()
    try:
        url, nb_pages = read_input()
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
    for i in range(nb_pages):
        page = get_page(url, i)
        rows += get_rows(page, nb_pages)
    header = read_header(page)
    print(header)
    athletes, temps, ligue, perfs, categorie, annee = get_liste(rows, categories, perf)
    liste = [athletes, temps, ligue, perfs, categorie, annee]
    data = get_data(liste)
    print(data.head(10))
    data.to_csv("output.csv", index=False)

if __name__ == "__main__":
    """Run main function."""
    main()