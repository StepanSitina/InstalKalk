@echo off
echo ==============================================
echo VYTVARIM SPUSTITELNY INSTALACNI LAUNCHER (.EXE)
echo ==============================================

rem Během kompilace pomocí PyInstaller vložíme všechny moduly
rem do jednoho výsledného .exe souboru.
rem V konečném souboru tedy bude obsažen i samotný Python.

pip install pyinstaller

pyinstaller --onefile --icon=NONE --name=InstalKalk_Launcher launcher.py

echo.
echo Hotovo! Soubor se nachazi ve slozce "dist\InstalKalk_Launcher.exe"
pause