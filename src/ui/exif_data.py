import exifread


def _num(tag):
    """Hodnota značky jako číslo (umí zlomky typu 1/250)."""
    v = tag.values[0] if getattr(tag, "values", None) else None
    if v is None:
        return None
    if hasattr(v, "num") and hasattr(v, "den"):
        return v.num / v.den if v.den else None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def read_exif(path: str) -> dict:
    info = {"Camera": "-", "Date": "-", "ISO": "-", "Aperture": "-",
            "Shutter": "-", "Focal length": "-"}
    if not path:
        return info
    try:
        with open(path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        make = str(tags.get("Image Make", "")).strip()
        model = str(tags.get("Image Model", "")).strip()
        if model:
            info["Camera"] = model if make and make in model else f"{make} {model}".strip()

        date = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
        if date:
            date_str = str(date).strip()
            # Rozdělíme datum a čas podle mezery (např. "2026:11:09 14:30:00")
            parts = date_str.split(" ")
            date_part = parts[0]
            time_part = parts[1] if len(parts) > 1 else ""
            date_pieces = date_part.split(":")
            if len(date_pieces) == 3:
                year, month, day = date_pieces
                formatted_date = f"{day}.{month}.{year}"
                info["Date"] = f"{formatted_date} {time_part}" if time_part else formatted_date
            else:
                info["Date"] = date_str

        if "EXIF ISOSpeedRatings" in tags:
            info["ISO"] = str(tags["EXIF ISOSpeedRatings"])

        f_number = _num(tags["EXIF FNumber"]) if "EXIF FNumber" in tags else None
        if f_number:
            info["Aperture"] = f"f/{f_number:.1f}"

        exposure = _num(tags["EXIF ExposureTime"]) if "EXIF ExposureTime" in tags else None
        if exposure:
            info["Shutter"] = f"1/{round(1 / exposure)} s" if exposure < 1 else f"{exposure:g} s"

        focal = _num(tags["EXIF FocalLength"]) if "EXIF FocalLength" in tags else None
        if focal:
            info["Focal length"] = f"{focal:.1f} mm"
    except Exception as ex:
        print("EXIF nelze přečíst:", ex)
    return info