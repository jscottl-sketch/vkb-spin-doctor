"""
problems/conductor.py  —  Module 02: Process Conductor
======================================================
Part of VKB Spin Doctor (Universal Input Device Assistant).

WHAT THIS MODULE DOES
---------------------
Detects process-level conflicts that break input devices on Windows
and recommends manual fixes. Covers 22 problems (P-001 -> P-022) drawn
from the Universal Input Device Database.

Three families of problem:
  - Companion software clashes  (G HUB vs Synapse vs iCUE — Fix Chain 3)
  - Multiple input-mapper apps running at once
  - Background overlays adding input lag

CRITICAL SAFETY RULE — READ BEFORE EDITING
------------------------------------------
This module **NEVER** kills, suspends, or terminates a running process.
It only DETECTS what is running and RECOMMENDS what the user should
close. The user does the closing.

Reason: closing a user's RGB software mid-game could break their
lighting profile, killing Discord could drop them from a call,
ending a streaming overlay could ruin a recording. The cost of a
wrong auto-kill is much higher than a polite "please close X".
Always warn, never act.

API CONTRACT (matches spin_doctor.py style)
-------------------------------------------
Every problem exposes two functions:
  detect()  -> str
      One of: "ok", "warn", "info", "not_installed".
      "warn" means an active conflict was found.
      "info" means advisory (no live detection possible).
  fix()     -> (bool, str)
      First element: True  = a recommendation applies (user should act).
                     False = no action needed (process not running etc.).
      Second element: human-readable recommendation text.
      fix() is read-only. It does not modify the system.

Iterate the PROBLEMS list at the bottom of the file to drive a
Knowledge-Base-tab style GUI or the microkernel engine's scanner.

Call refresh() between scans — it clears the cached tasklist snapshot
so the next detect() reads a fresh process list.
"""

import subprocess

CREATE_NO_WINDOW = 0x08000000  # subprocess flag — suppress console flash on Windows


# ── Process / service detection (cached per refresh) ──────────────────────────

_PROC_CACHE = None
_SERVICE_CACHE = {}


def refresh():
    """Clear cached process and service state. Call before re-running detect()."""
    global _PROC_CACHE, _SERVICE_CACHE
    _PROC_CACHE = None
    _SERVICE_CACHE = {}


def _running_processes():
    """Snapshot of lowercase process names from `tasklist`. Cached."""
    global _PROC_CACHE
    if _PROC_CACHE is not None:
        return _PROC_CACHE
    try:
        out = subprocess.check_output(
            ["tasklist.exe", "/fo", "csv", "/nh"],
            text=True, errors="replace",
            creationflags=CREATE_NO_WINDOW,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        _PROC_CACHE = set()
        return _PROC_CACHE

    names = set()
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith('"'):
            continue
        name = line.split('","', 1)[0].strip('"').lower()
        if name:
            names.add(name)
    _PROC_CACHE = names
    return names


def _which_running(*candidates):
    """Return the subset of `candidates` (lowercased) that are running."""
    procs = _running_processes()
    return [c for c in candidates if c.lower() in procs]


def _service_state(service_name):
    """Return 'running', 'stopped', or 'missing' for a Windows service. Cached."""
    if service_name in _SERVICE_CACHE:
        return _SERVICE_CACHE[service_name]
    try:
        out = subprocess.check_output(
            ["sc.exe", "query", service_name],
            text=True, errors="replace",
            creationflags=CREATE_NO_WINDOW,
        )
        state = "running" if "RUNNING" in out else "stopped"
    except subprocess.CalledProcessError:
        state = "missing"
    except (FileNotFoundError, OSError):
        state = "missing"
    _SERVICE_CACHE[service_name] = state
    return state


# ── Companion-software template ──────────────────────────────────────────────
# Most of the 22 problems share the same shape: "if X.exe is running,
# recommend closing it because it clashes with non-X input devices".
# This factory builds the detect() / fix() pair for that shape.

def _make_companion_check(label, executables, reason):
    """Return (detect_fn, fix_fn) closures for a 'please-close-this' problem."""

    def detect():
        return "warn" if _which_running(*executables) else "ok"

    def fix():
        found = _which_running(*executables)
        if not found:
            return False, f"{label} is not running — no action needed."
        proc_list = ", ".join(found)
        return True, (
            f"{label} is running ({proc_list}).\n\n"
            f"Why this matters: {reason}\n\n"
            f"How to close it safely:\n"
            f"  1. Look at the system tray (bottom-right of the taskbar). "
            f"Click the small ^ arrow if you don't see it.\n"
            f"  2. Right-click the {label} icon.\n"
            f"  3. Choose Quit / Exit / Close.\n"
            f"  4. Re-launch your game.\n\n"
            f"Avoid: Task Manager -> End Task on background services. "
            f"Some companion apps relaunch themselves automatically."
        )

    return detect, fix


# ── Group A — Companion software (Fix Chain 3) ───────────────────────────────

# P-001  Logitech G HUB
detect_p001, fix_p001 = _make_companion_check(
    label="Logitech G HUB",
    executables=("lghub.exe", "lghub_agent.exe", "lghub_updater.exe"),
    reason=(
        "G HUB can intercept input from non-Logitech devices and is known "
        "to add up to 1 second of input lag on the first key press of a "
        "session. If your stick or wheel feels sluggish, this is the most "
        "common cause."
    ),
)

# P-002  Logitech Gaming Software (legacy LGS)
detect_p002, fix_p002 = _make_companion_check(
    label="Logitech Gaming Software (LGS, legacy)",
    executables=("lcore.exe", "logitechgaminglogiledcore.exe", "lcorewine.exe"),
    reason=(
        "LGS is the older Logitech driver. Running it alongside G HUB or "
        "with non-Logitech input devices causes input conflicts and bind "
        "loss. If you also have G HUB installed, uninstall LGS entirely."
    ),
)

# P-003  Razer Synapse
detect_p003, fix_p003 = _make_companion_check(
    label="Razer Synapse",
    executables=("razer synapse.exe", "razer synapse 3.exe", "razersynapse.exe",
                 "razer central.exe"),
    reason=(
        "Synapse hooks every USB HID device, not just Razer ones. It is a "
        "frequent cause of joystick remap failure, double-input bugs, and "
        "delayed first key press in flight sims."
    ),
)

# P-004  Corsair iCUE
detect_p004, fix_p004 = _make_companion_check(
    label="Corsair iCUE",
    executables=("icue.exe", "icueservice.exe", "icuelaunch.exe"),
    reason=(
        "iCUE's input layer can fight with non-Corsair joysticks and wheels, "
        "and is a known source of phantom button presses and stuck axes."
    ),
)

# P-005  SteelSeries GG / Engine
detect_p005, fix_p005 = _make_companion_check(
    label="SteelSeries GG / Engine",
    executables=("steelseriesgg.exe", "steelseriesengine3.exe",
                 "ssengineservice.exe"),
    reason=(
        "SteelSeries GG enumerates all HID devices and can disrupt third-"
        "party joystick/wheel input even when no SteelSeries hardware is in "
        "use."
    ),
)

# P-006  ASUS Armoury Crate
detect_p006, fix_p006 = _make_companion_check(
    label="ASUS Armoury Crate",
    executables=("armourycrate.exe", "armourycrate.service.exe",
                 "armourycrate.usersessionhelper.exe", "asusoptimization.exe"),
    reason=(
        "Armoury Crate has a well-documented reputation for adding system-"
        "wide input lag and interfering with USB enumeration. If your stick "
        "is detected intermittently this is the first suspect."
    ),
)

# P-007  MSI Center / Dragon Center
detect_p007, fix_p007 = _make_companion_check(
    label="MSI Center / Dragon Center",
    executables=("msi.centralserver.exe", "msi_center.exe", "dragoncenter.exe"),
    reason=(
        "MSI's RGB and fan-control layer hooks into USB power management. "
        "Reports of joysticks losing power and being re-enumerated mid-game "
        "trace back to this."
    ),
)

# P-008  Thrustmaster TARGET
detect_p008, fix_p008 = _make_companion_check(
    label="Thrustmaster TARGET (T.A.R.G.E.T.)",
    executables=("targetgui.exe", "target.exe", "t.a.r.g.e.t. gui.exe"),
    reason=(
        "TARGET creates a virtual joystick that replaces your real one. If "
        "you're using a VKB or non-Thrustmaster stick and TARGET is running, "
        "the game will see TARGET's virtual device instead of your real "
        "stick."
    ),
)

# P-009  VKB DevCfg open during a game session
detect_p009, fix_p009 = _make_companion_check(
    label="VKB DevCfg",
    executables=("vkbdevcfg.exe", "vkbdevcfg-c.exe"),
    reason=(
        "Leaving VKB DevCfg open while playing can intercept the HID stream "
        "from your VKB stick. Use DevCfg to configure, then CLOSE it before "
        "launching the game."
    ),
)


# ── Group B — Input mapper conflicts ─────────────────────────────────────────

# P-010  DS4Windows (PlayStation controller mapper)
detect_p010, fix_p010 = _make_companion_check(
    label="DS4Windows",
    executables=("ds4windows.exe",),
    reason=(
        "DS4Windows is needed to use a DualShock 4 / DualSense as a real "
        "joystick — but if Steam Input is ALSO enabled, both will inject "
        "input and the controller will fight itself. Pick one: DS4Windows "
        "OR Steam Input, not both."
    ),
)

# P-011  Xpadder / JoyToKey
detect_p011, fix_p011 = _make_companion_check(
    label="Xpadder / JoyToKey",
    executables=("xpadder.exe", "joytokey.exe"),
    reason=(
        "These tools translate joystick movements into keyboard / mouse "
        "events. If a game already supports your stick natively, running "
        "these on top creates double inputs and phantom keystrokes."
    ),
)

# P-012  Joystick Gremlin / vJoy
detect_p012, fix_p012 = _make_companion_check(
    label="Joystick Gremlin / vJoy feeder",
    executables=("joystick_gremlin.exe", "vjoyconf.exe", "vjoymonitor.exe"),
    reason=(
        "Joystick Gremlin and vJoy are power-user remappers that publish a "
        "virtual joystick. Make sure the game is reading from the VIRTUAL "
        "stick, not your physical one — otherwise you'll get double inputs "
        "across both devices."
    ),
)

# P-013  X360CE (Xbox 360 controller emulator)
detect_p013, fix_p013 = _make_companion_check(
    label="X360CE",
    executables=("x360ce.exe", "x360ce_x64.exe"),
    reason=(
        "X360CE makes any input device look like an Xbox 360 pad. If left "
        "running globally it will hijack your joystick / wheel in games "
        "that expect a native flight-stick. Only run X360CE per-game."
    ),
)

# P-014  Steam.exe running (Steam Input overlay)
def detect_p014():
    return "warn" if _which_running("steam.exe") else "ok"

def fix_p014():
    if not _which_running("steam.exe"):
        return False, "Steam is not running — no action needed."
    return True, (
        "Steam is running. Module 03 (steam_input_conflict) handles the "
        "per-game Steam Input setting, but Steam itself can still intercept "
        "controller input through its overlay even for non-Steam games.\n\n"
        "If you launch your game OUTSIDE Steam and it still misbehaves:\n"
        "  1. Open Steam.\n"
        "  2. Settings -> In Game -> turn OFF Enable the Steam Overlay "
        "while in-game.\n"
        "  3. Settings -> Controller -> uncheck every Generic / PlayStation / "
        "Xbox / Switch Configuration Support box.\n"
        "  4. Restart Steam.\n\n"
        "Or close Steam entirely before launching your non-Steam game."
    )


# ── Group C — Overlay processes (input lag) ──────────────────────────────────

# P-015  NVIDIA GeForce Experience overlay
detect_p015, fix_p015 = _make_companion_check(
    label="NVIDIA GeForce Experience overlay",
    executables=("nvidia geforce experience.exe", "nvidia share.exe",
                 "nvcontainer.exe"),
    reason=(
        "The in-game overlay adds polling overhead that shows up as "
        "occasional input stutter on high-rate joysticks (1000 Hz). The "
        "driver itself is fine — only the overlay needs disabling."
    ),
)

# P-016  AMD Adrenalin overlay
detect_p016, fix_p016 = _make_companion_check(
    label="AMD Adrenalin overlay",
    executables=("radeonsoftware.exe", "amdrsserv.exe", "amdrsserv64.exe"),
    reason=(
        "Adrenalin's overlay (Alt+R) and instant-replay layer can add "
        "input lag, particularly on flight sims at high polling rates. "
        "Disable the overlay; keep the driver."
    ),
)

# P-017  Discord overlay
detect_p017, fix_p017 = _make_companion_check(
    label="Discord (with overlay)",
    executables=("discord.exe",),
    reason=(
        "Discord's in-game overlay hooks DirectInput and is a recurring "
        "cause of joystick stutter and dropped inputs. Discord itself is "
        "safe — only the overlay needs turning off."
    ),
)

# P-018  OBS Studio / Streamlabs
detect_p018, fix_p018 = _make_companion_check(
    label="OBS Studio / Streamlabs",
    executables=("obs64.exe", "obs32.exe", "streamlabs obs.exe",
                 "streamlabs desktop.exe"),
    reason=(
        "Game-capture sources hook the rendering pipeline and can add a "
        "frame or two of input lag. Acceptable when streaming — but if you "
        "left OBS running by accident, close it."
    ),
)

# P-019  Xbox Game Bar
detect_p019, fix_p019 = _make_companion_check(
    label="Xbox Game Bar",
    executables=("gamebar.exe", "gamebarftserver.exe", "gamebarpresencewriter.exe"),
    reason=(
        "Game Bar hooks every running game window and captures gamepad "
        "input by default. Press Windows key + G to confirm it's open, "
        "then disable: Settings -> Gaming -> Game Bar -> Off."
    ),
)


# ── Group D — Launch order & services ────────────────────────────────────────

# P-020  Game launched before device plugged in (advisory)
_KNOWN_GAMES = (
    "aces.exe",            # War Thunder
    "warthunder.exe",
    "elitedangerous64.exe",
    "elitedangerous32.exe",
    "starcitizen.exe",
    "rsilauncher.exe",
    "dcs.exe",
    "fs2020.exe", "flightsimulator.exe", "flightsimulator2024.exe",
    "il-2.exe", "il2.exe",
    "ac7.exe", "acecombat7.exe",
)

def detect_p020():
    """Advisory: a known flight/space game is running right now."""
    return "info" if _which_running(*_KNOWN_GAMES) else "ok"

def fix_p020():
    found = _which_running(*_KNOWN_GAMES)
    msg = (
        "Launch-order rule:\n"
        "  1. Plug ALL your input devices in first (stick, throttle, pedals).\n"
        "  2. Wait a few seconds for Windows to enumerate them.\n"
        "  3. Open joy.cpl (Windows key + R, type joy.cpl, Enter) and "
        "confirm every device is listed.\n"
        "  4. THEN launch the game.\n\n"
        "Why: most flight and space games scan for input devices once at "
        "startup. Anything plugged in afterwards will not register, even "
        "if Windows sees it perfectly.\n\n"
        "Also: some games (Elite Dangerous, Star Citizen) refuse to load a "
        "binding profile unless EVERY device referenced in that profile is "
        "currently connected."
    )
    if found:
        msg = f"Detected running game: {', '.join(found)}.\n\n" + msg
    return True, msg


# P-021  HidHide installed but Cloak service not running
def detect_p021():
    state = _service_state("HidHide")
    if state == "missing":
        return "not_installed"
    if state == "stopped":
        return "warn"
    return "ok"

def fix_p021():
    state = _service_state("HidHide")
    if state == "missing":
        return False, (
            "HidHide is not installed. This is fine — only install it if "
            "you have a specific double-input problem (PS5 controller seen "
            "alongside your joystick, for example).\n\n"
            "Project: github.com/ViGEm/HidHide"
        )
    if state == "running":
        return False, "HidHide service is running — no action needed."
    return True, (
        "HidHide is installed but the Cloak service is stopped. While it's "
        "stopped, hidden devices will reappear to every game and the U-003 "
        "double-input problem will come back.\n\n"
        "How to start it:\n"
        "  1. Press Windows key + R, type services.msc, press Enter.\n"
        "  2. Scroll to HidHide Service.\n"
        "  3. Right-click -> Start.\n"
        "  4. Right-click -> Properties -> set Startup type to Automatic so "
        "it survives a reboot.\n\n"
        "If the service won't start, reinstall HidHide from "
        "github.com/ViGEm/HidHide and reboot."
    )


# P-022  Multiple companion software running together (compounded conflict)
_COMPANION_GROUPS = {
    "Logitech G HUB":   ("lghub.exe", "lghub_agent.exe"),
    "Logitech LGS":     ("lcore.exe",),
    "Razer Synapse":    ("razer synapse.exe", "razer synapse 3.exe",
                         "razersynapse.exe"),
    "Corsair iCUE":     ("icue.exe",),
    "SteelSeries GG":   ("steelseriesgg.exe", "steelseriesengine3.exe"),
    "Armoury Crate":    ("armourycrate.exe",),
    "MSI Center":       ("msi_center.exe", "dragoncenter.exe"),
    "Thrustmaster TARGET": ("targetgui.exe", "target.exe"),
}

def _running_companions():
    return [name for name, exes in _COMPANION_GROUPS.items()
            if _which_running(*exes)]

def detect_p022():
    return "warn" if len(_running_companions()) >= 2 else "ok"

def fix_p022():
    running = _running_companions()
    if len(running) < 2:
        return False, (
            "Only one companion app (or none) is running — no compounded "
            "conflict."
        )
    listed = "\n".join(f"  - {name}" for name in running)
    return True, (
        f"Multiple companion apps are running at the same time:\n{listed}\n\n"
        f"When two or more of these run together, each one hooks every USB "
        f"HID device and they fight each other for control. Input lag, "
        f"phantom presses, and intermittent device loss become near-certain.\n\n"
        f"Recommended:\n"
        f"  1. Close every one of them via the system tray.\n"
        f"  2. Decide which ONE you actually need (the one matching the "
        f"hardware you're using right now).\n"
        f"  3. Re-open only that one.\n"
        f"  4. Launch your game.\n\n"
        f"Long term: uninstall the companion apps for hardware you no "
        f"longer own. The driver stays out of habit; uninstall is safe."
    )


# ── PROBLEM REGISTRY ─────────────────────────────────────────────────────────
# Engine and GUI iterate this list. Drop-in: no registration call needed
# beyond appending here.

PROBLEMS = [
    # Group A — Companion software (Fix Chain 3)
    {"id": "P-001", "category": "companion_software",
     "title": "Logitech G HUB running",
     "detect": detect_p001, "fix": fix_p001},
    {"id": "P-002", "category": "companion_software",
     "title": "Logitech Gaming Software (legacy LGS) running",
     "detect": detect_p002, "fix": fix_p002},
    {"id": "P-003", "category": "companion_software",
     "title": "Razer Synapse running",
     "detect": detect_p003, "fix": fix_p003},
    {"id": "P-004", "category": "companion_software",
     "title": "Corsair iCUE running",
     "detect": detect_p004, "fix": fix_p004},
    {"id": "P-005", "category": "companion_software",
     "title": "SteelSeries GG / Engine running",
     "detect": detect_p005, "fix": fix_p005},
    {"id": "P-006", "category": "companion_software",
     "title": "ASUS Armoury Crate running",
     "detect": detect_p006, "fix": fix_p006},
    {"id": "P-007", "category": "companion_software",
     "title": "MSI Center / Dragon Center running",
     "detect": detect_p007, "fix": fix_p007},
    {"id": "P-008", "category": "companion_software",
     "title": "Thrustmaster TARGET running",
     "detect": detect_p008, "fix": fix_p008},
    {"id": "P-009", "category": "companion_software",
     "title": "VKB DevCfg open during game session",
     "detect": detect_p009, "fix": fix_p009},

    # Group B — Input mapper conflicts
    {"id": "P-010", "category": "input_mapper",
     "title": "DS4Windows running",
     "detect": detect_p010, "fix": fix_p010},
    {"id": "P-011", "category": "input_mapper",
     "title": "Xpadder / JoyToKey running",
     "detect": detect_p011, "fix": fix_p011},
    {"id": "P-012", "category": "input_mapper",
     "title": "Joystick Gremlin / vJoy running",
     "detect": detect_p012, "fix": fix_p012},
    {"id": "P-013", "category": "input_mapper",
     "title": "X360CE running",
     "detect": detect_p013, "fix": fix_p013},
    {"id": "P-014", "category": "input_mapper",
     "title": "Steam overlay intercepting input",
     "detect": detect_p014, "fix": fix_p014},

    # Group C — Overlay processes (input lag)
    {"id": "P-015", "category": "overlay",
     "title": "NVIDIA GeForce Experience overlay running",
     "detect": detect_p015, "fix": fix_p015},
    {"id": "P-016", "category": "overlay",
     "title": "AMD Adrenalin overlay running",
     "detect": detect_p016, "fix": fix_p016},
    {"id": "P-017", "category": "overlay",
     "title": "Discord overlay running",
     "detect": detect_p017, "fix": fix_p017},
    {"id": "P-018", "category": "overlay",
     "title": "OBS Studio / Streamlabs running",
     "detect": detect_p018, "fix": fix_p018},
    {"id": "P-019", "category": "overlay",
     "title": "Xbox Game Bar running",
     "detect": detect_p019, "fix": fix_p019},

    # Group D — Launch order & services
    {"id": "P-020", "category": "launch_order",
     "title": "Launch order — plug devices in before launching",
     "detect": detect_p020, "fix": fix_p020},
    {"id": "P-021", "category": "service",
     "title": "HidHide Cloak service stopped",
     "detect": detect_p021, "fix": fix_p021},
    {"id": "P-022", "category": "compounded",
     "title": "Multiple companion apps running together",
     "detect": detect_p022, "fix": fix_p022},
]


# ── Convenience: scan all and print a report ─────────────────────────────────
# Run directly:  python conductor.py
# Useful for sanity-checking the module before wiring it into the GUI.

def scan_all():
    """Return a list of (problem_dict, status) tuples. Triggers a refresh first."""
    refresh()
    return [(p, p["detect"]()) for p in PROBLEMS]


def _print_report():
    results = scan_all()
    warns = [p for p, s in results if s == "warn"]
    print(f"\nProcess Conductor — scanned {len(results)} problems\n" + "=" * 60)
    for p, status in results:
        marker = {"ok": "[ ok ]", "warn": "[WARN]",
                  "info": "[info]", "not_installed": "[ -- ]"}.get(status, status)
        print(f"  {marker}  {p['id']}  {p['title']}")
    print("=" * 60)
    if not warns:
        print("No active process conflicts detected.\n")
        return
    print(f"\n{len(warns)} recommendation(s):\n")
    for p in warns:
        ok, msg = p["fix"]()
        print(f"--- {p['id']}  {p['title']} ---")
        print(msg)
        print()


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp1252 crashes on Win consoles
    except Exception:
        pass
    _print_report()
