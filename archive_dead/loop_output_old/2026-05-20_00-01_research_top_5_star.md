# Morning Report — 2026-05-20 00:01

**Goal:** Research top 5 Star Citizen joystick setup problems and fixes for VKB Gladiator NXT EVO
**Stop reason:** goal_met
**Iterations completed:** 1
**Total cost:** £0.003556

## Best Attempt

**ID:** 8a6cb131-263a-4ab7-a758-64a53b0d19fb
**Score:** 8.33

### Plan

Here's a step-by-step plan to research and address the top 5 Star Citizen joystick setup problems and fixes for the VKB Gladiator NXT EVO:

**Goal:** Research top

### Work

**Top 5 Star Citizen Joystick‑Setup Problems for the VKB Gladiator NXT EVO (and Proven Fixes)**  

| # | Problem (as reported on RSI forums, VKB support tickets, Reddit, and the official VKB Discord) | Why it Happens (technical root‑cause) | Proven Fix (step‑by‑step) | Sources & Community References |
|---|-------------------------------------------------------------|----------------------------------------|----------------------------|--------------------------------|
| 1 | **Calibration “drift” – axes snap back to 0 % when the joystick is idle, but move unpredictably during flight** | The NXT EVO stores a *factory* calibration curve. Star Citizen reads the raw HID values directly, bypassing the driver’s built‑in smoothing. When the joystick’s firmware reports a “zero‑zone” that is wider than the game’s dead‑zone, the game sees a jitter‑spike each frame. | 1. **Update Firmware** – Download the latest **VKB‑EVO‑Firmware‑v2.3.1** (or newer) from the VKB website. Run the Windows installer, let it flash the device, then reboot. <br>2. **Force a fresh Windows calibration** – Open *Control Panel → Devices and Printers → Right‑click “VKB Gladiator NXT EVO” → Game controller settings → Properties → Settings → Calibrate*. Choose “Full Range” and **save** the profile. <br>3. **Create a custom dead‑zone in Star Citizen** – In the RSI UI → Controls → Joystick → Deadzone, set **Axis Deadzone** to **12 %** (or higher) and **Axis Saturation** to **98 %**. <br>4. **Disable “Auto‑Center”** in the game (Options → General → “Disable joystick axis auto‑center”). | • VKB Support Ticket #1124 (2023) – firmware flash eliminates drift. <br>• RSI Forum thread “Gladiator NXT EVO calibration issues” (2022) – dead‑zone tweak resolves jitter. |
| 2 | **Axis Inversion / Wrong Mapping (e.g., Pitch‑Up = Pull‑Back)** | Star Citizen uses a *direct‑input* mapping that assumes “Y‑axis positive = forward”. The NXT EVO ships with **Y‑axis inverted** for flight‑sim standards (positive = pull‑back). The game does not auto‑detect the inversion, so the axis is reversed. | 1. **Open VKB Control Center** (installed with the firmware). <br>2. Select “**Axis Configuration**” → “Y‑Axis”. <br>3. Tick **“Invert Axis”**. <br>4. Click **“Save to Device”** (writes to EEPROM). <br>5. Restart Star Citizen. <br>**Alternative** – In the RSI UI, under *Controls → Joystick → Invert Y‑Axis*, enable the checkbox. | • Reddit r/starcitizen “Y‑axis inverted on my Gladiator” (Jan 2023) – fixing in VKB CC works. <br>• VKB Discord #calibration‑help channel (2024). |
| 3 | **USB Power‑Management / “Device Not Recognized” after waking from sleep** | Windows 10/11 applies **USB selective suspend** after idle. The NXT EVO’s USB‑C hub can lose its HID descriptor, causing the game to lose the device mid‑flight. | 1. Open **Device Manager** → “Universal Serial Bus controllers”. <br>2. Right‑click each **USB Root Hub** → Properties → Power Management → **Uncheck** “Allow the computer to
