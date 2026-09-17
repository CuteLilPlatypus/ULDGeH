"""
Fichier qui contient l'affichage principal du tournoi (TournoiVue), dans la
fenêtre de l'application. Affiche un onglet "Résultats" par niveau (grille de
plateaux x matchs, avec le code et le score de chaque équipe), suivi d'un onglet
"Stats ind." par niveau (tableau des statistiques individuelles des joueurs).
"""
import tkinter as tk
from tkinter import ttk

from src.modele.partie import Partie
from src.modele.tournoi import Tournoi
from src.vue.style import Couleur

# Couleur associée à chaque niveau de secondaire, pour l'identification visuelle
# des équipes dans la grille de résultats.
couleurs = {
    1: Couleur.ORANGE,
    2: Couleur.ROSE,
    3: Couleur.BLEU,
    4: Couleur.VERT,
    5: Couleur.JAUNE,
}


def creer_match(parent, equipe1, equipe2, score1, score2):
    """
    Crée le petit bloc visuel représentant un match : une case 2x2 avec, sur
    chaque rangée, le code de l'équipe (coloré selon son niveau) et son score.
    :param parent: widget parent dans lequel placer le bloc
    :param equipe1: code de l'équipe A (son 1er chiffre détermine le niveau/couleur)
    :param equipe2: code de l'équipe B
    :param score1: score (ou texte "Victoire"/"Forfait") de l'équipe A
    :param score2: score (ou texte "Victoire"/"Forfait") de l'équipe B
    :return: le Frame Tkinter représentant le match, prêt à être placé (grid/pack)
    """
    niveau = int(equipe1[0])
    couleur_niveau = couleurs[niveau]

    frame = tk.Frame(
        parent,
        bd=1,
        relief="solid",
        bg="black"
    )

    # (rangée, colonne, texte affiché, couleur de fond)
    configs = [
        (0, 0, equipe1, couleur_niveau),
        (0, 1, score1, "white"),
        (1, 0, equipe2, couleur_niveau),
        (1, 1, score2, "white"),
    ]

    for r, c, texte, couleur in configs:
        lbl = tk.Label(
            frame,
            text=str(texte),
            width=5,
            height=1,
            bg=couleur,
            font=("Arial", 16),
        )
        lbl.grid(row=r, column=c, sticky="nsew")

    return frame


class TournoiVue:
    """
    Vue principale de l'application : affiche le tournoi dans un widget à onglets
    (Notebook), avec un onglet "Résultats" et un onglet "Stats ind." par niveau
    de secondaire ayant des données à afficher.
    """
    tournoi: Tournoi

    def __init__(self, tournoi: Tournoi):
        self.tournoi = tournoi

    def afficher(self, parent: tk.Frame):
        """
        Construit et place tout l'affichage du tournoi dans `parent`.
        :param parent: widget dans lequel placer le Notebook d'onglets
        """
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=('Arial', '14', 'bold'), padding=10)
        navigation = ttk.Notebook(parent)

        # -----------------------------------------------------------------
        # 1) Un onglet "Résultats secondaire X" par niveau ayant des parties,
        #    affichant une grille Plateau x Match, chaque case étant un bloc
        #    créé par creer_match() (code + score de chaque équipe).
        # -----------------------------------------------------------------
        for niveau in self.tournoi.trier_parties():
            if not niveau:
                continue

            onglet = tk.Frame(navigation)
            navigation.add(onglet, text=f'Résultats secondaire {niveau[0].niveau}')

            # La grille peut être grande (beaucoup de plateaux/matchs) : on la place
            # dans un Canvas défilable, avec des barres de défilement horizontale et verticale.
            canvas = tk.Canvas(onglet)
            scrollbar_v = tk.Scrollbar(onglet, orient="vertical", width=25, command=canvas.yview)
            scrollbar_h = tk.Scrollbar(onglet, orient="horizontal", width=25, command=canvas.xview)
            canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")

            canvas.pack(side="left", fill="both", expand=True)

            # Frame interne contenant la grille elle-même, dessinée à l'intérieur du Canvas.
            interieur = tk.Frame(canvas)
            canvas.create_window((0, 0), window=interieur, anchor="nw")

            # Met à jour la zone de défilement à chaque changement de taille du contenu.
            interieur.bind("<Configure>", lambda e, can=canvas: can.configure(scrollregion=can.bbox("all")))

            # Active/désactive le défilement à la molette uniquement quand la souris
            # est au-dessus de ce Canvas précis (pour ne pas interférer avec les autres onglets).
            canvas.bind("<Enter>", lambda e, can=canvas: (
                can.bind_all("<MouseWheel>", lambda e, can=can: can.yview_scroll(int(-1 * (e.delta / 120)), "units")),
                can.bind_all("<Shift-MouseWheel>",
                             lambda e, can=can: can.xview_scroll(int(-1 * (e.delta / 120)), "units")),
            ))
            canvas.bind("<Leave>", lambda e, can=canvas: (
                can.unbind_all("<MouseWheel>"),
                can.unbind_all("<Shift-MouseWheel>"),
            ))

            # Regroupement des parties du niveau par numéro de plateau.
            parties_plateau: dict[int, list[Partie]] = {}
            for partie in niveau:
                if partie.plateau not in parties_plateau:
                    parties_plateau[partie.plateau] = []
                parties_plateau[partie.plateau].append(partie)

            match_max = max(partie.numero for partie in niveau)

            # Construction de la grille : une rangée par plateau, une colonne par match.
            for r in range(min(parties_plateau.keys()), max(parties_plateau.keys()) + 1):
                # Étiquette de la rangée (nom du plateau)
                tk.Label(
                    interieur,
                    text=f'Plateau {r}',
                    anchor="w",
                    font=("Arial", 14),
                    padx=10,
                ).grid(row=r + 1, column=0, sticky="nsw")

                for c in range(1, match_max + 1):
                    # Étiquette de la colonne (numéro de match), recréée à chaque plateau
                    # mais toujours placée sur la rangée d'en-tête (row=0).
                    tk.Label(
                        interieur,
                        text=f'Match {c}',
                        anchor="w",
                        font=("Arial", 14),
                        padx=10,
                    ).grid(row=0, column=c, sticky="ns")

                    # Recherche de la partie correspondant à ce plateau/match, s'il y en a une.
                    partie = next((p for p in parties_plateau[r] if p.numero == c), None)
                    if partie is None:
                        continue  # Case vide (aucun match prévu à cet emplacement)

                    equipe1 = partie.eq_a
                    equipe2 = partie.eq_b

                    score1 = self.tournoi.equipes[equipe1].scores[c - 1]
                    score2 = self.tournoi.equipes[equipe2].scores[c - 1]

                    # Score manquant pour au moins une équipe : le match s'est réglé
                    # par forfait (ou victoire par défaut), affiché comme tel plutôt qu'un score.
                    if score1 is None or score2 is None:
                        if partie.vainqueur == equipe1:
                            score1 = "Victoire"
                            score2 = "Forfait"
                        elif partie.vainqueur == equipe2:
                            score1 = "Forfait"
                            score2 = "Victoire"
                        else:
                            score1 = score2 = "Forfait"

                    bloc = creer_match(interieur, equipe1, equipe2, score1, score2)
                    bloc.grid(row=r + 1, column=c, padx=1, pady=1)

        # -----------------------------------------------------------------
        # 2) Un onglet "Stats ind. secondaire X" par niveau ayant des équipes,
        #    affichant un tableau (Treeview) de toutes les statistiques
        #    individuelles des joueurs (moyenne, score par match, etc.)
        # -----------------------------------------------------------------
        for niveau in self.tournoi.trier_equipes():
            if not niveau:
                continue
            # Largeurs personnalisées pour certaines colonnes (les autres utilisent 120 par défaut)
            largeurs = {
                "Code": 120,
                "Équipe": 360,
                "Joueur": 360,
                "Moyenne": 120,
            }

            onglet = tk.Frame(navigation)
            navigation.add(onglet, text=f'Stats ind. secondaire {niveau[0].code[0]}')

            # Nombre maximal de matchs joués par un joueur du niveau (détermine le nb de colonnes "Match")
            partie_max = max(len(joueur.scores) for joueur in (equipe_calcul for equipe_calcul in niveau))
            colonnes = ["Code", "Équipe", "Joueur", "Moyenne"] + [f"M{i + 1}" for i in range(partie_max)]

            ttk.Style().configure("Treeview", rowheight=80)

            tableau = ttk.Treeview(onglet, columns=colonnes, show="headings", style="Stats.Treeview")
            scrollbar_v = tk.Scrollbar(onglet, orient="vertical", width=25, command=tableau.yview)
            scrollbar_h = tk.Scrollbar(onglet, orient="horizontal", width=25, command=tableau.xview)
            tableau.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

            # Première passe : configuration des en-têtes/largeurs par défaut
            # (nécessaire pour que le tableau existe avant d'y insérer des lignes).
            for col in colonnes:
                tableau.heading(col, text=col)
                tableau.column(col, width=130, anchor="center")

            # Une ligne par joueur, tous niveaux/équipes confondus pour ce niveau.
            for equipe in niveau:
                for joueur in equipe.joueurs:
                    valeurs = [
                        equipe.code,
                        equipe.nom,
                        joueur.nom,
                        joueur.moyenne(),
                        # Score de chaque match (vide si le joueur n'a pas joué ou pas de score)
                        *[joueur.scores[i] if i < len(joueur.scores) and joueur.scores[i] else "" for i in
                          range(partie_max)]
                    ]
                    tableau.insert("", "end", values=valeurs)

            # Deuxième passe : applique les largeurs personnalisées définies plus haut
            # (remplace les largeurs par défaut posées avant l'insertion des données).
            for col in colonnes:
                tableau.heading(col, text=col)
                tableau.column(col, width=largeurs.get(col, 120), anchor="center", stretch=True)

            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")
            tableau.pack(side="left", fill="both", expand=True)

        navigation.pack(side='top', fill='both', expand=True)
