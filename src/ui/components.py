import flet as ft

#ZAKLADNI COLOUR PALETTE ZVOLENA PRO PROJEKT
COLOR_BG_MICA = "#202020"
COLOR_BG_LAYER = "#272727"
COLOR_BG_CARD = "#2d2d2d"
COLOR_BORDER = "#383838"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY = "#c5c5c5"
COLOR_ACCENT = "#a78bfa"
COLOR_SUCCESS = "#6ccb5f"


def create_recent_card(title: str, subtitle: str="", image_src: str=None, on_click=None) -> ft.Container:
    #Karta pro recents na homescreenu
    content_items = []

    if image_src:
        content_items.append(
            ft.Container(
                content=ft.Image(src=image_src, width=150, height=120, fit="cover"),
                border_radius=5,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        )
    content_items.append(
        ft.Text(title, size=13, weight=ft.FontWeight.W_500, color=COLOR_TEXT_PRIMARY, no_wrap=True)
    )

    if subtitle:
        content_items.append(
            ft.Text(subtitle, size=11, color=COLOR_TEXT_SECONDARY)
        )

    return ft.Container(
        content=ft.Column(content_items, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
        padding=10,
        bgcolor=COLOR_BG_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=8,
        on_click=on_click,
        animate=200,
    )

def create_nav_item(icon, tooltip, on_click):
    indicator = ft.Container(width=3, height=20, border_radius=2)
    button = ft.IconButton(icon=icon, icon_color=COLOR_TEXT_PRIMARY,
                           tooltip=tooltip, on_click=on_click)
    return ft.Row([indicator, button], spacing=0), indicator

def create_accent_button(text: str, icon=None, on_click=None) -> ft.FilledButton:
    #tlacitko
    return ft.FilledButton(
        content=text,
        icon=icon,
        style=ft.ButtonStyle(
            color=COLOR_TEXT_PRIMARY,
            bgcolor=COLOR_ACCENT,
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=12,
        ),
        on_click=on_click,
    )