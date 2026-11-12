@echo off
setlocal
cd /d "%~dp0"
title Installation

echo === Installation de l'application ===
echo.

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo Python 3 est introuvable.
    echo Installez-le depuis https://www.python.org/downloads/ en cochant
    echo "Add python.exe to PATH", puis relancez ce fichier.
    echo.
    pause
    exit /b 1
)

%PY% -c "import tkinter" >nul 2>nul
if errorlevel 1 (
    echo Le module tkinter est absent de cette installation de Python.
    echo Reinstallez Python depuis python.org en laissant coche "tcl/tk and IDLE".
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creation de l'environnement...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo Echec de la creation de l'environnement.
        pause
        exit /b 1
    )
)

echo Installation des dependances...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Echec de l'installation des dependances. Verifiez la connexion Internet.
    pause
    exit /b 1
)

echo.
echo Installation terminee. Lancez l'application avec lancer_windows.bat
echo.
pause
