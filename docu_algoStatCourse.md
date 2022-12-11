Le code est divisé en deux : algoStatCourse.ipynb et GraphAlgoStatCourse.ipynb
Le premier est à utiliser comme bibliothèque dans le code de data-visualisation.

Cette partie du projet permet d'entrer plus en profondeur lors de l'analyse des données. Elle permet d'accomplir l'objectif du projet,
qui est deproposer des possibilités de data-visualisation qui sortent des outils déjà existants dans les bibliothèques usuelles.
L'objectif est d'analyser la distribution des temps d'arrivée des coureurs sur les courses (scarppées par scraping.ipynb)

Il y a deux fonctionnalités essentielles : l'identification des "pics de performance", et l'identification des catégories de coureurs.
Les catégories de coureurs sont données par la forme globale de la distribution. On fait le postulat que n "bosses" dans la distribution des temps d'arrivée correspondent
à n catégorries de coureurs.
Il arrive aussi de voir distinctement des 'pics' de temps d'arrivée, c'est à dire des amas de coureurs autour de temps bien précis.
En remarquant que ces pics arrivent souvent sur des temps "ronds" (finir le marathon en 4h...), on considère que ces amas de coureurs correspondent à des personnes
qui se sont fixés un même objectif de performance.

Il y a deux fonctionnalités dans la bibliothèque : repérer les pics de performance, et les catégroies de coureurs.
Dans les deux cas, la méthodologie est semblable : il faut trouver des maxima et minima locaux dans les distributions.

Etapes : 
1) séparer la densité en tendance et bruit.
    -La tendance ne contient pas les pics de performance mais seulement la forme globale des temps d'arrivée. On lira les catégories de coureurs sur cette tendance.
    -le bruit oscille autour de zéro, mais contient les pics de performance. On lira les pics dans ce bruit.
2) trouver les maxima et minima locaux : pour ce faire, on interpole la tendance et le bruit (par une interpolation cubique -polynomiale par segment-), que l'on sait maximiser ou minimiser.
3) une fois trouvés, il faut replacer les pics de performance à leur place réelle (l'interpolation a fait décaler des valeurs)
4) une fois les variations de la tendance trouvées, on identifie les catégories de coureurs grâce aux "bosses".
5) trier les valeurs par ordre d'importance, pour ne tracer que les meilleures. (les pics les plus distinctifs, les bosses les plus nettes -par leur courbure-...).
6) En effet, on peut détecter des catégories de moins de 1% des coureurs ou des pics dont on attribuerait la présence au hasard (les moins "flagrants").


Le fichier algoStatCourse.ipynb contient les fonctions pour retourner les valeurs recherchées (limites des catégories, position des pics de performance)
Le fichier algoStatCourse.ipynb contient des précisions sur la construction des fonctions, la méthodologie, avec du code illustré par des graphes.

Techniquement :
-l'outil est sensible à deux variables : la qualité de la mesure de la densité, et le paramètre de filtrage (hp-filter).
La densité est mesurée à l'aide d'un histogramme, dont le nombre de batchs importe. Un nombre trop faible ne transcrira pas les variations intéressantes
et un nombre trop élevé donnera des variations ne disant rien sur la densité qu'on essaye d'estimer. la fonction idealBins sert à calculer un bon compromis.

-Le filtre hp sépare le signal du bruit, en accordant +/- d'importance au "lissage" avec un paramètre lambda.
Il fait l'équilibre entre l'information que contient le bruit et l'information que contient la tendance. s'il est trop élevé,on compte comme "bruit" des variations de la tendance : 
on rate alors des catégories et on détecte des pics sans intérêt. S'il est trop faible, on risque de trouver des catégories de coureurs là où il n'y a qu'un pic,
qui pourrait appartenir à une catégorie plus grande. une valeur de 1e-2 semble un bon compromis.



NB : 1)La méthodologie de séparation des catégories de coureurs n'A PAS DE FONDEMENT STATISTIQUE. Elle vise simplement à reproduire le jugé de l'oeil humain qui identifie les "bosses".
      on aurait pu faire le choix d'un modèle statistique qui serait une somme de n gaussiennes par exemple, mais la méthodologie retenue a permis de recycler les calculs d'optimisation.
     2)L'approximation par des polynômes pose deux problèmes : ils ont tendance à osciller plus que "nécessaire" lors de fortes variations ; de plus, il arrive que scipy rate tout simplement un minimum local.
       Dans ce cas, on ne comptera qu'une seule catégorie là où il y en a deux.
       Le code est donc soumis aux imprécisions du calcul scientifique (interpolation et minimisation)
       Il arrive qu'une partie des coureurs ne rentre dans aucune catégorie (pas de bosse), notament lorsqu'il y a des queues convexes dans les distributions.
      
       
GraphAlgoStatCourse.ipynb ne contient que des exécutions des fonctions 
