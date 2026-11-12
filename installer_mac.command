#!/bin/bash
# Installation de l'application (macOS) : double-cliquez sur ce fichier.
cd "$(dirname "$0")" || exit 1

pause_et_quitter() {
    echo
    read -n 1 -s -r -p "Appuyez sur une touche pour fermer..."
    echo
    exit "$1"
}

echo "=== Installation de l'application ==="
echo

# Le Python fourni par macOS (/usr/bin/python3) embarque un Tk 8.5 obsolète et défectueux :
# on cherche d'abord un Python de python.org ou de Homebrew, avec Tk >= 8.6.
trouver_python() {
    local candidat
    for candidat in \
        /Library/Frameworks/Python.framework/Versions/Current/bin/python3 \
        /opt/homebrew/bin/python3 \
        /usr/local/bin/python3 \
        "$(command -v python3)"; do
        if [ -x "$candidat" ] && "$candidat" -c "import sys, tkinter; sys.exit(0 if tkinter.TkVersion >= 8.6 else 1)" 2>/dev/null; then
            echo "$candidat"
            return 0
        fi
    done
    return 1
}

PY="$(trouver_python)"
if [ -z "$PY" ]; then
    echo "Aucun Python 3 avec Tk 8.6 ou plus n'a été trouvé."
    echo "Installez Python depuis https://www.python.org/downloads/macos/ puis relancez ce fichier."
    echo "(Avec Homebrew : brew install python python-tk)"
    pause_et_quitter 1
fi
echo "Python utilisé : $PY"

if [ ! -x ".venv/bin/python" ]; then
    echo "Création de l'environnement..."
    "$PY" -m venv .venv || { echo "Échec de la création de l'environnement."; pause_et_quitter 1; }
fi

echo "Installation des dépendances..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt || {
    echo
    echo "Échec de l'installation des dépendances. Vérifiez la connexion Internet."
    pause_et_quitter 1
}

echo
echo "Installation terminée. Lancez l'application avec lancer_mac.command"
pause_et_quitter 0
