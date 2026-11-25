import tkinter as tk
from tkinter import filedialog, messagebox

from src.modele.generateur_horaire import exporter_horaires


class UIHoraire(tk.Canvas):
    """Fenêtre (Toplevel) de génération d'un horaire pour un ou plusieurs niveaux."""

    def __init__(self, master, tournoi, sur_fermeture=None, **kwargs):
        super().__init__(master)
        self.tournoi = tournoi
        self.sur_fermeture = sur_fermeture
        self.fenetre = tk.Toplevel(master)
        self.fenetre.bind("<Escape>", lambda e: self.fermer())
        self.fenetre.protocol("WM_DELETE_WINDOW", self.fermer)
        self.voulu: dict[int, tk.BooleanVar] = {}
        self.afficher()

    def fermer(self):
        if self.sur_fermeture:
            self.sur_fermeture(self.tournoi)
        self.fenetre.destroy()

    def _sauvegarder_horaire(self):
        niveaux = [niveau for niveau, var in self.voulu.items() if var.get()]
        if not niveaux:
            messagebox.showwarning("Horaire", "Sélectionnez au moins un niveau.",
                                   parent=self.fenetre)
            return

        chemin = filedialog.asksaveasfilename(
            parent=self.fenetre,
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not chemin:
            return

        try:
            exporter_horaires(self.tournoi, niveaux, chemin)
        except (ValueError, OSError) as e:
            messagebox.showerror("Horaire", str(e), parent=self.fenetre)
            return

        messagebox.showinfo("Horaire", "Horaire enregistré.", parent=self.fenetre)
        self.fermer()

    def afficher(self):
        niveaux = sorted({int(e[0].code[0])
                          for e in self.tournoi.trier_equipes()
                          if e[0] is not None})

        cadre = tk.Frame(self.fenetre)
        cadre.pack(padx=20, pady=20)

        self.voulu = {niveau: tk.BooleanVar() for niveau in niveaux}
        for niveau, var in self.voulu.items():
            tk.Checkbutton(cadre, text=f'Secondaire {niveau}',
                           variable=var, font=('Arial', 12)).pack(anchor='w')

        tk.Button(cadre, text="Générer", command=self._sauvegarder_horaire).pack(anchor='w', pady=(10, 0))