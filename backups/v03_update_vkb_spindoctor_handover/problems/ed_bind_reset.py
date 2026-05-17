"""
problems/ed_bind_reset.py  —  Module 07: ED Bind Reset Prevention
=================================================================
Part of VKB Spin Doctor (Universal Input Device Assistant).

WHAT THIS MODULE DOES
---------------------
Elite Dangerous silently overwrites the player's custom .binds file after
game updates, wiping every keybinding. This module renames the custom
file to add a "_PROTECTED" suffix before the .binds extension. ED only
overwrites files it created itself, so a renamed file is left alone.

Trade-off (the user is warned in the GUI before applying):
  After protection, ED no longer recognises the file as its active preset
  and will revert to defaults until the user renames it back or imports
  the protected file manually.

API CONTRACT
------------
scan()           -> dict
    Inspect the user's Bindings folder and report what's there.
    Keys returned:
        status:      "no_folder" | "no_custom" | "found" | "already"
        folder:      Path to the Bindings folder
        unprotected: list[Path] — custom .binds files needing protection
        protected:   list[Path] — files already renamed _PROTECTED

protect(path)    -> (bool, Path-or-str)
    Rename a single .binds file, inserting _PROTECTED before the suffix.
    Returns (True, new_path) on success, (False, error_message) otherwise.

protect_all(paths) -> (int, list[(name, error)])
    Apply protect() to every path. Returns (renamed_count, errors_list).

Stdlib only. No external packages.
"""

import os
from pathlib import Path


ED_USER_BINDINGS = (Path(os.environ.get("LOCALAPPDATA", ""))
                    / "Frontier Developments" / "Elite Dangerous"
                    / "Options" / "Bindings")

PROTECTED_SUFFIX = "_PROTECTED"


def _is_protected(p):
    return p.suffix.lower() == ".binds" and PROTECTED_SUFFIX in p.stem


def _is_custom_unprotected(p):
    return p.suffix.lower() == ".binds" and PROTECTED_SUFFIX not in p.stem


def scan():
    folder = ED_USER_BINDINGS
    result = {
        "status": "",
        "folder": folder,
        "unprotected": [],
        "protected": [],
    }

    if not folder.is_dir():
        result["status"] = "no_folder"
        return result

    binds = sorted(folder.glob("*.binds"))
    result["protected"]   = [b for b in binds if _is_protected(b)]
    result["unprotected"] = [b for b in binds if _is_custom_unprotected(b)]

    if result["unprotected"]:
        result["status"] = "found"
    elif result["protected"]:
        result["status"] = "already"
    else:
        result["status"] = "no_custom"

    return result


def protect(filepath):
    src = Path(filepath)
    if not src.exists():
        return False, f"File not found: {src.name}"
    if _is_protected(src):
        return False, f"Already protected: {src.name}"

    dest = src.with_name(src.stem + PROTECTED_SUFFIX + src.suffix)
    if dest.exists():
        return False, f"Target already exists: {dest.name}"

    src.rename(dest)
    return True, dest


def protect_all(filepaths):
    renamed = 0
    errors = []
    for fp in filepaths:
        ok, msg = protect(fp)
        if ok:
            renamed += 1
        else:
            errors.append((Path(fp).name, msg))
    return renamed, errors
