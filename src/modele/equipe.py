"""
Fichier qui contient le code de la classe «Equipe.»
"""
from src.modele.joueur import Joueur
from src.modele.partie import ResultatMatch, Partie


class Equipe:
    """
    Classe de représentation d'une équipe
    """
    code: str  # Code de l'équipe
    nom: str  # Nom de l'équipe
    joueurs: list[Joueur]  # Liste des joueurs de l'équipe
    scores: list[int | None]  # Liste des scores de l'équipe

    def __init__(self, code: str, nom: str, joueurs: list[Joueur]):
        """
        :param code: Code de l'équipe.
        :param nom:  Nom de l'équipe.
        :param joueurs: Liste des joueurs de l'équipe.
        """
        self.code = code
        self.nom = nom
        self.joueurs = joueurs
        self.scores = []

    def __str__(self):
        return f'{self.nom} {self.code}'

    def moy_pts_pour(self) -> float:
        """
        Calcule la moyenne des points scorés par l'école
        :return: la moyenne des points
        """
        nb_parties = sum(score is not None for score in self.scores)
        if nb_parties == 0:
            return 0
        points = sum(score for score in self.scores if score is not None)
        return points / nb_parties

    def ajouter_partie(self, partie: ResultatMatch):
        """
        Ajoute une partie à la liste des parties de l'équipe
        :param partie: Résultats d'un match
        """
        prefixe = "A" if partie.scores["Équipe"]["nom_A"] == self.code else "B"
        self.scores.append(int(partie.scores["Équipe"][f"score_{prefixe}"]))

        for i in range(4):
            idx = i + 1
            score = partie.scores[f"Joueur {idx}"][f"score_{prefixe}"]
            if score is None:
                continue
            nom = partie.scores[f"Joueur {idx}"][f"nom_{prefixe}"]
            if nom is None:
                raise ValueError(f"Score du Joueur {idx} ({prefixe}) saisi sans nom de joueur.")
            joueur = next((j for j in self.joueurs if j.nom == nom), None)
            if joueur is None:
                raise ValueError(f"Joueur introuvable dans l'équipe {self.code} : {nom!r}")
            joueur.scores.append(int(score))

    def obtenir_liste_noms(self):
        """
        Fonction qui renvoie la liste des noms des joueurs d'une équipe
        :return: liste des joueurs de l'équipe
        """
        return [joueur.nom for joueur in self.joueurs]

    def a_joue_partie(self, partie: Partie):
        """
        Fonction qui vérifie si une équipe a joué une partie
        :param partie: la partie à tester
        :return: True si l'équipe a joué la partie, False sinon
        """
        return self.code in [partie.eq_a, partie.eq_b]

    def to_dict(self):
        """
        Fonction interne pour le stockage au format JSON
        :return: le dict de stockage
        """
        return {
            "code": self.code,
            "nom": self.nom,
            "joueurs": [j.to_dict() for j in self.joueurs],
            "scores": self.scores
        }

    @staticmethod
    def from_dict(data: dict) -> 'Equipe':
        """
        Fonction qui renvoie une équipe à partir d'un dict (JSON.)
        :param data:
        :return:
        """
        e = Equipe(data['code'], data['nom'], [Joueur.from_dict(j) for j in data['joueurs']])
        e.scores = data['scores']
        return e
