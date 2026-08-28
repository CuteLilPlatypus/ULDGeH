class Joueur:
    nom: str  # Nom du joueur
    scores: list[int | None]  # Liste des scores

    def __init__(self, nom: str):
        self.nom = nom
        self.scores = []

    def __str__(self):
        return f'{self.nom}'

    def moyenne(self):
        try:
            return sum(score for score in self.scores if score is not None) / sum(
                score is not None for score in self.scores)
        except ZeroDivisionError:
            return 0

    def to_dict(self):
        return {
            "nom": self.nom,
            "scores": self.scores
        }

    @staticmethod
    def from_dict(data: dict) -> 'Joueur':
        j = Joueur(data['nom'])
        j.scores = data['scores']
        return j