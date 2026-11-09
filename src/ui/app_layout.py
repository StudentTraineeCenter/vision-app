import flet as ft
from ui.components import (
    COLOR_BG_MICA,
    COLOR_BG_LAYER,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BG_CARD,
    COLOR_ACCENT,
    create_nav_item
)
from settings_store import load_settings


class AppLayout:
    def __init__(self, page: ft.Page):
        self.page = page
        self.settings = load_settings()
        self.page.title = "Vision"
        self.page.bgcolor = COLOR_BG_MICA
        self.page.padding = 0
        self.page.window.width = 1100
        self.page.window.height = 720
        self.page.window.min_width = 900
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(color_scheme_seed=COLOR_ACCENT, font_family="Segoe UI")

        self.selected_file = None
        self.preview_path = None
        self.exported_file = None
        self.exported_preview = None
        self.last_export = None

        self.last_export = {"format": "JPEG", "size_bytes": 2_700_000, "time_s": 6.7, "path": ""}

        #main container
        self.content_area = ft.Container(expand=True, padding=20, bgcolor=ft.Colors.TRANSPARENT)
        self.active_screen = "home"

        self.nav_items = {}
        self.indicators = {}
        for key, icon, tooltip in [
            ("home", ft.Icons.HOME_ROUNDED, "Home"),
            ("export", ft.Icons.FOLDER_OPEN_ROUNDED, "Export & Settings"),
            ("compare", ft.Icons.BALANCE, "Comparison")
        ]:
            row, indicator = create_nav_item(icon, tooltip, lambda _, k=key: self.navigate_to(k))
            self.nav_items[key] = row
            self.indicators[key] = indicator

    #menu na levé straně
    def build_sidebar(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Column(
                        [
                            ft.IconButton(ft.Icons.MENU, icon_color=COLOR_TEXT_SECONDARY),
                            self.nav_items["home"],
                            self.nav_items["export"],
                            self.nav_items["compare"],
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.IconButton(ft.Icons.INFO_OUTLINE, icon_color=COLOR_TEXT_SECONDARY, tooltip="Nápověda", on_click=lambda _: self.navigate_to("info")),
                            ft.IconButton(ft.Icons.SETTINGS_OUTLINED, icon_color=COLOR_TEXT_SECONDARY, tooltip="Nastavení", on_click=lambda _: self.navigate_to("settings")),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=56,
            padding=4,
            bgcolor=COLOR_BG_LAYER,
        )

    #zvyrazneni prave aktivni (selectnute) karty v menu
    def update_active_state_sidebar(self):
        for key, indicator in self.indicators.items():
            indicator.bgcolor = COLOR_ACCENT if key == self.active_screen else None

    def navigate_to(self, screen_name: str):
        self.active_screen = screen_name
        self.update_active_state_sidebar()

        if screen_name == "home":
            from ui.home_screen import create_home_screen
            self.content_area.content = create_home_screen(self)
        elif screen_name == "export":
            from ui.export_screen import create_export_screen
            self.content_area.content = create_export_screen(self)
        elif screen_name == "compare":
            from ui.compare_screen import create_compare_screen
            self.content_area.content = create_compare_screen(self)
        elif screen_name == "info":
            from ui.info_section import create_info_screen
            self.content_area.content = create_info_screen()
        elif screen_name == "settings":
            from ui.settings_screen import create_settings_screen
            self.content_area.content = create_settings_screen()

        self.page.update()

    def render(self):
        self.update_active_state_sidebar()
        self.navigate_to("home")

        main_row = ft.Row([
            self.build_sidebar(),
            ft.VerticalDivider(width=1, color=COLOR_BORDER),
            self.content_area,
        ], 
            expand=True,
            spacing=0,
        )

        root_container = ft.Container(
            gradient=ft.RadialGradient(
                center=ft.Alignment.TOP_LEFT,
                radius=1.1,
                colors=["#363143", COLOR_BG_MICA],
                stops=[0.0, 0.7],
            ),
            content=main_row,
            expand=True,
        )

        self.page.add(root_container)