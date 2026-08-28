import os
import tkinter as tk

from tkinter import filedialog

from src.vue.fenetre_ajout_fiches import UIAjoutPartie
from src.modele.tournoi import Tournoi
from src.vue.tournoi_vue import TournoiVue


def initialiser_tournoi():
    for fichier in os.listdir(os.getcwd()+"/src"):
        if fichier == "dernier.json":
            return Tournoi.charger(os.getcwd() + "/" + fichier)
    return None


class App:
    """
    Application principale du logiciel
    """

    tournoi: Tournoi | None

    def __init__(self, racine: tk.Tk):
        """
        Initialisation
        :param racine: composant dans lequel l'app est desinnées.
        """
        self.racine = racine
        self.tournoi = initialiser_tournoi()

        racine.title("ULDGeH")

        cadre = tk.Canvas(racine, width=1800, height=1345)
        cadre.pack()

        # Barre de boutons
        barre = tk.Frame(cadre)
        barre.pack(fill="both")

        tk.Button(barre, text="ajouter", command=self.creer_fenetre_ajout_partie).pack(side="left")
        tk.Button(barre, text="ouvrir", command=self.ouvrir_tournoi).pack(side="left")
        tk.Button(barre, text="sauvegarder", command=self.sauvegarder_json).pack(side="left")
        tk.Button(barre, text="Exporter au format XLSX", command = self.sauvegarder_excel).pack(side="left")

        # Contenu principal
        page = self.page=tk.Frame(cadre)
        self.rafraichir()

        page.pack(fill="both")

    def ouvrir_tournoi(self):
        chemin = filedialog.askopenfilename(parent=self.racine, filetypes=[("json", ".json"),("xlsx", ".xlsx")])
        if chemin:
            self.tournoi = Tournoi.charger(chemin)
            self.tournoi.sauvegarder("dernier.json")
        self.rafraichir()

    def _maj_tournoi(self, tournoi):
        if tournoi is not None:
            self.tournoi = tournoi
            print("Tounoi mis à jour avec succès")
            self.rafraichir()

    def rafraichir(self):
        # Vider le contenu actuel
        for widget in self.page.winfo_children():
            widget.destroy()

        #Nouveau contenu
        if self.tournoi:
            TournoiVue(tournoi=self.tournoi).afficher(self.page)
        else:
            tk.Label(self.page, text="Veuillez charger un tournoi").pack(side="left")

    def sauvegarder_excel(self):
        chemin = filedialog.asksaveasfilename(parent=self.racine, filetypes=[("xlsx", ".xlsx")])
        if chemin and self.tournoi:
            self.tournoi.generer_excel(chemin)

    def sauvegarder_json(self):
        if self.tournoi:
            self.tournoi.sauvegarder("dernier.json")

    def creer_fenetre_ajout_partie(self):
        if not self.tournoi:
            return 1

        UIAjoutPartie(self.racine, self.tournoi, self._maj_tournoi)


if __name__ == "__main__":
    racine = tk.Tk()
    app = App(racine)
    racine.mainloop()
