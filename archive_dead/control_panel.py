# control_panel.py
# Universal AI Control Panel
# Works on ANY project. Drop it in any folder with a panel_config.json
#
# Run: python control_panel.py
# Or:  python control_panel.py --project "C:\path\to\project"

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import json
import time
import sys
import os
import argparse
from pathlib import Path

# ─── ARGS ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--project", default=None)
args, _ = parser.parse_known_args()

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "panel_config.json"
DEFAULT_DIR = Path(r"C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor")

def load_config():
    d = {
        "project_name": "VKB Spin Doctor",
        "project_path": str(DEFAULT_DIR),
        "models_dir":   r"D:\lm-models",
        "python_path":  r"C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe",
    }
    if args.project:
        d["project_path"] = args.project
        d["project_name"] = Path(args.project).name
        return d
    if CONFIG_FILE.exists():
        try:
            d.update(json.loads(CONFIG_FILE.read_text()))
        except Exception:
            pass
    return d

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

CONFIG      = load_config()
PROJECT_DIR = Path(CONFIG["project_path"])
MODELS_DIR  = Path(CONFIG["models_dir"])
DB_PATH     = PROJECT_DIR / "task_db.json"

sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

# ─── COLOURS ──────────────────────────────────────────────────────────────────
BG      = "#0f0f1a"
SURFACE = "#16162a"
SURF2   = "#1e1e35"
SURF3   = "#242440"
BORDER  = "#2a2a45"
TEXT    = "#e8e8f0"
TEXT2   = "#8888aa"
TEXT3   = "#4444aa"
ACCENT  = "#5b6af0"
GREEN   = "#2ecc8a"
AMBER   = "#f0a030"
RED     = "#e85050"
PURPLE  = "#9b72ef"

# ─── AI MODEL DEFINITIONS ─────────────────────────────────────────────────────

MODEL_DEFS = [
    {
        "key":      "vision",
        "label":    "Vision AI",
        "sub":      "Reads screens & images",
        "icon":     "👁",
        "db_name":  "qwen2.5-vl-32b-instruct",
        "model":    "Qwen2.5-VL 32B",
        "provider": "Local — LM Studio",
        "cost":     "FREE",
        "size":     "21 GB on disk",
        "what_is": (
            "Qwen2.5-VL is a vision model — it can see images and screenshots and describe "
            "what's in them, just like a human looking at your screen. It reads game menus, "
            "UI elements, error messages, and anything else visual."
        ),
        "best_for": [
            "Reading what's on a game screen (menus, settings, error messages)",
            "Diagnosing a problem from a screenshot",
            "Checking whether a fix worked by looking at the result",
            "Reading text from an image you cannot copy-paste",
        ],
        "not_for": [
            "Writing or editing code — use Code AI for that",
            "Planning what to build — use Thinking AI",
            "Quick text questions — Fast AI is faster and uses less memory",
        ],
        "examples": [
            "What does this screenshot of the War Thunder controls screen show?",
            "Is the spin bug fixed? Here is a screenshot of the axis settings.",
            "What error message is showing on this screen?",
        ],
    },
    {
        "key":      "code",
        "label":    "Code AI",
        "sub":      "Writes & fixes Python",
        "icon":     "💻",
        "db_name":  "qwen2.5-coder-32b-instruct",
        "model":    "Qwen2.5-Coder 32B",
        "provider": "Local — LM Studio",
        "cost":     "FREE",
        "size":     "20 GB on disk",
        "what_is": (
            "Qwen2.5-Coder is trained on billions of lines of code from across the internet. "
            "It understands Python deeply, reads config files, writes functions from scratch, "
            "finds bugs, and explains what existing code does. Comparable to GitHub Copilot "
            "but free, private, and running entirely on your machine."
        ),
        "best_for": [
            "Writing new Python functions or entire modules",
            "Fixing bugs in .py files",
            "Reading and editing game config files (.blk, .xml, .binds, .json)",
            "Explaining what a piece of code does in plain English",
            "Refactoring messy code into something cleaner",
        ],
        "not_for": [
            "Looking at screenshots — use Vision AI for that",
            "High-level planning and architecture — Thinking AI reasons better",
            "Quick one-line questions — Fast AI responds faster",
        ],
        "examples": [
            "Write a Python function to parse a War Thunder .blk config file",
            "Fix the bug in spin_fix.py where the axis name is wrong",
            "Read the Elite Dangerous .binds file and find the mouse axis settings",
        ],
    },
    {
        "key":      "plan",
        "label":    "Thinking AI",
        "sub":      "Plans, reasons & decides",
        "icon":     "🧠",
        "db_name":  "deepseek-r1-70b",
        "model":    "DeepSeek R1 70B",
        "provider": "Local — LM Studio",
        "cost":     "FREE",
        "size":     "Already downloaded",
        "what_is": (
            "DeepSeek R1 is a reasoning model — before answering it thinks through the problem "
            "step by step, like a consultant who works carefully rather than guessing. It is slower "
            "than the other AIs but produces better answers when the question requires real logic, "
            "planning, or weighing up several options."
        ),
        "best_for": [
            "Deciding what to build next and in what order",
            "Diagnosing complex problems with multiple possible causes",
            "Designing the architecture of new software before writing it",
            "Weighing tradeoffs between different approaches",
            "Creating a roadmap or battle plan",
        ],
        "not_for": [
            "Writing actual code — Code AI is more accurate for that",
            "Reading screenshots — use Vision AI",
            "Quick factual questions — DeepSeek is slow, use Fast AI instead",
        ],
        "examples": [
            "What is the best way to add local AI to the SFL agent?",
            "Plan the next 5 features for VKB Spin Doctor in priority order",
            "Why might the router be picking the wrong model for my tasks?",
        ],
    },
    {
        "key":      "fast",
        "label":    "Fast AI",
        "sub":      "Quick answers, zero wait",
        "icon":     "⚡",
        "db_name":  "llama-3.3-70b-versatile",
        "model":    "Llama 3.3 70B via Groq",
        "provider": "Online — Groq free API",
        "cost":     "FREE",
        "size":     "No download needed",
        "what_is": (
            "Llama 3.3 70B running on Groq's free cloud service. Groq uses special hardware "
            "that runs AI at 500+ tokens per second — about 10x faster than a local model loading "
            "from disk. Free up to generous rate limits for personal use. Needs only a free "
            "Groq API key from console.groq.com — no download, no VRAM used."
        ),
        "best_for": [
            "Quick questions that need a fast answer",
            "Summarising text, logs, or error messages",
            "When local models are not loaded yet and you need something now",
            "Simple rewrites, renames, or small text edits",
            "Checking grammar or rephrasing a message",
        ],
        "not_for": [
            "Long complex code tasks — context window is smaller than local models",
            "Anything that must stay private — Fast AI sends data to Groq servers",
            "Vision tasks — text only, cannot see images",
        ],
        "examples": [
            "Summarise this error log in plain English",
            "What does axis deadzone mean in flight sim controls?",
            "Rewrite this function name to be clearer",
        ],
    },
]


# ─── MODEL STATUS ─────────────────────────────────────────────────────────────

def get_model_status(m):
    if MODELS_DIR.exists():
        folders = [p.name.lower() for p in MODELS_DIR.iterdir() if p.is_dir()]
        if m["key"] == "vision"  and any("vl" in f and "32b" in f for f in folders):
            return "Ready", GREEN
        if m["key"] == "code"    and any("coder" in f for f in folders):
            return "Ready", GREEN
        if m["key"] == "plan"    and any("deepseek" in f or "r1" in f for f in folders):
            return "Ready", GREEN
    if m["key"] == "fast":
        env = PROJECT_DIR / ".env"
        if env.exists() and "GROQ_API_KEY" in env.read_text():
            return "Online — free", GREEN
        return "Needs Groq key", AMBER
    return "Not downloaded", AMBER


# ─── MAIN GUI ─────────────────────────────────────────────────────────────────

class ControlPanel:

    def __init__(self, root):
        self.root         = root
        self.router       = None
        self.allow_paid   = False
        self.free_calls   = 0
        self.paid_calls   = 0
        self.expanded_key = None

        self.root.title(f"AI Control Panel — {CONFIG['project_name']}")
        self.root.geometry("860x760")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self._build_topbar()
        self._build_model_cards()
        self._build_detail_panel()
        self._build_chat()
        self._build_input()
        self._build_statusbar()

        self._load_router()
        self._refresh_model_status()
        self._welcome()

    # ── TOP BAR ───────────────────────────────────────────────────────────────

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="⚙  AI Control Panel",
                 bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, padx=14, pady=12)

        tk.Label(bar, text=f"Project: {CONFIG['project_name']}",
                 bg=SURFACE, fg=TEXT2, font=("Segoe UI", 9)
                 ).pack(side=tk.LEFT, padx=4)

        tk.Button(bar, text="⇄ Switch project",
                  bg=SURF2, fg=TEXT2, font=("Segoe UI", 9),
                  relief=tk.FLAT, cursor="hand2", padx=8, pady=4,
                  command=self._switch_project
                  ).pack(side=tk.LEFT, padx=8)

        self.paid_btn = tk.Button(
            bar, text="Paid API: OFF",
            bg=SURF2, fg=RED,
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, cursor="hand2", padx=10, pady=4,
            command=self._toggle_paid)
        self.paid_btn.pack(side=tk.RIGHT, padx=12, pady=10)

        self.cost_label = tk.Label(
            bar, text="£0.00 today",
            bg=SURF2, fg=GREEN, font=("Segoe UI", 9), padx=8, pady=4)
        self.cost_label.pack(side=tk.RIGHT, padx=4, pady=10)

    # ── MODEL CARDS ───────────────────────────────────────────────────────────

    def _build_model_cards(self):
        self.cards_frame = tk.Frame(self.root, bg=BG)
        self.cards_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.model_widgets = {}

        for m in MODEL_DEFS:
            card = tk.Frame(self.cards_frame, bg=SURFACE,
                            highlightbackground=BORDER,
                            highlightthickness=1, cursor="hand2")
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

            top = tk.Frame(card, bg=SURFACE)
            top.pack(fill=tk.X, padx=10, pady=(10, 2))
            tk.Label(top, text=m["icon"], bg=SURFACE,
                     font=("Segoe UI", 16)).pack(side=tk.LEFT)
            tk.Label(top, text=m["label"], bg=SURFACE, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=6)

            tk.Label(card, text=m["sub"], bg=SURFACE, fg=TEXT2,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=10)

            status_lbl = tk.Label(card, text="Checking...",
                                  bg=SURFACE, fg=AMBER, font=("Segoe UI", 9))
            status_lbl.pack(anchor="w", padx=10, pady=(2, 2))

            more_btn = tk.Label(card, text="▼ What is this?",
                                bg=SURFACE, fg=TEXT3,
                                font=("Segoe UI", 8), cursor="hand2")
            more_btn.pack(anchor="w", padx=10, pady=(0, 8))

            key = m["key"]
            for w in (card, top, more_btn, status_lbl):
                w.bind("<Button-1>", lambda e, k=key: self._toggle_detail(k))

            self.model_widgets[key] = {
                "card":       card,
                "status_lbl": status_lbl,
                "more_btn":   more_btn,
            }

    # ── DETAIL PANEL ──────────────────────────────────────────────────────────

    def _build_detail_panel(self):
        self.detail_frame = tk.Frame(self.root, bg=SURF3,
                                     highlightbackground=BORDER,
                                     highlightthickness=1)

        self.d_title    = tk.Label(self.detail_frame, bg=SURF3, fg=TEXT,
                                   font=("Segoe UI", 12, "bold"), anchor="w")
        self.d_title.pack(fill=tk.X, padx=14, pady=(12, 2))

        self.d_meta     = tk.Label(self.detail_frame, bg=SURF3, fg=TEXT2,
                                   font=("Segoe UI", 9), anchor="w")
        self.d_meta.pack(fill=tk.X, padx=14, pady=(0, 8))

        self.d_what     = tk.Label(self.detail_frame, bg=SURF3, fg=TEXT,
                                   font=("Segoe UI", 10),
                                   wraplength=800, justify=tk.LEFT, anchor="w")
        self.d_what.pack(fill=tk.X, padx=14, pady=(0, 8))

        self.d_best  = tk.Frame(self.detail_frame, bg=SURF3)
        self.d_best.pack(fill=tk.X, padx=14, pady=(0, 2))

        self.d_not   = tk.Frame(self.detail_frame, bg=SURF3)
        self.d_not.pack(fill=tk.X, padx=14, pady=(0, 2))

        self.d_ex    = tk.Frame(self.detail_frame, bg=SURF3)
        self.d_ex.pack(fill=tk.X, padx=14, pady=(0, 14))

    def _toggle_detail(self, key):
        if self.expanded_key == key:
            self.detail_frame.pack_forget()
            self.expanded_key = None
            for k, w in self.model_widgets.items():
                w["more_btn"].config(text="▼ What is this?", fg=TEXT3)
                w["card"].config(highlightbackground=BORDER)
            return

        self.expanded_key = key
        m = next(x for x in MODEL_DEFS if x["key"] == key)

        for k, w in self.model_widgets.items():
            if k == key:
                w["more_btn"].config(text="▲ Hide info", fg=ACCENT)
                w["card"].config(highlightbackground=ACCENT)
            else:
                w["more_btn"].config(text="▼ What is this?", fg=TEXT3)
                w["card"].config(highlightbackground=BORDER)

        self.d_title.config(text=f"{m['icon']}  {m['label']}  —  {m['cost']}")
        self.d_meta.config(
            text=f"Model: {m['model']}   |   Provider: {m['provider']}   |   Disk: {m['size']}")
        self.d_what.config(text=m["what_is"])

        for frame in (self.d_best, self.d_not, self.d_ex):
            for w in frame.winfo_children():
                w.destroy()

        tk.Label(self.d_best, text="Best for:",
                 bg=SURF3, fg=GREEN,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        for item in m["best_for"]:
            tk.Label(self.d_best, text=f"  ✓  {item}",
                     bg=SURF3, fg=TEXT, font=("Segoe UI", 9),
                     wraplength=800, justify=tk.LEFT).pack(anchor="w")

        tk.Label(self.d_not, text="Not ideal for:",
                 bg=SURF3, fg=AMBER,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0))
        for item in m["not_for"]:
            tk.Label(self.d_not, text=f"  –  {item}",
                     bg=SURF3, fg=TEXT2, font=("Segoe UI", 9),
                     wraplength=800, justify=tk.LEFT).pack(anchor="w")

        tk.Label(self.d_ex, text="Click an example to use it:",
                 bg=SURF3, fg=PURPLE,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0))
        for item in m["examples"]:
            row = tk.Frame(self.d_ex, bg=SURF3, cursor="hand2")
            row.pack(fill=tk.X, pady=1)
            lbl = tk.Label(row, text=f'  → "{item}"',
                           bg=SURF3, fg=TEXT2,
                           font=("Segoe UI", 9, "italic"),
                           wraplength=780, justify=tk.LEFT,
                           cursor="hand2")
            lbl.pack(side=tk.LEFT)
            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, t=item: self._paste_example(t))

        self.detail_frame.pack(fill=tk.X, padx=10, pady=(4, 0),
                               after=self.cards_frame)

    def _paste_example(self, text):
        self.input_box.delete(0, tk.END)
        self.input_box.insert(0, text)
        self.input_box.config(fg=TEXT)
        self.input_box.focus()

    # ── CHAT ──────────────────────────────────────────────────────────────────

    def _build_chat(self):
        self.chat = scrolledtext.ScrolledText(
            self.root,
            bg=SURFACE, fg=TEXT,
            font=("Segoe UI", 11),
            relief=tk.FLAT, wrap=tk.WORD,
            state=tk.DISABLED,
            padx=14, pady=10,
            highlightbackground=BORDER,
            highlightthickness=1,
            insertbackground=TEXT,
        )
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 0))

        self.chat.tag_config("you",      foreground=TEXT,   font=("Segoe UI", 11))
        self.chat.tag_config("you_name", foreground=TEXT2,  font=("Segoe UI", 9))
        self.chat.tag_config("ai",       foreground=TEXT,   font=("Segoe UI", 11))
        self.chat.tag_config("ai_name",  foreground=PURPLE, font=("Segoe UI", 9, "bold"))
        self.chat.tag_config("step",     foreground=TEXT2,  font=("Segoe UI", 10))
        self.chat.tag_config("step_ok",  foreground=GREEN,  font=("Segoe UI", 10))
        self.chat.tag_config("step_err", foreground=RED,    font=("Segoe UI", 10))

    # ── INPUT ─────────────────────────────────────────────────────────────────

    def _build_input(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill=tk.X, padx=10, pady=10)

        self.input_box = tk.Entry(
            row, bg=SURF2, fg=TEXT,
            font=("Segoe UI", 12), relief=tk.FLAT,
            insertbackground=TEXT,
            highlightbackground=BORDER, highlightthickness=1)
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 8))
        self.input_box.insert(0, "Tell your AI team what to do...")
        self.input_box.config(fg=TEXT2)
        self.input_box.bind("<FocusIn>",  self._clear_ph)
        self.input_box.bind("<FocusOut>", self._restore_ph)
        self.input_box.bind("<Return>",   self._send)

        self.send_btn = tk.Button(
            row, text="Send  →",
            bg=ACCENT, fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=18, pady=10,
            command=self._send)
        self.send_btn.pack(side=tk.RIGHT)

    # ── STATUS BAR ────────────────────────────────────────────────────────────

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status_var,
                 bg=SURFACE, fg=TEXT2, font=("Segoe UI", 9)
                 ).pack(side=tk.LEFT, padx=12)

        self.stats_var = tk.StringVar(value="Free calls: 0  |  Paid: 0")
        tk.Label(bar, textvariable=self.stats_var,
                 bg=SURFACE, fg=TEXT2, font=("Segoe UI", 9)
                 ).pack(side=tk.RIGHT, padx=12)

    # ── WELCOME ───────────────────────────────────────────────────────────────

    def _welcome(self):
        self._ai_say(
            f"Project loaded: {CONFIG['project_name']}\n\n"
            "Click any AI card above to see what it does, what it is good for, "
            "and example tasks — click an example to use it instantly.\n\n"
            "Type anything in the box below and I will pick the right AI automatically."
        )

    # ── ROUTER ────────────────────────────────────────────────────────────────

    def _load_router(self):
        try:
            from model_router import ModelRouter
            self.router = ModelRouter(db_path=DB_PATH, verbose=False)
            self._set_status("AI team connected")
        except FileNotFoundError:
            self._set_status("task_db.json not found — run full_auto_setup.py first")
        except Exception as e:
            self._set_status(f"Router error: {e}")

    def _refresh_model_status(self):
        for m in MODEL_DEFS:
            text, colour = get_model_status(m)
            w = self.model_widgets.get(m["key"])
            if w:
                w["status_lbl"].config(text=text, fg=colour)
        self.root.after(10000, self._refresh_model_status)

    # ── SWITCH PROJECT ────────────────────────────────────────────────────────

    def _switch_project(self):
        folder = filedialog.askdirectory(title="Select project folder")
        if not folder:
            return
        CONFIG["project_path"] = folder
        CONFIG["project_name"] = Path(folder).name
        save_config(CONFIG)
        messagebox.showinfo(
            "Project switched",
            f"Switched to: {CONFIG['project_name']}\n\nRestart the panel to load it.")

    # ── PAID TOGGLE ───────────────────────────────────────────────────────────

    def _toggle_paid(self):
        self.allow_paid = not self.allow_paid
        if self.allow_paid:
            self.paid_btn.config(text="Paid API: ON  ⚠", fg=AMBER)
            if self.router:
                self.router.toggle_paid(True)
            self._ai_say("Paid API is ON. Claude used as last resort. This costs money.")
        else:
            self.paid_btn.config(text="Paid API: OFF", fg=RED)
            if self.router:
                self.router.toggle_paid(False)
            self._ai_say("Paid API is OFF. Free models only.")

    # ── SEND / RUN ────────────────────────────────────────────────────────────

    def _send(self, event=None):
        task = self.input_box.get().strip()
        if not task or task == "Tell your AI team what to do...":
            return
        self.input_box.delete(0, tk.END)
        self._you_say(task)
        self.send_btn.config(state=tk.DISABLED, text="Working...")
        self._set_status("AI team working...")
        threading.Thread(target=self._run_task, args=(task,), daemon=True).start()

    def _run_task(self, task):
        if not self.router:
            self.root.after(0, lambda: self._ai_say(
                "Router not loaded. Run full_auto_setup.py first then restart."))
            self.root.after(0, self._re_enable)
            return

        task_type = self.router.classify_task(task)
        labels = {"vision": "Vision AI 👁", "code": "Code AI 💻",
                  "plan": "Thinking AI 🧠", "fast": "Fast AI ⚡"}
        self.root.after(0, lambda: self._step(
            f"Routing to {labels.get(task_type, task_type)}"))

        models   = self.router.db["task_types"][task_type]["models"]
        free     = [m for m in models if m["cost_per_call"] == 0]
        chain    = " → ".join(self._fname(m["name"]) for m in free)
        self.root.after(0, lambda: self._step(f"Will try (free first): {chain}"))

        try:
            t0       = time.time()
            response = self.router.run(task, verbose=False)
            elapsed  = time.time() - t0

            if response.startswith("ERROR"):
                self.root.after(0, lambda: self._step("All AIs offline", error=True))
                self.root.after(0, lambda: self._ai_say(
                    "Could not reach any AI.\n\n"
                    "Check:\n"
                    "  1. LM Studio is open\n"
                    "  2. Server is running (green button, port 1234)\n"
                    "  3. A model is loaded in LM Studio\n"
                    "  4. Your Groq API key is set for online fallback"))
            else:
                self.free_calls += 1
                self.root.after(0, lambda: self._step(
                    f"Response in {elapsed:.1f}s  ✓", ok=True))
                self.root.after(0, lambda r=response: self._ai_say(r))
                self.root.after(0, self._update_stats)
        except Exception as e:
            self.root.after(0, lambda: self._ai_say(f"Error: {e}"))
        finally:
            self.root.after(0, self._re_enable)
            self.root.after(0, lambda: self._set_status("Ready"))

    def _fname(self, name):
        for k, v in {
            "qwen2.5-coder": "Code AI", "qwen2.5-vl": "Vision AI",
            "deepseek": "Thinking AI", "llama-3.3": "Fast AI",
            "phi-4": "Fast AI (local)", "claude": "Claude (paid)",
        }.items():
            if k in name.lower():
                return v
        return name

    # ── CHAT HELPERS ──────────────────────────────────────────────────────────

    def _append(self, text, tag="ai"):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, text, tag)
        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def _you_say(self, text):
        self._append("\n\nYou\n", "you_name")
        self._append(text + "\n", "you")

    def _ai_say(self, text):
        self._append("\nAI Team\n", "ai_name")
        self._append(text + "\n", "ai")

    def _step(self, text, ok=False, error=False):
        tag    = "step_ok" if ok else ("step_err" if error else "step")
        prefix = "  ✓ " if ok else ("  ✗ " if error else "  → ")
        self._append(prefix + text + "\n", tag)

    def _re_enable(self):
        self.send_btn.config(state=tk.NORMAL, text="Send  →")

    def _set_status(self, text):
        self.status_var.set(text)

    def _update_stats(self):
        self.stats_var.set(
            f"Free calls: {self.free_calls}  |  Paid: {self.paid_calls}")
        self.cost_label.config(
            text=f"£{self.paid_calls * 0.003:.4f} today")

    def _clear_ph(self, e):
        if self.input_box.get() == "Tell your AI team what to do...":
            self.input_box.delete(0, tk.END)
            self.input_box.config(fg=TEXT)

    def _restore_ph(self, e):
        if not self.input_box.get():
            self.input_box.insert(0, "Tell your AI team what to do...")
            self.input_box.config(fg=TEXT2)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    ControlPanel(root)
    root.mainloop()
