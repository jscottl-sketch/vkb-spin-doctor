"""spin_doctor_kb.py — Knowledge Base problem data for VKB Spin Doctor."""

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
