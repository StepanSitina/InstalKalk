import os
from kivy.utils import platform

# Nastavení správné cesty pro SQLite databázi na Androidu
if platform == "android":
    from android.storage import app_storage_path
    DB_DIR = app_storage_path()
else:
    DB_DIR = os.path.dirname(os.path.abspath(__file__))

import database
database.DB_PATH = os.path.join(DB_DIR, "instalkalk.db")
# Inicializace databáze
database.init_db()

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import TwoLineListItem, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

import scraper

KV = '''
ScreenManager:
    ProjectListScreen:
    ProjectDetailScreen:
    SearchScreen:

<ProjectListScreen>:
    name: 'projects'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Instalkalk - Projekty"
            elevation: 4
            md_bg_color: app.theme_cls.primary_color
        ScrollView:
            MDList:
                id: project_list
    MDFloatingActionButton:
        icon: "plus"
        pos_hint: {"center_x": .85, "center_y": .1}
        on_release: app.show_new_project_dialog()

<ProjectDetailScreen>:
    name: 'project_detail'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: app.current_project_name
            left_action_items: [["arrow-left", lambda x: app.go_to_projects()]]
            elevation: 4
        MDLabel:
            id: total_label
            text: "Celkem s DPH: 0.00 Kč"
            halign: "center"
            size_hint_y: None
            height: "48dp"
            bold: True
            theme_text_color: "Custom"
            text_color: 0, 0.5, 0, 1
        ScrollView:
            MDList:
                id: item_list
    MDFloatingActionButton:
        icon: "magnify"
        pos_hint: {"center_x": .85, "center_y": .1}
        on_release: app.go_to_search()

<SearchScreen>:
    name: 'search'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Hledat materiál"
            left_action_items: [["arrow-left", lambda x: app.go_to_project_detail()]]
            elevation: 4
        BoxLayout:
            size_hint_y: None
            height: "60dp"
            padding: "10dp"
            spacing: "10dp"
            MDTextField:
                id: search_input
                hint_text: "Např.: Koleno 110° PVC"
                on_text_validate: app.perform_search()
            MDRaisedButton:
                text: "Hledat"
                on_release: app.perform_search()
        ScrollView:
            MDList:
                id: search_results
'''

class ProjectListScreen(Screen):
    pass

class ProjectDetailScreen(Screen):
    pass

class SearchScreen(Screen):
    pass

class InstalkalkApp(MDApp):
    current_project_id = None
    current_project_name = "Kalkulace"
    dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.sm = Builder.load_string(KV)
        return self.sm

    def on_start(self):
        self.load_projects()

    def go_to_projects(self):
        self.sm.current = 'projects'
        self.load_projects()

    def go_to_project_detail(self):
        self.sm.current = 'project_detail'
        self.load_items()

    def go_to_search(self):
        self.sm.current = 'search'

    def load_projects(self):
        list_obj = self.sm.get_screen('projects').ids.project_list
        list_obj.clear_widgets()
        conn = database.get_db()
        projects = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        for proj in projects:
            item = TwoLineListItem(
                text=proj['name'],
                secondary_text=proj['created_at'].split()[0], # Jen datum
                on_release=lambda x, p_id=proj['id'], p_name=proj['name']: self.open_project(p_id, p_name)
            )
            list_obj.add_widget(item)

    def open_project(self, p_id, p_name):
        self.current_project_id = p_id
        self.current_project_name = p_name
        self.go_to_project_detail()

    def show_new_project_dialog(self):
        if not self.dialog:
            self.project_name_input = MDTextField(hint_text="Název projektu")
            self.dialog = MDDialog(
                title="Nový projekt",
                type="custom",
                content_cls=self.project_name_input,
                buttons=[
                    MDFlatButton(text="Zrušit", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="Vytvořit", on_release=lambda x: self.create_project())
                ],
            )
        self.project_name_input.text = ""
        self.dialog.open()

    def create_project(self):
        name = self.project_name_input.text
        if name:
            conn = database.get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            conn.commit()
            self.dialog.dismiss()
            self.load_projects()

    def load_items(self):
        list_obj = self.sm.get_screen('project_detail').ids.item_list
        list_obj.clear_widgets()
        conn = database.get_db()
        items = conn.execute("SELECT * FROM items WHERE project_id = ?", (self.current_project_id,)).fetchall()
        
        total_bez_dph = 0
        for item in items:
            total = item['price'] * item['quantity']
            total_bez_dph += total
            list_item = TwoLineListItem(
                text=f"{item['quantity']}x {item['name']}",
                secondary_text=f"{item['price']:.2f} Kč/ks | Celkem: {total:.2f} Kč | Obchod: {item['shop']}"
            )
            list_obj.add_widget(list_item)
            
        total_s_dph = total_bez_dph * 1.21
        self.sm.get_screen('project_detail').ids.total_label.text = f"Celkem s DPH: {total_s_dph:.2f} Kč"

    def perform_search(self):
        query = self.sm.get_screen('search').ids.search_input.text
        if not query: return
        results = scraper.search_products(query)
        
        list_obj = self.sm.get_screen('search').ids.search_results
        list_obj.clear_widgets()
        
        for res in results:
            item = TwoLineListItem(
                text=res['name'],
                secondary_text=f"{res['price']} Kč - {res['shop']}",
                on_release=lambda x, p=res: self.add_found_item(p)
            )
            list_obj.add_widget(item)

    def add_found_item(self, product):
        # Pro zjednodušení na mobilu automaticky přidáme 1 ks
        # V ostré verzi by zde byl dialog pro výběr počtu kusů
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO items (project_id, name, quantity, price, shop, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.current_project_id, product['name'], 1.0, product['price'], product['shop'], product['url']))
        conn.commit()
        
        # Vrátíme se do detailu
        self.go_to_project_detail()

if __name__ == '__main__':
    InstalkalkApp().run()