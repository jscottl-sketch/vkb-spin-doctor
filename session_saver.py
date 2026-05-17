"""
session_saver.py — Auto session saver for Claude Code projects.
No pip installs needed. Uses ctypes (clipboard) and urllib (Anthropic API).
"""
import ctypes
import json
import sys
import urllib.request
import urllib.error
import webbrowser
from datetime import datetime
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────
HERE         = Path(__file__).parent
CONFIG_FILE  = HERE / "session_saver_config.json"
ENV_FILE     = HERE / ".env"
MODEL        = "claude-haiku-4-5-20251001"
MAX_CHARS    = 30_000   # ~7k tokens — keeps API cost to ~1 penny


# ── Config & .env ────────────────────────────────────────────────────────────

def load_config():
    if not CONFIG_FILE.exists():
        default = {
            "project_name": "My Project",
            "project_folder": str(HERE),
            "claude_project_url": "https://claude.ai/projects"
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        print("\nCreated session_saver_config.json")
        print("Edit 'project_name' and 'claude_project_url', then run again.")
        input("\nPress Enter to close...")
        sys.exit(0)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_api_key():
    """Read ANTHROPIC_API_KEY from .env — no pip install needed."""
    if not ENV_FILE.exists():
        return ""
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY") and "=" in line:
                _, _, val = line.partition("=")
                return val.strip().strip('"').strip("'")
    return ""


# ── Clipboard (ctypes — Windows only, no pip install) ────────────────────────

def get_clipboard():
    CF_UNICODETEXT = 13
    u = ctypes.windll.user32
    k = ctypes.windll.kernel32
    if not u.OpenClipboard(0):
        return ""
    try:
        h = u.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return ""
        ptr = k.GlobalLock(h)
        if not ptr:
            return ""
        try:
            return ctypes.wstring_at(ptr)
        finally:
            k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()


def set_clipboard(text):
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE  = 0x0002
    u = ctypes.windll.user32
    k = ctypes.windll.kernel32
    encoded = (text + "\x00").encode("utf-16-le")
    h = k.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
    ptr = k.GlobalLock(h)
    ctypes.memmove(ptr, encoded, len(encoded))
    k.GlobalUnlock(h)
    if u.OpenClipboard(0):
        u.EmptyClipboard()
        u.SetClipboardData(CF_UNICODETEXT, h)
        u.CloseClipboard()


# ── Anthropic API (urllib — no pip install) ──────────────────────────────────

SUMMARY_PROMPT = """\
You are summarising a Claude Code session for the project "{project}".

Read the chat log below and produce ONLY these six sections in markdown. \
Use bullet points. Name specific files and reasons. Write "None." if a section is empty. \
Output nothing before or after the six sections.

## What Was Built / Changed

## Decisions Made

## Ideas to Note

## Acca Codes / Ratings
(Acca Codes: WMBW = Why Might Be Wrong, CR = Confidence Rating, Y.O = Your Opinion)

## Next Steps

## Blockers

CHAT LOG:
{chat}"""


def call_claude(api_key, chat_text, project_name):
    truncated = chat_text[:MAX_CHARS]
    if len(chat_text) > MAX_CHARS:
        truncated += "\n\n[...truncated to keep cost low...]"

    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": SUMMARY_PROMPT.format(project=project_name, chat=truncated)
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        method="POST",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"], None
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8", errors="replace")
        return None, f"HTTP {e.code}: {body_err[:200]}"
    except Exception as exc:
        return None, str(exc)


# ── Manual questions (fallback) ──────────────────────────────────────────────

def ask(prompt, optional=False):
    tag = "  (just press Enter to skip)" if optional else ""
    print(f"\n  {prompt}{tag}")
    print("  " + "─" * 50)
    print("  Type answer, press Enter twice when done.")
    lines = []
    while True:
        line = input("  ")
        if line == "" and (not lines or lines[-1] == ""):
            break
        lines.append(line)
    return "\n".join(lines).strip()


def run_manual_questions():
    print("\n" + "─" * 55)
    print("  MANUAL QUESTIONS  (6 of 6)")
    print("─" * 55)

    built      = ask("[ Q1 ]  What did you BUILD or CHANGE this session?")
    decisions  = ask("[ Q2 ]  What DECISIONS did you make? (and why?)")
    ideas      = ask("[ Q3 ]  Any IDEAS to note for later?", optional=True)
    print("\n  Acca Codes: WMBW=Why Might Be Wrong  CR=Confidence Rating  Y.O=Your Opinion")
    acca       = ask("[ Q4 ]  Any ACCA CODES or ratings?", optional=True)
    next_steps = ask("[ Q5 ]  What are the NEXT STEPS for next session?")
    blockers   = ask("[ Q6 ]  Any BLOCKERS?", optional=True)

    return dict(built=built, decisions=decisions, ideas=ideas,
                acca=acca, next_steps=next_steps, blockers=blockers)


def format_manual(a):
    def s(h, v): return f"## {h}\n{v if v else 'None.'}\n"
    return "\n".join([
        s("What Was Built / Changed", a["built"]),
        s("Decisions Made",           a["decisions"]),
        s("Ideas to Note",            a["ideas"]),
        s("Acca Codes / Ratings",     a["acca"]),
        s("Next Steps",               a["next_steps"]),
        s("Blockers",                 a["blockers"]),
    ])


# ── File helper ──────────────────────────────────────────────────────────────

def save_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    config         = load_config()
    project_name   = config.get("project_name",       "Unknown Project")
    project_folder = Path(config.get("project_folder", HERE))
    project_url    = config.get("claude_project_url",  "https://claude.ai/projects")
    api_key        = load_api_key()

    now          = datetime.now()
    ts           = now.strftime("%Y-%m-%d_%H-%M")
    date_display = now.strftime("%d %B %Y at %H:%M")

    print("\n" + "=" * 55)
    print(f"  SESSION SAVER  —  {project_name}")
    print(f"  {date_display}")
    print("=" * 55)

    # ────────────────────────────────────────────────────────────
    # STEP 1  Copy the Claude chat
    # ────────────────────────────────────────────────────────────
    print("\n[ STEP 1 of 5 ]  Copy your Claude chat")
    print("─" * 55)
    print("  1. Click your Claude chat tab  (Alt+Tab or taskbar)")
    print("  2. Press  Ctrl + A  to select all")
    print("  3. Press  Ctrl + C  to copy")
    print("  4. Click back to this window")
    input("\n  Done? Press Enter here to read the clipboard: ")

    chat_text  = get_clipboard()
    chat_saved = False

    if len(chat_text) >= 100:
        chat_file = project_folder / "chat_logs" / f"chat_{ts}.txt"
        save_file(chat_file, chat_text)
        print(f"\n  Captured {len(chat_text):,} characters.")
        print(f"  Saved  ->  chat_logs/chat_{ts}.txt")
        chat_saved = True
    else:
        print("\n  Clipboard looks empty or too short.")
        print("  Tip: click the Claude page first, then Ctrl+A, Ctrl+C.")
        retry = input("  Press Enter to try again, or type SKIP: ").strip().upper()
        if retry != "SKIP":
            chat_text = get_clipboard()
            if len(chat_text) >= 100:
                chat_file = project_folder / "chat_logs" / f"chat_{ts}.txt"
                save_file(chat_file, chat_text)
                print(f"  Captured {len(chat_text):,} characters.")
                chat_saved = True
            else:
                print("  Still empty — continuing without chat.")
                chat_text = ""

    # ────────────────────────────────────────────────────────────
    # STEP 2  Generate AI summary
    # ────────────────────────────────────────────────────────────
    print("\n[ STEP 2 of 5 ]  Generating AI summary")
    print("─" * 55)

    summary_text = ""
    api_used     = False

    if not api_key:
        print("  No ANTHROPIC_API_KEY found in .env — skipping AI step.")
    elif not chat_saved:
        print("  No chat captured — skipping AI step.")
    else:
        print(f"  Sending to Claude Haiku (~1 penny)... ", end="", flush=True)
        summary_text, err = call_claude(api_key, chat_text, project_name)
        if summary_text:
            print("done!")
            api_used = True
        else:
            print(f"failed.\n  Error: {err}")
            print("  Will use manual questions instead.")

    # ────────────────────────────────────────────────────────────
    # STEP 3  Manual questions (fallback or extra notes)
    # ────────────────────────────────────────────────────────────
    print("\n[ STEP 3 of 5 ]  Notes")
    print("─" * 55)

    manual_answers = None

    if not api_used:
        print("  No AI summary — please answer the 6 questions.")
        manual_answers = run_manual_questions()
    else:
        add = input("  AI summary ready! Add manual notes on top? (Y / Enter to skip): ").strip().upper()
        if add == "Y":
            manual_answers = run_manual_questions()

    # ────────────────────────────────────────────────────────────
    # STEP 4  Save files
    # ────────────────────────────────────────────────────────────
    print("\n[ STEP 4 of 5 ]  Saving files")
    print("─" * 55)

    core_body = summary_text if api_used else format_manual(manual_answers)

    extra_block = ""
    if manual_answers and api_used:
        extra_block = "\n---\n\n## Extra Notes (Added Manually)\n\n" + format_manual(manual_answers)

    footer_lines = ["---"]
    if chat_saved:
        footer_lines.append(f"_Chat log:    chat_logs/chat_{ts}.txt_")
    footer_lines.append(f"_Session log: session_logs/session_{ts}.md_")
    footer = "\n".join(footer_lines)

    session_content = "\n".join([
        f"# Session Log — {project_name}",
        f"_Date: {date_display}_",
        "",
        "---",
        "",
        core_body,
        extra_block,
        "",
        footer,
    ])

    handover_content = "\n".join([
        f"# Latest Handover — {project_name}",
        f"_Last updated: {date_display}_",
        "",
        "> Auto-updated by session_saver.py after each session.",
        "",
        "---",
        "",
        core_body,
        extra_block,
        "",
        footer,
    ])

    session_file  = project_folder / "session_logs" / f"session_{ts}.md"
    handover_file = project_folder / "handover" / "LATEST_HANDOVER.md"

    save_file(session_file,  session_content)
    save_file(handover_file, handover_content)

    print(f"  Session log  ->  session_logs/session_{ts}.md")
    print(f"  Handover     ->  handover/LATEST_HANDOVER.md")

    # ────────────────────────────────────────────────────────────
    # STEP 5  Copy path + open upload page
    # ────────────────────────────────────────────────────────────
    print("\n[ STEP 5 of 5 ]  Upload to Claude project")
    print("─" * 55)

    handover_abs = str(handover_file.resolve())
    set_clipboard(handover_abs)
    print(f"  File path copied to clipboard:")
    print(f"  {handover_abs}")
    print(f"\n  Opening browser -> {project_url}")
    webbrowser.open(project_url)
    print("  In Claude: click Add content > Upload file > Ctrl+V to paste the path.")

    # ────────────────────────────────────────────────────────────
    # Done
    # ────────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  ALL DONE!")
    print("=" * 55)
    print(f"  AI summary : {'YES  (Claude Haiku, ~1p)' if api_used else 'NO   (manual answers used)'}")
    print(f"  Chat saved : {'YES' if chat_saved else 'NO'}")
    print(f"  Handover   : handover/LATEST_HANDOVER.md")
    print(f"  Session    : session_logs/session_{ts}.md")
    print("\n  Great work today. See you next session!")
    print("=" * 55)
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
