import flet as ft
from ui.components import (
    COLOR_BG_LAYER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    create_recent_card,
)
import asyncio
from pathlib import Path
from settings_store import add_recent, get_recents
from ui.preview import make_preview

def create_home_screen(layout_manager) -> ft.Column:
    picker_holder = {"obj": None}

    async def pick_dng(e):
        page = e.control.page
        if picker_holder["obj"] is None:
            picker_holder["obj"] = ft.FilePicker()
            page.services.append(picker_holder["obj"])

        files = await picker_holder["obj"].pick_files(
            dialog_title="Select DNG file",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["dng"],
            allow_multiple=False,
        )

        if files:
            path = files[0].path
            layout_manager.selected_file = path
            layout_manager.exported_preview = None
            layout_manager.last_export = None
            try:
                layout_manager.preview_path = await asyncio.to_thread(make_preview, path)
            except Exception as ex:
                print("Preview error: ", ex)
                layout_manager.preview_path = None
            add_recent(layout_manager.settings, path)
            layout_manager.navigate_to("export")

    def open_file(path):
        layout_manager.selected_file = path
        layout_manager.preview_path = None
        layout_manager.exported_preview = None
        layout_manager.last_export = None     
        layout_manager.navigate_to("export")

    upload_zone = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.UPLOAD_OUTLINED, size=56, color=COLOR_TEXT_PRIMARY),
                ft.Text("Upload", size=32, weight=ft.FontWeight.W_500, color=COLOR_TEXT_PRIMARY),
                ft.Text("Select a DNG file here", color=COLOR_TEXT_SECONDARY, size=16),
                ft.TextButton("Click to Browse", style=ft.ButtonStyle(color=COLOR_ACCENT), on_click=pick_dng),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        expand=True,
        border=ft.Border.all(1.5, ft.Colors.with_opacity(0.4, COLOR_TEXT_SECONDARY)),
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        bgcolor=COLOR_BG_LAYER,
        ink=True,
        on_click=pick_dng,
    )

    recent_cards = []
    for r in get_recents(layout_manager.settings):
        try:
            thumb = Path(make_preview(r["path"])).read_bytes()
        except Exception:
            continue
        recent_cards.append(
            create_recent_card(
                title=Path(r["path"]).name,
                subtitle=r["opened"],
                image_src=thumb,
                on_click=lambda _, p=r["path"]: open_file(p)
            )
        )

    if not recent_cards:
        recent_cards = [ft.Text("No recent files yet", size=14, color=COLOR_TEXT_SECONDARY)]


    recent_section = ft.Column(
        [
            ft.Text("Recents", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
            ft.Row(recent_cards, spacing=15, scroll=ft.ScrollMode.AUTO),
        ],
        spacing=15,
    )
    return ft.Column(
        [
            ft.Text("Open a photo", size=28, weight=ft.FontWeight.W_500, color=COLOR_ACCENT),
            upload_zone,
            recent_section,
        ],
        spacing=20,
        expand=True
    )