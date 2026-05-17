# =====================================================
# HOW TO ADD THE SCREENSHOT DIAGNOSTIC BUTTON
# INTO spin_doctor.py
# =====================================================
#
# Step 1 — Copy screenshot_diagnostic.py into your
#           VKB-SpinDoctor folder (same folder as spin_doctor.py)
#
# Step 2 — Add this import near the TOP of spin_doctor.py
#           (after your existing imports):
# =====================================================

import subprocess
import sys
import os

# =====================================================
# Step 3 — Add this function anywhere in spin_doctor.py
#           (before your button definitions is fine):
# =====================================================

def open_screenshot_diagnostic():
    """Opens the Screenshot Diagnostic tool as a separate window."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot_diagnostic.py")
    
    if not os.path.exists(script_path):
        # Show error if file not found
        import tkinter.messagebox as mb
        mb.showerror(
            "File Not Found",
            f"screenshot_diagnostic.py not found.\n\nExpected location:\n{script_path}\n\n"
            "Make sure screenshot_diagnostic.py is in the same folder as spin_doctor.py."
        )
        return
    
    # Launch as a separate process so VKB Helper stays open
    subprocess.Popen([sys.executable, script_path])


# =====================================================
# Step 4 — Add this button wherever you want it
#           in your existing Tkinter GUI layout.
#
#           Replace 'your_frame' with whatever frame
#           or window you want it to appear in.
# =====================================================

# Example button code (paste into your GUI layout):
#
#   tk.Button(
#       your_frame,
#       text="📸  Screenshot Diagnostic",
#       command=open_screenshot_diagnostic,
#       font=("Segoe UI", 10),
#       bg="#89b4fa",
#       fg="#1e1e2e",
#       relief="flat",
#       padx=12, pady=6
#   ).pack(pady=4)


# =====================================================
# FOLDER STRUCTURE after adding:
#
#   VKB-SpinDoctor/
#   ├── spin_doctor.py              ← existing file (you edit this)
#   ├── screenshot_diagnostic.py    ← new file (copy here)
#   ├── api_key.txt                 ← auto-created on first run
#   ├── RUN_VKB.bat
#   └── backups/
#       └── WarThunder/
# =====================================================
