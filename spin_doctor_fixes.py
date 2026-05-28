"""spin_doctor_fixes.py — File detection, backup, and fix logic for VKB Spin Doctor."""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from config import ELITE_PATH, ELITE_DANGEROUS_INSTALL_DIRS, STAR_CITIZEN_PATH

SCRIPT_DIR  = Path(__file__).parent
BACKUP_ROOT = SCRIPT_DIR / "backups"

# ── Elite Dangerous constants ─────────────────────────────────────────────────
_ED_USER_BINDINGS = ELITE_PATH

# MouseXMode / MouseYMode values that cause spin when a joystick is also bound
_ED_SPIN_VALUES = {"Bindings_MouseRoll", "Bindings_MousePitch", "Bindings_MouseYaw"}

# Matches e.g.  <MouseXMode Value="Bindings_MouseRoll"  and captures the value in group 1
_ED_MODE_RE = re.compile(r'<Mouse[XY]Mode\s+Value="([^"]*)"')


# ── Path finders ───────────────────────────────────────────────────────────────

def find_warthunder_machine_blk():
    profile = Path(os.environ.get("USERPROFILE", "C:/Users/Default"))
    bases = [
        profile / "OneDrive" / "My Documents" / "My Games" / "WarThunder" / "Saves",
        profile / "Documents"                  / "My Games" / "WarThunder" / "Saves",
        profile / "OneDrive" / "Documents"     / "My Games" / "WarThunder" / "Saves",
    ]
    for base in bases:
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.name.isdigit():
                candidate = entry / "production" / "machine.blk"
                if candidate.exists():
                    return candidate
    return None


def _ed_find_default_preset(preset_name):
    """Return the path to preset_name.binds inside the game's ControlSchemes folder."""
    for folder in ELITE_DANGEROUS_INSTALL_DIRS:
        candidate = folder / f"{preset_name}.binds"
        if candidate.exists():
            return candidate
    return None


def find_elite_binds():
    """Return the active .binds file — user's custom file if it exists, otherwise
    the game's built-in default preset so the status check can still work."""
    user_dir = _ED_USER_BINDINGS
    if not user_dir.is_dir():
        return None

    preset_name = None
    start_file = user_dir / "StartPreset.start"
    if start_file.exists():
        preset_name = start_file.read_text(encoding="utf-8").strip()

    if preset_name:
        user_file = user_dir / f"{preset_name}.binds"
        if user_file.exists():
            return user_file

    user_binds = list(user_dir.glob("*.binds"))
    if user_binds:
        return user_binds[0]

    if preset_name:
        return _ed_find_default_preset(preset_name)

    return None


def find_starcitizen_xml():
    base = STAR_CITIZEN_PATH
    if not base.is_dir():
        return None
    xmls = list(base.glob("*.xml"))
    return xmls[0] if xmls else None


# ── Status detection ───────────────────────────────────────────────────────────

def _blk_has_mouse_axis_in(filepath, target_blocks):
    """Returns True if any of target_blocks inside an 'axes' parent has a mouseAxisId line."""
    content = Path(filepath).read_text(encoding="utf-8", errors="replace")
    stack = []
    for line in content.splitlines():
        s = line.strip()
        if s.endswith("{") and not s.startswith("//"):
            stack.append(s[:-1].strip())
        if (len(stack) >= 2
                and stack[-2] == "axes"
                and stack[-1] in target_blocks
                and s.startswith("mouseAxisId:")):
            return True
        if s == "}" and stack:
            stack.pop()
    return False


def check_warthunder_status(filepath):
    if filepath is None or not Path(filepath).exists():
        return "no_file"
    if _blk_has_mouse_axis_in(filepath, {"ailerons", "elevator"}):
        return "spin_risk"
    return "fixed"


def check_elite_status(filepath):
    if filepath is None or not Path(filepath).exists():
        return "no_file"
    content = Path(filepath).read_text(encoding="utf-8", errors="replace")
    for m in _ED_MODE_RE.finditer(content):
        if m.group(1) in _ED_SPIN_VALUES:
            return "spin_risk"
    return "fixed"


def check_not_implemented(filepath):
    return "no_file"


# ── Backup & fix ───────────────────────────────────────────────────────────────

def make_backup(filepath, game_name):
    """Copy filepath into ./backups/[game]/[timestamp]/. Returns the backup folder."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest_dir = BACKUP_ROOT / game_name / timestamp
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, dest_dir / Path(filepath).name)
    return dest_dir


def fix_warthunder(filepath):
    """Remove mouseAxisId lines from ailerons and elevator blocks. Returns (ok, message)."""
    content = Path(filepath).read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines(keepends=True)
    result = []
    stack = []
    removed = 0

    for line in lines:
        s = line.strip()
        if s.endswith("{") and not s.startswith("//"):
            stack.append(s[:-1].strip())
        skip = (len(stack) >= 2
                and stack[-2] == "axes"
                and stack[-1] in ("ailerons", "elevator")
                and s.startswith("mouseAxisId:"))
        if skip:
            removed += 1
        else:
            result.append(line)
        if s == "}" and stack:
            stack.pop()

    if removed == 0:
        return False, "No mouse axis bindings found — file may already be fixed."
    Path(filepath).write_text("".join(result), encoding="utf-8")
    return True, f"Removed {removed} mouse axis binding(s)."


def fix_elite(filepath):
    """Set MouseXMode and MouseYMode to empty in the .binds file.

    If filepath is the game's built-in default (not in the user folder), copies it
    to the user folder first so Elite Dangerous picks up the override.
    Returns (ok, message).
    """
    filepath = Path(filepath)
    user_dir = _ED_USER_BINDINGS

    try:
        filepath.relative_to(user_dir)
    except ValueError:
        user_dir.mkdir(parents=True, exist_ok=True)
        dest = user_dir / filepath.name
        shutil.copy2(filepath, dest)
        filepath = dest

    content = filepath.read_text(encoding="utf-8", errors="replace")

    fixed_count = [0]

    def _zero_spin(m):
        val = m.group(1)
        if val in _ED_SPIN_VALUES:
            fixed_count[0] += 1
            return m.group(0).replace(f'"{val}"', '""', 1)
        return m.group(0)

    new_content = _ED_MODE_RE.sub(_zero_spin, content)

    if fixed_count[0] == 0:
        return False, "No active mouse axis bindings found — file may already be fixed."

    filepath.write_text(new_content, encoding="utf-8")
    return True, f"Disabled {fixed_count[0]} mouse axis binding(s)."


def restore_last_backup(game_name, filepath):
    """Copy the most recent backup back over filepath. Returns (ok, message)."""
    backup_dir = BACKUP_ROOT / game_name
    if not backup_dir.is_dir():
        return False, "No backups found."
    backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], reverse=True)
    if not backups:
        return False, "No backups found."
    source = backups[0] / Path(filepath).name
    if not source.exists():
        return False, f"Backup does not contain {Path(filepath).name}."
    shutil.copy2(source, filepath)
    return True, f"Restored from backup dated {backups[0].name}."


def has_backup(game_name):
    backup_dir = BACKUP_ROOT / game_name
    return backup_dir.is_dir() and any(backup_dir.iterdir())
