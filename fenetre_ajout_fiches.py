import tkinter as tk

from struct_donnees import ResultatMatch, Tournoi


def _calculer_commun(chaines: list[str]) -> str:
    """Calcule le plus long préfixe commun entre plusieurs chaines (insensible à la casse)."""
    if not chaines:
        return ""
    ref = chaines[0]
    max_len = min(len(s) for s in chaines)
    n = 0
    while n < max_len and all(s[n].lower() == ref[n].lower() for s in chaines):
        n += 1
    return ref[:n]

def _extraire_valeurs(entrees: dict) -> dict:
    """Convertit récursivement un dict de widgets (ou dict de dicts de widgets)
    en un dict de même structure, mais avec les valeurs (.var.get()) au lieu des widgets."""
    resultat = {}
    for cle, val in entrees.items():
        if isinstance(val, dict):
            resultat[cle] = _extraire_valeurs(val)
        else:
            if isinstance(val, ChampAvancementAuto):
                resultat[cle] = val.var.get()
            else:
                resultat[cle] = val.ecrit
            if resultat[cle] == "":
                resultat[cle] = None
    return resultat

def _interpreter_score_equipe(valeur: str) -> int | None:
    """Convertit la valeur brute d'un champ score d'équipe.
    '+' et '-' deviennent None (remplacés dans scores), un nombre reste un nombre."""
    valeur = valeur.strip()
    if valeur in ("+", "-"):
        return None
    try:
        return int(valeur)
    except ValueError:
        return None  # valeur invalide/vide : traité comme None aussi


def _determiner_vainqueur(brut_a: str, brut_b: str, code_a: str, code_b: str) -> str | None:
    """Détermine le vainqueur à partir des valeurs BRUTES ('+', '-', ou nombre) des scores d'équipe."""
    brut_a = brut_a.strip()
    brut_b = brut_b.strip()

    if brut_a == "+" or brut_b == "+":
        # Une des deux équipes a "+" -> elle gagne (l'autre devrait avoir "-")
        return code_a if brut_a == "+" else code_b

    if brut_a == "-" and brut_b == "-":
        return None

    # Cas normal : comparaison numérique
    score_a = _interpreter_score_equipe(brut_a)
    score_b = _interpreter_score_equipe(brut_b)

    if score_a is None or score_b is None:
        return None  # score manquant/invalide d'un côté, pas de vainqueur déterminable

    if score_a > score_b:
        return code_a
    if score_b > score_a:
        return code_b
    return None  # égalité


class ChampAvancementAuto(tk.Entry):
    """Un champ qui avance au suivant une fois max_len caractères atteints, ou sur Entrée."""

    def __init__(self, master, max_len, next_widget=None, **kwargs):
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.max_len = max_len
        self.next_widget = next_widget
        self.var.trace_add("write", self.sur_mod)
        self.bind("<Return>", self.passer_suivant)
        self.bind("<KP_Enter>", self.passer_suivant)

    def sur_mod(self, *args):
        value = self.var.get()
        if len(value) >= self.max_len:
            self.var.set(value[:self.max_len])
            self.passer_suivant()

    def passer_suivant(self, event=None):
        if self.next_widget:
            self.next_widget.focus_set()
            if hasattr(self.next_widget, "icursor"):
                self.next_widget.icursor(tk.END)
            if hasattr(self.next_widget, "select_range"):
                self.next_widget.select_range(0, tk.END)


class ChampAutoCompletion(tk.Entry):
    """
    Champ d'autocomplétion dont la liste de candidats est obtenue dynamiquement
    (via get_candidats), puisqu'elle peut dépendre d'un autre champ pas encore rempli.
    """

    TOUCHES_IGNOREES = {
        "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
        "Left", "Right", "Up", "Down", "Home", "End", "Tab", "Caps_Lock"
    }

    def __init__(self, master, get_candidats, next_widget=None, **kwargs):
        super().__init__(master, **kwargs)
        self.get_candidats = get_candidats
        self.next_widget = next_widget
        self.ecrit = ""
        self.bind("<KeyRelease>", self.sur_touche_lachee)
        self.bind("<Return>", self.passer_suivant)
        self.bind("<KP_Enter>", self.passer_suivant)

    def sur_touche_lachee(self, event):
        if event.keysym in self.TOUCHES_IGNOREES:
            return

        is_suppr = event.keysym in ("BackSpace", "Delete")

        if is_suppr:
            self.ecrit = self.get()
        else:
            pos = self.index(tk.INSERT)
            self.ecrit = self.get()[:pos]

        self._maj_candidats(autoriser_completion=not is_suppr or self._a_un_seul_candidat())

    def _candidats_disponibles(self):
        """Récupère la liste à jour, en gérant le cas où la source n'est pas encore prête."""
        try:
            return self.get_candidats() or []
        except (KeyError, AttributeError):
            return []

    def _a_un_seul_candidat(self):
        candidats = self._filtrer()
        return len(candidats) == 1 and candidats[0].lower() == self.ecrit.lower()

    def _filtrer(self):
        if not self.ecrit:
            return []
        return [c for c in self._candidats_disponibles() if c.lower().startswith(self.ecrit.lower())]

    def _maj_candidats(self, autoriser_completion):
        candidats = self._filtrer()

        if not candidats:
            self._set_affichage(self.ecrit, len(self.ecrit))
            return

        plc = _calculer_commun(candidats) if autoriser_completion else self.ecrit
        self._set_affichage(plc, len(self.ecrit))

        if len(candidats) == 1 and candidats[0].lower() == plc.lower():
            self.ecrit = plc
            self.passer_suivant()

    def _set_affichage(self, texte, longueur):
        self.delete(0, tk.END)
        self.insert(0, texte)
        self.icursor(longueur)
        if len(texte) > longueur:
            self.select_range(longueur, tk.END)

    def passer_suivant(self, event=None):
        if self.next_widget:
            self.next_widget.focus_set()
            if hasattr(self.next_widget, "icursor"):
                self.next_widget.icursor(tk.END)
            if hasattr(self.next_widget, "select_range"):
                self.next_widget.select_range(0, tk.END)


class UIAjoutPartie(tk.Canvas):
    BORDURE = {"relief": "solid", "borderwidth": 1}

    def __init__(self, master, tournoi, sur_fermeture=None, **kwargs):
        super().__init__(master)
        self.tournoi = tournoi
        self.fenetre = tk.Toplevel(master)
        self.sur_fermeture = sur_fermeture
        self.fenetre.protocol("WM_DELETE_WINDOW", self.fermer)
        self.afficher()

    def fermer(self):
        self.fenetre.destroy()

    def valider(self):
        partie = self._construire_resultat()
        self.tournoi.ajouter_partie_depuis_resultat(partie)
        self.sur_fermeture(self.tournoi)
        self.fermer()

    def _construire_resultat(self) -> ResultatMatch:
        scores = _extraire_valeurs(self.entrees)

        brut_score_a = scores["Équipe"]["score_A"]
        brut_score_b = scores["Équipe"]["score_B"]
        code_a = scores["Équipe"]["nom_A"]
        code_b = scores["Équipe"]["nom_B"]

        vainqueur = _determiner_vainqueur(brut_score_a, brut_score_b, code_a, code_b)

        # On remplace les scores bruts ("+"/"-") par leur interprétation (nombre ou None)
        scores["Équipe"]["score_A"] = _interpreter_score_equipe(brut_score_a)
        scores["Équipe"]["score_B"] = _interpreter_score_equipe(brut_score_b)

        return ResultatMatch(
            num_match=self.champ_num_match.var.get(),
            niveau=int(scores["Équipe"]["nom_A"][0]),
            plateau=self.champ_plateau.var.get(),
            scores=scores,
            vainqueur=vainqueur,
        )

    def afficher(self):
        def texte(master, contenu, ran, col, l_col=1, **kw):
            txt = tk.Label(master, text=contenu, **UIAjoutPartie.BORDURE, padx=4, pady=2, **kw)
            txt.grid(row=ran, column=col, columnspan=l_col, sticky="nsew")
            return txt

        def _placer_grille(champ, champ_precedent, ran, col):
            champ.grid(row=ran, column=col, sticky="nsew")
            if champ_precedent is not None:
                champ_precedent.next_widget = champ

        def entree_nom(master, ran, col, champ_code: ChampAvancementAuto, tournoi, champ_precedent=None, **kw):
            def _get_candidats():
                code = str(champ_code.var.get())
                try:
                    return tournoi.equipes[code].obtenir_liste_noms()
                except KeyError:
                    return []

            entree = ChampAutoCompletion(master, _get_candidats)
            _placer_grille(entree, champ_precedent, ran, col)

            return entree

        def entree_val(master, ran, col, max_car, champ_precedent=None, **kw):
            entree = ChampAvancementAuto(master, max_car)
            _placer_grille(entree, champ_precedent, ran, col)

            return entree

        # 1 Création de la grille
        cadre = tk.Frame(self.fenetre)
        cadre.pack(padx=20, pady=20)

        # 1re rangée : en-têtes
        texte(cadre, "", 0, 0)  # Coin vide
        texte(cadre, "Équipe A", 0, 1, l_col=2)
        texte(cadre, "Équipe B", 0, 3, l_col=2)

        # 2e rangée : Indication des colonnes
        texte(cadre, "", 1, 0)
        texte(cadre, "Nom (code)", 1, 1)
        texte(cadre, "Score", 1, 2)
        texte(cadre, "Nom (code)", 1, 3)
        texte(cadre, "Score", 1, 4)

        # Zone d'entrée des données
        lignes = ["Équipe", "Joueur 1", "Joueur 2", "Joueur 3", "Joueur 4"]
        self.entrees = {nom_ligne: {} for nom_ligne in lignes}

        # Titres des rangées
        for i, nom_ligne in enumerate(lignes):
            texte(cadre, nom_ligne, i + 2, 0)

        def construire_colonne(prefixe, col_nom, col_score, dernier_champ):
            """Construit toute une colonne d'équipe (code, puis nom/score de chaque joueur),
            chaînée verticalement. Retourne le dernier champ créé."""

            # Rangée "Équipe" : le code
            rangee = 2
            champ_code = entree_val(cadre, rangee, col_nom, 3, champ_precedent=dernier_champ)
            self.entrees["Équipe"][f"nom_{prefixe}"] = champ_code
            champ_score = entree_val(cadre, rangee, col_score, 3, champ_code)
            self.entrees["Équipe"][f"score_{prefixe}"] = champ_score
            dernier_champ = champ_score

            # Rangées "Joueur 1" à "Joueur 4" : nom (autocomplétion) puis score
            for i, nom_ligne in enumerate(lignes[1:], start=1):
                rangee = i + 2

                champ_nom = entree_nom(
                    cadre, rangee, col_nom,
                    champ_code, self.tournoi,
                    champ_precedent=dernier_champ,
                )
                self.entrees[nom_ligne][f"nom_{prefixe}"] = champ_nom
                dernier_champ = champ_nom

                champ_score = entree_val(cadre, rangee, col_score, 3, champ_precedent=dernier_champ)
                self.entrees[nom_ligne][f"score_{prefixe}"] = champ_score
                dernier_champ = champ_score

            return dernier_champ

        dernier_champ = construire_colonne("A", col_nom=1, col_score=2, dernier_champ=None)
        dernier_champ = construire_colonne("B", col_nom=3, col_score=4, dernier_champ=dernier_champ)

        # Ajout de la section pour le match, le plateau et le niveau
        texte(cadre, "Match", 7, 0)
        self.champ_num_match = entree_val(cadre, 8, 0, 2, champ_precedent=dernier_champ)
        texte(cadre, "Plateau", 7, 1)
        self.champ_plateau = entree_val(cadre, 8, 1, 2, champ_precedent=self.champ_num_match)


        bouton_valider = tk.Button(cadre, text="Valider", command=self.valider)
        bouton_valider.bind("<Return>", lambda e: bouton_valider.invoke())
        self.champ_plateau.next_widget = bouton_valider
        bouton_valider.grid(column=3, row=8, sticky="nsew")
        bouton_annuler = tk.Button(cadre, text="Annuler", command=self.fermer)
        bouton_annuler.grid(column=4, row=8, sticky="nsew")

        self.entrees["Équipe"]["nom_A"].focus_set()