import flet as ft
from ui.app_layout import AppLayout

def main(page: ft.Page):
    app = AppLayout(page)
    app.render()

ft.run(main)