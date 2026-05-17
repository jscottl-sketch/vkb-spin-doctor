# UNIVERSAL INPUT DEVICE PROBLEM DATABASE
**Project:** Spin Doctor (Universal Edition)
**Compiled:** 08 May 2026 | Recovered: 12 May 2026
**Scope:** ALL input devices — joysticks, HOTAS, steering wheels, controllers, mice, pedals, handbrakes, button boxes
**Vision:** One tool. Any hardware. Any game. Plug it in, it sorts it out.

---

# THE 8 UNIVERSAL PROBLEMS
## (Hit every device type, every game — fix these first, covers 80% of all complaints)

---

### U-001 | DEVICE NOT DETECTED BY GAME ⭐ #1 MOST REPORTED
**Devices affected:** ALL
**What happens:** Hardware works in Windows. Game ignores it. Or game sees generic Xbox controller instead of real device.
**Root causes:**
- Steam "Generic Gamepad Configuration Support" enabled — translates everything to Xbox input
- Game launched before device was plugged in
- Too many devices connected, game hits limit
- USB hub or front panel port — not enough power/bandwidth
- Wrong USB mode switch position on device

**Fixes:**
1. Steam → Settings → Controller → General Controller Settings → UNCHECK Generic Gamepad Configuration Support
2. Unplug device → reboot → plug directly into rear motherboard USB port → launch game
3. Disable Steam Input per-game: Library → right-click game → Properties → Controller → Disable Steam Input
4. Reduce number of connected devices

**Auto-fixable:** ✅ Full (Steam settings) / ⚠️ Guide (USB port)

---

### U-002 | BINDINGS RESET AFTER UPDATE OR RESTART ⭐ #2 MOST REPORTED
**Devices affected:** ALL
**What happens:** Hours of custom setup wiped. Game reverts to defaults after patches or missing device at launch.
**Root causes:**
- Game patch overwrites config files
- Game only loads profiles where ALL referenced devices are connected
- Some games re-detect hardware on settings menu open and reset

**Fixes:**
1. Back up config files before every update
2. Always plug in ALL devices before launching game
3. Restore from backup after reset

**Auto-fixable:** ✅ Full — backup/restore system

---

### U-003 | DOUBLE INPUT / CONTROLLER CONFLICT ⭐ #3 MOST REPORTED
**Devices affected:** ALL — especially when multiple devices connected
**What happens:** Axis moves on its own. Inputs fight each other. Character/vehicle spins or twitches.
**Root causes:**
- PS5/Xbox controller connected alongside joystick/wheel
- Steam Input enabled on multiple devices simultaneously
- Two devices mapped to same axis

**Fixes:**
1. Unplug any controllers not being used for that game
2. Disable Steam Input globally or per-game
3. Use HidHide (open source) to hide unused devices from specific games

**Auto-fixable:** ✅ Full

---

### U-004 | SENSITIVITY WRONG — OVER/UNDER RESPONSIVE ⭐ #4
**Devices affected:** ALL
**What happens:** Every new user. Tiny movement = massive reaction, or huge movement = tiny reaction.
**Root causes:**
- Game defaults assume mouse/controller, not joystick/wheel
- No starter curve applied
- Linear curve on device that needs non-linear

**Fixes:**
1. Apply starter sensitivity values per game (community-tested)
2. Add non-linear curve in game or via device software

**Auto-fixable:** ✅ Full — write starter values to config

---

### U-005 | AXIS DRIFT AT REST ⭐ #5
**Devices affected:** Joystick, wheel, gamepad
**What happens:** Vehicle/camera drifts slowly when hands off controls.
**Root causes:**
- Deadzone set to zero
- Cheap potentiometer hardware (normal wear)
- Electrical interference

**Fixes:**
1. Set deadzone to 3–8% in game or device software
2. Recalibrate in Windows (joy.cpl)
3. Check USB port (EMI from other devices)

**Auto-fixable:** ⚠️ Partial — can write deadzone values, can't fix hardware

---

### U-006 | INVERTED AXES ⭐ #6
**Devices affected:** Joystick, wheel, pedals
**What happens:** Pull back = nose down. Turn left = goes right.
**Root causes:**
- Game default assumes opposite direction
- Device axis polarity not matched to game expectation

**Fixes:**
1. Invert axis in game settings
2. Or invert in device software

**Auto-fixable:** ✅ Full

---

### U-007 | STEAM INPUT INTERFERING ⭐ #7
**Devices affected:** ALL (Steam games)
**What happens:** Game receives wrong input type. Joystick treated as controller. Bindings ignored.
**Root causes:**
- Steam "Generic Gamepad Configuration Support" silently enabled by default
- Steam overlay intercepting inputs

**Fixes:**
1. Steam → Settings → Controller → uncheck all Generic Support options
2. Per-game: Properties → Controller → Disable Steam Input

**Auto-fixable:** ✅ Full

---

### U-008 | WRONG DEVICE NAME IN CONFIG FILE ⭐ #8
**Devices affected:** ALL
**What happens:** After driver update or USB port change, device ID changes. Game can't find saved profile.
**Root causes:**
- Windows assigns new device ID when plugged into different port
- Driver update changes device string

**Fixes:**
1. Always use same USB port
2. Rename device in config to match new ID
3. Use HidHide to assign persistent device names

**Auto-fixable:** ✅ Full — detect and rewrite device name in config

---

# DEVICE-SPECIFIC PROBLEMS

---

## JOYSTICK / HOTAS

| # | Problem | Auto-Fix? |
|---|---|---|
| J-001 | Mouse axis spin bug (new joystick) | ✅ Full — THIS is what we built |
| J-002 | Force feedback / rumble not working | ⚠️ Partial |
| J-003 | Twist/rudder axis not detected | ✅ Full |
| J-004 | Throttle not registering as analogue | ✅ Full |
| J-005 | Dual stick — only one seen by game | ❌ In-game fix only |

---

## STEERING WHEEL

| # | Problem | Auto-Fix? |
|---|---|---|
| W-001 | Wheel not detected at all | ✅ Full |
| W-002 | Force feedback dead / clipping / oscillating | ⚠️ Partial |
| W-003 | Rotation angle wrong (e.g. 180° instead of 900°) | ✅ Full |
| W-004 | Pedals inverted or combined as one axis | ⚠️ Partial |
| W-005 | Settings reset after game update | ✅ Backup |
| W-006 | Wheel locks / goes stiff suddenly | ⚠️ Guide |

---

## CONTROLLER (XBOX / PS)

| # | Problem | Auto-Fix? |
|---|---|---|
| C-001 | PS controller seen as Xbox | ✅ Full |
| C-002 | Double input with another device | ✅ Full |
| C-003 | Not working in non-Steam game | ✅ Full |
| C-004 | Stick drift | ⚠️ Deadzone workaround |

---

## MOUSE

| # | Problem | Auto-Fix? |
|---|---|---|
| M-001 | Input lag (polling rate wrong) | ✅ Full |
| M-002 | Acceleration active (ruins aim) | ✅ Full |
| M-003 | DPI mismatch between device and game | ✅ Full |
| M-004 | Wireless interference | ✅ Detect + guide |

---

## PEDALS / EXTRAS

| # | Problem | Auto-Fix? |
|---|---|---|
| X-001 | Pedals combined as one axis instead of separate | ⚠️ Guide |
| X-002 | Handbrake not detected | ✅ Full |
| X-003 | Button box / Arduino not recognised | ❌ Guide only |

---

# MASTER PRIORITY TABLE

| Rank | Problem | Hardware | Auto-Fix? | Frequency |
|---|---|---|---|---|
| 1 | Device not detected / wrong device seen | ALL | ✅ Full | Millions of reports |
| 2 | Bindings reset after update | ALL | ✅ Backup | Constant, all games |
| 3 | Double input / controller conflict | ALL | ✅ Full | Huge |
| 4 | Sensitivity wrong | ALL | ✅ Starter values | Every new user |
| 5 | Axis drift at rest | Joystick/Wheel/Pad | ⚠️ Partial | Very common |
| 6 | Inverted axes | Joystick/Wheel/Pedal | ✅ Full | Every new user |
| 7 | Steam Input interfering | ALL (Steam) | ✅ Full | Epidemic since 2019 |
| 8 | Wrong device name in config | ALL | ✅ Full | Post-update constant |
| 9 | Mouse axis spin bug | Joystick | ✅ Full | Every new joystick user |
| 10 | Force feedback not working | Wheel/Joystick | ⚠️ Partial | Every new sim racer |
| 11 | Wheel rotation angle wrong | Wheel | ✅ Full | Very common |
| 12 | Pedals inverted / combined axis | Pedals | ⚠️ Partial | Common |
| 13 | PS controller seen as Xbox | Controller | ✅ Full | Very common |
| 14 | Controller double input | Controller | ✅ Full | Common |
| 15 | Mouse input lag | Mouse | ✅ Full | Very common |
| 16 | Mouse acceleration active | Mouse | ✅ Full | Common |
| 17 | Wireless mouse interference | Mouse | ✅ Detect + guide | Moderate |
| 18 | Deadzone resets | Joystick | ✅ Full | Moderate |
| 19 | Wheel locks / goes stiff | Wheel | ⚠️ Guide | Moderate |
| 20 | Pedals not separate axes | Pedals | ⚠️ Guide | Moderate |
| 21 | Handbrake not detected | Handbrake | ✅ Full | Moderate |
| 22 | Stick drift (controller) | Controller | ⚠️ Deadzone | Massive (class action) |
| 23 | Dual stick only one seen | Joystick | ❌ In-game | Growing |
| 24 | Button box not recognised | Button box | ❌ Guide | Niche but loyal |

---

# SCORE
- **Total problems documented:** 24
- **Fully auto-fixable:** 13
- **Partially auto-fixable:** 8
- **Guide only:** 3

---

# THE KEY INSIGHT
Fix the top 8 universal problems and you solve 80% of all complaints — regardless of whether the user has a £30 Logitech stick or a £600 Fanatec DD wheel.

Steam "Generic Gamepad Configuration Support" is silently breaking joysticks and wheels for millions of people. The fix is unchecking one box. Nobody has built a tool that does this automatically.

**Nobody has built this. This is the product.**

---
*Sources: Steam forums, Reddit r/hotas r/simracing, manufacturer forums, Thrustmaster/Fanatec/Logitech support, iRacing docs, community guides*
*Original research: 08 May 2026 | Recovered: 12 May 2026*
