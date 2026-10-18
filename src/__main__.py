"""
Main execution entrypoint for running the package as a module:
python -m src
"""

import sys
from pathlib import Path

# Ensure src/ and project root are in sys.path
_SRC_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SRC_DIR.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from bot import main_entry

if __name__ == "__main__":
    main_entry()
