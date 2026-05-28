"""config.py — Central path constants for VKB Spin Doctor.

Auto-detects PROJECT_ROOT from this file's location, so the whole
folder can be moved and paths still resolve correctly.
"""
import os
from pathlib import Path

# ── Project root ───────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()

# ── Python executable ──────────────────────────────────────────────────────────
PYTHON_EXE = Path(
    r"C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe"
)

# ── War Thunder ────────────────────────────────────────────────────────────────
# Base saves folder — find_warthunder_machine_blk() searches sub-dirs at runtime
WAR_THUNDER_PATH = (
    Path(os.environ.get("USERPROFILE", ""))
    / "Documents" / "My Games" / "WarThunder" / "Saves"
)

# ── Elite Dangerous ────────────────────────────────────────────────────────────
# User bindings folder (AppData\Local)
ELITE_PATH = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings"
)

# Possible game install directories to search for built-in default presets
ELITE_DANGEROUS_INSTALL_DIRS = [
    Path("C:/Program Files/Epic Games/EliteDangerous/Products/elite-dangerous-odyssey-64/ControlSchemes"),
    Path("C:/Program Files/Epic Games/EliteDangerous/Products/elite-dangerous-64/ControlSchemes"),
    Path("C:/Program Files (x86)/Epic Games/EliteDangerous/Products/elite-dangerous-odyssey-64/ControlSchemes"),
    Path("C:/Program Files (x86)/Epic Games/EliteDangerous/Products/elite-dangerous-64/ControlSchemes"),
    Path("C:/Program Files (x86)/Steam/steamapps/common/Elite Dangerous/ControlSchemes"),
    Path("C:/Program Files/Steam/steamapps/common/Elite Dangerous/ControlSchemes"),
]

# ── Star Citizen ───────────────────────────────────────────────────────────────
STAR_CITIZEN_PATH = Path(
    "C:/Program Files/Roberts Space Industries"
    "/StarCitizen/LIVE/USER/Client/0/Controls/Mappings"
)

# ── Arma Reforger ─────────────────────────────────────────────────────────────
ARMA_PATH = (
    Path(os.environ.get("USERPROFILE", ""))
    / "Documents" / "My Games" / "ArmaReforger"
    / "profile" / ".save" / "settings" / "customInputConfigs"
)

# ── Claude Code project files ──────────────────────────────────────────────────
CLAUDE_PROJ = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "projects"
