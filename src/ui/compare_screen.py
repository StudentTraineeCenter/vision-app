import flet as ft
from pathlib import Path
from datetime import date
from PIL import Image as PILImage

from .components import (
    COLOR_BG_LAYER,
    COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_SUCCESS
)

from .exif_data import read_exif

def create_compare_screen(layout_manager) -> ft.Container:

    def read_bytes(path):
        try:
            with open(path, "rb") as f:
                return f.read()
        except (OSError, TypeError):
            return None

    aspect = 1.5
    if layout_manager.preview_path:
        try:
            with PILImage.open(layout_manager.preview_path) as im:
                aspect = im.width / im.height
        except OSError:
            pass

    before_bytes = read_bytes(layout_manager.preview_path)

    if before_bytes is None:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.IMAGE_OUTLINED, size=56, color=COLOR_TEXT_SECONDARY),
                    ft.Text("Nothing to compare yet", size=20, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                    ft.Text("Load a DNG file and export it first.", size=14, color=COLOR_TEXT_SECONDARY),
                    ft.Container(
                        content=ft.Text("Go to Home", size=14, weight=ft.FontWeight.W_600, color="#111111"),
                        bgcolor=COLOR_ACCENT,
                        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
                        border_radius=8,
                        ink=True,
                        on_click=lambda _: layout_manager.navigate_to("home"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            expand=True,
            alignment=ft.Alignment.CENTER,
        )
    before_src = before_bytes
    after_src = read_bytes(getattr(layout_manager, "exported_preview", None)) or before_bytes

    state = {
        "w": 600.0,
        "h": 400.0,
        "split": 0.26,
    }


    LINE_WIDTH = 2
    HANDLE_SIZE = 36

    after_img = ft.Image(
        src=after_src,
        width=600,
        height=400,
        fit=ft.BoxFit.CONTAIN,
        left=0,
        top=0,
    )

    before_img = ft.Image(
        src=before_src,
        width=600,
        height=400,
        fit=ft.BoxFit.CONTAIN,
        left=0,
        top=0,
    )

    orig_name, orig_size, orig_date = "-", "-", "-"
    if layout_manager.selected_file:
        p = Path(layout_manager.selected_file)
        st = p.stat()
        orig_name = p.suffix.lstrip(".").upper() or "-"
        orig_size = f"{st.st_size / 1024 / 1024:.1f} MB"
        exif_info = read_exif(layout_manager.selected_file)
        orig_date = exif_info.get("Date", "-")

    def fmt_size(b):
        return f"{b / 1024 / 1024:.1f} MB" if b >= 1024 * 1024 else f"{b / 1024:.0f} KB"

    def fmt_time(s):
        if s < 1:
            return f"{s * 1000:.0f} ms"
        if s < 60:
            return f"{s:.1f} s"
        m, sec = divmod(round(s), 60)
        return f"{m} min {sec} s"

    orig_bytes = Path(layout_manager.selected_file).stat().st_size if layout_manager.selected_file else None
    info = layout_manager.last_export

    if info and orig_bytes:
        new_bytes = info["size_bytes"]
        change = (new_bytes / orig_bytes - 1) * 100
        smaller = change <= 0
        saving_title = "Smaller than original" if smaller else "Larger than original"
        saving_value = f"{'−' if smaller else '+'}{abs(change):.1f} %"
        saving_color = COLOR_ACCENT if smaller else "#ff9a6b"
        saving_detail = f"{fmt_size(orig_bytes)} → {fmt_size(new_bytes)}"
        exp_format, exp_size = info["format"], fmt_size(new_bytes)
        exp_time = fmt_time(info["time_s"])
    else:
        saving_title, saving_value, saving_color = "Size change", "—", COLOR_TEXT_SECONDARY
        saving_detail = "Export a file first"
        exp_format = exp_size = exp_time = "-"

    before_viewport = ft.Stack(
        controls=[before_img],
        width=600,
        height=400,
        left=0,
        top=0,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    divider = ft.Container(
        width=2,
        height=400,
        bgcolor=ft.Colors.WHITE,
        left=0,
        top=0,
        shadow=ft.BoxShadow(
            blur_radius=6,
            color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
        ),
    )

    handle = ft.Container(
        width=HANDLE_SIZE,
        height=HANDLE_SIZE,
        border_radius=HANDLE_SIZE / 2,
        bgcolor=ft.Colors.WHITE,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.UNFOLD_MORE, size=20, color="#111111", rotate=1.5708),
        left=0,
        top=0,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.45, ft.Colors.BLACK),
        ),
    )

    def make_badge(text, **pos):
        return ft.Container(
            content=ft.Text(text, color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.W_600),
            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
            border_radius=6,
            **pos,
        )

    before_badge = make_badge("Original", left=12, top=12)
    after_badge = make_badge("Exported", right=12, top=12)

    before_badge = ft.Container(
        content=ft.Text(
            "Before (Imported file)",
            color=ft.Colors.WHITE,
            size=9,
            weight=ft.FontWeight.W_500,
        ),
        bgcolor=ft.Colors.with_opacity(0.72, ft.Colors.BLACK),
        padding=5,
        border_radius=3,
        left=5,
        top=5,
    )

    after_badge = ft.Container(
        content=ft.Text(
            "After (Exported file)",
            color=ft.Colors.WHITE,
            size=9,
            weight=ft.FontWeight.W_500,
        ),
        bgcolor=ft.Colors.with_opacity(0.72, ft.Colors.BLACK),
        padding=5,
        border_radius=3,
        right=5,
        top=5,
    )

    slider_stack = ft.Stack(
        controls=[
            after_img,
            before_viewport,
            divider,
            handle,
            before_badge,
            after_badge,
        ],
        expand=True,
        alignment=ft.Alignment.TOP_LEFT,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )


    def update_slider(send_update=True):

        w = state["w"]
        h = state["h"]

        if w <= 0 or h <= 0:
            return
        
        x = state["split"] * w

        after_img.width = w
        after_img.height = h

        before_img.width = w
        before_img.height = h

        before_viewport.width = x
        before_viewport.height = h

        divider.left = x - 1
        divider.height = h


        handle.left = max(
            0, min(x - HANDLE_SIZE / 2, w - HANDLE_SIZE)
        )

        handle.top = (h - HANDLE_SIZE) / 2

        if send_update:
            slider_stack.update()


    def set_position(x):

        w = state["w"]

        if w <= 0:
            return

        x = max(0.0, min(x, w))

        state["split"] = x / w

        update_slider()


    def on_drag(e):
        delta = e.primary_delta

        if delta is None and e.local_delta is not None:
            delta = e.local_delta.x

        if delta is None:
            return

        current_x = state["split"] * state["w"]

        set_position(current_x + delta)

    def on_tap(e):

        set_position(e.local_position.x)

    gesture = ft.GestureDetector(
        content=slider_stack,
        expand=True,
        on_horizontal_drag_update=on_drag,
        on_tap_down=on_tap,
        drag_interval=0,
        mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
    )

    slider_frame = ft.Container(
        content=gesture,
        width=600,
        height=400,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=8,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        bgcolor=COLOR_BG_LAYER,
    )

    def on_preview_resize(e):
        if not e.width or not e.height:
            return
        target_w = min(e.width * 0.95, e.height * 0.95 * aspect)
        target_h = target_w / aspect

        if target_w <= 0 or target_h <= 0:
            return

        if (
            abs(target_w - state["w"]) < 1
            and abs(target_h - state["h"]) < 1
            ):
                return
        state["w"] = target_w
        state["h"] = target_h

        slider_frame.width = target_w
        slider_frame.height = target_h

        update_slider(send_update=False)

        slider_frame.update()
        slider_stack.update()

    preview = ft.Container(
        content=slider_frame,
        expand=True,
        alignment=ft.Alignment.CENTER,
        on_size_change=on_preview_resize,
    )

    update_slider(send_update=False)

    def info_row(label, value):
        return ft.Row(
            [
                ft.Text(label, size=14, color=COLOR_TEXT_SECONDARY),
                ft.Text(value, size=14, color=COLOR_TEXT_PRIMARY, weight=ft.FontWeight.W_500),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    def info_card(title, rows):
        return ft.Container(
            content=ft.Column(
                [ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY)]
                + [info_row(k, v) for k, v in rows],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            bgcolor=COLOR_BG_CARD,
            padding=14,
            border_radius=8,
            border=ft.Border.all(1, COLOR_BORDER),
            expand=3
        )


    card_saving = ft.Container(
        content=ft.Column(
            [
                ft.Text(saving_title, color=COLOR_TEXT_SECONDARY, size=15),
                ft.Text(saving_value, color=saving_color, size=50, weight=ft.FontWeight.BOLD),
                ft.Text(saving_detail, color=COLOR_TEXT_SECONDARY, size=15),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLOR_BG_CARD,
        padding=ft.Padding.symmetric(vertical=20, horizontal=14),
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER),
        alignment=ft.Alignment.CENTER,
        expand=4,
    )

    card_original = info_card("Original file", [("Format", f".{orig_name}"), ("Size", orig_size), ("Date", orig_date)])
    card_exported = info_card("Exported file", [("Format", exp_format), ("Size", exp_size), ("Export time", exp_time)])


    def snap(value):
        state["split"] = value
        update_slider()

    def seg_btn(label, value):
        return ft.Container(
            content=ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=COLOR_TEXT_PRIMARY),
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(vertical=10),
            border_radius=6,
            ink=True,
            on_click=lambda _: snap(value)
        )

    view_switch = ft.Container(
        content=ft.Row(
            [seg_btn("Original", 1.0), seg_btn("Split", 0.5), seg_btn("Exported", 0.0)],
            spacing=2,
        ),
        bgcolor="#1f1f1f",
        padding=2,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    side_panel = ft.Container(
        content=ft.Column(
            [view_switch, card_saving, card_original, card_exported],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        width=320,
        bgcolor=COLOR_BG_LAYER,
        padding=15,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    preview_area = ft.Container(
        content=preview,
        expand=True,
        bgcolor="#1b1b1b",
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        
    )

    file_name = Path(layout_manager.selected_file).name if layout_manager.selected_file else "No file loaded"

    header = ft.Column(
        [
            ft.Text("Compare", size=28, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
            ft.Text(file_name, size=13, color=COLOR_TEXT_SECONDARY),
        ],
        spacing=2,
    )

    content_row = ft.Row(
        [preview_area, side_panel],
        expand=True,
        spacing=15,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return ft.Container(
        content=ft.Column([header, content_row], spacing=15, expand=True),
        padding=15,
        expand=True,
    )
