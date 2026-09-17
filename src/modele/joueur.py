"""
Fichier qui contient le code de la classe joueur
"""

class Joueur:
    """
    Classe de représentation d'un joueur individuel au sein d'une équipe.
    """
    nom: str  # Nom du joueur
    # Liste des scores du joueur, un élément par partie jouée par son équipe.
    # None signifie que le joueur n'a pas joué (ou n'a pas de score) pour cette partie.
    scores: list[int | None]

    def __init__(self, nom: str):
        """
        :param nom: str, nom du joueur
        """
        self.nom = nom
        self.scores = []

    def __str__(self):
        return f'{self.nom}'

    def moyenne(self):
        """
        Fonction qui calcule la moyenne de points du joueur
        :return: float moyenne de points du joueur
        """
        try:
            # Somme des scores valides (non None) divisée par le nombre de parties
            # réellement jouées (aussi le nombre de scores non None).
            return sum(score for score in self.scores if score is not None) / sum(
                score is not None for score in self.scores)
        except ZeroDivisionError:
            # Aucune partie jouée (ou aucun score valide) : moyenne nulle par convention.
            return 0

    def to_dict(self):
        """
        Fonction interne pour le stockage au format JSON
        :return: le dict de stockage
        """
        return {
            "nom": self.nom,
            "scores": self.scores
        }


    @staticmethod
    def from_dict(data: dict) -> 'Joueur':
        """
        Fonction qui renvoie un Joueur à partir d'un dict (JSON.)
        :param data: les données du dict
        :return: Joueur
        """
        j = Joueur(data['nom'])
        j.scores = data['scores']
        return j