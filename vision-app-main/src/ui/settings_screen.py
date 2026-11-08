import flet as ft
from .components import (
    COLOR_BG_LAYER,
    COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_BORDER,
)
from core.settings import load_settings, save_settings

def create_settings_screen(layout_manager=None) -> ft.Container:
    current_settings = load_settings()

    def create_settings_card(title: str, description: str, control: ft.Control):
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(title, color=COLOR_TEXT_PRIMARY, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(description, color=COLOR_TEXT_SECONDARY, size=12),
                ], spacing=2, expand=True),
                control
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COLOR_BG_CARD,
            padding=15,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    header = ft.Column([
        ft.Text("Application Settings", size=26, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT),
        ft.Text("Customise your appearance and preferences", size=13, color=COLOR_TEXT_SECONDARY),
    ], spacing=4)

    def on_switch_change(e):
        current_settings["auto_recents"] = e.control.value
        save_settings(current_settings)

    switch_auto_recents = ft.Switch(
        value=current_settings.get("auto_recents", True),
        active_color=COLOR_ACCENT,
        on_change=on_switch_change
    )

    def on_dropdown_change(e):
        current_settings["default_format"] = e.control.value
        save_settings(current_settings)

    dropdown_format = ft.Dropdown(
        width=140,
        value=current_settings.get("default_format", "JPEG"),
        options=[
            ft.dropdown.Option("JPEG"),
            ft.dropdown.Option("PNG"),
            ft.dropdown.Option("TIFF"),
        ],
        border_color=COLOR_BORDER,
        color=COLOR_TEXT_PRIMARY,
        bgcolor=COLOR_BG_LAYER,
        text_size=12,
        content_padding=10,
        on_select=on_dropdown_change,
    )

    settings_recents = create_settings_card(
        "Automatic Recent Files History",
        "Every opened file is automatically saved to the list of recent files.",
        switch_auto_recents,
    )

    settings_format = create_settings_card(
        "Default Export Format",
        "Pre-selected format for quick handling and configuration.",
        dropdown_format,
    )

    return ft.Container(
        content=ft.Column([
            header,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Column([
                settings_recents,
                settings_format,
            ], spacing=10)
        ], spacing=15),
        expand=True,
        padding=10,
        bgcolor=ft.Colors.TRANSPARENT
    )