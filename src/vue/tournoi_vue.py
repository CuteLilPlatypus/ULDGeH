import tkinter as tk
from tkinter import ttk

from src.modele.partie import Partie
from src.modele.tournoi import Tournoi
from src.vue.style import Couleur

couleurs = {
    1: Couleur.ORANGE,
    2: Couleur.ROSE,
    3: Couleur.BLEU,
    4: Couleur.VERT,
    5: Couleur.JAUNE,
}


def creer_match(parent, equipe1, equipe2, score1, score2):
    niveau = int(equipe1[0])
    couleur_niveau = couleurs[niveau]

    frame = tk.Frame(
        parent,
        bd=1,
        relief="solid",
        bg="black"
    )

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
    tournoi: Tournoi

    def __init__(self, tournoi: Tournoi):
        self.tournoi = tournoi

    def afficher(self, parent: tk.Frame):
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=('Arial', '14', 'bold'), padding=10)
        navigation = ttk.Notebook(parent)

        for niveau in self.tournoi.trier_parties():
            if not niveau:
                continue

            onglet = tk.Frame(navigation)
            navigation.add(onglet, text=f'Résultats secondaire {niveau[0].niveau}')
            canvas = tk.Canvas(onglet)
            scrollbar_v = tk.Scrollbar(onglet, orient="vertical", width=25, command=canvas.yview)
            scrollbar_h = tk.Scrollbar(onglet, orient="horizontal", width=25, command=canvas.xview)
            canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")

            canvas.pack(side="left", fill="both", expand=True)

            interieur = tk.Frame(canvas)
            canvas.create_window((0, 0), window=interieur, anchor="nw")

            interieur.bind("<Configure>", lambda e, can=canvas: can.configure(scrollregion=can.bbox("all")))

            canvas.bind("<Enter>", lambda e, can=canvas: (
                can.bind_all("<MouseWheel>", lambda e, can=can: can.yview_scroll(int(-1 * (e.delta / 120)), "units")),
                can.bind_all("<Shift-MouseWheel>",
                             lambda e, can=can: can.xview_scroll(int(-1 * (e.delta / 120)), "units")),
            ))
            canvas.bind("<Leave>", lambda e, can=canvas: (
                can.unbind_all("<MouseWheel>"),
                can.unbind_all("<Shift-MouseWheel>"),
            ))

            parties_plateau: dict[int, list[Partie]] = {}
            for partie in niveau:
                if partie.plateau not in parties_plateau:
                    parties_plateau[partie.plateau] = []
                parties_plateau[partie.plateau].append(partie)

            match_max = max(partie.numero for partie in niveau)

            for r in range(min(parties_plateau.keys()), max(parties_plateau.keys()) + 1):
                tk.Label(
                    interieur,
                    text=f'Plateau {r}',
                    anchor="w",
                    font=("Arial", 14),
                    padx=10,
                ).grid(row=r + 1, column=0, sticky="nsw")

                for c in range(1, match_max + 1):
                    tk.Label(
                        interieur,
                        text=f'Match {c}',
                        anchor="w",
                        font=("Arial", 14),
                        padx=10,
                    ).grid(row=0, column=c, sticky="ns")

                    partie = next((p for p in parties_plateau[r] if p.numero == c), None)
                    if partie is None:
                        continue

                    equipe1 = partie.eq_a
                    equipe2 = partie.eq_b

                    score1 = self.tournoi.equipes[equipe1].scores[c - 1]
                    score2 = self.tournoi.equipes[equipe2].scores[c - 1]

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

        for niveau in self.tournoi.trier_equipes():
            if not niveau:
                continue
            largeurs = {
                "Code": 120,
                "Équipe": 360,
                "Joueur": 360,
                "Moyenne": 120,
            }

            onglet = tk.Frame(navigation)
            navigation.add(onglet, text=f'Stats ind. secondaire {niveau[0].code[0]}')

            partie_max = max(len(joueur.scores) for joueur in (equipe_calcul for equipe_calcul in niveau))
            colonnes = ["Code", "Équipe", "Joueur", "Moyenne"] + [f"M{i + 1}" for i in range(partie_max)]

            ttk.Style().configure("Treeview", rowheight=80)

            tableau = ttk.Treeview(onglet, columns=colonnes, show="headings", style="Stats.Treeview")
            scrollbar_v = tk.Scrollbar(onglet, orient="vertical", width=25, command=tableau.yview)
            scrollbar_h = tk.Scrollbar(onglet, orient="horizontal", width=25, command=tableau.xview)
            tableau.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

            for col in colonnes:
                tableau.heading(col, text=col)
                tableau.column(col, width=130, anchor="center")

            for equipe in niveau:
                for joueur in equipe.joueurs:
                    valeurs = [
                        equipe.code,
                        equipe.nom,
                        joueur.nom,
                        joueur.moyenne(),
                        *[joueur.scores[i] if i < len(joueur.scores) and joueur.scores[i] else "" for i in
                          range(partie_max)]
                    ]
                    tableau.insert("", "end", values=valeurs)

            for col in colonnes:
                tableau.heading(col, text=col)
                tableau.column(col, width=largeurs.get(col, 120), anchor="center", stretch=True)

            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")
            tableau.pack(side="left", fill="both", expand=True)

        navigation.pack(side='top', fill='both', expand=True)
