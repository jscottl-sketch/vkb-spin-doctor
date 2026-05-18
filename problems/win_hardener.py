"""
problems/win_hardener.py  —  Module 08: Windows Hardware Hardener
=================================================================
Part of VKB Spin Doctor (Universal Input Device Assistant).

WHAT THIS MODULE DOES
---------------------
Detects Windows-level USB, HID, and registry configuration problems
that cause joystick axis spin, device enumeration failure, polling
rate issues, and GameInput conflicts. Covers 9 problems (W-001 → W-009).

CRITICAL SAFETY RULE
---------------------
This module is READ-ONLY. It detects problems and recommends fixes.
It does NOT modify the registry, stop services, or change system config.
Every fix() returns instructions for the user to follow manually.

API CONTRACT (matches conductor.py pattern)
-------------------------------------------
detect()  -> "ok" | "warn" | "info" | "not_installed"
fix()     -> (bool, str)  — (True=action recommended, message)
PROBLEMS  — list of dicts; engine and GUI iterate this.
scan_all() -> list[(problem_dict, status_str)]
refresh()  -> clear cached state (call before re-scanning)
"""

import os
import re
import subprocess
import winreg

CREATE_NO_WINDOW = 0x08000000


# ── Cached state ──────────────────────────────────────────────────────────────

_PROC_CACHE = None


def refresh():
    """Clear cached process snapshot. Call before re-running detect()."""
    global _PROC_CACHE
    _PROC_CACHE = None


def _running_processes():
    global _PROC_CACHE
    if _PROC_CACHE is not None:
        return _PROC_CACHE
    try:
        out = subprocess.check_output(
            ["tasklist.exe", "/fo", "csv", "/nh"],
            text=True, errors="replace",
            creationflags=CREATE_NO_WINDOW,
        )
        names = set()
        for line in out.splitlines():
            if line.startswith('"'):
                name = line.split('","', 1)[0].strip('"').lower()
                if name:
                    names.add(name)
        _PROC_CACHE = names
    except Exception:
        _PROC_CACHE = set()
    return _PROC_CACHE


def _reg_read(hive, path, value_name):
    """Read a registry DWORD/string value. Returns (value, type) or raises."""
    k = winreg.OpenKey(hive, path)
    try:
        return winreg.QueryValueEx(k, value_name)
    finally:
        winreg.CloseKey(k)


# ── W-001: USB Selective Suspend ──────────────────────────────────────────────

def _usb_selective_suspend_on() -> bool:
    """Return True if USB selective suspend is active in the current power plan."""
    SUB_USB     = "2a737441-1930-4402-8d77-b2bebba308a3"
    SETTING_USS = "48e6b7a6-50f5-4782-a5d4-53bb8f07e226"
    try:
        out = subprocess.check_output(
            ["powercfg", "/query", "SCHEME_CURRENT", SUB_USB, SETTING_USS],
            text=True, errors="replace",
            creationflags=CREATE_NO_WINDOW,
        )
        for line in out.splitlines():
            if "Current AC Power Setting Index:" in line:
                return "0x00000001" in line
    except Exception:
        pass
    return False


def detect_w001():
    return "warn" if _usb_selective_suspend_on() else "ok"


def fix_w001():
    if not _usb_selective_suspend_on():
        return False, "USB Selective Suspend is already disabled — no action needed."
    return True, (
        "USB Selective Suspend is ENABLED in your active power plan.\n\n"
        "This lets Windows cut USB power to joysticks to save energy. "
        "When it triggers mid-session the device disconnects and reconnects, "
        "resetting all axes and losing bindings.\n\n"
        "Method A — per-device (Device Manager):\n"
        "  1. Right-click Start → Device Manager.\n"
        "  2. Expand Universal Serial Bus controllers.\n"
        "  3. Right-click each USB Root Hub → Properties → Power Management.\n"
        "  4. Uncheck 'Allow the computer to turn off this device to save power'.\n"
        "  5. Repeat for every Root Hub and USB hub entry.\n\n"
        "Method B — global (Power Plan):\n"
        "  1. Control Panel → Power Options → Change plan settings\n"
        "     → Change advanced power settings.\n"
        "  2. USB settings → USB selective suspend setting → Disabled.\n"
        "  3. Apply.\n\n"
        "Reboot to confirm."
    )


# ── W-002: Polling Rate (advisory) ───────────────────────────────────────────

def detect_w002():
    return "info"


def fix_w002():
    return True, (
        "Polling rate advisory — VKB NXT EVO defaults to 125 Hz (8 ms latency).\n\n"
        "At 1000 Hz inputs are 8× more responsive. For fast manoeuvres in DCS, "
        "War Thunder, or Star Citizen, 1000 Hz is strongly recommended.\n\n"
        "How to check and change:\n"
        "  1. Close your game and all game launchers.\n"
        "  2. Open VKB DevCfg (the blue VKB configuration app).\n"
        "  3. Connect your stick — it appears in the device list.\n"
        "  4. Navigate to Advanced → Polling rate (or HID report rate).\n"
        "  5. Set to 1000 Hz (or the highest option available).\n"
        "  6. Save → disconnect and reconnect the stick.\n\n"
        "Important: some USB hubs cap devices at 125 Hz regardless of firmware. "
        "Plug directly into a rear motherboard USB 2.0 port for full 1000 Hz."
    )


# ── W-003: joy.cpl Calibration ────────────────────────────────────────────────

def _joycpl_exists() -> bool:
    sysroot = os.environ.get("SystemRoot", r"C:\Windows")
    return os.path.exists(os.path.join(sysroot, "System32", "joy.cpl"))


def detect_w003():
    return "warn" if not _joycpl_exists() else "info"


def fix_w003():
    if not _joycpl_exists():
        return True, (
            "joy.cpl is MISSING from System32. This file should always be present.\n\n"
            "Recovery:\n"
            "  1. Open an elevated command prompt (Run as Administrator).\n"
            "  2. Run: sfc /scannow\n"
            "     This scans and restores missing system files.\n"
            "  3. Reboot. If still missing:\n"
            "     DISM /Online /Cleanup-Image /RestoreHealth\n"
            "     Then: sfc /scannow again."
        )
    return True, (
        "Verify and fix joystick calibration via joy.cpl:\n"
        "  1. Press Windows key + R, type joy.cpl, press Enter.\n"
        "  2. Select your joystick → Properties → Settings → Calibrate.\n"
        "  3. Follow on-screen steps. Centre the stick when asked.\n\n"
        "If joystick does NOT appear in the list:\n"
        "  - Unplug and replug it.\n"
        "  - Try a different USB port.\n"
        "  - Check Device Manager for yellow ! on the HID device.\n\n"
        "If calibration data is corrupted (axis stuck at max):\n"
        "  - joy.cpl → Properties → Settings → Reset to Defaults.\n"
        "  - If that fails, open regedit and delete the device's subkey under:\n"
        "    HKCU\\System\\CurrentControlSet\\Control\\MediaResources\\joystick\n"
        "  - Unplug, replug, recalibrate."
    )


# ── W-004: HID Device Error Code ─────────────────────────────────────────────

def _hid_error_devices() -> list:
    """Return friendly names of HID devices that have a Windows error config flag."""
    errors = []
    try:
        hid_base = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Enum\HID",
        )
    except FileNotFoundError:
        return errors
    try:
        i = 0
        while True:
            try:
                dev_class = winreg.EnumKey(hid_base, i)
            except OSError:
                break
            i += 1
            try:
                class_key = winreg.OpenKey(hid_base, dev_class)
                j = 0
                while True:
                    try:
                        instance = winreg.EnumKey(class_key, j)
                    except OSError:
                        break
                    j += 1
                    try:
                        inst_key = winreg.OpenKey(class_key, instance)
                        try:
                            flags, _ = winreg.QueryValueEx(inst_key, "ConfigFlags")
                            if flags & 0x0400:
                                try:
                                    desc, _ = winreg.QueryValueEx(inst_key, "FriendlyName")
                                except Exception:
                                    try:
                                        desc, _ = winreg.QueryValueEx(inst_key, "DeviceDesc")
                                    except Exception:
                                        desc = f"HID\\{dev_class}"
                                errors.append(str(desc).split(";")[-1].strip())
                        except Exception:
                            pass
                        winreg.CloseKey(inst_key)
                    except Exception:
                        pass
                winreg.CloseKey(class_key)
            except Exception:
                pass
    finally:
        winreg.CloseKey(hid_base)
    return errors


def detect_w004():
    return "warn" if _hid_error_devices() else "ok"


def fix_w004():
    devices = _hid_error_devices()
    if not devices:
        return False, "No HID devices with error codes — all enumerated cleanly."
    listed = "\n".join(f"  - {d}" for d in devices)
    return True, (
        f"HID devices with Windows error codes (failed to enumerate):\n{listed}\n\n"
        "Windows recognised the device but the driver failed to install. "
        "The game will not see the device until this is resolved.\n\n"
        "How to fix:\n"
        "  1. Right-click Start → Device Manager.\n"
        "  2. Find the device under Human Interface Devices (yellow ! icon).\n"
        "  3. Right-click → Update driver → Search automatically.\n"
        "  4. If that fails: Uninstall device → tick 'Delete driver software'\n"
        "     → unplug → replug.\n"
        "  5. Still failing: try a different USB port, or reinstall VKB "
        "firmware via VKB DevCfg."
    )


# ── W-005: Registry Cleaner Damage ───────────────────────────────────────────

_REG_HEALTH_CHECKS = [
    (winreg.HKEY_LOCAL_MACHINE,
     r"SYSTEM\CurrentControlSet\Services\HidUsb",
     "HidUsb driver service"),
    (winreg.HKEY_LOCAL_MACHINE,
     r"SYSTEM\CurrentControlSet\Services\hid",
     "HID class driver (hid)"),
    (winreg.HKEY_LOCAL_MACHINE,
     r"SYSTEM\CurrentControlSet\Control\Class\{4d36e96c-e325-11ce-bfc1-08002be10318}",
     "Multimedia device class registration"),
    (winreg.HKEY_LOCAL_MACHINE,
     r"SYSTEM\CurrentControlSet\Control\Class\{745a17a0-74d3-11d0-b6fe-00a0c90f57da}",
     "HID device class registration"),
]


def _damaged_reg_keys() -> list:
    damaged = []
    for hive, path, label in _REG_HEALTH_CHECKS:
        try:
            k = winreg.OpenKey(hive, path)
            winreg.CloseKey(k)
        except FileNotFoundError:
            damaged.append(label)
    return damaged


def detect_w005():
    return "warn" if _damaged_reg_keys() else "ok"


def fix_w005():
    damaged = _damaged_reg_keys()
    if not damaged:
        return False, "All critical HID registry keys present — no registry damage detected."
    listed = "\n".join(f"  - {d}" for d in damaged)
    return True, (
        f"Critical registry keys are MISSING:\n{listed}\n\n"
        "These are created by Windows and USB/HID drivers. Registry cleaners "
        "(CCleaner, Wise, etc.) commonly delete them, breaking joystick detection.\n\n"
        "Recovery:\n"
        "  1. Open an elevated command prompt (Run as Administrator).\n"
        "  2. Run: sfc /scannow\n"
        "  3. If that doesn't restore them:\n"
        "     DISM /Online /Cleanup-Image /RestoreHealth\n"
        "     Then run sfc /scannow again.\n"
        "  4. Reboot.\n\n"
        "Long term: uninstall registry cleaners. They routinely delete valid "
        "driver keys and are a leading cause of joystick enumeration failure."
    )


# ── W-006: Duplicate Device Entries ──────────────────────────────────────────

def _duplicate_oem_entries() -> list:
    """Return list of (base, [full_names]) for suspected duplicates in joystick OEM key."""
    try:
        oem_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"System\CurrentControlSet\Control\MediaProperties"
            r"\PrivateProperties\Joystick\OEM",
        )
    except FileNotFoundError:
        return []
    names = []
    i = 0
    while True:
        try:
            names.append(winreg.EnumKey(oem_key, i))
            i += 1
        except OSError:
            break
    winreg.CloseKey(oem_key)

    base_map = {}
    for name in names:
        base = re.sub(r"_\d+$", "", name)
        base_map.setdefault(base, []).append(name)
    return [(b, e) for b, e in base_map.items() if len(e) > 1]


def detect_w006():
    return "warn" if _duplicate_oem_entries() else "ok"


def fix_w006():
    dupes = _duplicate_oem_entries()
    if not dupes:
        return False, "No duplicate joystick OEM entries found."
    listed = "\n".join(f"  - {b}: {', '.join(e)}" for b, e in dupes)
    return True, (
        f"Duplicate joystick device entries in registry:\n{listed}\n\n"
        "This happens when the same device is plugged into different USB ports "
        "or after driver reinstalls. DirectInput games see all entries as separate "
        "devices, assigning IDs 0, 1, 2 unpredictably.\n\n"
        "How to clean up:\n"
        "  1. Unplug ALL joysticks and input devices.\n"
        "  2. Open Device Manager → View → Show hidden devices.\n"
        "  3. Expand Human Interface Devices.\n"
        "  4. Right-click each greyed-out duplicate → Uninstall device.\n"
        "  5. Reboot.\n"
        "  6. Plug your joystick into the same USB port you always use.\n\n"
        "Always use the same USB port. Windows creates a new device ID every "
        "time you swap ports, which breaks game profiles bound by device index."
    )


# ── W-007: Enumeration Order (advisory) ──────────────────────────────────────

def detect_w007():
    return "info"


def fix_w007():
    return True, (
        "Device enumeration order advisory.\n\n"
        "DirectInput assigns joystick IDs (0, 1, 2...) based on startup order. "
        "If you plug devices in a different order, or change USB ports, IDs shift. "
        "Game profiles bound to 'Joystick 0' then point to the wrong device.\n\n"
        "Best practices:\n"
        "  1. Always plug devices into the same USB ports.\n"
        "  2. Always plug in the same order (stick first, throttle second, etc.).\n"
        "  3. After any port change: rebind axes in-game or edit the profile XML.\n\n"
        "Tools that help:\n"
        "  - HidHide (free) — hide unused devices so only your primary stick gets ID 0.\n"
        "  - Joystick Gremlin (free) — maps physical axes to a fixed virtual device "
        "regardless of enumeration order."
    )


# ── W-008: Raw Input / HidUsb Driver ─────────────────────────────────────────

def _hidusb_disabled() -> bool:
    try:
        val, _ = _reg_read(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\HidUsb",
            "Start",
        )
        return val == 4  # 4 = SERVICE_DISABLED
    except Exception:
        return False


def detect_w008():
    return "warn" if _hidusb_disabled() else "ok"


def fix_w008():
    if not _hidusb_disabled():
        return False, "HidUsb driver is not disabled — raw input working normally."
    return True, (
        "HidUsb driver is set to DISABLED.\n\n"
        "HidUsb is the low-level Windows driver that converts USB HID data into "
        "raw input events. Disabled = joystick appears in Device Manager but "
        "produces no input in any game.\n\n"
        "Method A (Device Manager):\n"
        "  1. Right-click Start → Device Manager.\n"
        "  2. View → Show hidden devices.\n"
        "  3. Expand Human Interface Devices.\n"
        "  4. Right-click your HID device → Enable device.\n\n"
        "Method B (Registry — advanced users only):\n"
        "  1. Open regedit as Administrator.\n"
        "  2. Navigate to:\n"
        "     HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\HidUsb\n"
        "  3. Set Start from 4 (Disabled) to 3 (Manual).\n"
        "  4. Reboot.\n\n"
        "If disabled by antivirus or endpoint security software, add a driver "
        "exclusion for HidUsb in your security software."
    )


# ── W-009: GameInput Service Conflict ────────────────────────────────────────

_GAMEINPUT_PROCS = ("gameinputbroker.exe", "gameinput.exe", "gameinputsvc.exe")
_GAMEINPUT_SVC   = "GameInputBroker"


def _gameinput_running() -> bool:
    procs = _running_processes()
    return any(p in procs for p in _GAMEINPUT_PROCS)


def _gameinput_svc_running() -> bool:
    try:
        out = subprocess.check_output(
            ["sc.exe", "query", _GAMEINPUT_SVC],
            text=True, errors="replace",
            creationflags=CREATE_NO_WINDOW,
        )
        return "RUNNING" in out
    except Exception:
        return False


def detect_w009():
    return "warn" if (_gameinput_running() or _gameinput_svc_running()) else "ok"


def fix_w009():
    running = _gameinput_running()
    svc     = _gameinput_svc_running()
    if not running and not svc:
        return False, "GameInput is not running — no conflict detected."
    return True, (
        "GameInput / GameInputBroker is running alongside the legacy "
        "DirectInput/XInput stack. Known symptoms:\n"
        "  - Phantom button presses\n"
        "  - Joystick axes appearing at half range\n"
        "  - Device seen twice (once via DirectInput, once via GameInput)\n\n"
        "Most affected games: Star Citizen, some DCS builds, games built on "
        "Windows GDK that mix XInput and legacy DirectInput.\n\n"
        "Short-term fix:\n"
        "  1. Press Windows key + R, type services.msc, press Enter.\n"
        "  2. Scroll to GameInputBroker.\n"
        "  3. Right-click → Stop.\n"
        "  4. Right-click → Properties → set Startup type to Manual.\n"
        "  5. Relaunch your game.\n\n"
        "Note: disabling GameInput may break Xbox Cloud Gaming / Game Pass "
        "streaming apps. Re-enable GameInputBroker if you use those."
    )


# ── Problem Registry ──────────────────────────────────────────────────────────

PROBLEMS = [
    {"id": "W-001", "category": "usb_power",
     "title": "USB Selective Suspend enabled (can disconnect joystick mid-session)",
     "detect": detect_w001, "fix": fix_w001},
    {"id": "W-002", "category": "polling_rate",
     "title": "Polling rate — VKB defaults to 125 Hz, 1000 Hz recommended",
     "detect": detect_w002, "fix": fix_w002},
    {"id": "W-003", "category": "calibration",
     "title": "joy.cpl calibration — verify calibration data is intact",
     "detect": detect_w003, "fix": fix_w003},
    {"id": "W-004", "category": "hid_error",
     "title": "HID device has Windows error code (failed to enumerate)",
     "detect": detect_w004, "fix": fix_w004},
    {"id": "W-005", "category": "registry",
     "title": "Registry cleaner damage — critical HID/joystick keys deleted",
     "detect": detect_w005, "fix": fix_w005},
    {"id": "W-006", "category": "duplicates",
     "title": "Duplicate joystick device entries (causes unpredictable device IDs)",
     "detect": detect_w006, "fix": fix_w006},
    {"id": "W-007", "category": "enumeration",
     "title": "Device enumeration order — advisory (port changes break profiles)",
     "detect": detect_w007, "fix": fix_w007},
    {"id": "W-008", "category": "raw_input",
     "title": "HidUsb / raw input driver disabled",
     "detect": detect_w008, "fix": fix_w008},
    {"id": "W-009", "category": "gameinput",
     "title": "GameInput / GameInputBroker service conflict",
     "detect": detect_w009, "fix": fix_w009},
]


# ── Convenience ───────────────────────────────────────────────────────────────

def scan_all():
    """Refresh state, scan all problems, return list of (problem_dict, status)."""
    refresh()
    return [(p, p["detect"]()) for p in PROBLEMS]


def _print_report():
    results = scan_all()
    warns = [p for p, s in results if s == "warn"]
    print(f"\nWin Hardener — scanned {len(results)} problems\n" + "=" * 64)
    for p, status in results:
        marker = {"ok": "[ ok ]", "warn": "[WARN]",
                  "info": "[info]", "not_installed": "[ -- ]"}.get(status, status)
        print(f"  {marker}  {p['id']}  {p['title']}")
    print("=" * 64)
    if not warns:
        print("No active Windows hardware issues detected.\n")
        return
    print(f"\n{len(warns)} recommendation(s):\n")
    for p in warns:
        _, msg = p["fix"]()
        print(f"--- {p['id']}  {p['title']} ---")
        print(msg)
        print()


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _print_report()
