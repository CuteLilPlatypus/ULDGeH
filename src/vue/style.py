"""
Fichier qui contient les couleurs utilisées pour identifier visuellement
chaque niveau (secondaire 1 à 5), autant dans l'interface (tournoi_vue.py)
que dans le rapport Excel généré (tournoi.py).
"""
from enum import Enum

class Couleur(str, Enum):
    # Une couleur par niveau de secondaire (1 à 5), dans l'ordre.
    ORANGE = "#FF9933",
    ROSE = "#FF99CC",
    BLEU = "#00B0F0",
    VERT = "#FFFF4A",
    JAUNE = "#A8D08D",
