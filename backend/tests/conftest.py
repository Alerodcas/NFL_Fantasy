from pathlib import Path
import sys

# Se asegura de que `backend/src` este en sys.path antes de importar paquetes de la aplicacion
ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Add backend/src to sys.path so tests can import `config` and `modules` packages
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Also add the tests directory itself so helper modules (tests/helpers) can be imported
TESTS_DIR = str(Path(__file__).resolve().parent)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)
