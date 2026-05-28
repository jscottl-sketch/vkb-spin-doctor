"""spin_doctor_ui.py — GUI components for VKB Spin Doctor."""

import tkinter as tk
from tkinter import messagebox

# Module 02 — Process Conductor
try:
    from problems import conductor
    _CONDUCTOR_OK  = True
    _CONDUCTOR_ERR = None
except Exception as _e:
    conductor      = None
    _CONDUCTOR_OK  = False
    _CONDUCTOR_ERR = f"{type(_e).__name__}: {_e}"

# Module 07 — ED Bind Reset Prevention
try:
    from problems import ed_bind_reset
    _ED_RESET_OK  = True
    _ED_RESET_ERR = None
except Exception as _e:
    ed_bind_reset = None
    _ED_RESET_OK  = False
    _ED_RESET_ERR = f"{type(_e).__name__}: {_e}"

# Module 08 — Windows Hardware Hardener
try:
    from problems import win_hardener
    _WIN_HARDENER_OK  = True
    _WIN_HARDENER_ERR = None
except Exception as _e:
    win_hardener      = None
    _WIN_HARDENER_OK  = False
    _WIN_HARDENER_ERR = f"{type(_e).__name__}: {_e}"

from spin_doctor_fixes import (
    find_warthunder_machine_blk, find_elite_binds, find_starcitizen_xml,
    check_warthunder_status, check_elite_status, check_not_implemented,
    fix_warthunder, fix_elite,
    make_backup, restore_last_backup, has_backup,
)
from spin_doctor_kb import KB_DATA

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


# ── GameCard ───────────────────────────────────────────────────────────────────

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
            self.filepath = self.finder_fn()
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


# ── EDBindResetCard ────────────────────────────────────────────────────────────

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


# ── KnowledgeBaseTab ───────────────────────────────────────────────────────────

class KnowledgeBaseTab(tk.Frame):
    """Scrollable list of common problems and fixes, filtered by selected game."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_WIN)
        self._game_var = tk.StringVar(value="War Thunder")
        self._build()

    def _build(self):
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

        self._canvas.yview_moveto(0)

    def _make_card(self, entry):
        card = tk.Frame(self._inner, bg=BG_CARD, padx=14, pady=10)
        card.pack(fill="x", pady=(0, 6))

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

        tk.Label(card, text=entry["desc"],
                 font=("Segoe UI", 9),
                 bg=BG_CARD, fg=FG_DIM,
                 wraplength=530, justify="left", anchor="w"
                 ).pack(fill="x", pady=(6, 4))

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


# ── ProcessConductorTab ────────────────────────────────────────────────────────

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
        self._canvas.bind("<Enter>", lambda _e: self._canvas.bind_all("<MouseWheel>", self._on_wheel))
        self._canvas.bind("<Leave>", lambda _e: self._canvas.unbind_all("<MouseWheel>"))

    def _on_wheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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


# ── WinHardenerCard ────────────────────────────────────────────────────────────

class WinHardenerCard(tk.Frame):
    """Module 08 — Windows Hardware Diagnostics widget for the Fix tab."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_GREY, padx=16, pady=10)
        self._last_results = []
        self._build()
        if _WIN_HARDENER_OK:
            self.refresh()
        else:
            self._render_load_error()

    def _build(self):
        bg = BG_GREY
        tk.Label(self, text="Windows Hardware Diagnostics",
                 font=("Segoe UI", 11, "bold"), bg=bg, fg=FG_WHITE,
                 ).grid(row=0, column=0, sticky="w")
        tk.Label(self,
                 text=("USB power · HID errors · registry damage · "
                       "duplicate entries · raw input · GameInput conflicts."),
                 font=("Segoe UI", 8), bg=bg, fg=FG_DIM,
                 wraplength=520, justify="left",
                 ).grid(row=1, column=0, sticky="w", pady=(1, 6))

        self.status_lbl = tk.Label(self, text="",
                                    font=("Segoe UI", 9, "bold"),
                                    bg=bg, fg=FG_WHITE,
                                    wraplength=520, justify="left", anchor="w")
        self.status_lbl.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        btn_row = tk.Frame(self, bg=bg)
        btn_row.grid(row=3, column=0, sticky="w")

        self.scan_btn = tk.Button(
            btn_row, text="Scan Windows",
            font=("Segoe UI", 10, "bold"),
            bg=C_BLUE, fg=FG_WHITE, padx=14, pady=5,
            relief="flat", cursor="hand2",
            command=self.refresh)
        self.scan_btn.pack(side="left", padx=(0, 8))

        self.detail_btn = tk.Button(
            btn_row, text="Show Details",
            font=("Segoe UI", 10),
            bg=FG_DIM, fg=FG_WHITE, padx=14, pady=5,
            relief="flat", cursor="hand2",
            command=self._show_details)
        self.detail_btn.pack(side="left")

    def refresh(self):
        if not _WIN_HARDENER_OK:
            return
        self.status_lbl.config(text="Scanning…", fg=FG_DIM)
        self.update_idletasks()
        try:
            self._last_results = win_hardener.scan_all()
        except Exception as exc:
            self.status_lbl.config(text=f"Scan failed: {exc}", fg=C_RED)
            return
        warns = [p for p, s in self._last_results if s == "warn"]
        if warns:
            self.status_lbl.config(
                text=f"⚠  {len(warns)} issue(s) found — click Show Details.",
                fg=C_RED)
        else:
            self.status_lbl.config(
                text=f"✓  All {len(self._last_results)} Windows hardware checks clear.",
                fg=C_GREEN)

    def _show_details(self):
        if not self._last_results:
            messagebox.showinfo("No data", "Click Scan Windows first.")
            return
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Windows Hardware Diagnostics — Details")
        win.configure(bg=BG_WIN)
        win.transient(self.winfo_toplevel())
        win.resizable(False, False)

        txt = tk.Text(win, wrap="word", font=("Segoe UI", 9),
                      bg=BG_CARD, fg=FG_WHITE,
                      width=78, height=26,
                      padx=14, pady=10,
                      relief="flat", borderwidth=0, highlightthickness=0)
        txt.pack(padx=20, pady=(12, 0), fill="both", expand=True)

        lines = []
        for problem, status in self._last_results:
            marker = {"ok": "[ ok ]", "warn": "[WARN]",
                      "info": "[info]", "not_installed": "[ -- ]"}.get(status, status)
            lines.append(f"{marker}  {problem['id']}  {problem['title']}")
            if status in ("warn", "info"):
                try:
                    _, msg = problem["fix"]()
                    lines.append(msg[:400] + ("…" if len(msg) > 400 else ""))
                except Exception:
                    pass
            lines.append("")
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")

        tk.Button(win, text="Close",
                  font=("Segoe UI", 10, "bold"),
                  bg=C_BLUE, fg=FG_WHITE, padx=24, pady=6,
                  relief="flat", cursor="hand2",
                  command=win.destroy,
                  ).pack(pady=(8, 16))

    def _render_load_error(self):
        self.status_lbl.config(
            text=f"Module 08 failed to load: {_WIN_HARDENER_ERR}", fg=C_RED)
        self.scan_btn.config(state="disabled", bg=C_GREY, cursor="arrow")
        self.detail_btn.config(state="disabled", bg=C_GREY, cursor="arrow")


# ── SpinDoctorApp ──────────────────────────────────────────────────────────────

class SpinDoctorApp:
    def __init__(self, root):
        self.root = root
        root.title("VKB Spin Doctor")
        root.configure(bg=BG_WIN)
        root.resizable(False, False)
        self._build()

    def _build(self):
        hdr = tk.Frame(self.root, bg=BG_WIN, pady=16)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="VKB Spin Doctor",
                 font=("Segoe UI", 20, "bold"), bg=BG_WIN, fg=FG_WHITE
                 ).pack(side="left")
        tk.Label(hdr, text="  v1.0  —  fixes mouse-axis spin for joystick users",
                 font=("Segoe UI", 9), bg=BG_WIN, fg=FG_DIM
                 ).pack(side="left")

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

        EDBindResetCard(self._fix_frame).pack(fill="x", pady=(0, 6))

        tk.Frame(self._fix_frame, bg=C_DIV, height=1).pack(fill="x", pady=2)

        GameCard(self._fix_frame,
                 game_name="Star Citizen",
                 finder_fn=find_starcitizen_xml,
                 status_fn=check_not_implemented,
                 fix_fn=lambda f: (False, "Not yet implemented."),
                 greyed=True,
                 ).pack(fill="x", pady=(2, 6))

        tk.Frame(self._fix_frame, bg=C_DIV, height=1).pack(fill="x", pady=2)

        WinHardenerCard(self._fix_frame).pack(fill="x", pady=(2, 0))

        self._conductor_frame = ProcessConductorTab(self.root)
        self._kb_frame = KnowledgeBaseTab(self.root)

        self._tabs = {
            "fix":       (self._tab_fix_btn,       self._fix_frame),
            "conductor": (self._tab_conductor_btn, self._conductor_frame),
            "kb":        (self._tab_kb_btn,        self._kb_frame),
        }

        self._show_tab("fix")

    def _show_tab(self, active):
        for name, (btn, frame) in self._tabs.items():
            if name == active:
                frame.pack(fill="both", padx=20, pady=(8, 20))
                btn.config(bg=BG_CARD, fg=FG_WHITE, font=("Segoe UI", 10, "bold"))
            else:
                frame.pack_forget()
                btn.config(bg=BG_WIN, fg=FG_DIM, font=("Segoe UI", 10))
