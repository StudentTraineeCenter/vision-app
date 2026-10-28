"""Creates a .venv next to this file and installs everything from requirements.txt.

Usage:  python setup_env.py
Then activate:
    Windows (PowerShell):  .venv\\Scripts\\Activate.ps1
    Windows (cmd):         .venv\\Scripts\\activate.bat
    macOS / Linux:         source .venv/bin/activate
"""
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"

MIN_PYTHON = (3, 10)


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(*args: str) -> None:
    print(">", " ".join(args))
    subprocess.check_call(list(args))


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        sys.exit(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required, "
                 f"you have {sys.version.split()[0]}.")

    if not REQUIREMENTS.exists():
        sys.exit("requirements.txt not found next to setup_env.py.")

    if VENV_DIR.exists():
        print(f"Virtual environment already exists: {VENV_DIR}")
    else:
        print(f"Creating virtual environment: {VENV_DIR}")
        venv.create(VENV_DIR, with_pip=True)

    py = str(venv_python())
    run(py, "-m", "pip", "install", "--upgrade", "pip")
    run(py, "-m", "pip", "install", "-r", str(REQUIREMENTS))

    print("\nVerifying imports...")
    check = (
        "import flet, rawpy, PIL, numpy, tifffile;"
        "print('flet     ', flet.__version__);"
        "print('rawpy    ', rawpy.__version__);"
        "print('pillow   ', PIL.__version__);"
        "print('numpy    ', numpy.__version__);"
        "print('tifffile ', tifffile.__version__)"
    )
    run(py, "-c", check)

    print("\nDone. Activate the environment:")
    print(r"  Windows (PowerShell): .venv\Scripts\Activate.ps1")
    print(r"  Windows (cmd):        .venv\Scripts\activate.bat")
    print("  macOS / Linux:        source .venv/bin/activate")


if __name__ == "__main__":
    main()