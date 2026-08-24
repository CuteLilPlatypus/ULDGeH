# ULDGeH

**ULDGeH** (*Un Logiciel De Génies en Herbe*) est un petit programme Python servant à administrer un tournoi de Génies en herbe. Il vise à accélérer la compilation des résultats, remplaçant ainsi le document Excel qui remplissait auparavant cette fonction.

Programme développé par Simon Charbonneau.

## Fonctionnalités

Le logiciel permet de :

- **Initialiser un tournoi** à partir du fichier Excel envoyé par le MPGHP, ce qui crée automatiquement les équipes ;
- **Ajouter des parties** à ce tournoi ;
- **Exporter** celui-ci au format JSON et Excel (export Excel en cours de développement) pour la diffusion des résultats ;
- **Compiler automatiquement les statistiques** et établir les classements généraux, tant pour les équipes que pour les joueurs.

## Utilisation

### Ouvrir un tournoi

Cliquer sur le bouton **« ouvrir »** et sélectionner le fichier voulu :
- un fichier **JSON** pour reprendre un tournoi déjà initialisé ;
- un fichier **Excel** pour en créer un nouveau.

### Sauvegarder un tournoi

Il est possible d'enregistrer le tournoi au format JSON pour une utilisation ultérieure. Pour ce faire, cliquer simplement sur le bouton **« sauvegarder »**. Un fichier `dernier.json` sera créé dans le même dossier que le fichier principal du programme, `main.py`.

### Exporter un tournoi

Pour exporter le fichier au format XLSX (Excel, Sheets, Calc et autres tableurs), cliquer sur le bouton **« Exporter au format XLSX »**.

### Ajouter une partie

Pour ajouter une partie, cliquer sur le bouton **« ajouter »** et remplir le tableau :

| Colonne | Description |
|---|---|
| **Nom (code)** | Nom du joueur ou code de l'équipe. Si un code d'équipe valide est entré, le nom de l'équipe se complète automatiquement lorsque le joueur y est enregistré. |
| **Score** | Score de l'entité inscrite dans la colonne à sa gauche (équipe ou joueur). |
| **Match** | Numéro du match, calculé sur l'ensemble de la saison et non par soirée (ex. : le premier match de la deuxième soirée porte le numéro 5). |
| **Plateau** | Numéro du plateau où se déroule la partie. |

**Raccourcis de saisie :**
- La touche **Entrée** permet de passer directement à la case suivante.
- Les cases de code d'équipe et de score avancent automatiquement à la case suivante une fois trois chiffres saisis.
- Les cases de numéro de match et de plateau avancent automatiquement une fois deux chiffres saisis.
- Les cases de nom avancent automatiquement à la case suivante une fois le nom complété (autocomplétion).
