# Gestion de tournoi

Application de bureau (Python / Tkinter) pour suivre un tournoi par équipes réparties en niveaux
(secondaire 1 à 5) : saisie des parties, résultats par plateau, statistiques individuelles et
export Excel.

## Installation

### Prérequis

Python 3.9 ou plus récent, **avec tkinter**, à installer depuis
[python.org](https://www.python.org/downloads/).

- **Windows** : cochez « Add python.exe to PATH » pendant l'installation.
- **macOS** : utilisez l'installateur de python.org. Le Python fourni avec macOS (`/usr/bin/python3`)
  embarque un Tk 8.5 obsolète qui peut afficher une fenêtre vide. Avec Homebrew :
  `brew install python python-tk`.

### Première utilisation

Double-cliquez sur le fichier correspondant à votre système (une seule fois, Internet requis) :

| Système | Installation            | Lancement            |
|---------|-------------------------|----------------------|
| Windows | `installer_windows.bat` | `lancer_windows.bat` |
| macOS   | `installer_mac.command` | `lancer_mac.command` |

L'installation crée un environnement isolé dans le dossier `.venv` du projet et y installe
les dépendances de `requirements.txt` (`openpyxl`). Rien n'est modifié dans le Python du système.

Notes :

- **Windows** : le lancement utilise `pythonw` (pas de fenêtre noire). Pour voir les erreurs,
  remplacez `pythonw` par `python` dans `lancer_windows.bat`.
- **macOS** : la fenêtre du Terminal reste ouverte pendant l'exécution ; la fermer quitte
  l'application. Si macOS refuse d'ouvrir un fichier `.command` : clic droit > Ouvrir, ou, dans le
  Terminal depuis le dossier du projet :
  ```
  xattr -dr com.apple.quarantine .
  chmod +x *.command
  ```

### Lancement manuel (développement)

Depuis la **racine du projet** (le dossier qui contient `src/`), car les imports sont de la forme
`from src...` :

```
python -m src.main
```

## Utilisation

### Barre d'outils et raccourcis

| Action                    | Bouton                      | Raccourci |
|---------------------------|-----------------------------|-----------|
| Ajouter une partie        | **Ajouter**                 | `Ctrl+A`  |
| Ouvrir un tournoi         | **Ouvrir**                  | `Ctrl+O`  |
| Sauvegarder (JSON)        | **Sauvegarder**             | `Ctrl+S`  |
| Exporter en Excel         | **Exporter au format XLSX** | `Ctrl+E`  |

Sur macOS, les raccourcis utilisent la touche `Ctrl` (et non `Cmd`).

Tant qu'aucun tournoi n'est chargé, l'écran affiche « Veuillez charger un tournoi » et les actions
d'ajout, de sauvegarde et d'export sont sans effet.

### Ouvrir un tournoi

Le bouton **Ouvrir** accepte deux types de fichiers :

- **`.json`** : un tournoi déjà sauvegardé (reprise du travail en cours) ;
- **`.xlsx`** : la liste des inscriptions, pour créer un nouveau tournoi. Première ligne = en-têtes,
  puis une ligne par équipe :
  - colonne 1 : nom de l'école ;
  - colonne 2 : niveau (le premier caractère est utilisé, de 1 à 5) ;
  - colonne 4 et suivantes : un joueur par colonne.

  Les codes d'équipe sont générés automatiquement (101, 102… pour le niveau 1, 201, 202… pour le
  niveau 2, etc.). Si une école a plusieurs équipes dans un même niveau, une lettre est ajoutée à
  son nom (« École A », « École B »…).

Le tournoi ouvert est enregistré dans `dernier.json`, et **rechargé automatiquement au prochain
démarrage** s'il se trouve dans le dossier de travail.

### Ajouter une partie

La fenêtre d'ajout (`Ctrl+A`) contient, pour chaque équipe, le nom (ou code) de l'équipe, son
score, et le nom et le score de chacun de ses 4 joueurs, puis le numéro de match et le plateau.

- La saisie est pensée pour le clavier : le curseur passe automatiquement au champ suivant et les
  noms d'équipes et de joueurs sont auto-complétés.
- **Forfaits** : saisissez `+` comme score de l'équipe gagnante et `-` pour l'équipe qui déclare
  forfait. Deux `-` donnent un forfait des deux équipes.
- **Échap** ferme la fenêtre.

### Affichage

Une paire d'onglets est créée pour chaque niveau comportant des données :

- **Résultats secondaire N** : grille des matchs par plateau (lignes) et par numéro de match
  (colonnes). Chaque bloc affiche le code des deux équipes sur la couleur de leur niveau et leur
  score (« Victoire » / « Forfait » lorsqu'il n'y a pas de score) ;
- **Stats ind. secondaire N** : tableau des joueurs avec code, équipe, moyenne et score à chaque
  match, avec une bande de fond par équipe.

Le défilement fonctionne à la molette et au **pavé tactile (deux doigts)** ; `Maj` + molette (ou un
balayage horizontal) fait défiler horizontalement. Les onglets s'adaptent à la taille de la fenêtre
(minimum 900 × 500).

### Export Excel

Le bouton **Exporter au format XLSX** génère un classeur avec le classement général, les stats
individuelles et les résultats de matchs de chaque niveau.

## Structure du projet

```
.
├── installer_windows.bat / lancer_windows.bat
├── installer_mac.command / lancer_mac.command
├── requirements.txt
└── src/
    ├── main.py                       # fenêtre principale, barre d'outils, raccourcis
    ├── modele/
    │   ├── tournoi.py                # tournoi, classements, export Excel, sauvegarde JSON
    │   ├── equipe.py
    │   ├── joueur.py
    │   └── partie.py
    └── vue/
        ├── style.py                  # thème (couleurs, polices) et couleurs des niveaux
        ├── tournoi_vue.py            # onglets de résultats et de statistiques
        ├── fenetre_ajout_fiches.py   # fenêtre d'ajout d'une partie
        ├── widgets.py                # champs de saisie (avancement auto, auto-complétion)
        └── defilement.py             # défilement molette / pavé tactile
```
