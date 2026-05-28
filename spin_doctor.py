"""VKB Spin Doctor — fixes mouse-axis spin for VKB joystick users.

Thin launcher. Logic lives in:
  spin_doctor_fixes.py  — file detection, backup, and fix functions
  spin_doctor_kb.py     — knowledge base problem data
  spin_doctor_ui.py     — all GUI classes
"""

import tkinter as tk
from spin_doctor_ui import SpinDoctorApp


def main():
    root = tk.Tk()
    SpinDoctorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
