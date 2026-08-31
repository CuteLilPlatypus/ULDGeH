"""
Fichier qui contient le code de la classe joueur
"""

class Joueur:
    nom: str  # Nom du joueur
    scores: list[int | None]  # Liste des scores

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
            return sum(score for score in self.scores if score is not None) / sum(
                score is not None for score in self.scores)
        except ZeroDivisionError:
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