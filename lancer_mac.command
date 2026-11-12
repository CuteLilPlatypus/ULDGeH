#!/bin/bash
# Lancement de l'application (macOS) : double-cliquez sur ce fichier.
cd "$(dirname "$0")" || exit 1

if [ ! -x ".venv/bin/python" ]; then
    echo "L'application n'est pas installée. Lancez d'abord installer_mac.command"
    echo
    read -n 1 -s -r -p "Appuyez sur une touche pour fermer..."
    echo
    exit 1
fi

exec .venv/bin/python -m src.main
