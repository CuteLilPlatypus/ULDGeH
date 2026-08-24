import json


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
            return sum(score for score in self.scores if score is not None)/ sum(score is not None for score in self.scores)
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


class Equipe:
    code: str  # Code de l'équipe
    nom: str  # Nom de l'équipe
    joueurs: list[Joueur]  # Liste des joueurs de l'équipe
    scores: list[int | None]  # Liste des scores de l'équipe

    def __init__(self, code: str, nom: str, joueurs: list[Joueur]):
        self.code = code
        self.nom = nom
        self.joueurs = joueurs

    def __str__(self):
        return f'{self.nom} {self.code}'

    def moy_pts_pour(self) -> float:
        nb_parties = sum(score is not None for score in self.scores)
        points = sum(score for score in self.scores if score is not None)
        return points / nb_parties

    def ajouter_partie(self, partie: 'ResultatMatch'):
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
        return [joueur.nom for joueur in self.joueurs]

    def a_joue_partie(self, partie: 'Partie'):
        return self.code in [partie.eq_a, partie.eq_b]

    def to_dict(self):
        return {
            "code": self.code,
            "nom": self.nom,
            "joueurs": [j.to_dict() for j in self.joueurs],
            "scores": self.scores
        }

    @staticmethod
    def from_dict(data: dict) -> 'Equipe':
        e = Equipe(data['code'], data['nom'], [Joueur.from_dict(j) for j in data['joueurs']])
        e.scores = data['scores']
        return e

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


class Tournoi:
    nom: str  # Le nom du tournoi général
    parties: list[Partie]  # La liste des parties qui ont été disputées durant le tournoi
    equipes: dict[str, Equipe]  # La liste des équipes inscrites

    def __init__(self, nom: str):
        self.nom = nom
        self.parties = []
        self.equipes = {}

    def ajouter_partie(self, partie: Partie):
        self.parties.append(partie)

    def ajouter_partie_depuis_resultat(self, resultat: ResultatMatch):
        self.ajouter_partie(Partie.from_resultat(resultat))
        self.equipes[resultat.scores["Équipe"]["nom_A"]].ajouter_partie(resultat)
        self.equipes[resultat.scores["Équipe"]["nom_B"]].ajouter_partie(resultat)

    def ajouter_equipe(self, equipe: Equipe):
        if equipe.code not in self.equipes:
            self.equipes[equipe.code] = equipe

    def trier_parties(self):
        parties_niveau: list[list[Partie]] = [[], [], [], [], []]
        for partie in self.parties:
            parties_niveau[partie.niveau - 1].append(partie)
        return parties_niveau

    def trier_equipes(self):
        equipes_niveau: list[list[Equipe]] = [[], [], [], [], []]
        for code in self.equipes:
            equipes_niveau[int(code[0]) - 1].append(self.equipes[code])
        return equipes_niveau

    def classement_niveau(self, niveau: int) -> list[Equipe]:
        equipes = self.trier_equipes()[niveau - 1]

        def cle_tri(equipe: Equipe):
            code = equipe.code

            critere1 = self.points(code) / self.pj(code) if self.pj(code)>0 else 0
            critere2 = self.moy_pts_diff(code)
            critere3 = equipe.moy_pts_pour()

            return (critere1, critere2, critere3)

        return sorted(equipes, key=cle_tri, reverse=True)

    # Gestion d'une équipe pour les stats
    def pj(self, code: str) -> int:
        equipe = self.equipes[code]
        return len([p for p in self.parties if equipe.a_joue_partie(p)])

    def victoires(self, code: str) -> int:
        equipe = self.equipes[code]
        return sum(
            equipe.code == partie.vainqueur
            for partie in self.parties
        )

    def defaites(self, code: str) -> int:
        equipe = self.equipes[code]
        return sum(
            (
                    (partie.vainqueur is not None and partie.vainqueur != equipe.code)
                    or
                    (partie.vainqueur is None and equipe.scores[partie.numero - 1] is None)
            )
            for partie in self.parties
            if equipe.a_joue_partie(partie)
        )

    def nulles(self, code: str) -> int:
        equipe = self.equipes[code]
        return sum(
            partie.vainqueur is None
            for partie in self.parties
            if equipe.scores[partie.numero - 1] is not None
            and equipe.a_joue_partie(partie)
        )

    def points(self, code: str) -> int:
        return 2 * self.victoires(code) + self.nulles(code)

    def moy_pts_diff(self, code: str):
        equipe = self.equipes[code]
        total = 0
        pj = 0

        for partie in self.parties:
            if not equipe.a_joue_partie(partie):
                continue
            score_equipe = equipe.scores[partie.numero - 1]
            adv_code = partie.eq_a if equipe.code == partie.eq_b else partie.eq_b
            score_adversaire = self.equipes[adv_code].scores[partie.numero - 1]

            if score_equipe is not None and score_adversaire is not None:
                total += score_equipe - score_adversaire
                pj += 1

        return total / pj if pj > 0 else 0


    #Stockage vers un fichier
    def to_dict(self):
        return {
            "nom": self.nom,
            "parties": [p.to_dict() for p in self.parties],
            "equipes": {code: eq.to_dict() for code, eq in self.equipes.items()}
        }

    @staticmethod
    def from_dict(data: dict) -> 'Tournoi':
        t = Tournoi(data["nom"])
        t.parties = [Partie.from_dict(p) for p in data["parties"]]
        t.equipes = {code: Equipe.from_dict(eq) for code, eq in data["equipes"].items()}
        return t

    def sauvegarder(self, chemin: str) -> None:
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def charger(chemin: str):
        with open(chemin, 'r', encoding='utf-8') as f:
            return Tournoi.from_dict(json.load(f))
