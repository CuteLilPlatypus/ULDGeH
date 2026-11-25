import math, copy, random

from collections.abc import Iterable
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as col
from openpyxl.worksheet.formula import ArrayFormula
from src.modele.tournoi import Tournoi
from src.vue.style import Couleur
# ---- Paramètres --------------------------------------------------------------
HEURES = ['16h30', '17h15', '18h30', '19h15'] #Heures des matchs
NB_MATCHS = 20 #Nombre de matchs du tournoi
POLICE = 'Arial'

_FIN = Side(style='thin')
_EPAIS = Side(style='medium')
_BORD = Border(left=_FIN, right=_FIN, top=_FIN, bottom=_FIN)
_CENTRE = Alignment(horizontal='center', vertical='center')

# ---- Utilitaires -------------------------------------------------------------
COULEURS=[Couleur.ORANGE[1:], Couleur.ROSE[1:], Couleur.BLEU[1:], Couleur.JAUNE[1:], Couleur.VERT[1:]]
def _code(equipe):
    """Code d'équipe : entier si possible (201), sinon texte ('Pause')."""
    c = str(equipe.code)
    return int(c) if c.isdigit() else c


def _nom(equipe):
    return getattr(equipe, 'nom', None) or getattr(equipe, 'name', None) or ''

def _style(cell, fond=None, gras=False, bordure=True, rotation=0):
    cell.font = Font(name=POLICE, size=11, bold=gras)
    cell.alignment = Alignment(horizontal='center', vertical='center', text_rotation=rotation)
    if bordure:
        cell.border = _BORD
    if fond:
        cell.fill = PatternFill('solid', start_color=fond, end_color=fond)

def _generer_horaire(tournoi:Tournoi, niveau:int):
    equipes = list(tournoi.trier_equipes()[niveau-1])   # copie
    random.shuffle(equipes)
    if len(equipes) % 2 == 1:
        pause = copy.copy(equipes[0])
        pause.code = 'Pause'
        equipes.append(pause)
    n = len(equipes)
    m = n - 1
    tours = []
    for r in range(m):
        matchs = [(equipes[r], equipes[n-1])]
        for k in range(1, n // 2):
            matchs.append((equipes[(r+k) % m], equipes[(r-k) % m]))
        tours.append(matchs)
    return tours


# ---- Données -----------------------------------------------------------------
def _construire_niveau(tournoi:Tournoi, niveau:int):
    liste = [e for e in tournoi.trier_equipes()[niveau - 1] if e is not None]
    if not liste:
        return None
    equipes = sorted(((_code(e), _nom(e)) for e in liste), key=lambda t: t[0])
    codes = [c for c, _ in equipes]

    tours = _generer_horaire(tournoi, niveau)
    if NB_MATCHS:
        tours = tours[:NB_MATCHS]

    grille: dict[int | str, list[int | str | None]] = {c: [None] * len(tours) for c in codes}
    for r, tour in enumerate(tours):
        for a, b in tour:
            ca, cb = _code(a), _code(b)
            if ca == 'Pause':
                grille[cb][r] = 'Pause'
            elif cb == 'Pause':
                grille[ca][r] = 'Pause'
            else:
                grille[ca][r] = cb
                grille[cb][r] = ca

    if any(v is None for ligne in grille.values() for v in ligne):
        raise ValueError(
            f"Niveau {niveau} : _generer_horaire ne donne pas un horaire complet "
            f"(une équipe n'a pas d'adversaire dans un des matchs).")

    return {'niveau': niveau, 'equipes': equipes, 'grille': grille,
            'nb_matchs': len(tours), 'impair': len(codes) % 2 == 1}


# ---- Feuilles ----------------------------------------------------------------
def _feuille_equipes(wb, niveaux):
    ws = wb.active
    ws.title = 'Équipes'
    for i, d in enumerate(niveaux):
        c1, c2 = 2 * i + 1, 2 * i + 2
        fond = COULEURS[(d['niveau']-1) % len(COULEURS)]
        ws.merge_cells(start_row=1, start_column=c1, end_row=1, end_column=c2)
        ws.cell(1, c1, f"Secondaire {d['niveau']}")
        for c in (c1, c2):
            _style(ws.cell(1, c), gras=True)
        for r, (code, nom) in enumerate(d['equipes'], start=2):
            ws.cell(r, c1, code)
            ws.cell(r, c2, nom)
            _style(ws.cell(r, c1), fond)
            _style(ws.cell(r, c2), fond)
            ws.cell(r, c2).alignment = Alignment(horizontal='left', vertical='center')
        ws.column_dimensions[col(c1)].width = 7
        ws.column_dimensions[col(c2)].width = 42


def _feuille_grille(wb, d, k):
    """Grille équipe × match du niveau (équivalent de Feuil2 / Horaire2)."""
    ws = wb.create_sheet(f"Horaire S{d['niveau']}")
    n, R = len(d['equipes']), d['nb_matchs']
    for s in range(math.ceil(R / k)):
        c1 = 2 + s * k
        c2 = min(c1 + k - 1, 1 + R)
        ws.merge_cells(start_row=1, start_column=c1, end_row=1, end_column=c2)
        ws.cell(1, c1, f'Soirée {s + 1}')
        for c in range(c1, c2 + 1):
            _style(ws.cell(1, c), gras=True)
    ws.cell(2, 1, 'équipe')
    _style(ws.cell(2, 1), gras=True)
    for m in range(1, R + 1):
        ws.cell(2, 1 + m, m)
        _style(ws.cell(2, 1 + m), gras=True)
    for i, (code, _) in enumerate(d['equipes']):
        r = 3 + i
        ws.cell(r, 1, code)
        _style(ws.cell(r, 1), gras=True)
        for m in range(R):
            ws.cell(r, 2 + m, d['grille'][code][m])
            _style(ws.cell(r, 2 + m))
    # trait épais au début de chaque soirée
    for r in range(1, 3 + n):
        for s in range(math.ceil(R / k)):
            c = ws.cell(r, 2 + s * k)
            b = c.border
            c.border = Border(left=_EPAIS, right=b.right, top=b.top, bottom=b.bottom)
    ws.column_dimensions['A'].width = 9
    for m in range(1, R + 1):
        ws.column_dimensions[col(1 + m)].width = 7
    d['ref_equipes'] = f"'{ws.title}'!$A$3:$A${2 + n}"
    d['ref_grille'] = f"'{ws.title}'!$B$3:${col(1 + R)}${2 + n}"


def _feuille_soiree(wb, niveaux, s, k):
    """Tableau des plateaux d'une soirée (équivalent de Feuil1, colonnes F:L)."""
    ws = wb.create_sheet(f'Soirée {s + 1}')

    # Colonnes : A = niveau, B = plateau, puis les matchs, « Repas » au milieu.
    colonnes, c = [], 3
    for j in range(k):
        if j == k // 2:
            colonnes.append(('repas', None, c))
            c += 1
        colonnes.append(('match', j, c))
        c += 1
    derniere = c - 1

    ws.cell(1, 2, 'Plateau')
    _style(ws.cell(1, 2), gras=True)
    precedent = None
    for type_, j, c in colonnes:
        cell = ws.cell(1, c)
        if type_ == 'repas':
            cell.value = 'Repas'
        else:
            # Le numéro de match est une vraie valeur numérique, affichée « M17 : 16h30 ».
            cell.value = s * k + 1 if precedent is None else f'={precedent}1+1'
            cell.number_format = f'"M"0" : {HEURES[j]}"'
            precedent = col(c)
        _style(cell, gras=True)
    _style(ws.cell(1, 1), bordure=True)

    ligne = 2
    numero = 0
    for i, d in enumerate(niveaux):
        fond = COULEURS[(d['niveau']-1) % len(COULEURS)]
        debut = ligne
        n = len(d['equipes'])
        eq, gr = d['ref_equipes'], d['ref_grille']
        lignes: list[tuple[str,int|None]]
        lignes = [('plateau', p) for p in range(1, n // 2 + 1)]
        if d['impair']:
            lignes.append(('pause', None))

        for type_, p in lignes:
            if type_ == 'plateau':
                numero += 1
                ws.cell(ligne, 2, numero)
            else:
                ws.cell(ligne, 2, 'Pause')
            _style(ws.cell(ligne, 2), fond)

            for kind, j, c in colonnes:
                cell = ws.cell(ligne, c)
                if kind == 'match':
                    m = f'{col(c)}$1'
                    partenaires = f'INDEX({gr},0,{m})'
                    if type_ == 'plateau':
                        tete = f'SMALL(IF(({eq}<{partenaires})*ISNUMBER({partenaires}),{eq}),{p})'
                        f = (f'=IFERROR({tete}&" c. "&'
                             f'INDEX({gr},MATCH({tete},{eq},0),{m}),"")')
                        cell.value = ArrayFormula(cell.coordinate, f)
                    else:
                        cell.value = (f'=IFERROR(INDEX({eq},MATCH("Pause",{partenaires},0))'
                                      f'&" - Pause","")')
                _style(cell, fond)
            ligne += 1

        # Étiquette du niveau, fusionnée verticalement
        if ligne - 1 > debut:
            ws.merge_cells(start_row=debut, start_column=1, end_row=ligne - 1, end_column=1)
        ws.cell(debut, 1, f"{d['niveau']}e Secondaire")
        for r in range(debut, ligne):
            _style(ws.cell(r, 1), fond, rotation=90)
        # trait épais sous chaque niveau
        for r in (ligne - 1,):
            for c in range(1, derniere + 1):
                b = ws.cell(r, c).border
                ws.cell(r, c).border = Border(left=b.left, right=b.right, top=b.top, bottom=_EPAIS)

    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 9
    for _, _, c in colonnes:
        ws.column_dimensions[col(c)].width = 14


# ---- Point d'entrée ----------------------------------------------------------

def exporter_horaires(tournoi, niveaux: Iterable[int], chemin='Horaires.xlsx'):
    """
    tournoi          : le Tournoi (utilise tournoi.trier_equipes()).
    niveaux          : niveaux voulus, ex. [2, 3] (le « masque » de cases à cocher).
    chemin           : fichier .xlsx à créer.
    """
    k = len(HEURES)
    donnees = []
    for niv in sorted(set(niveaux)):
        d = _construire_niveau(tournoi, niv)
        if d is not None:
            donnees.append(d)
    if not donnees:
        raise ValueError('Aucun niveau à exporter.')

    wb = Workbook()
    _feuille_equipes(wb, donnees)
    for d in donnees:
        _feuille_grille(wb, d, k)
    nb_soirees = math.ceil(int(max(d['nb_matchs'] for d in donnees)) / k)
    for s in range(nb_soirees):
        _feuille_soiree(wb, donnees, s, k)
    wb.save(chemin)
    return chemin