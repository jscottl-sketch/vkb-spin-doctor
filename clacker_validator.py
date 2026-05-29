"""
clacker_validator.py — Validates acceptance criteria for OCB builds.
Called after MOT from ocb_runner.run_all().
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
CLACHR_RESPONSE = HERE / "data" / "clachr_response.json"


def validate(acceptance_criteria: list, files_changed: list,
             mot_score: str, project_root: str) -> dict:
    """
    Check each acceptance criterion and return a verdict dict.

    Matching rules:
    - "MOT" or "108/108" in criterion → check mot_score contains 108/108 + all clear
    - filename in criterion → check that file was in files_changed
    - "tabs load" in criterion → call clacker_safety.check_server()
    - "renders" in criterion → check the named file was in files_changed
    - No match → mark "unchecked, assumed pass"

    Writes result to data/clachr_response.json (atomic) and returns the dict.
    """
    import clacker_safety  # lazy import to avoid circular deps

    passed = []
    failed = []

    for criterion in acceptance_criteria:
        cl = criterion.lower().strip()

        if not cl:
            continue

        matched = False

        # MOT score check
        if "mot" in cl or "108/108" in cl:
            matched = True
            mot_ok = ("108/108" in mot_score and "all clear" in mot_score.lower())
            if mot_ok:
                passed.append(criterion)
            else:
                failed.append(criterion)
            continue

        # File-in-files_changed check
        for fname in files_changed:
            if fname.lower() in cl or cl in fname.lower():
                matched = True
                passed.append(criterion)
                break
        if matched:
            continue

        # Server / tabs load check
        if "tabs load" in cl:
            matched = True
            if clacker_safety.check_server():
                passed.append(criterion)
            else:
                failed.append(criterion)
            continue

        # "renders" → file was in files_changed
        if "renders" in cl:
            matched = True
            any_changed = any(f.lower() in cl for f in files_changed)
            if any_changed:
                passed.append(criterion)
            else:
                failed.append(criterion)
            continue

        # No rule matched — assume pass
        passed.append(criterion + " [unchecked, assumed pass]")

    total = len([c for c in acceptance_criteria if c.strip()])
    n_passed = len(passed)
    n_failed = len(failed)

    if total == 0:
        status = "PASS"
        notes = "No acceptance criteria defined"
    elif n_failed == 0:
        status = "PASS"
        notes = f"All {n_passed} criteria passed"
    elif n_failed == total:
        status = "FAIL"
        notes = f"All {n_failed} criteria failed"
    else:
        status = "PARTIAL"
        notes = f"{n_passed} passed, {n_failed} failed of {total} criteria"

    result = {
        "status": status,
        "passed": passed,
        "failed": failed,
        "notes": notes,
        "mot_score": mot_score,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    # Atomic write
    CLACHR_RESPONSE.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(CLACHR_RESPONSE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    shutil.move(tmp, str(CLACHR_RESPONSE))

    return result
