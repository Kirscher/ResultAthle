import utils.scraping as scraping
import utils.stat as stat

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = scraping.get_results("https://bases.athle.fr/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=282742", 13)

print(data.head())