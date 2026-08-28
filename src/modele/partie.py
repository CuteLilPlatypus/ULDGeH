class Partie:
    """La classe qui contient les infos d'une partie"""
    niveau: int  # Niveau de la partie
    plateau: int  # Numéro du plateau de jeu
    numero: int  # Numéro de la partie (ex. 1 pour le match 1)
    eq_a: str  # Le code de l'équipe A
    eq_b: str  # Le code de l'équipe B
    vainqueur: str | None

    def __init__(self, niveau, plateau, numero, eq_a, eq_b, vainqueur):
        self.niveau = niveau
        self.plateau = plateau
        self.numero = numero
        self.eq_a = eq_a
        self.eq_b = eq_b
        self.vainqueur = vainqueur

    def to_dict(self):
        return vars(self)  # ok si tous les attributs sont déjà sérialisables

    @staticmethod
    def from_dict(data: dict) -> 'Partie':
        return Partie(
            data["niveau"], data["plateau"], data["numero"],
            data["eq_a"], data["eq_b"], data["vainqueur"]
        )

    @staticmethod
    def from_resultat(r: 'ResultatMatch'):
        return Partie(
            niveau=int(r.niveau),
            plateau=int(r.plateau),
            numero=int(r.num_match),
            eq_a=r.scores["Équipe"]["nom_A"],
            eq_b=r.scores["Équipe"]["nom_B"],
            vainqueur=r.vainqueur
        )


class ResultatMatch:
    """Classe qui contient tous les résultats d'une partie, incluant les scores"""

    def __init__(self, num_match, niveau, plateau, scores, vainqueur):
        self.num_match = num_match
        self.niveau = niveau
        self.plateau = plateau
        self.scores = scores
        self.vainqueur = vainqueur