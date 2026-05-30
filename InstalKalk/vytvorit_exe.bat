@echo off
echo ==============================================
echo VYTVARIM SPUSTITELNY SOUBOR (InstalKalk.exe)
echo ==============================================

rem Aktivujeme lokalni prostredi a zabalime kod a HTML
call .venv\Scripts\activate.bat
pyinstaller --clean --onefile --windowed --name=InstalKalk --add-data "templates;templates" start_local.py

echo Presouvam InstalKalk.exe primo na Vasi plochu...
move /Y dist\InstalKalk.exe "%USERPROFILE%\Desktop\InstalKalk.exe"
rmdir /S /Q dist
rmdir /S /Q build
del InstalKalk.spec

echo.
echo Hotovo! Program InstalKalk.exe se nyni nachazi rovnou na vasi PLOSE.
pause