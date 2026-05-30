import os
import sys
import threading
import time
import webbrowser
import multiprocessing
import uvicorn
from main import app

def open_browser():
    time.sleep(2)  # Počkáme 2 sekundy, než naběhne server
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == '__main__':
    # Nutné pro PyInstaller v OS Windows
    multiprocessing.freeze_support()
    
    # Otevřeme prohlížeč na pozadí
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Spustíme samotný backend
    uvicorn.run(app, host="127.0.0.1", port=8000)