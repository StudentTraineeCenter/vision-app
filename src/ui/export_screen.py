import flet as ft
from .components import (
    COLOR_BG_LAYER,
    COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_BORDER
)
from .preview import make_preview
from .histogram import make_histogram
from .exif_data import read_exif
import asyncio
from pathlib import Path

def create_export_screen(layout_manager) -> ft.Column:
    def safe_update(control):
        try:
            control.update()
        except RuntimeError:
            pass
    #hodnoty slovniku pro nasledny vyber nastaveni
    current_format = {"value": "JPEG"}

    quality_value = {"value": 85}
    subsampling_value = {"value": "4:4:4"}
    jpeg_optimize = {"value": True}
    jpeg_progressive = {"value": False}

    compress_level_value = {"value": 6}
    png_colors = {"value": "256"}
    png_color_mode = {"value": "RGB"}
    png_optimize = {"value": True}
    shown_level = 9 if png_optimize["value"] else compress_level_value["value"]

    tiff_compression = {"value": "LZW"}

    #nastaveni file folders
    export_dir = {"value":None}
    picker_holder = {"obj": None}

    destination_text = ft.Text(
        "Not Selected",
        color=COLOR_TEXT_SECONDARY,
        size=11,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
        tooltip="Not Selected"
    )
    

    settings_content_container = ft.Container(expand=True)

    def set_subsampling(value):
        subsampling_value["value"] = value
        update_setting_view(should_update=True)

    def on_png_optimize_change(e):
        png_optimize["value"] = e.control.value
        update_setting_view(should_update=True)

    def collapsible(title, content, expanded=False):
        shape = ft.RoundedRectangleBorder(radius=6)
        return ft.Container(
            content=ft.ExpansionTile(
                title=ft.Text(title, size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                controls=[
                    ft.Container(
                        content=content,
                        padding=ft.Padding.only(left=10, right=10, bottom=10),
                    )
                ],
                expanded=expanded,
                bgcolor=COLOR_BG_CARD,
                collapsed_bgcolor=COLOR_BG_CARD,
                icon_color=COLOR_TEXT_SECONDARY,
                collapsed_icon_color=COLOR_TEXT_SECONDARY,
                shape=shape,
                collapsed_shape=shape,
                tile_padding=ft.Padding.symmetric(horizontal=10),
                dense=True,
            ),
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=6,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    def update_setting_view(should_update=False):
        fmt = current_format["value"]

        jpeg_btn.bgcolor = COLOR_ACCENT if fmt == "JPEG" else COLOR_BG_CARD
        jpeg_btn.content.color = "#111111" if fmt == "JPEG" else COLOR_TEXT_SECONDARY

        png_btn.bgcolor = COLOR_ACCENT if fmt == "PNG" else COLOR_BG_CARD
        png_btn.content.color = "#111111" if fmt == "PNG" else COLOR_TEXT_SECONDARY
        
        tiff_btn.bgcolor = COLOR_ACCENT if fmt == "TIFF" else COLOR_BG_CARD
        tiff_btn.content.color = "#111111" if fmt == "TIFF" else COLOR_TEXT_SECONDARY

        if fmt == "JPEG":

            quality_text = ft.Text(
                str(quality_value["value"]),
                color=COLOR_TEXT_PRIMARY,
                size=12,
                weight=ft.FontWeight.BOLD,
            )

            def on_quality_change(e):
                quality_value["value"] = round(e.control.value)
                quality_text.value = str(quality_value["value"])
                quality_text.update()

            quality_slider = ft.Slider(
                min=0,
                max=95,
                value=min(quality_value["value"], 95),
                divisions=94,
                active_color=COLOR_ACCENT,
                on_change=on_quality_change,
                tooltip="Controls the balance between image clarity and file size"
            )

            quality_control = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Quality",
                                color=COLOR_TEXT_SECONDARY,
                                size=12,
                            ),
                            quality_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    quality_slider,
                ],
                spacing=2,
            )

            subsampling_control = ft.Column(
        [
            ft.Text(
                "Subsampling",
                color=COLOR_TEXT_SECONDARY,
                size=12,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            "4:4:4",
                            color=(
                                ft.Colors.WHITE if subsampling_value["value"] == "4:4:4" else COLOR_TEXT_SECONDARY
                            ),
                            size=11,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=(
                            COLOR_ACCENT
                            if subsampling_value["value"] == "4:4:4"
                            else COLOR_BG_CARD
                        ),
                        padding=8,
                        border_radius=4,
                        on_click=lambda e: set_subsampling("4:4:4"),
                        ink=True,
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        tooltip="Full color detail, largest file"
                    ),
                    ft.Container(
                        content=ft.Text(
                            "4:2:2",
                            color=(
                                ft.Colors.WHITE
                                if subsampling_value["value"] == "4:2:2"
                                else COLOR_TEXT_SECONDARY
                            ),
                            size=11,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=(
                            COLOR_ACCENT
                            if subsampling_value["value"] == "4:2:2"
                            else COLOR_BG_CARD
                        ),
                        padding=8,
                        border_radius=4,
                        on_click=lambda e: set_subsampling("4:2:2"),
                        ink=True,
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        tooltip="Half horizontal color resolution"
                    ),
                    ft.Container(
                        content=ft.Text(
                            "4:2:0",
                            color=(
                                ft.Colors.WHITE
                                if subsampling_value["value"] == "4:2:0"
                                else COLOR_TEXT_SECONDARY
                            ),
                            size=11,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=(
                            COLOR_ACCENT
                            if subsampling_value["value"] == "4:2:0"
                            else COLOR_BG_CARD
                        ),
                        padding=8,
                        border_radius=4,
                        on_click= lambda e: set_subsampling("4:2:0"),
                        ink=True,
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        tooltip="Smallest file, slight color loss"
                    ),
                ],
                spacing=5,
                expand=True,
            ),
        ],
        spacing=5,
    )

            quality_card = ft.Container(
                content=quality_control,
                bgcolor=COLOR_BG_CARD,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
            )

            subsampling_card = ft.Container(
                content=subsampling_control,
                bgcolor=COLOR_BG_CARD,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
            )

            optimize_control = ft.Row(
                [
                    ft.Text("Optimize", color=COLOR_TEXT_PRIMARY, size=12),
                    ft.Switch(
                        value=jpeg_optimize["value"],
                        active_color=COLOR_ACCENT,
                        on_change=lambda e: jpeg_optimize.update(
                            value=e.control.value
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            progressive_control = ft.Row(
                [
                    ft.Text("Progressive", color=COLOR_TEXT_PRIMARY, size=12),
                    ft.Switch(
                        value=jpeg_progressive["value"],
                        active_color=COLOR_ACCENT,
                        on_change=lambda e: jpeg_progressive.update(
                            value=e.control.value
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            optimize_card = ft.Container(
                content=optimize_control,
                bgcolor=COLOR_BG_CARD,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )
            progressive_card = ft.Container(
                content=progressive_control,
                bgcolor=COLOR_BG_CARD,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
            )

            controls = [
                quality_card,
                subsampling_card,
                optimize_card,
                progressive_card,
            ]

        elif fmt == "PNG":
            compress_level_text = ft.Text(
                str(shown_level),
                color=COLOR_TEXT_PRIMARY,
                size=12,
                weight=ft.FontWeight.BOLD,
            )
            def on_compress_level_change(e):
                compress_level_value["value"] = round(e.control.value)
                compress_level_text.value = str(compress_level_value["value"])
                compress_level_text.update()

            compress_level_slider = ft.Slider(
                min=0,
                max=9,
                value=shown_level,
                divisions=9,
                active_color=COLOR_ACCENT,
                disabled=png_optimize["value"],
                on_change=on_compress_level_change,
            )

            compress_level_control = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Compress Level",
                                color=COLOR_TEXT_SECONDARY,
                                size=12,
                            ),
                            compress_level_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    compress_level_slider,
                ],
                spacing=2,
            )

            compress_level_card = ft.Container(
                content=compress_level_control,
                bgcolor=COLOR_BG_CARD,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )

            png_optimize_control = ft.Row(
                [
                    ft.Text("Optimize", color=COLOR_TEXT_PRIMARY, size=12),
                    ft.Switch(
                        value=png_optimize["value"],
                        active_color=COLOR_ACCENT,
                        on_change=on_png_optimize_change,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            png_optimize_card = ft.Container(
                content=png_optimize_control,
                bgcolor=COLOR_BG_CARD,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
            )

            png_colors_control = ft.Column([
                ft.Text("Max Colours", color=COLOR_TEXT_SECONDARY, size=12),
                ft.Dropdown(
                    value=png_colors["value"],
                    options=[
                        ft.dropdown.Option("256"),
                        ft.dropdown.Option("16"),
                        ft.dropdown.Option("TrueColor"),
                    ],
                    bgcolor=COLOR_BG_CARD,
                    color=COLOR_TEXT_PRIMARY,
                    border_color=COLOR_BORDER,
                    width=220,
                    on_select=lambda e: png_colors.update(value=e.control.value)
                ),
            ], spacing=5)

            png_colors_card = ft.Container(
                content=png_colors_control,
                bgcolor=COLOR_BG_CARD,
                width=float("inf"),
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
            )

            png_color_mode_control = ft.Column([
                ft.Text("Colour Mode", color=COLOR_TEXT_SECONDARY, size=12),
                ft.Dropdown(
                    value=png_color_mode["value"],
                    options=[
                        ft.dropdown.Option("RGB"), 
                        ft.dropdown.Option("RGBA"), 
                        ft.dropdown.Option("Palette"),
                        ft.dropdown.Option("Grayscale"),
                    ],
                    bgcolor=COLOR_BG_CARD,
                    color=COLOR_TEXT_PRIMARY,
                    border_color=COLOR_BORDER,
                    width=220,
                    on_select=lambda e: png_color_mode.update(value=e.control.value)
                ),
            ], spacing=5)

            png_color_mode_card = ft.Container(
                content=png_color_mode_control,
                bgcolor=COLOR_BG_CARD,
                width=float('inf'),
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
            )

            controls = [
                compress_level_card,
                png_optimize_card,
                png_colors_card,
                png_color_mode_card,

                
            ]

        else:  # TIFF
            tiff_compression_control = ft.Column([
                ft.Text("TIFF Compression", color=COLOR_TEXT_SECONDARY, size=12),
                ft.Dropdown(
                    value=tiff_compression["value"],
                    options=[
                        ft.dropdown.Option("LZW"),
                        ft.dropdown.Option("Deflate"),
                        ft.dropdown.Option("Packbits"),
                        ft.dropdown.Option("None"),
                    ],
                    bgcolor=COLOR_BG_CARD,
                    color=COLOR_TEXT_PRIMARY,
                    border_color=COLOR_BORDER,
                    width=220,
                    on_select=lambda e: tiff_compression.update(
                        value=e.control.value
                    ),
                ),
            ], spacing=5)

            tiff_compression_card = ft.Container(
                content=tiff_compression_control,
                bgcolor=COLOR_BG_CARD,
                width=260,
                padding=12,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )

            controls = [
                tiff_compression_card
            ]

        settings_content_container.content = ft.Column(controls, spacing=12)
        if should_update:
            settings_content_container.update()
            jpeg_btn.update()
            png_btn.update()
            tiff_btn.update()


    def set_format(fmt):
        current_format["value"] = fmt
        update_setting_view(should_update=True)


    jpeg_btn = ft.Container(
        content=ft.Text("JPEG", size=12, weight=ft.FontWeight.W_500),
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=12,
        border_radius=6,
        on_click=lambda _: set_format("JPEG"),
        ink=True
    )
    png_btn = ft.Container(
        content=ft.Text("PNG", size=12,  weight=ft.FontWeight.W_500),
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=12,
        border_radius=6,
        on_click=lambda _: set_format("PNG"),
        ink=True,
    )
    tiff_btn = ft.Container(
        content=ft.Text("TIFF", size=12,  weight=ft.FontWeight.W_500),
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=12,
        border_radius=6,
        on_click=lambda _: set_format("TIFF"),
        ink=True,
    )

    format_row = ft.Container(
        content=ft.Row([jpeg_btn, png_btn, tiff_btn], spacing=2), 
        bgcolor="1f1f1f",
        padding=2,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    update_setting_view(should_update=False)

    async def choose_destination(e):
        page = e.control.page

        if picker_holder["obj"] is None:
            picker_holder["obj"] = ft.FilePicker()
            page.services.append(picker_holder["obj"])

        path = await picker_holder["obj"].get_directory_path(
            dialog_title="Choose destination"
        )

        if path:
            export_dir["value"] = path
            destination_text.value = path
            destination_text.tooltip = path
            destination_text.update()

    destination_btn = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, size=16, color=COLOR_TEXT_PRIMARY),
                ft.Text("Choose destination", size=12, color=COLOR_TEXT_PRIMARY),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=COLOR_BG_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=6,
        padding=12,
        ink=True,
        on_click=choose_destination,
    )

    destination_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Destination", color=COLOR_TEXT_SECONDARY, size=12),
                destination_btn,
                destination_text,
            ],
            spacing=8,
        ),
        bgcolor=COLOR_BG_CARD,
        padding=12,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER),
    )


    export_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.DOWNLOAD, size=18, color="#111111"),
            ft.Text("Export", color="#111111", weight=ft.FontWeight.W_500, size=14),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=COLOR_ACCENT,
        height=44,
        border_radius=8,
        ink=True,
        on_click=lambda _: print("Export spuštěn!"),  # LOGIKA HERE POTOM!!!
    )

    exif_column = ft.Column([], spacing=3)

    def show_exif(info):
        exif_column.controls = [
            ft.Text(f"{k}: {v}", color=COLOR_TEXT_PRIMARY, size=11) for k, v in info.items()
        ]
        safe_update(exif_column)

    show_exif(read_exif(""))

    exif_box = collapsible("EXIF Data", exif_column)

    histogram_image = ft.Container(height=90)

    histogram_box = collapsible("RGB Histogram", histogram_image)


    right_panel = ft.Container(
        content=ft.Column([
            format_row,
            settings_content_container,
            destination_card,
            export_btn,
            exif_box,
            histogram_box,
        ], spacing=12, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
        width=300,
        bgcolor=COLOR_BG_LAYER,
        padding=15,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    preview_loading = ft.ProgressRing(visible=False, color=COLOR_ACCENT)

    preview_holder = ft.Container(
        expand=True,
        bgcolor="#1b1b1b",
        alignment=ft.Alignment.CENTER,
        content=ft.Text("Load a DNG file first", color=COLOR_TEXT_SECONDARY, size=12)
    )

    def show_image(path):
        with open(path, "rb") as f:
            data = f.read()
        preview_holder.content = ft.Image(src=data, fit=ft.BoxFit.CONTAIN, expand=True)
        preview_holder.alignment = None
        preview_holder.padding = 16
        safe_update(preview_holder)

        histogram_image.content = ft.Image(
            src=make_histogram(path), fit=ft.BoxFit.FILL, height=90,
        )
        safe_update(histogram_image)


    async def load_preview():
        print("LOAD_PREVIEW SPUSTENY")
        if layout_manager.preview_path:
            show_image(layout_manager.preview_path)
            return
        preview_holder.content = preview_loading
        preview_loading.visible = True
        safe_update(preview_holder)

        try:
            path = await asyncio.to_thread(make_preview, layout_manager.selected_file)
            layout_manager.preview_path = path
            show_image(path)
        except Exception as ex:
            preview_holder.content = ft.Text(f"Preview failed: {ex}", color=COLOR_TEXT_SECONDARY, size=12)
            safe_update(preview_holder)

    async def load_exif():
        info = await asyncio.to_thread(read_exif, layout_manager.selected_file)
        show_exif(info)

    preview_area = ft.Container(
        content=preview_holder,
        expand=True,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    if layout_manager.selected_file:
        layout_manager.page.run_task(load_preview)
        layout_manager.page.run_task(load_exif)


    content_row = ft.Row([
        preview_area, right_panel], 
        expand=True, 
        spacing=15,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    file_name = Path(layout_manager.selected_file).name if layout_manager.selected_file else "No file loaded"

    header = ft.Column(
        [
            ft.Text("Export", size=24, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
            ft.Text(file_name, size=12, color=COLOR_TEXT_SECONDARY),
        ],
        spacing=2,
    )
    return ft.Column([header, content_row], spacing=15, expand=True)