"""
Fichier principal du projet
"""
import os
import tkinter as tk

from tkinter import filedialog

from src.vue.fenetre_ajout_fiches import UIAjoutPartie
from src.modele.tournoi import Tournoi
from src.vue.tournoi_vue import TournoiVue


def initialiser_tournoi() -> Tournoi:
    """
    Initialise un tournoi depuis le fichier de sauvegarde, s'il existe.
    :return: Un tournoi initialisé, si un fichier existe, sinon un tournoi vide.
    """
    for fichier in os.listdir(os.getcwd()):
        if fichier == "dernier.json":
            return Tournoi.charger(os.getcwd() + "/" + fichier)
    return Tournoi()


class App:
    """
    Application principale du logiciel
    """

    def __init__(self, racine: tk.Tk):
        """
        Initialisation
        :param racine: composant dans lequel l'app est dessinée.
        """
        self.racine = racine
        self.tournoi = initialiser_tournoi()

        #Titre de fenêtre et cadre principal
        racine.title("ULDGeH")
        cadre = tk.Canvas(racine, width=1200, height=1500)
        cadre.pack()

        # Barre de boutons
        barre = tk.Frame(cadre)
        barre.pack(fill="both")

        # Chaque bouton appelle la méthode correspondante ci-dessous (voir plus bas dans la classe)
        tk.Button(barre, text="ajouter", command=self.creer_fenetre_ajout_partie).pack(side="left")
        tk.Button(barre, text="ouvrir", command=self.ouvrir_tournoi).pack(side="left")
        tk.Button(barre, text="sauvegarder", command=self.sauvegarder_json).pack(side="left")
        tk.Button(barre, text="Exporter au format XLSX", command = self.sauvegarder_excel).pack(side="left")
        # Raccourcis clavier connexes aux boutons (mêmes fonctions que ci-dessus)
        racine.bind("<Control-a>", lambda e: self.creer_fenetre_ajout_partie())
        racine.bind("<Control-s>", lambda e: self.sauvegarder_json())
        racine.bind("<Control-e>", lambda e: self.sauvegarder_excel())
        racine.bind("<Control-o>", lambda e: self.ouvrir_tournoi())

        # Contenu principal : un cadre vide au départ, rempli par rafraichir()
        # (qui affichera soit la vue du tournoi, soit un message si aucun tournoi n'est chargé)
        page = self.page=tk.Frame(cadre)
        self.rafraichir()

        page.pack()

    def ouvrir_tournoi(self):
        """
        Fonction qui sert à charger un tournoi dans l'App
        """
        chemin = filedialog.askopenfilename(parent=self.racine, filetypes=[("json", ".json"),("xlsx", ".xlsx")])
        if chemin:
            self.tournoi = Tournoi.charger(chemin)
            self.tournoi.sauvegarder_json("dernier.json")
        self.rafraichir()

    def _maj_tournoi(self, tournoi: Tournoi):
        """
        Fonction interne pour remplacer le tournoi interne par un autre et mettre l'affichage à jour
        :param tournoi: Tournoi de remplacement
        """
        if tournoi is not None:
            self.tournoi = tournoi
            self.rafraichir()

    def rafraichir(self):
        """
        Fonction qui sert à rafraichir tout l'affichage de l'App
        """
        # Vider le contenu actuel
        for widget in self.page.winfo_children():
            widget.destroy()

        #Nouveau contenu
        if self.tournoi:
            TournoiVue(tournoi=self.tournoi).afficher(self.page)
        else:
            tk.Label(self.page, text="Veuillez charger un tournoi").pack(side="left")

    # Fonctions des boutons
    def sauvegarder_excel(self):
        """
        Fonction du bouton "Exporter au format XLSX" : demande à l'utilisateur
        où enregistrer le fichier, puis génère le rapport Excel du tournoi.
        """
        chemin = filedialog.asksaveasfilename(parent=self.racine, filetypes=[("xlsx", ".xlsx")])
        if chemin and self.tournoi:
            self.tournoi.generer_excel(chemin)

    def sauvegarder_json(self):
        """
        Fonction du bouton "sauvegarder" : sauvegarde l'état actuel du tournoi
        dans le fichier "dernier.json", qui sera rechargé automatiquement
        au prochain démarrage de l'application (voir initialiser_tournoi).
        """
        if self.tournoi:
            self.tournoi.sauvegarder_json("dernier.json")

    def creer_fenetre_ajout_partie(self):
        """
        Fonction du bouton "ajouter" : ouvre la fenêtre de saisie d'une nouvelle
        partie. Ne fait rien si aucun tournoi n'est chargé.
        Une fois la partie ajoutée, self._maj_tournoi est appelée (voir UIAjoutPartie)
        pour mettre à jour l'affichage.
        """
        if not self.tournoi:
            return 1

        UIAjoutPartie(self.racine, self.tournoi, self._maj_tournoi)


if __name__ == "__main__":
    racine = tk.Tk()
    app = App(racine)
    racine.mainloop()
