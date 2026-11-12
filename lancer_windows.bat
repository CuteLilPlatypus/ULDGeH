@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo L'application n'est pas installee. Lancez d'abord installer_windows.bat
    echo.
    pause
    exit /b 1
)

rem pythonw : pas de fenetre noire. Pour voir les erreurs, remplacez pythonw par python.
start "" ".venv\Scripts\pythonw.exe" -m src.main
