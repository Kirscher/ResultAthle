# Algorithmes pour séparer les couteurs en catégories et identifier les pics de performance

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as pltlines
import matplotlib.colors as colors
import math
import statsmodels.tsa.filters.hp_filter as stat

import seaborn as sns
from datetime import datetime
import time
import scipy

from sklearn.neighbors import KernelDensity


def idealBins(l):
    # Trouve ne bon nombre de batch à utiliser. A force d'essais, on constate qu'au delà de 25, le signal est trop précis pour en tirer une loi lisse, au dessous de 10, ce package n'a plus d'intérêt.
    # Input : l : longueur d'un data frame (ou autre itérable)
    # Output : bins : nombre entier, à entrer dans les arguments de la fonction dens

    return int(
        np.rint(max(min(10 + (l - 100) / 70, 25), 10))
    )  # +1 batch par 70 personnes, entre 10 et 25.


def dens(dur, **kwargs):
    # calcule une densité d'un itérable
    # **kwargs vont etre redonnés à la fonction maptplotlib.pyplot.hist
    # l'argument density est forcé à : True
    # input :  dur, itérable (liste, série...) de dimension 1 contenant les valeurs dont la densité nous intéresse
    # output : dens : array nupmy de dimension 2, dens[0] : abscisses des points, dens[1] : ordonnées des points

    # bins = 20 pour un marathon,
    # bins = 12 pour un 10km
    kwargs["density"] = True
    h = plt.hist(dur, **kwargs)
    xhist = []
    plt.close()
    for i in range(len(h[1]) - 1):
        x = (h[1][i + 1] + h[1][i]) / 2
        xhist.append(x)

    densite = np.zeros((2, len(xhist)))
    densite[0, :] = xhist
    densite[1, :] = h[0]
    return densite


def skdensiteLissee(dur, **kwargs):
    # cette fonction permet de trouver une densité sans passeer par les histogrammes
    # Input : dur : array numpy de taille (1,n) ou (n,1) contenant les données dont la distribution nous intéresse
    # Output : fonction à appliquer à un array numpy de taille (1,n) ou (k,1) pour calculer la valeur de la densité en ces points

    dur = dur.reshape(-1, 1)  # format demandé par KernelDensity
    kde = KernelDensity(
        kernel="epanechnikov", bandwidth=150, **kwargs
    )  # bandwidth déterminée au jugé
    a = kde.fit(dur)

    def f(x):
        return np.exp(a.score_samples(x.reshape(-1, 1)))

    return f


def separate(densite):
    # prend en argument un array numpy de valeurs et sépare le signal en "tendance" et "bruit" avec un lambda de 0.1
    # input :  densite : array numpy de dimension 2, taille (k,n)
    # output : array nupmy de dimension 2, taille (k+1,n) où les 2 dernières lignes sont le bruit et la tendance de la derniere ligne de l'input

    b, t = stat.hpfilter(densite[-1, :], lamb=0.01)
    result = np.zeros((len(densite) + 1, len(densite[0])))
    result[0 : len(densite), :] = densite
    result[-2] = b
    result[-1] = t
    return result


def lissage(
    x, sep=False, kind="cubic", beginend=False
):  # sans **kwargs pour simplifier son utilisation
    # prend en argument un ensemble de points à interpoler stockés dans un array numpy et retourne la fonction d'interpolation cubique si kind = 'cubic' ou linéaire sinon
    # Input :    x : array numpy de dimension 2, taille(2,n) avec les abscisses des points à interpoler dans x[0] et leurs ordonnées dans x[1]
    #          sep : booléen. True si le signal doit être filtré par un HP filter
    #         kind : 'cubic' pour une interpolation polyonomiale par morceaux, l'interpolation est linéaire sinon
    #     beginend : tuple. Permet de forcer la fonction à prendre des valeurs nulles en beginend[0] et beginend[1]
    # Output :   f : fonction d'une seule variable

    if (
        beginend != False
    ):  # pour imposer des points de début et de fin (ne sert que pour le tracé, pas les calculs !)
        begin = np.zeros((2, 1))
        end = np.zeros((2, 1))
        begin[0, 0] = beginend[0]
        end[0, 0] = beginend[-1]

        x = np.concatenate((begin, x, end), axis=1)

    if sep == True:

        t = separate(x)[2]
    else:
        t = x[1]
    if kind == "cubic":
        poly = scipy.interpolate.splrep(x[0], t)

        def f(X):
            return np.maximum(
                scipy.interpolate.splev(X, poly, der=0), 0
            )  # le max sert à faire des graphes où la densité est toujours positive

    else:
        interp = scipy.interpolate.interp1d(
            x[0], t, kind="linear", fill_value="extrapolate"
        )

        def f(X):
            return interp(X)

    return f


def perfgoals(A):
    # Fonction qui retrouve les pics de densité dans une distribution estimée, et les rend dans leur ordre d'importance
    # input :        A : array numpy de dimension 2, taille (2,n) avec A[0] les abscisses et A[1] les ordonnées des points mesurés
    # output :  result : array numpy de dimension 2, taille (2,k) avec result[0] les abscisses des pics et result[1] les valeurs de la densite en ces points
    #                   l'output est trié par ordre d'importance (hauteur des pics)
    signal = separate(A)
    poly = scipy.interpolate.splrep(signal[0], signal[1])

    # derivee du bruit
    def f1(x):
        return 1e2 * scipy.interpolate.splev(x, poly, der=1)

    # derivee seconde pour la concavite
    def f2(x):
        return 1e2 * scipy.interpolate.splev(x, poly, der=2)

    guess = signal[
        0
    ]  # on s'attend à ce que les points critiques soient proches des points où la é est mesurée
    roots = scipy.optimize.root(f1, guess).x  # trouve les zéros de f1
    # dans le cadre du cours, il est meilleur d'utiliser un pd.Series, et de sélectionner les valeurs à l'aide d'un vecteur booléen. plutôt que de travailler sur un array ou une liste
    r = pd.Series(roots)
    bools = abs(f1(r)) < 1e-4
    #     print(f'bools : {bools}')
    r = r[bools]
    #     print(f'vraies racines :\n{r}')
    # Les algorithmes de racines trouvent plusieurs fois les mêmes racines, à epsilon près. Supression des doublons:
    r = np.rint(
        r
    )  # rint (entier le plus proche) permet de se limiter aux valeurs entières et eliminer les doublons dûs à scipy.optimize.root
    #     print(f'arrondis : {r}')
    r.drop_duplicates(inplace=True)
    #     print(f'dédoubloné :\n{r}')
    r.sort_values(inplace=True)
    #     print((f"sorted : \n{r}"))

    # élimination des valeurs hors bornes:
    bool1 = r > A[0, 0]
    bool2 = r < A[0, -1]
    #     print(bool1)
    #     print(bool2)
    #     print(bool1*bool2)

    roots = list(r[bool1 * bool2])
    #     print(f"racines valables : {roots}")
    # ----------------------------- Ancienne méthode non robuste
    #     print(f"racines : {roots}")
    #     roots = list(set(np.rint(roots))) #floor permet de se limiter aux valeurs entieres et eliminer les doublons dus a scipy.optimize.root
    #     print(f"floor : {roots}")
    #     roots=sorted(roots)
    #     print((f"sorted : {roots}"))
    # -----------------------------
    tops = []
    for i in range(len(roots)):
        if f2(roots[i]) < 0:  # selection des maximums parmi les points critiques
            tops.append(roots[i])
    #     print(tops)
    realTops = []
    for i in tops:
        ind = np.argmin(abs(signal[0] - i))
        #         print(f'Comparaison : {signal[0,ind]} , {i}')
        realTops = realTops + [signal[0, ind]]

    # tri par ordre d'importance
    bruit = signal[0:2, :]
    g = lissage(bruit, sep=False, kind="linear")
    values = g(realTops)
    sortedTops = np.take(realTops, np.argsort(values))
    sortedTops = np.flip(sortedTops)
    values = np.flip(np.sort(values))

    h = lissage(
        A, sep=False, kind="linear"
    )  # pour retrouver les vraies valeurs aux points approximés. Les vraies valeurs sont recalculées plutôt que lues
    result = np.zeros((2, len(sortedTops)))
    result[0, :] = sortedTops
    result[1, :] = h(sortedTops)

    return result


def topbotts(A, sort="performance"):
    # retourne une liste contenant les abscisses des maxima locaux et une autre contenant les abscisses des minima locaux
    # Inputs : A : array numpy de dimension 2, taille (2,n) avec A[0] les abscisses et A[1] les ordonnées des points mesurés
    #      sort : façon de trier les outputs.
    #             -Soit par ordre croissant des abscisses ('performance')
    #             -Soit par ordre croissant de courbure, les clusters les plus distincts ('values')
    # Outputs : tops, botts : tupple de listes d'abscisses contenant sommets et creux.

    signal = separate(A)

    poly = scipy.interpolate.splrep(
        signal[0], signal[2]
    )  # interpolation polynomiale par morceaux de la tendance

    def f1(x):
        return 1e3 * scipy.interpolate.splev(
            x, poly, der=1
        )  # derivee de la fonction de tendance

    def f2(x):
        return 1e3 * scipy.interpolate.splev(
            x, poly, der=2
        )  # derivee seconde (pour tests de concavite)

    tendance = np.take(signal, [0, 2], axis=0)
    guess = A[
        0
    ]  # on s'attend à ce que les racines de f1 soient proches des abscisses originales, puisque les maximums originaux en font partie
    roots = scipy.optimize.root(f1, guess).x  # trouve les points critiques de f
    #    print(f"racines : {roots}\n")

    # parfois, scipy.optimize.roots trouve des "racines" qui ne le sont pas il faut nettoyer ces données:

    # dans le cadre du cours, il est meilleur d'utiliser un pd.Series, et de sélectionner les valeurs à l'aide d'un vecteur booléen. plutôt que de travailler sur un array ou une liste
    r = pd.Series(roots)
    bools = abs(f1(r)) < 1e-4
    #     print(f'bools : {bools}')
    r = r[bools]
    #     print(f'vraies racines :\n{r}')
    # Les algorithmes de racines trouvent plusieurs fois les mêmes racines, à epsilon près. Supression des doublons:
    r = np.rint(
        r
    )  # rint (entier le plus proche) permet de se limiter aux valeurs entières et eliminer les doublons dûs à scipy.optimize.root
    #     print(f'arrondis : {r}')
    r.drop_duplicates(inplace=True)
    #     print(f'dédoubloné :\n{r}')
    r.sort_values(inplace=True)
    #     print((f"sorted : \n{r}"))

    # élimination des valeurs hors bornes:
    bool1 = r > A[0, 0]
    bool2 = r < A[0, -1]
    #     print(bool1)
    #     print(bool2)
    #     print(bool1*bool2)

    roots = list(r[bool1 * bool2])
    #     print(f"racines valables : {roots}")
    tops = []  # selection des valeurs où f est concave : les maximums
    botts = []
    for i in range(len(roots)):
        if f2(roots[i]) < 0:
            tops.append(roots[i])
        else:
            botts.append(roots[i])

    #     print(f'tops : {tops}')
    #     print(f'botts : {botts}')
    # partie si on veut obtenir les valeurs approchées par les abscisses originales.
    #     realTops = [] #valeur réelle la plus proche
    #     for i in tops:
    #         ind=np.argmin(abs(tendance[0]-i))
    #         print(f'Comparaison : {tendance[0,ind]} , {i}')
    #         realTops=realTops+[tendance[0, ind]]

    #     realBotts = []
    #     for i in botts:
    #         ind=np.argmin(abs(tendance[0]-i))
    #         print(f'Comparaison : {tendance[0,ind]} , {i}')
    #         realBotts=realBotts+[tendance[0, ind]]

    #     tops=realTops
    #     botts=realBotts

    botts = sorted(
        botts
    )  # devrait être inutile par construction, mais comme scipy.optimize.roots est boîte-noire, je préfère le metttre.
    if sort == "performance":  # devrait être inutile par construction
        tops = sorted(tops)
    # tri par ordre de courbure : plus la courbure (f2) est grande en norme, meilleurs sont les points (c'est à dire que la concentration est plus flagrante)
    if sort == "values":
        values = f2(tops)
        ind = np.argsort(values)
        tops = np.take(tops, ind, axis=0)
        values = sorted(values)
    #         print(f'values{values}')
    #         print(f'tops{tops}')

    return tops, botts


def limiters(A, **kwargs):
    """
    Forme les zones distinctes (catégories de coureurs) à partir de listes de sommets et creux.

    Args:
        A (numpy.ndarray): Array of dimension 2, size (2,n) with A[0] as the abscissas and A[1] as the ordinates of the measured points.
        **kwargs: Additional arguments passed to topbotts. Possible arguments: sort='performance' or sort='values'.

    Returns:
        list: List of tuples representing the formed zones [(inf1,sup1), (inf2,sup2)...]
    """
    tops, botts = topbotts(A, **kwargs)

    lim = []
    for i in tops:
        under = A[0, 0]
        test = False
        j = 0
        while j < (len(botts)) and test == False:
            if botts[j] < i:
                under = botts[j]
                j += 1
            else:
                test = True

        over = A[0, -1]
        test = False
        j = len(botts) - 1
        while j >= 0 and test == False:
            if botts[j] > i:
                over = botts[j]
                j -= 1
            else:
                test = True
        lim.append((under, over))
    print(lim)
    return lim
