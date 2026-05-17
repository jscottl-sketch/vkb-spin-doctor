#!/usr/bin/env python3
"""VKB Spin Doctor — fixes mouse-axis spin for VKB joystick users."""

import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from pathlib import Path

# Module 02 — Process Conductor. Wrapped so a broken module disables the
# tab gracefully instead of crashing the whole GUI.
try:
    from problems import conductor
    _CONDUCTOR_OK  = True
    _CONDUCTOR_ERR = None
except Exception as _e:
    conductor      = None
    _CONDUCTOR_OK  = False
    _CONDUCTOR_ERR = f"{type(_e).__name__}: {_e}"

# Module 07 — ED Bind Reset Prevention. Same wrap pattern.
try:
    from problems import ed_bind_reset
    _ED_RESET_OK  = True
    _ED_RESET_ERR = None
except Exception as _e:
    ed_bind_reset = None
    _ED_RESET_OK  = False
    _ED_RESET_ERR = f"{type(_e).__name__}: {_e}"


SCRIPT_DIR = Path(__file__).parent
BACKUP_ROOT = SCRIPT_DIR / "backups"

# ── Colours ────────────────────────────────────────────────────────────────────
BG_WIN    = "#1a252f"
BG_CARD   = "#2c3e50"
BG_GREY   = "#283747"
FG_WHITE  = "#ecf0f1"
FG_DIM    = "#7f8c8d"
FG_DIMMER = "#5d6d7e"
C_RED     = "#e74c3c"
C_GREEN   = "#27ae60"
C_BLUE    = "#2980b9"
C_GREY    = "#555e6b"
C_DIV     = "#1e2f3d"
C_AMBER   = "#f39c12"

STATUS_DISPLAY = {
    "spin_risk": ("⚠  SPIN RISK",           C_RED,   FG_WHITE),
    "fixed":     ("✓  FIXED",               C_GREEN, FG_WHITE),
    "no_file":   ("—  NOT YET CUSTOMISED",  C_GREY,  FG_DIM),
}


# ── Knowledge Base data ────────────────────────────────────────────────────────
# Problems pulled from Universal_Input_Device_Database.md, filtered per game.
KB_DATA = {
    "War Thunder": [
        {
            "id":    "J-001",
            "title": "Mouse Axis Spin Bug",
            "auto":  "✅  This tool fixes it",
            "desc":  "Plugging in a joystick causes War Thunder to auto-bind mouse movement "
                     "to roll and pitch axes. Any mouse movement = constant uncontrolled spin.",
            "fixes": [
                'Go to the "Fix Mouse Spin" tab and click "Fix Mouse Spin".',
                "Spin Doctor removes the mouseAxisId lines from the ailerons and elevator "
                "blocks inside machine.blk and backs up the original first.",
            ],
        },
        {
            "id":    "U-001",
            "title": "Device Not Detected (or seen as Xbox pad)",
            "auto":  "⚠️  Manual fix",
            "desc":  "Joystick works in Windows but War Thunder ignores it, or treats it as "
                     "a generic Xbox controller instead of a real joystick.",
            "fixes": [
                "Steam → Settings → Controller → General Controller Settings → "
                "uncheck Generic Gamepad Configuration Support.",
                "Right-click War Thunder in Steam Library → Properties → Controller → "
                "Disable Steam Input.",
                "Plug directly into a rear motherboard USB port, not a hub or front panel.",
                "Launch War Thunder AFTER the joystick is already plugged in.",
            ],
        },
        {
            "id":    "U-002",
            "title": "Bindings Reset After Game Update",
            "auto":  "✅  Use Restore button",
            "desc":  "A War Thunder patch overwrites machine.blk and all your custom "
                     "bindings vanish.",
            "fixes": [
                'Click "Restore Last Backup" on the Fix tab — Spin Doctor backs up '
                "your file before every fix.",
                "Keep the backups folder safe. It survives game updates.",
            ],
        },
        {
            "id":    "U-003",
            "title": "Double Input / Controller Conflict",
            "auto":  "⚠️  Manual fix",
            "desc":  "Axis moves on its own, or inputs fight each other. Most common when "
                     "a PS5 or Xbox controller is connected alongside the joystick.",
            "fixes": [
                "Unplug any controllers not being used for War Thunder.",
                "Disable Steam Input (see U-001 above).",
                "Use HidHide (free open-source tool) to hide unused devices from War Thunder.",
            ],
        },
        {
            "id":    "U-005",
            "title": "Axis Drift at Rest",
            "auto":  "⚠️  Manual fix",
            "desc":  "Aircraft drifts slowly when you take your hands off the joystick.",
            "fixes": [
                "War Thunder: Options → Controls → Axis → set Deadzone to 3–8% for each axis.",
                "Windows: press Windows key + R, type joy.cpl, press Enter → recalibrate.",
                "Try a different rear USB port to rule out electrical interference.",
            ],
        },
        {
            "id":    "U-006",
            "title": "Inverted Axes",
            "auto":  "⚠️  Manual fix",
            "desc":  "Pulling the stick back makes the nose go down, or other axes are reversed.",
            "fixes": [
                "War Thunder: Options → Controls → Axis → tick the Invert checkbox "
                "for the affected axis.",
            ],
        },
    ],

    "Elite Dangerous": [
        {
            "id":    "J-001",
            "title": "Mouse Axis Spin Bug",
            "auto":  "✅  This tool fixes it",
            "desc":  "Joystick connected but MouseXMode / MouseYMode in the .binds file "
                     "are still set to Bindings_MouseRoll / Bindings_MousePitch. "
                     "Any mouse movement causes constant spin.",
            "fixes": [
                'Go to the "Fix Mouse Spin" tab and click "Fix Mouse Spin".',
                "Spin Doctor sets MouseXMode and MouseYMode to empty in the .binds file "
                "and backs up the original first.",
            ],
        },
        {
            "id":    "U-001",
            "title": "Device Not Detected",
            "auto":  "⚠️  Manual fix",
            "desc":  "Elite Dangerous does not see your joystick, or reverts to "
                     "keyboard-only mode.",
            "fixes": [
                "Launch Elite Dangerous AFTER the joystick is plugged in.",
                "If using the Steam version: right-click game → Properties → "
                "Controller → Disable Steam Input.",
                "Plug into a rear motherboard USB port.",
                "In-game: Options → Controls → click an axis field and move the stick to bind it.",
            ],
        },
        {
            "id":    "U-002",
            "title": "Bindings Reset After Game Update",
            "auto":  "✅  Use Restore button",
            "desc":  "A Frontier update resets custom bindings back to the default preset.",
            "fixes": [
                "Spin Doctor backs up your .binds file before every fix. "
                'Use "Restore Last Backup".',
                "Also manually copy your .binds file somewhere safe before major updates.",
            ],
        },
        {
            "id":    "U-003",
            "title": "Double Input / Controller Conflict",
            "auto":  "⚠️  Manual fix",
            "desc":  "Ship spins or twitches when another controller is also bound "
                     "to the same flight axis.",
            "fixes": [
                "Options → Controls → check each axis. Remove duplicate device entries.",
                "Unplug unused controllers before launching.",
                "In the .binds file: axes bound to {NoDevice} are safe — "
                "remove Mouse bindings if joystick is primary.",
            ],
        },
        {
            "id":    "U-005",
            "title": "Axis Drift at Rest",
            "auto":  "⚠️  Manual fix",
            "desc":  "Ship drifts when you let go of the stick.",
            "fixes": [
                "Options → Controls → Axis Tuning → increase Deadzone for the drifting axis.",
                "Recalibrate in Windows: press Windows key + R, type joy.cpl, press Enter.",
            ],
        },
        {
            "id":    "J-003",
            "title": "Twist / Rudder Axis Not Detected",
            "auto":  "⚠️  Manual fix",
            "desc":  "The joystick twist (Z-axis / rudder) does not appear in Elite's "
                     "axis binding list.",
            "fixes": [
                "Options → Controls → click the Yaw Axis field → twist the joystick to bind it.",
                "If still not detected: check joy.cpl — if Windows shows the axis there, "
                "try a different USB port.",
            ],
        },
    ],

    "Star Citizen": [
        {
            "id":    "J-001",
            "title": "Mouse Axis Spin Bug",
            "auto":  "🚧  Coming soon",
            "desc":  "Mouse movement controls flight axes alongside the joystick, "
                     "causing uncontrolled spin.",
            "fixes": [
                "Options → Keybindings → Mouse → set mouse flight axes to None.",
                "Spin Doctor will fix this automatically in a future update.",
            ],
        },
        {
            "id":    "U-001",
            "title": "Device Not Detected",
            "auto":  "⚠️  Manual fix",
            "desc":  "Star Citizen does not see your joystick or only sees some of its axes. "
                     "Star Citizen has a device limit — too many connected at once and some "
                     "will be ignored.",
            "fixes": [
                "Launch Star Citizen AFTER plugging in all devices.",
                "Plug directly into a rear USB port.",
                "Disconnect any devices you are not using.",
                "In-game: Options → Keybindings → Advanced Controls → map axes manually.",
            ],
        },
        {
            "id":    "U-002",
            "title": "Bindings Reset After Game Update",
            "auto":  "✅  Use Restore button",
            "desc":  "A PTU or LIVE patch overwrites your custom XML mapping file.",
            "fixes": [
                "Spin Doctor backs up your file before every fix. "
                'Use "Restore Last Backup".',
                "Custom mappings live in: StarCitizen\\LIVE\\USER\\Client\\0\\Controls\\Mappings\\",
                "Back up that folder before major updates.",
            ],
        },
        {
            "id":    "U-003",
            "title": "Double Input / Controller Conflict",
            "auto":  "⚠️  Manual fix",
            "desc":  "Ship spins or inputs fight each other. Common when a gamepad is "
                     "connected alongside the joystick.",
            "fixes": [
                "Unplug unused controllers before launching Star Citizen.",
                "Options → Keybindings → check for duplicate axis bindings across devices.",
                "Use HidHide (free tool) to hide unused devices from Star Citizen.",
            ],
        },
        {
            "id":    "U-005",
            "title": "Axis Drift at Rest",
            "auto":  "⚠️  Manual fix",
            "desc":  "Ship drifts when hands are off the controls.",
            "fixes": [
                "Options → Keybindings → Joystick → increase the deadzone for drifting axes.",
                "Recalibrate in Windows: press Windows key + R, type joy.cpl, press Enter.",
            ],
        },
        {
            "id":    "U-008",
            "title": "Wrong Device Name After USB Port Change",
            "auto":  "⚠️  Manual fix",
            "desc":  "After plugging into a different USB port, Star Citizen loses your "
                     "joystick profile because Windows assigned it a new device ID.",
            "fixes": [
                "Always plug your joystick into the same USB port.",
                "If you moved ports: re-bind axes in Options → Keybindings.",
                "Use HidHide to assign a persistent device name.",
            ],
        },
    ],
}


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


_ED_USER_BINDINGS = (Path(os.environ.get("LOCALAPPDATA", ""))
                     / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings")

# MouseXMode / MouseYMode values that cause spin when a joystick is also bound
_ED_SPIN_VALUES = {"Bindings_MouseRoll", "Bindings_MousePitch", "Bindings_MouseYaw"}

# Matches e.g.  <MouseXMode Value="Bindings_MouseRoll"  and captures the value in group 1
_ED_MODE_RE = re.compile(r'<Mouse[XY]Mode\s+Value="([^"]*)"')


def _ed_find_default_preset(preset_name):
    """Return the path to preset_name.binds inside the game's ControlSchemes folder."""
    folders = [
        Path("C:/Program Files/Epic Games/EliteDangerous/Products/elite-dangerous-odyssey-64/ControlSchemes"),
        Path("C:/Program Files/Epic Games/EliteDangerous/Products/elite-dangerous-64/ControlSchemes"),
        Path("C:/Program Files (x86)/Epic Games/EliteDangerous/Products/elite-dangerous-odyssey-64/ControlSchemes"),
        Path("C:/Program Files (x86)/Epic Games/EliteDangerous/Products/elite-dangerous-64/ControlSchemes"),
        Path("C:/Program Files (x86)/Steam/steamapps/common/Elite Dangerous/ControlSchemes"),
        Path("C:/Program Files/Steam/steamapps/common/Elite Dangerous/ControlSchemes"),
    ]
    for folder in folders:
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

    # User's own file for the active preset takes priority
    if preset_name:
        user_file = user_dir / f"{preset_name}.binds"
        if user_file.exists():
            return user_file

    # Any other user .binds file
    user_binds = list(user_dir.glob("*.binds"))
    if user_binds:
        return user_binds[0]

    # No user file at all — fall back to the game's read-only default
    if preset_name:
        return _ed_find_default_preset(preset_name)

    return None


def find_starcitizen_xml():
    base = Path("C:/Program Files/Roberts Space Industries"
                "/StarCitizen/LIVE/USER/Client/0/Controls/Mappings")
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

    # If the file lives outside the user folder it's a read-only game default — copy it
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


# ── GUI ────────────────────────────────────────────────────────────────────────

class GameCard(tk.Frame):
    def __init__(self, parent, game_name, finder_fn, status_fn, fix_fn, greyed=False):
        bg = BG_GREY if greyed else BG_CARD
        super().__init__(parent, bg=bg, padx=16, pady=14)

        self.game_name = game_name
        self.finder_fn = finder_fn
        self.status_fn = status_fn
        self.fix_fn    = fix_fn
        self.greyed    = greyed
        self.filepath  = finder_fn()

        self._build(bg)
        self.refresh()

    def _build(self, bg):
        tk.Label(self, text=self.game_name,
                 font=("Segoe UI", 13, "bold"), bg=bg, fg=FG_WHITE
                 ).grid(row=0, column=0, sticky="w")

        self.path_lbl = tk.Label(self, text="",
                                  font=("Segoe UI", 8), bg=bg, fg=FG_DIM,
                                  wraplength=520, justify="left")
        self.path_lbl.grid(row=1, column=0, sticky="w", pady=(1, 6))

        self.status_lbl = tk.Label(self, text="",
                                    font=("Segoe UI", 9, "bold"), padx=10, pady=3)
        self.status_lbl.grid(row=2, column=0, sticky="w", pady=(0, 8))

        if self.greyed:
            tk.Label(self,
                     text="Launch the game, go to Controls, change any binding, then click Re-scan.",
                     font=("Segoe UI", 9, "italic"), bg=bg, fg=FG_DIMMER,
                     wraplength=520, justify="left"
                     ).grid(row=3, column=0, sticky="w", pady=(0, 8))

        btn_row = tk.Frame(self, bg=bg)
        btn_row.grid(row=4, column=0, sticky="w")

        self.fix_btn = tk.Button(
            btn_row, text="Fix Mouse Spin",
            font=("Segoe UI", 10, "bold"),
            bg=C_RED, fg=FG_WHITE, padx=14, pady=5,
            relief="flat", cursor="hand2",
            command=self._on_fix)
        self.fix_btn.pack(side="left", padx=(0, 8))

        self.restore_btn = tk.Button(
            btn_row, text="Restore Last Backup",
            font=("Segoe UI", 10),
            bg=FG_DIM, fg=FG_WHITE, padx=14, pady=5,
            relief="flat", cursor="hand2",
            command=self._on_restore)
        self.restore_btn.pack(side="left", padx=(0, 8))

        if self.greyed:
            tk.Button(
                btn_row, text="Re-scan",
                font=("Segoe UI", 10),
                bg=C_BLUE, fg=FG_WHITE, padx=14, pady=5,
                relief="flat", cursor="hand2",
                command=self._on_rescan
            ).pack(side="left")

    def refresh(self):
        self.path_lbl.config(
            text=str(self.filepath) if self.filepath
            else "Binding file not found on this system"
        )

        status = self.status_fn(self.filepath)
        label, bg_col, fg_col = STATUS_DISPLAY[status]
        self.status_lbl.config(text=label, bg=bg_col, fg=fg_col)

        can_fix = (status == "spin_risk")
        self.fix_btn.config(
            state="normal" if can_fix else "disabled",
            bg=C_RED if can_fix else C_GREY,
            cursor="hand2" if can_fix else "arrow")

        can_restore = has_backup(self.game_name) and self.filepath is not None
        self.restore_btn.config(
            state="normal" if can_restore else "disabled",
            bg=FG_DIM if can_restore else C_GREY,
            cursor="hand2" if can_restore else "arrow")

    def _on_fix(self):
        if not messagebox.askyesno(
                "Confirm Fix",
                f"Fix mouse spin for {self.game_name}?\n\n"
                "Your binding file will be backed up first."):
            return
        try:
            backup_dir = make_backup(self.filepath, self.game_name)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Could not create backup:\n{e}")
            return
        success, msg = self.fix_fn(self.filepath)
        if success:
            self.filepath = self.finder_fn()  # re-scan: ED may have created a new user file
            messagebox.showinfo("Fixed!", f"{msg}\n\nBackup saved to:\n{backup_dir}")
        else:
            messagebox.showerror("Fix Failed", msg)
        self.refresh()

    def _on_restore(self):
        if not messagebox.askyesno(
                "Confirm Restore",
                f"Restore last backup for {self.game_name}?\n\n"
                "This will undo your last fix."):
            return
        success, msg = restore_last_backup(self.game_name, self.filepath)
        if success:
            messagebox.showinfo("Restored", msg)
        else:
            messagebox.showerror("Restore Failed", msg)
        self.refresh()

    def _on_rescan(self):
        self.filepath = self.finder_fn()
        self.refresh()


class EDBindResetCard(tk.Frame):
    """Module 07 widget. Sits under the Elite Dangerous fix card on the
    Fix Mouse Spin tab. Renames custom .binds files so ED won't overwrite
    them on update."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_GREY, padx=16, pady=10)
        self._last_unprotected = []
        self._build()
        if _ED_RESET_OK:
            self.refresh()
        else:
            self._render_load_error()

    def _build(self):
        bg = BG_GREY

        tk.Label(self, text="Elite Dangerous — Bind Reset Prevention",
                 font=("Segoe UI", 11, "bold"), bg=bg, fg=FG_WHITE
                 ).grid(row=0, column=0, sticky="w")

        tk.Label(self,
                 text=("Renames your custom .binds file so Elite Dangerous won't "
                       "overwrite it on the next game update."),
                 font=("Segoe UI", 8), bg=bg, fg=FG_DIM,
                 wraplength=520, justify="left"
                 ).grid(row=1, column=0, sticky="w", pady=(1, 6))

        self.status_lbl = tk.Label(self, text="",
                                    font=("Segoe UI", 9, "bold"),
                                    bg=bg, fg=FG_WHITE,
                                    wraplength=520, justify="left", anchor="w")
        self.status_lbl.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        btn_row = tk.Frame(self, bg=bg)
        btn_row.grid(row=3, column=0, sticky="w")

        self.protect_btn = tk.Button(
            btn_row, text="Protect Bindings",
            font=("Segoe UI", 10, "bold"),
            bg=C_RED, fg=FG_WHITE, padx=14, pady=5,
            relief="flat", cursor="hand2",
            command=self._on_protect)
        self.protect_btn.pack(side="left", padx=(0, 8))

        self.rescan_btn = tk.Button(
            btn_row, text="Re-scan",
            font=("Segoe UI", 10),
            bg=C_BLUE, fg=FG_WHITE, padx=14, pady=5,
            relief="flat", cursor="hand2",
            command=self.refresh)
        self.rescan_btn.pack(side="left")

    def refresh(self):
        if not _ED_RESET_OK:
            return
        result = ed_bind_reset.scan()
        status = result["status"]
        self._last_unprotected = result["unprotected"]

        if status == "no_folder":
            self.status_lbl.config(
                text=(f"Bindings folder does not exist:\n{result['folder']}\n\n"
                      "Elite Dangerous only creates this folder after the first "
                      "binding customisation. Launch the game, change any binding, "
                      "then click Re-scan."),
                fg=FG_DIM)
            self._set_protect_enabled(False)

        elif status == "no_custom":
            self.status_lbl.config(
                text=("No custom .binds file found yet. Launch Elite Dangerous, "
                      "go to Options → Controls, change any binding to create one, "
                      "then click Re-scan."),
                fg=C_AMBER)
            self._set_protect_enabled(False)

        elif status == "already":
            names = ", ".join(p.name for p in result["protected"])
            self.status_lbl.config(
                text=f"✓  Already protected — ED cannot overwrite: {names}",
                fg=C_GREEN)
            self._set_protect_enabled(False)

        elif status == "found":
            names = ", ".join(p.name for p in result["unprotected"])
            self.status_lbl.config(
                text=f"⚠  Unprotected custom binding file(s): {names}",
                fg=C_RED)
            self._set_protect_enabled(True)

    def _set_protect_enabled(self, enabled):
        self.protect_btn.config(
            state="normal" if enabled else "disabled",
            bg=C_RED if enabled else C_GREY,
            cursor="hand2" if enabled else "arrow")

    def _on_protect(self):
        files = self._last_unprotected
        if not files:
            return
        preview = "\n".join(
            f"  • {p.name}  →  {p.stem}{ed_bind_reset.PROTECTED_SUFFIX}{p.suffix}"
            for p in files)
        if not messagebox.askyesno(
                "Confirm Rename",
                "Rename the following file(s)?\n\n"
                f"{preview}\n\n"
                "After this, Elite Dangerous will not overwrite the file on update.\n\n"
                "Note: Elite Dangerous may also stop loading the file until you rename "
                "it back, so your bindings could appear to reset to defaults inside the "
                "game until then."):
            return

        renamed, errors = ed_bind_reset.protect_all(files)
        if errors:
            err_text = "\n".join(f"  • {name}: {msg}" for name, msg in errors)
            messagebox.showwarning(
                "Partial Success",
                f"Renamed {renamed} file(s). {len(errors)} failed:\n\n{err_text}")
        else:
            messagebox.showinfo(
                "Protected!",
                f"Renamed {renamed} file(s). Your bindings are now safe from "
                "Elite Dangerous updates.")
        self.refresh()

    def _render_load_error(self):
        self.status_lbl.config(
            text=f"Module 07 failed to load: {_ED_RESET_ERR}",
            fg=C_RED)
        self.protect_btn.config(state="disabled", bg=C_GREY, cursor="arrow")
        self.rescan_btn.config(state="disabled", bg=C_GREY, cursor="arrow")


class KnowledgeBaseTab(tk.Frame):
    """Scrollable list of common problems and fixes, filtered by selected game."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_WIN)
        self._game_var = tk.StringVar(value="War Thunder")
        self._build()

    def _build(self):
        # ── Game selector ──
        sel = tk.Frame(self, bg=BG_WIN, pady=12)
        sel.pack(fill="x", padx=4)

        tk.Label(sel, text="Show help for:",
                 font=("Segoe UI", 10), bg=BG_WIN, fg=FG_DIM
                 ).pack(side="left", padx=(0, 10))

        for game in ("War Thunder", "Elite Dangerous", "Star Citizen"):
            tk.Radiobutton(
                sel, text=game,
                variable=self._game_var, value=game,
                font=("Segoe UI", 10),
                bg=BG_WIN, fg=FG_WHITE,
                selectcolor=BG_CARD,
                activebackground=BG_WIN, activeforeground=FG_WHITE,
                command=self._refresh,
            ).pack(side="left", padx=6)

        tk.Frame(self, bg=C_DIV, height=1).pack(fill="x", padx=4, pady=(0, 8))

        # ── Scrollable canvas ──
        container = tk.Frame(self, bg=BG_WIN)
        container.pack(fill="both", expand=True, padx=4)

        self._canvas = tk.Canvas(container, bg=BG_WIN, highlightthickness=0, height=420)
        sb = tk.Scrollbar(container, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=BG_WIN)
        self._win_id = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", self._on_inner_resize)
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind_all("<MouseWheel>", self._on_wheel)

        self._refresh()

    # ── internal helpers ──

    def _on_inner_resize(self, _event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _on_wheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _refresh(self):
        for w in self._inner.winfo_children():
            w.destroy()

        entries = KB_DATA.get(self._game_var.get(), [])
        for entry in entries:
            self._make_card(entry)

        # Reset scroll to top
        self._canvas.yview_moveto(0)

    def _make_card(self, entry):
        card = tk.Frame(self._inner, bg=BG_CARD, padx=14, pady=10)
        card.pack(fill="x", pady=(0, 6))

        # Header: ID badge + title + auto indicator
        hdr = tk.Frame(card, bg=BG_CARD)
        hdr.pack(fill="x")

        tk.Label(hdr, text=entry["id"],
                 font=("Segoe UI", 8, "bold"),
                 bg=C_BLUE, fg=FG_WHITE, padx=6, pady=2
                 ).pack(side="left")

        tk.Label(hdr, text=f"  {entry['title']}",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_CARD, fg=FG_WHITE
                 ).pack(side="left")

        tk.Label(hdr, text=entry["auto"],
                 font=("Segoe UI", 8),
                 bg=BG_CARD, fg=FG_DIM
                 ).pack(side="right", padx=(0, 2))

        # Description
        tk.Label(card, text=entry["desc"],
                 font=("Segoe UI", 9),
                 bg=BG_CARD, fg=FG_DIM,
                 wraplength=530, justify="left", anchor="w"
                 ).pack(fill="x", pady=(6, 4))

        # Fix steps
        for fix in entry["fixes"]:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text="•",
                     font=("Segoe UI", 9), bg=BG_CARD, fg=C_GREEN
                     ).pack(side="left", anchor="n", padx=(0, 4))
            tk.Label(row, text=fix,
                     font=("Segoe UI", 9), bg=BG_CARD, fg=FG_WHITE,
                     wraplength=510, justify="left"
                     ).pack(side="left", fill="x")


class ProcessConductorTab(tk.Frame):
    """Scan results from problems/conductor.py — companion software, input
    mappers, overlays, launch order. Conflicts shown first, with a button
    on each to open the recommendation text. Never auto-kills processes."""

    STATUS_LOOK = {
        "warn":          ("CONFLICT",      C_RED,   FG_WHITE),
        "info":          ("ADVISORY",      C_AMBER, FG_WHITE),
        "not_installed": ("NOT INSTALLED", C_GREY,  FG_DIM),
        "ok":            ("OK",            C_GREEN, FG_WHITE),
    }
    _SORT_ORDER = {"warn": 0, "info": 1, "not_installed": 2, "ok": 3}

    def __init__(self, parent):
        super().__init__(parent, bg=BG_WIN)
        self._results = []
        self._build()
        if _CONDUCTOR_OK:
            self._scan()
        else:
            self._render_load_error()

    def _build(self):
        # ── Top bar: scan button + summary ──
        bar = tk.Frame(self, bg=BG_WIN, pady=12)
        bar.pack(fill="x", padx=4)

        self._scan_btn = tk.Button(
            bar, text="Scan Now",
            font=("Segoe UI", 10, "bold"),
            bg=C_BLUE, fg=FG_WHITE, padx=18, pady=5,
            relief="flat", cursor="hand2",
            command=self._scan)
        self._scan_btn.pack(side="left", padx=(0, 14))

        self._summary_lbl = tk.Label(bar, text="",
                                     font=("Segoe UI", 10, "bold"),
                                     bg=BG_WIN, fg=FG_DIM)
        self._summary_lbl.pack(side="left")

        tk.Label(self,
                 text="Never auto-kills processes. Recommends only. You decide what to close.",
                 font=("Segoe UI", 8, "italic"),
                 bg=BG_WIN, fg=FG_DIMMER
                 ).pack(anchor="w", padx=8, pady=(0, 4))

        tk.Frame(self, bg=C_DIV, height=1).pack(fill="x", padx=4, pady=(0, 8))

        # ── Scrollable canvas ──
        container = tk.Frame(self, bg=BG_WIN)
        container.pack(fill="both", expand=True, padx=4)

        self._canvas = tk.Canvas(container, bg=BG_WIN, highlightthickness=0, height=400)
        sb = tk.Scrollbar(container, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=BG_WIN)
        self._win_id = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>",
                         lambda _e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._win_id, width=e.width))
        # Only bind the wheel while the cursor is over THIS canvas — otherwise
        # the KB tab's wheel binding could fight ours.
        self._canvas.bind("<Enter>", lambda _e: self._canvas.bind_all("<MouseWheel>", self._on_wheel))
        self._canvas.bind("<Leave>", lambda _e: self._canvas.unbind_all("<MouseWheel>"))

    def _on_wheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Scan + render ──

    def _scan(self):
        if not _CONDUCTOR_OK:
            return
        self._summary_lbl.config(text="Scanning…", fg=FG_DIM)
        self.update_idletasks()
        try:
            self._results = conductor.scan_all()
        except Exception as e:
            self._results = []
            self._summary_lbl.config(text=f"Scan failed: {e}", fg=C_RED)
            return
        self._render()

    def _render(self):
        for w in self._inner.winfo_children():
            w.destroy()

        sorted_results = sorted(
            self._results,
            key=lambda r: (self._SORT_ORDER.get(r[1], 9), r[0]["id"]))

        warns = sum(1 for _, s in self._results if s == "warn")
        infos = sum(1 for _, s in self._results if s == "info")
        total = len(self._results)

        if warns == 0 and infos == 0:
            self._summary_lbl.config(
                text=f"✓  All {total} checks clear — no process conflicts.",
                fg=C_GREEN)
        else:
            bits = []
            if warns:
                bits.append(f"{warns} conflict{'s' if warns != 1 else ''}")
            if infos:
                bits.append(f"{infos} advisory")
            self._summary_lbl.config(
                text=f"{' · '.join(bits)}   (of {total} checks)",
                fg=C_RED if warns else C_AMBER)

        for problem, status in sorted_results:
            self._make_card(problem, status)

        self._canvas.yview_moveto(0)

    def _make_card(self, problem, status):
        is_active = status in ("warn", "info")
        bg = BG_CARD if is_active else BG_GREY

        card = tk.Frame(self._inner, bg=bg, padx=14, pady=8)
        card.pack(fill="x", pady=(0, 4))

        hdr = tk.Frame(card, bg=bg)
        hdr.pack(fill="x")

        tk.Label(hdr, text=problem["id"],
                 font=("Segoe UI", 8, "bold"),
                 bg=C_BLUE, fg=FG_WHITE, padx=6, pady=2
                 ).pack(side="left")

        tk.Label(hdr, text=f"  {problem['title']}",
                 font=("Segoe UI", 10, "bold" if is_active else "normal"),
                 bg=bg, fg=FG_WHITE if is_active else FG_DIM,
                 anchor="w"
                 ).pack(side="left", fill="x", expand=True)

        # Status badge (right-aligned)
        label, badge_bg, badge_fg = self.STATUS_LOOK[status]
        tk.Label(hdr, text=label,
                 font=("Segoe UI", 8, "bold"),
                 bg=badge_bg, fg=badge_fg, padx=8, pady=2
                 ).pack(side="right", padx=(8, 0))

        if is_active:
            tk.Button(hdr, text="Show recommendation",
                      font=("Segoe UI", 9),
                      bg=C_BLUE, fg=FG_WHITE, padx=10, pady=2,
                      relief="flat", cursor="hand2",
                      command=lambda p=problem: self._show_recommendation(p),
                      ).pack(side="right", padx=4)

    def _show_recommendation(self, problem):
        try:
            _ok, msg = problem["fix"]()
        except Exception as e:
            messagebox.showerror("Recommendation error",
                                 f"Could not load recommendation:\n{e}")
            return

        win = tk.Toplevel(self.winfo_toplevel())
        win.title(f"{problem['id']} — {problem['title']}")
        win.configure(bg=BG_WIN)
        win.transient(self.winfo_toplevel())
        win.resizable(False, False)

        tk.Label(win, text=problem["title"],
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_WIN, fg=FG_WHITE,
                 padx=20, pady=14, anchor="w"
                 ).pack(fill="x")

        txt = tk.Text(win, wrap="word",
                      font=("Segoe UI", 10),
                      bg=BG_CARD, fg=FG_WHITE,
                      width=72, height=18,
                      padx=14, pady=10,
                      relief="flat",
                      borderwidth=0, highlightthickness=0)
        txt.insert("1.0", msg)
        txt.config(state="disabled")
        txt.pack(padx=20, pady=(0, 12), fill="both", expand=True)

        tk.Button(win, text="Close",
                  font=("Segoe UI", 10, "bold"),
                  bg=C_BLUE, fg=FG_WHITE, padx=24, pady=6,
                  relief="flat", cursor="hand2",
                  command=win.destroy
                  ).pack(pady=(0, 16))

    def _render_load_error(self):
        self._scan_btn.config(state="disabled", bg=C_GREY, cursor="arrow")
        self._summary_lbl.config(text="Conductor module not loaded", fg=C_RED)
        tk.Label(self._inner,
                 text=("problems/conductor.py failed to import. "
                       "The rest of the app still works — only this tab is disabled.\n\n"
                       f"Error: {_CONDUCTOR_ERR}"),
                 font=("Segoe UI", 10),
                 bg=BG_WIN, fg=FG_DIM,
                 wraplength=520, justify="left",
                 padx=20, pady=20
                 ).pack(fill="x")


class SpinDoctorApp:
    def __init__(self, root):
        self.root = root
        root.title("VKB Spin Doctor")
        root.configure(bg=BG_WIN)
        root.resizable(False, False)
        self._build()

    def _build(self):
        # ── Header ──
        hdr = tk.Frame(self.root, bg=BG_WIN, pady=16)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="VKB Spin Doctor",
                 font=("Segoe UI", 20, "bold"), bg=BG_WIN, fg=FG_WHITE
                 ).pack(side="left")
        tk.Label(hdr, text="  v1.0  —  fixes mouse-axis spin for joystick users",
                 font=("Segoe UI", 9), bg=BG_WIN, fg=FG_DIM
                 ).pack(side="left")

        # ── Tab bar ──
        tab_bar = tk.Frame(self.root, bg=BG_WIN)
        tab_bar.pack(fill="x", padx=20)

        self._tab_fix_btn = tk.Button(
            tab_bar, text="Fix Mouse Spin",
            font=("Segoe UI", 10, "bold"),
            bg=BG_CARD, fg=FG_WHITE,
            padx=16, pady=6, relief="flat", cursor="hand2",
            command=lambda: self._show_tab("fix"))
        self._tab_fix_btn.pack(side="left")

        self._tab_conductor_btn = tk.Button(
            tab_bar, text="Process Conductor",
            font=("Segoe UI", 10),
            bg=BG_WIN, fg=FG_DIM,
            padx=16, pady=6, relief="flat", cursor="hand2",
            command=lambda: self._show_tab("conductor"))
        self._tab_conductor_btn.pack(side="left")

        self._tab_kb_btn = tk.Button(
            tab_bar, text="Knowledge Base",
            font=("Segoe UI", 10),
            bg=BG_WIN, fg=FG_DIM,
            padx=16, pady=6, relief="flat", cursor="hand2",
            command=lambda: self._show_tab("kb"))
        self._tab_kb_btn.pack(side="left")

        tk.Frame(self.root, bg=C_DIV, height=1).pack(fill="x", padx=20, pady=(4, 0))

        # ── Fix tab content ──
        self._fix_frame = tk.Frame(self.root, bg=BG_WIN)

        GameCard(self._fix_frame,
                 game_name="War Thunder",
                 finder_fn=find_warthunder_machine_blk,
                 status_fn=check_warthunder_status,
                 fix_fn=fix_warthunder,
                 greyed=False,
                 ).pack(fill="x", pady=(0, 6))

        tk.Frame(self._fix_frame, bg=C_DIV, height=1).pack(fill="x", pady=2)

        GameCard(self._fix_frame,
                 game_name="Elite Dangerous",
                 finder_fn=find_elite_binds,
                 status_fn=check_elite_status,
                 fix_fn=fix_elite,
                 greyed=False,
                 ).pack(fill="x", pady=(2, 2))

        # Module 07 — ED Bind Reset Prevention. Sits visually under the ED card.
        EDBindResetCard(self._fix_frame).pack(fill="x", pady=(0, 6))

        tk.Frame(self._fix_frame, bg=C_DIV, height=1).pack(fill="x", pady=2)

        GameCard(self._fix_frame,
                 game_name="Star Citizen",
                 finder_fn=find_starcitizen_xml,
                 status_fn=check_not_implemented,
                 fix_fn=lambda f: (False, "Not yet implemented."),
                 greyed=True,
                 ).pack(fill="x", pady=(2, 0))

        # ── Process Conductor tab content (Module 02) ──
        self._conductor_frame = ProcessConductorTab(self.root)

        # ── Knowledge Base tab content ──
        self._kb_frame = KnowledgeBaseTab(self.root)

        self._tabs = {
            "fix":       (self._tab_fix_btn,       self._fix_frame),
            "conductor": (self._tab_conductor_btn, self._conductor_frame),
            "kb":        (self._tab_kb_btn,        self._kb_frame),
        }

        # Start on fix tab
        self._show_tab("fix")

    def _show_tab(self, active):
        for name, (btn, frame) in self._tabs.items():
            if name == active:
                frame.pack(fill="both", padx=20, pady=(8, 20))
                btn.config(bg=BG_CARD, fg=FG_WHITE, font=("Segoe UI", 10, "bold"))
            else:
                frame.pack_forget()
                btn.config(bg=BG_WIN, fg=FG_DIM, font=("Segoe UI", 10))


def main():
    root = tk.Tk()
    SpinDoctorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
