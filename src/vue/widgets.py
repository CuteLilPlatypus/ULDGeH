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


