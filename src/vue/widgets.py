"""
Fichier qui contient des widgets Tkinter personnalisés, réutilisés dans le
formulaire d'ajout de partie (fenetre_ajout_fiches.py) :
- ChampAvancementAuto : un champ texte simple qui passe automatiquement au champ
  suivant une fois la longueur maximale atteinte (ex. pour les codes courts).
- ChampAutoCompletion : un champ texte avec autocomplétion dynamique (ex. pour
  saisir le nom d'un joueur à partir du code de son équipe).
"""
import tkinter as tk

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
        """Appelée à chaque modification du texte : tronque si trop long et avance au suivant."""
        value = self.var.get()
        if len(value) >= self.max_len:
            self.var.set(value[:self.max_len])
            self.passer_suivant()

    def passer_suivant(self, event=None):
        """Donne le focus au champ suivant (s'il existe) et sélectionne tout son contenu,
        pour permettre à l'utilisateur de continuer à taper directement (le remplaçant)."""
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
        """
        :param get_candidats: fonction sans argument qui retourne la liste actuelle
            des candidats possibles (appelée à chaque frappe, car elle peut dépendre
            d'un autre champ, ex. le code d'équipe, qui peut ne pas encore être rempli).
        :param next_widget: widget à activer une fois la saisie terminée (Entrée ou
            complétion unique).
        """
        super().__init__(master, **kwargs)
        self.get_candidats = get_candidats
        self.next_widget = next_widget
        self.ecrit = ""  # Ce que l'utilisateur a réellement tapé (sans la partie auto-complétée)
        self.bind("<KeyRelease>", self.sur_touche_lachee)
        self.bind("<Return>", self.passer_suivant)
        self.bind("<KP_Enter>", self.passer_suivant)

    def sur_touche_lachee(self, event):
        """Appelée à chaque relâchement de touche : met à jour self.ecrit puis rafraîchit
        la complétion affichée dans le champ."""
        if event.keysym in self.TOUCHES_IGNOREES:
            return

        is_suppr = event.keysym in ("BackSpace", "Delete")

        if is_suppr:
            # Sur suppression, on considère tout le texte restant comme "écrit"
            # (pas de sélection auto-complétée à retirer).
            self.ecrit = self.get()
        else:
            # Sinon, seule la portion avant le curseur est considérée comme "écrite"
            # par l'utilisateur (le reste peut être une complétion déjà affichée).
            pos = self.index(tk.INSERT)
            self.ecrit = self.get()[:pos]

        # On n'autorise une nouvelle complétion après une suppression que s'il ne
        # reste qu'un seul candidat possible correspondant exactement.
        self._maj_candidats(autoriser_completion=not is_suppr or self._a_un_seul_candidat())

    def _candidats_disponibles(self):
        """Récupère la liste à jour, en gérant le cas où la source n'est pas encore prête."""
        try:
            return self.get_candidats() or []
        except (KeyError, AttributeError):
            return []

    def _a_un_seul_candidat(self):
        """Vrai si un seul candidat correspond exactement (casse ignorée) à self.ecrit."""
        candidats = self._filtrer()
        return len(candidats) == 1 and candidats[0].lower() == self.ecrit.lower()

    def _filtrer(self):
        """Retourne la liste des candidats dont le nom commence par ce qui a été tapé
        (insensible à la casse). Liste vide si rien n'a encore été tapé."""
        if not self.ecrit:
            return []
        return [c for c in self._candidats_disponibles() if c.lower().startswith(self.ecrit.lower())]

    def _maj_candidats(self, autoriser_completion):
        """Recalcule les candidats correspondants et met à jour l'affichage du champ :
        - Si aucun candidat : affiche simplement ce qui a été tapé.
        - Sinon : complète (si autorisé) jusqu'au plus long préfixe commun aux candidats,
          la partie complétée étant sélectionnée (pour pouvoir être remplacée en continuant à taper).
        - Si un seul candidat correspond exactement au résultat affiché, on passe
          automatiquement au champ suivant.
        """
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
        """Affiche `texte` dans le champ, avec le curseur juste après la portion
        réellement tapée par l'utilisateur (longueur), et sélectionne le reste
        (la partie auto-complétée) s'il y en a."""
        self.delete(0, tk.END)
        self.insert(0, texte)
        self.icursor(longueur)
        if len(texte) > longueur:
            self.select_range(longueur, tk.END)

    def passer_suivant(self, event=None):
        """Donne le focus au champ suivant (s'il existe) et sélectionne tout son contenu."""
        if self.next_widget:
            self.next_widget.focus_set()
            if hasattr(self.next_widget, "icursor"):
                self.next_widget.icursor(tk.END)
            if hasattr(self.next_widget, "select_range"):
                self.next_widget.select_range(0, tk.END)


