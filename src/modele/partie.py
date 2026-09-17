"""
Fichier qui contient les classes Partie et ResultatMatch.

- ResultatMatch : représentation "brute" d'une partie telle que saisie dans le
  formulaire (contient TOUS les scores individuels des joueurs et des équipes).
- Partie : version "légère" d'une partie, uniquement utilisée pour le suivi du
  tournoi (qui a joué qui, sur quel plateau, qui a gagné). C'est cette version
  qui est stockée dans Tournoi.parties et sauvegardée dans le JSON.
"""
class Partie:
    """La classe qui contient les infos d'une partie"""
    niveau: int  # Niveau de la partie
    plateau: int  # Numéro du plateau de jeu
    numero: int  # Numéro de la partie (ex. 1 pour le match 1)
    eq_a: str  # Le code de l'équipe A
    eq_b: str  # Le code de l'équipe B
    vainqueur: str | None  # Code de l'équipe gagnante, ou None (égalité / non déterminé)

    def __init__(self, niveau, plateau, numero, eq_a, eq_b, vainqueur):
        self.niveau = niveau
        self.plateau = plateau
        self.numero = numero
        self.eq_a = eq_a
        self.eq_b = eq_b
        self.vainqueur = vainqueur

    def to_dict(self):
        """
        Fonction interne pour le stockage au format JSON.
        :return: dict des attributs de l'objet (tous sérialisables tels quels)
        """
        return vars(self)  # ok si tous les attributs sont déjà sérialisables

    @staticmethod
    def from_dict(data: dict) -> 'Partie':
        """
        Reconstruit une Partie à partir d'un dict (issu du JSON de sauvegarde).
        :param data: dict contenant les clés niveau/plateau/numero/eq_a/eq_b/vainqueur
        :return: Partie correspondante
        """
        return Partie(
            data["niveau"], data["plateau"], data["numero"],
            data["eq_a"], data["eq_b"], data["vainqueur"]
        )

    @staticmethod
    def from_resultat(r: 'ResultatMatch'):
        """
        Construit une Partie "résumée" à partir d'un ResultatMatch complet
        (celui rempli via le formulaire d'ajout de partie).
        On ne conserve ici que les infos de suivi du tournoi (pas les scores détaillés
        des joueurs, qui sont plutôt ajoutés directement aux Joueur/Equipe concernés).
        :param r: résultat complet du match saisi
        :return: Partie correspondante, prête à être ajoutée au tournoi
        """
        return Partie(
            niveau=int(r.niveau),
            plateau=int(r.plateau),
            numero=int(r.num_match),
            eq_a=r.scores["Équipe"]["nom_A"],
            eq_b=r.scores["Équipe"]["nom_B"],
            vainqueur=r.vainqueur
        )


class ResultatMatch:
    """Classe qui contient tous les résultats d'une partie, incluant les scores
    de l'équipe et de chacun de ses joueurs. C'est l'objet produit par le
    formulaire d'ajout de partie (UIAjoutPartie), avant d'être éclaté en :
    - une Partie (ajoutée à Tournoi.parties)
    - des scores ajoutés aux Equipe/Joueur concernés (via Equipe.ajouter_partie)
    """

    def __init__(self, num_match, niveau, plateau, scores, vainqueur):
        """
        :param num_match: numéro du match
        :param niveau: niveau du match
        :param plateau: plateau du match
        :param scores: scores des équipes et des joueurs (dict), structuré par
            rangée ("Équipe", "Joueur 1", ...) puis par clé "nom_A"/"score_A"/"nom_B"/"score_B"
        :param vainqueur: code de l'équipe victorieuse
        """
        self.num_match = num_match
        self.niveau = niveau
        self.plateau = plateau
        self.scores = scores
        self.vainqueur = vainqueur