import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.request import Request, urlopen
from requests import get, Session
from bs4 import BeautifulSoup
import re
import dtale
import astropy.units as u

# %%
url = "https://etilbudsavis.dk/search/tomat"

# Set geo cookie to close proximity
geocook = "{%22address%22:{%22formattedAddress%22:%22%25C3%2598ster%2520Voldgade%252010%252C%25201350%2520K%25C3%25B8benhavn%2520K%252C%2520Danmark%22%2C%22timestamp%22:1590434143553%2C%22source%22:%22google.maps%22}%2C%22searchRadius%22:1000%2C%22searchRadiusSource%22:%22user%22%2C%22position%22:{%22coordinates%22:{%22latitude%22:55.68805452424639%2C%22longitude%22:12.581700642989032%2C%22accuracy%22:100}%2C%22timestamp%22:1590434143553%2C%22source%22:%22google.maps%22}}"

s = Session()
txt = s.get(url, cookies={"sgn-geo": geocook}).text
soup = BeautifulSoup(txt,"html.parser")

navne = soup.find_all("header")
butiker = soup.find_all(attrs={'class': "UniversalCard__ListItemBusinessDiv-sc-1hzrvmb-1 ciHEPE"})
priser = soup.find_all(attrs={'class': 'UniversalCard__OfferPcs-sc-1hzrvmb-2 keVehx'})

navne = np.array([navn.get_text(strip=True) for navn in navne[1:]])
butiker = np.array([butiken.get_text(strip=True) for butiken in butiker])
priser = np.array([pris.get_text(strip=True) for pris in priser])

navne = navne[navne!=""]
priser = priser[priser!=""]
butiker = butiker[butiker!=""]
# %%
def units(input):
    if input == "g":
        return u.g
    if input== "kg":
        return u.kg
    if input == "l":
        return u.liter
    if input == "ml":
        return u.ml

# %%
vægt = []
priskg = []
i = 0
for pris in priser:
    newstr = ''.join((ch if ch in '0123456789x-.,e' else ' ') for ch in pris).replace(".","").replace(",",".")
    if "x" in newstr or "-" in newstr:
        newstr = newstr.split()
        if "x" in newstr[0] and "-" in newstr[0]:
            avgstr = ''.join((ch if ch in '0123456789.e' else ' ') for ch in newstr[0]).split()
            vægt.append(float(avgstr[0]) * np.mean([float(s) for s in avgstr[1:]]))
            priskg.append(float(newstr[1]))

        if "-" in newstr[0] and "x" not in newstr[0]:
            avgstr = ''.join((ch if ch in '0123456789.e' else ' ') for ch in newstr[0]).split()
            vægt.append(np.mean([float(s) for s in avgstr[0:]]))
            priskg.append(float(newstr[1]))

        if "x" in newstr[0] and "-" not in newstr[0]:
            avgstr = ''.join((ch if ch in '0123456789.e' else ' ') for ch in newstr[0]).split()
            vægt.append(float(avgstr[1]))
            priskg.append(float(newstr[1]))
    else:
        newstr = newstr.split()
        vægt.append(float(newstr[0]))
        priskg.append(float(newstr[1]))

    unit = ''.join((ch if ch in 'mgkl' else ' ') for ch in pris).split()
    vægt[i] = vægt[i] * units(unit[0])
    priskg[i] = priskg[i] * 1/units(unit[-1])
    i += 1
# %%
