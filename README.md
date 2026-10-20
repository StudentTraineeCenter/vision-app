# Vision 📸

**Vision** je desktopová aplikace určená pro operační systém Windows 11, která slouží k načítání digitálních fotografií ve formátu RAW (`.dng`), jejich zpracování a následnému exportu do tří cílových formátů: **JPEG, PNG a TIFF** s detailní možností konfigurace kompresních parametrů.


---

## 🛠️ Tech Stack

- **Jazyk:** Python 3.10+
- **Uživatelské rozhraní:** [Flet](https://flet.dev/) (framework založený na Flutteru s podporou Fluent Designu pro Windows 11)
- **Dekódování RAW:** `rawpy` (LibRaw wrapper) pro převod DNG na NumPy bitmapu v paměti
- **Zpracování obrazu & Komprese:** `Pillow` + `NumPy`
- **Asynchronní správa:** Běh náročných výpočtů v samostatných vláknech na pozadí (non-blocking UI)

---

## ⚙️ Podporované Formáty a Parametry

### 1. JPEG
- **Quality:** Nastavení kvality obrazu (0–100 %)
- **Subsampling:** Barevné podvzorkování (`4:4:4`, `4:2:2`, `4:2:0`)
- **Optimize:** Sestavení Huffmanových tabulek na míru obrázku
- **Progressive:** Progresivní ukládání po vrstvách

### 2. PNG
- **Compress Level:** Úroveň komprese Deflate (0–9)
- **Optimize:** Aplikace optimálních pre-processing filtrů
- **Počet barev:** Redukce barev (kvantizace / paleta)
- **Barevný režim:** Převod mezi RGB, RGBA a Grayscale

### 3. TIFF
- **Volba komprese:** Výběr metody komprese (`None`, `LZW`, `DEFLATE`, `PackBits`) s páskovým zpracováním

---

##  Jak aplikaci spustit

### 1. Klonování repozitáře
```bash
git clone [https://github.com/THartigova/vision-app.git](https://github.com/THartigova/vision-app.git)
cd vision-app

##  Detailní Architektura a Struktura Projektu

Struktura repozitáře je navržena tak, aby striktně oddělovala uživatelské rozhraní (UI) od backendové výpočetní logiky a kompresních algoritmů.

```text
vision-app/
├── .gitignore              # Ignorované soubory (venv, cache, výstupní fotky)
├── README.md               # Dokumentace a návod k projektu
├── requirements.txt        # Seznam závislostí pro pip
│
├── assets/                 # Statické zdroje a testovací data
│   └── sample.dng          # Vzorový .dng soubor pro vývoj a testování[cite: 5]
│
├── src/                    # Hlavní zdrojový kód aplikace
│   ├── main.py             # Vstupní bod – inicializace a spustitelná Flet aplikace[cite: 5]
│   │
│   ├── ui/                 # Uživatelské rozhraní (Flet / Windows 11 Fluent)[cite: 5]
│   │   ├── __init__.py
│   │   ├── app_layout.py   # Hlavní kostra okna (sidebar + hlavní pracovní plocha)
│   │   ├── components.py   # Ovládací prvky (slidery, dropdowny, přepínače parametrů)[cite: 5]
│   │   └── preview.py      # Náhledové okno, porovnání kvalit a statistiky exportu[cite: 5]
│   │
│   └── core/               # Zpracování obrazu a kompresní logika[cite: 5, 6]
│       ├── __init__.py
│       ├── loader.py       # Dekódování .dng přes rawpy na NumPy RGB bitmapu[cite: 5]
│       ├── exporter_jpeg.py# Logika pro JPEG (YCbCr, 8x8 mřížky, DCT, Huffman)[cite: 9]
│       ├── exporter_png.py # Logika pro PNG (Deflate, filtry, kvantizace barev)[cite: 7]
│       ├── exporter_tiff.py# Logika pro TIFF (dělení na pásy, LZW, PackBits, Deflate)[cite: 10, 11]
│       └── worker.py       # Asynchronní běh konverzí v samostatných vláknech[cite: 6]
│
└── tests/                  # Testovací skripty
    ├── __init__.py
    ├── test_loader.py      # Testy načítání DNG souborů
    └── test_exporters.py   # Testy komprese a správnosti výstupních formátů