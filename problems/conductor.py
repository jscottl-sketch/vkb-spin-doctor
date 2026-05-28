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

import json
import subprocess
from pathlib import Path

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


# ── Group A/B — Companion + input mapper checks (data now in conductor_problems.json)
# _make_companion_check is still used by _build_problems() below.

# ── P-014  Steam.exe running (Steam Input overlay) ────────────────────────────
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


# ── Group C/D — Overlay + launch order (data now in conductor_problems.json)
# Special function implementations are below.

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
# Problem DEFINITIONS live in conductor_problems.json (same directory).
# This function loads them at import time and wires up detect/fix callables.

def _build_problems():
    data_file = Path(__file__).parent / "conductor_problems.json"
    with open(data_file, encoding="utf-8") as f:
        definitions = json.load(f)

    _special = {
        "P-014": (detect_p014, fix_p014),
        "P-020": (detect_p020, fix_p020),
        "P-021": (detect_p021, fix_p021),
        "P-022": (detect_p022, fix_p022),
    }

    problems = []
    for defn in definitions:
        if defn["type"] == "companion":
            detect, fix = _make_companion_check(
                defn["label"], defn["executables"], defn["reason"]
            )
        else:
            detect, fix = _special[defn["id"]]
        problems.append({
            "id":       defn["id"],
            "category": defn["category"],
            "title":    defn["title"],
            "detect":   detect,
            "fix":      fix,
        })
    return problems


PROBLEMS = _build_problems()


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
