from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os

from database import init_db, get_db
from scraper import search_products
from export import generate_word, generate_excel

import sys

app = FastAPI(title="InstalKalk - Kalkulátor materiálů")

def get_base_path():
    """Získá správnou cestu k souborům i zkompilovaném (zabaleném) .exe souboru."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()
os.makedirs(os.path.join(base_path, "templates"), exist_ok=True)

# Datové modely Pydantic
class ProjectCreate(BaseModel):
    name: str

class ItemCreate(BaseModel):
    project_id: int
    name: str
    quantity: float
    price: float
    shop: str
    url: str

class SearchQuery(BaseModel):
    query: str

@app.on_event("startup")
def startup():
    init_db()

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = os.path.join(get_base_path(), "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/projects")
def create_project(proj: ProjectCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name) VALUES (?)", (proj.name,))
    conn.commit()
    return {"id": cursor.lastrowid, "name": proj.name}

@app.get("/api/projects")
def get_projects():
    conn = get_db()
    projs = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    return [dict(p) for p in projs]

@app.get("/api/projects/{project_id}/items")
def get_items(project_id: int):
    conn = get_db()
    items = conn.execute("SELECT * FROM items WHERE project_id = ?", (project_id,)).fetchall()
    return [dict(i) for i in items]

@app.post("/api/items")
def add_item(item: ItemCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (project_id, name, quantity, price, shop, url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (item.project_id, item.name, item.quantity, item.price, item.shop, item.url))
    conn.commit()
    return {"status": "success", "id": cursor.lastrowid}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    return {"status": "success"}

@app.post("/api/search")
def search_items(sq: SearchQuery):
    results = search_products(sq.query)
    return results

@app.get("/api/export/word/{project_id}")
def export_word(project_id: int):
    conn = get_db()
    proj = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not proj: return {"error": "Project not found"}
    
    items = conn.execute("SELECT * FROM items WHERE project_id=?", (project_id,)).fetchall()
    filepath = generate_word(proj['name'], [dict(i) for i in items])
    return FileResponse(filepath, filename=f"{proj['name']}_nabidka.docx")

@app.get("/api/export/excel/{project_id}")
def export_excel(project_id: int):
    conn = get_db()
    proj = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not proj: return {"error": "Project not found"}
    
    items = conn.execute("SELECT * FROM items WHERE project_id=?", (project_id,)).fetchall()
    filepath = generate_excel(proj['name'], [dict(i) for i in items])
    return FileResponse(filepath, filename=f"{proj['name']}_kalkulace.xlsx")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)