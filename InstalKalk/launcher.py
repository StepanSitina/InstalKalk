import os
import sys
import json
import urllib.request
import zipfile
import subprocess
import threading
import time
from pathlib import Path

# --- EXPLICITNÍ IMPORTY ZÁVISLOSTÍ ---
# Slouží k tomu, aby je PyInstaller automaticky zabalil do výsledného launcher.exe.
# Aplikace tak nebude vyžadovat instalaci Pythonu na koncovém PC.
import fastapi
import uvicorn
import docx
import openpyxl
import pydantic
import jinja2
import bs4
import requests

# Zde nastavíte URL repozitáře (zip) pro stahování aktualizací
# Příklad: "https://github.com/jmeno/Instalkalk/archive/refs/heads/main.zip"
DOWNLOAD_URL = "https://github.com/VASE_UZIVATELSKE_JMENO/Instalkalk/archive/refs/heads/main.zip"
VERSION_URL = "https://raw.githubusercontent.com/VASE_UZIVATELSKE_JMENO/Instalkalk/main/version.txt"

# Výchozí složka pro instalaci: %APPDATA%\InstalKalk
APPDATA_DIR = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
APP_DIR = APPDATA_DIR / 'InstalKalk'
VERSION_FILE = APP_DIR / 'version.txt'

def check_internet():
    try:
        urllib.request.urlopen('http://www.google.com', timeout=3)
        return True
    except:
        return False

def get_remote_version():
    try:
        response = urllib.request.urlopen(VERSION_URL, timeout=3)
        return response.read().decode('utf-8').strip()
    except:
        return None

def get_local_version():
    if VERSION_FILE.exists():
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return "0.0.0"

def download_and_extract_app():
    print("Stahuji aktuální soubory aplikace z cloudu...")
    zip_path = APP_DIR / "update.zip"
    try:
        # Povolíme přesměrování a stáhneme
        urllib.request.urlretrieve(DOWNLOAD_URL, zip_path)
        
        print("Rozbaluji aplikaci...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Rozbalíme obsah
            zip_ref.extractall(APP_DIR)
            
        os.remove(zip_path)
        print("Instalace / Aktualizace dokončena.")
        return True
    except Exception as e:
        print(f"Chyba při stahování: {e}")
        if zip_path.exists():
            os.remove(zip_path)
        return False

def install_or_update():
    if not APP_DIR.exists():
        APP_DIR.mkdir(parents=True, exist_ok=True)
        print("InstalKalk není nainstalován. Zahajuji instalaci...")
        if check_internet():
            if download_and_extract_app():
                remote_version = get_remote_version() or "1.0.0"
                with open(VERSION_FILE, 'w', encoding='utf-8') as f:
                    f.write(remote_version)
        else:
            print("K první instalaci je bezpodmínečně nutné připojení k internetu.")
            input("Stiskněte Enter pro ukončení...")
            sys.exit(1)
    else:
        print("Hledám aktualizace...")
        if check_internet():
            remote_v = get_remote_version()
            local_v = get_local_version()
            if remote_v and remote_v != local_v:
                print(f"Nalezena nová verze: {remote_v} (Aktuální: {local_v}). Aktualizuji...")
                if download_and_extract_app():
                    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
                        f.write(remote_v)
            else:
                print("Aplikace je aktuální.")
        else:
            print("Režim offline. Spouštím místní verzi aplikace.")

def run_app():
    print("Startuji InstalKalk server na pozadí...")
    
    # Github .zip obvykle vytvoří složku Instalkalk-main - to je třeba najít
    app_source_dir = APP_DIR
    for d in APP_DIR.iterdir():
        if d.is_dir() and "Instalkalk" in d.name:
            app_source_dir = d
            break
            
    # Musíme upravit sys.path, aby Python našel stažené zdrojáky (main.py)
    sys.path.insert(0, str(app_source_dir))
    
    # Otevřít prohlížeč se zpožděním
    def open_browser():
        time.sleep(2)
        os.system("start http://127.0.0.1:8000")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        import main # Tento main.py se nahraje z app_source_dir
        # Spustíme Uvicorn bez reloadu v aktuálním procesu (už máme vše potřebné v paměti)
        uvicorn.run(main.app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"Kritická chyba při spouštění serveru: {e}")
        input("Stiskněte Enter pro ukončení...")

if __name__ == '__main__':
    install_or_update()
    run_app()
