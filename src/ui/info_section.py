import flet as ft
from .components import (
    COLOR_BG_LAYER,
    COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_BORDER
)

def create_info_screen(layout_manager=None) -> ft.Container:
    
    def create_step_card(number: str, title: str, description: str):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(number, color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_ACCENT,
                    width=36,
                    height=36,
                    border_radius=18,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text(title, color=COLOR_TEXT_PRIMARY, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(description, color=COLOR_TEXT_SECONDARY, size=12),
                ], spacing=2, expand=True)
            ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COLOR_BG_CARD,
            padding=15,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
            expand=True,
            height=95,
        )

    def create_setting_item(name: str, desc: str):
        return ft.Row([
            ft.Container(
                content=ft.Text(name, color=COLOR_ACCENT, size=12, weight=ft.FontWeight.BOLD),
                width=140,
            ),
            ft.Text(desc, color=COLOR_TEXT_SECONDARY, size=12, expand=True),
        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=10)

    header = ft.Column([
        ft.Text("Help and Settings Overview", size=26, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT),
        ft.Text("A guide to controlling the Vision project and a detailed description of individual parameters.", size=13, color=COLOR_TEXT_SECONDARY),
    ], spacing=4)

    step_1 = create_step_card(
        "1", "File Import", "Upload your RAW format into the application via the Import tab."
    )
    step_2 = create_step_card(
        "2", "Processing & Editing", "Apply filters or wait for export."
    )
    step_3 = create_step_card(
        "3", "Comparison", "On the Comparing screen, drag the centre slider to check format differences."
    )

    steps_row = ft.Row([step_1, step_2, step_3], 
                       spacing=15)

    settings_glossary_card = ft.Container(
        content=ft.Column([
            ft.Text("Parameters & Settings Glossary", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
            ft.Text("Detailed overview of values displayed in information cards and interface:", size=12, color=COLOR_TEXT_SECONDARY),
            ft.Divider(color=COLOR_BORDER, height=15),
            
            create_setting_item("File Format", "Determines the file format. .dng serves as the raw input format, while JPEG/PNG/TIFF represents the final compressed output."),
            ft.Divider(color=COLOR_BORDER, height=10),

            create_setting_item("Quality", "Controls the balance between image clarity and file size."),
            ft.Divider(color=COLOR_BORDER, height=10),

            create_setting_item("Subsampling", "Reduces colour data to save space with minimal visual loss."),
            ft.Divider(color=COLOR_BORDER, height=10),

            create_setting_item("Optimise", "Computes optimal Huffman tables for a smaller file size."),
            ft.Divider(color=COLOR_BORDER, height=10),

            create_setting_item("Compression Level", "Higher levels reduce file size but increase processing time."),
            ft.Divider(color=COLOR_BORDER, height=10),

            create_setting_item("Max Colours", "Limits the colour palette to drastically reduce file size."),
            ft.Divider(color=COLOR_BORDER, height=10),

            create_setting_item("Colour Mode", "Selects the colour representation format (e.g., RGB, Greyscale)."),
            ft.Divider(color=COLOR_BORDER, height=10),
            
            create_setting_item("Export Time", "Image processing time measured in milliseconds (ms). Shows efficiency and lightning-fast rendering speed.")
            
        ], spacing=10),
        bgcolor=COLOR_BG_CARD,
        padding=20,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    content_column = ft.Column(
        [
            header,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=5),
            steps_row,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=5),
            settings_glossary_card,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=5),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    return ft.Container(
        content=content_column,
        padding=20,
        expand=True,
    )