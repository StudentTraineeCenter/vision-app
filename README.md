# Vision

Desktopová aplikace pro Windows 11, která načte RAW soubor (`.dng`), ukáže jeho náhled, EXIF a histogram a vyexportuje ho do **JPEG**, **PNG** nebo **TIFF** s nastavitelnými parametry. Součástí je porovnání před/po s úsporou místa a časem exportu.

Projekt vznikl v rámci A&I Labs.

## Funkce

- Načtení `.dng` (včetně telefonních DNG, např. Samsung Galaxy S25+)
- Náhled, **RGB histogram** a **EXIF** údaje
- Export do **JPEG / PNG / TIFF** s parametry formátu
- Vlastní název souboru, výběr cílové složky, nic se nepřepisuje (`_1`, `_2`)
- **Compare:** slider před/po, úspora místa a čas exportu
- Poslední otevřené soubory (Recents), uložení nastavení

## Parametry exportu

| Formát | Parametry |
|---|---|
| **JPEG** | kvalita (1–95), subsampling (4:4:4 / 4:2:2 / 4:2:0), optimize, progressive |
| **PNG** | compress level (0–9), optimize, počet barev, barevný režim (RGB, RGBA, Grayscale, Palette) |
| **TIFF** | komprese (LZW, Deflate, Packbits, None) |


## Rozdíly formátů ve zkratce

| | JPEG | PNG | TIFF |
|---|---|---|---|
| Komprese | ztrátová | bezeztrátová | bezeztrátová / žádná |
| Velikost fotky | malá | velká | největší |
| Průhlednost | ne | ano | ano |
| Využití | fotky, web | grafika, text, loga | archiv, tisk, úpravy |

Příklad z naší fotky (8160 × 6120): DNG 60,8 MB → JPEG 2,0 MB (−96,7 %), export 9,4 s.

## Technologie

Python · [Flet](https://flet.dev) 1.0.5 (GUI) · rawpy · Pillow · tifffile · imagecodecs · exifread

## Instalace a spuštění

Doporučujeme **Python 3.14 z [python.org](https://www.python.org/downloads/)**.

```powershell
git clone <URL repozitáře>
cd vision-app
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

## Struktura projektu

```
vision-app/
├── src/
│   ├── main.py            # vstupní bod
│   ├── ui/                # obrazovky (Home, Export, Compare, Settings)
│   ├── core/              # načtení DNG a exportéry (JPEG, PNG, TIFF)
│   └── settings_store.py  # uložení nastavení a recents
├── tests/
├── requirements.txt
└── README.md
```
