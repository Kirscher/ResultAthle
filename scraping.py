import sys
import os
import lxml
import urllib
import bs4
import pandas as pd
import numpy as np
import re
from urllib import request

os.system('pip install lxml')

def read_input():
    if len(sys.argv[1:])<=2:
        url=sys.argv[1:][0]
        nb_pages=sys.argv[1:][1]
        return(url, int(nb_pages))
    else: 
        return("Bad parameter value")

try:
    url, nb_pages=read_input()
except ValueError:
    print( "Bad parameter value")
    exit()

#bareme et table de cotation
#source: https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=125

perf = {'IA': 40, 'IB': 35, #international
        'N1': 30, 'N2': 28, 'N3': 26, 'N4': 24, #national
        'IR1': 21, 'IR2': 20, 'IR3': 19, 'IR4': 18, #inter-regional
        'R1': 15, 'R2': 14, 'R3': 13, 'R4': 12, 'R5': 11, 'R6': 10, #regional
        'D1': 8, 'D2': 7, 'D3': 6, 'D4': 5, 'D5': 4, 'D6': 3, 'D7': 2} #departemental

#categories d'âge en 2023
#source: https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=25

cat = {'M10': 'Masters 10', 'M9': 'Masters 9', 'M8': 'Masters 8', 'M7': 'Masters 7', 'M6': 'Masters 6',
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

#ajout de féminin (F) et masculin (M) aux categories

categoriesF=list(cat.keys())

#ajout des catégories féminines
for i in range(len(categoriesF)):
    categoriesF[i]+='F'
categoriesM=list(cat.keys())

#ajout des catégories masculines
for i in range(len(categoriesM)):
    categoriesM[i]+='M'
    
categories=categoriesF+categoriesM

L=[]
for i in range(nb_pages):
    url_i=url+"&frmposition="+str(i)
    request_text = request.urlopen(url_i).read()
    page = bs4.BeautifulSoup(request_text, "lxml")
    for i in page.find_all('tr'):
        if "groups" not in str(i) and "mainheaders" not in str(i) and "barButtons" not in str(i) and "subheaderscom" not in str(i):
            L.append(i)
    url_i=url

def read_header(page):
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
        print(label)
    except IndexError:
        print("Pas de label pour cette compétition")
        label=None

    compet= {'nom': nom,
    'lieu': lieu,
    'date': date,
    'dept': dept,
    'label': label}

    return compet

print(read_header(page))

re_athlete = re.compile("[A-Z]{2,} ?-?[A-Z]* ?-?[A-Z]* ?-?[A-Z]*[A-Z]{1}[a-z]+ ?-?[A-Z]?[a-z]*")
athletes=[]
for i in L:
    athletes.append(re_athlete.findall(str(i)))
athletes=[x for x in athletes if x!=[]]

re_temps = re.compile("<b>(?=\d).*(?=<\/b>)")
temps=[]
for i in L:
    temps.append(re_temps.findall(str(i)))
temps=[x for x in temps if x!=[]]
for i in range(len(temps)):
    temps[i]=temps[i][0].replace("<b>","")
    temps[i]=pd.to_datetime(temps[i], format='%Hh%M\'%S\'\'', errors='ignore')
    temps[i]=pd.to_datetime(temps[i], format='%M\'%S\'\'', errors='ignore')
    temps[i]=pd.to_datetime(temps[i], format='%S\'\'', errors='ignore')

re_ligue = re.compile("[A-Z]{3,}(?=<)|[A-Z]-[A-Z](?=<)")
ligue=[]
for i in L:
    match = re_ligue.search(str(i))
    if (match==None) or (match.group() in categories):
        ligue.append('0')
    else:
        ligue.append(match.group())

re_perf = re.compile("[A-Z]{1}[1-8](?=<)|I[A,B](?=<)")
perfs=[]
for i in L:
    match= str(re_perf.findall(str(i))).replace('[','').replace(']','').replace('\'','')
    if match in list(perf.keys()):
        perfs.append(match)
    else:
        perfs.append('')

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

#identification du début de la table de résultats individuels à l'aide de la liste des catégories 
i = 0
while categorie[i]==None:
    i+=1
debut=i
print(debut)

liste=[]
for i in range(len(athletes)):
    ligne=[]
    ligne.append(athletes[i][0])
    ligne.append(ligue[i+debut])
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

print(data.head(10))

data.to_csv("output.csv", index=False)