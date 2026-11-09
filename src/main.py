import flet as ft
from ui.app_layout import AppLayout

def main(page: ft.Page):
    page.title = "Vision"
    app = AppLayout(page)
    app.render()

ft.run(main)