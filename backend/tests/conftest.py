from pathlib import Path
import sys

# Add backend/src to sys.path so tests can import `config` and `modules` packages
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
