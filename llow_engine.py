"""
llow_engine.py — Loop Law Organiser Window (LLOW) Engine.
Manages LLOW workflows: create, validate, export as CLACR, save/load.
"""
import datetime
import json
import uuid
from pathlib import Path

HERE = Path(__file__).parent
ELEMENTS_FILE  = HERE / "data" / "llow_elements.json"
ARROWS_FILE    = HERE / "data" / "llow_arrows.json"
WORKFLOWS_DIR  = HERE / "data" / "llow_workflows"


class LLOWEngine:
    def __init__(self):
        with open(ELEMENTS_FILE, encoding="utf-8") as f:
            self.elements = json.load(f)
        with open(ARROWS_FILE, encoding="utf-8") as f:
            self.arrow_types = json.load(f)["arrows"]

        # Flat lookup: element_id → {id, name, desc, category, colour, icon}
        self._el_map: dict = {}
        for cat_name, cat in self.elements.get("categories", {}).items():
            for el in cat.get("elements", []):
                self._el_map[el["id"]] = {
                    **el,
                    "category": cat_name,
                    "colour": cat.get("colour", "#888"),
                    "icon": cat.get("icon", ""),
                }

        # Arrow type lookup
        self._arrow_map = {a["id"]: a for a in self.arrow_types}

        WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Workflow creation ─────────────────────────────────────────────────────

    def create_workflow(self, name: str) -> dict:
        return {
            "name": name,
            "steps": [],
            "arrows": [],
            "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        }

    # ── Step management ───────────────────────────────────────────────────────

    def add_step(self, workflow: dict, element_id: str,
                 position_x: int, position_y: int, params: dict | None = None) -> str:
        if element_id not in self._el_map:
            raise ValueError(f"Unknown element_id: {element_id}")
        step_id = f"step-{uuid.uuid4().hex[:8]}"
        workflow["steps"].append({
            "id": step_id,
            "element_id": element_id,
            "x": position_x,
            "y": position_y,
            "params": params or {},
        })
        return step_id

    # ── Arrow management ──────────────────────────────────────────────────────

    def add_arrow(self, workflow: dict, from_step_id: str, to_step_id: str,
                  arrow_type: str, params: dict | None = None) -> str:
        step_ids = {s["id"] for s in workflow["steps"]}
        if from_step_id not in step_ids:
            raise ValueError(f"Unknown from_step_id: {from_step_id}")
        if to_step_id not in step_ids:
            raise ValueError(f"Unknown to_step_id: {to_step_id}")
        if arrow_type not in self._arrow_map:
            raise ValueError(f"Unknown arrow_type: {arrow_type}")

        params = params or {}
        arrow_def = self._arrow_map[arrow_type]
        for req_param in arrow_def.get("params", {}):
            if req_param not in params:
                params[req_param] = None  # fill with None — UI sets values

        arrow_id = f"arrow-{uuid.uuid4().hex[:8]}"
        workflow["arrows"].append({
            "id": arrow_id,
            "from": from_step_id,
            "to": to_step_id,
            "arrow_type": arrow_type,
            "params": params,
        })
        return arrow_id

    # ── Validation ────────────────────────────────────────────────────────────

    def validate_workflow(self, workflow: dict) -> tuple[bool, list[str]]:
        steps   = workflow.get("steps", [])
        arrows  = workflow.get("arrows", [])
        valid   = True
        warns   = []

        # 1. Must have at least one step
        if not steps:
            return False, ["Workflow has no steps"]

        step_ids = {s["id"] for s in steps}

        # Build adjacency list
        adj: dict = {sid: [] for sid in step_ids}
        for a in arrows:
            if a["from"] in adj:
                adj[a["from"]].append(a["to"])

        # 2. Check reachability from first step via BFS
        first_id = steps[0]["id"]
        visited: set = set()
        queue = [first_id]
        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            queue.extend(adj.get(curr, []))

        orphans = step_ids - visited
        if orphans:
            valid = False
            warns.append(f"{len(orphans)} orphaned step(s) not reachable from the first step")

        # 3. Every branch arrow needs at least 2 outgoing arrows from that step
        for a in arrows:
            if a.get("arrow_type") == "branch":
                out_count = sum(1 for x in arrows if x["from"] == a["from"])
                if out_count < 2:
                    valid = False
                    warns.append(
                        f"Branch arrow from step '{a['from']}' needs a second path defined"
                    )

        # 4. Must have an ending step
        ending_ids = set()
        for cat_name, cat in self.elements.get("categories", {}).items():
            if cat_name == "endings":
                for el in cat.get("elements", []):
                    ending_ids.add(el["id"])
        has_ending = any(s["element_id"] in ending_ids for s in steps)
        if not has_ending:
            valid = False
            warns.append(
                "No ending step — add WCCS_END, SESUM_END, CNP, or HARD_STOP"
            )

        # 5. ALP gate warning if >5 steps
        if len(steps) > 5:
            alp_element_ids = {"ALP", "ALP_GATE"}
            alp_arrow_types = {"alp_gate"}
            has_alp = any(s["element_id"] in alp_element_ids for s in steps) or \
                      any(a["arrow_type"] in alp_arrow_types for a in arrows)
            if not has_alp:
                warns.append(
                    "WARNING: >5 steps but no ALP gate found — add one to protect allowance"
                )

        return valid, warns

    # ── CLACR export ─────────────────────────────────────────────────────────

    def export_as_clacr(self, workflow: dict) -> str:
        steps  = workflow.get("steps", [])
        arrows = workflow.get("arrows", [])
        name   = workflow.get("name", "Unnamed Workflow")

        if not steps:
            return f"# CLAC Request — {name}\n\n(Empty workflow)\n"

        # Outgoing arrows per step
        out: dict = {}
        for a in arrows:
            out.setdefault(a["from"], []).append(a)

        # BFS traversal order from first step
        ordered: list[str] = []
        visited: set = set()
        queue = [steps[0]["id"]]
        step_map = {s["id"]: s for s in steps}
        while queue:
            sid = queue.pop(0)
            if sid in visited:
                continue
            visited.add(sid)
            ordered.append(sid)
            for a in out.get(sid, []):
                if a["to"] not in visited:
                    queue.append(a["to"])

        step_nums = {sid: i + 1 for i, sid in enumerate(ordered)}

        lines = [
            f"# CLAC Request — {name}",
            f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]

        for sid in ordered:
            step = step_map.get(sid, {})
            el   = self._el_map.get(step.get("element_id", ""), {})
            n    = step_nums[sid]
            cat  = el.get("category", "")
            el_name = el.get("name", step.get("element_id", "?"))
            el_desc = el.get("desc", "")

            if cat == "modes":
                lines.append(f"{n}. Set mode: {el_name} — {el_desc}")
            elif cat == "approval_gates":
                p = step.get("params", {})
                threshold = p.get("threshold", "")
                thresh_str = f" (threshold: {threshold})" if threshold else ""
                lines.append(
                    f"{n}. STOP — approval gate: {el_name}{thresh_str}"
                    f" — wait for approval before continuing"
                )
            elif cat == "endings":
                lines.append(f"{n}. END — {el_name}: {el_desc}")
            else:
                lines.append(f"{n}. {el_name}: {el_desc}")

            # Arrow flow control annotations
            for a in out.get(sid, []):
                target_n = step_nums.get(a["to"], "?")
                atype = a.get("arrow_type", "continue")
                p = a.get("params", {})

                if atype == "continue":
                    pass  # no annotation needed
                elif atype == "loop_back":
                    lines.append("   ↺ Loop back to step 1")
                elif atype == "jump_back":
                    n_steps = p.get("n") or 1
                    lines.append(f"   ⤴ Jump back {n_steps} step(s)")
                elif atype == "jump_forward":
                    n_steps = p.get("n") or 1
                    lines.append(f"   ⤵ Skip forward {n_steps} step(s) to step {target_n}")
                elif atype == "repeat":
                    times = p.get("n") or 1
                    lines.append(f"   🔁 Repeat this section ×{times}")
                elif atype == "branch":
                    cond = p.get("condition") or "condition"
                    lines.append(f"   🔀 IF {cond}: go to step {target_n}")
                elif atype == "pause":
                    lines.append("   ⏸ PAUSE — wait for user input before continuing")
                elif atype == "hard_stop":
                    lines.append("   ⛔ HARD STOP — end loop immediately")
                elif atype == "alp_gate":
                    min_pct = p.get("min_pct") or 20
                    lines.append(f"   ⚠ ALP Safety Gate: STOP if ALP below {min_pct}%")
                elif atype == "approval":
                    lines.append(
                        f"   👍 APPROVAL GATE → step {target_n} — "
                        "stop here until approved"
                    )
                elif atype == "timer":
                    secs = p.get("seconds") or 60
                    lines.append(f"   🕒 Wait {secs}s before continuing")
                elif atype == "scheduled":
                    dt = p.get("datetime") or "specified time"
                    lines.append(f"   📅 Wait until {dt}")
                elif atype == "ab_split":
                    lines.append(
                        f"   🧪 A/B Split → run two paths in parallel, compare at step {target_n}"
                    )
                elif atype == "trigger":
                    lines.append(f"   ⚡ Trigger → step {target_n}")
                elif atype == "checkpoint":
                    lines.append("   🎯 Checkpoint — save progress marker")
                else:
                    lines.append(f"   → Continue to step {target_n}")

        lines += ["", "# END OF CLAC REQUEST"]
        return "\n".join(lines)

    # ── Persistence ───────────────────────────────────────────────────────────

    def save_workflow(self, workflow: dict, filename: str) -> Path:
        WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
        if not filename.endswith(".json"):
            filename += ".json"
        path = WORKFLOWS_DIR / filename
        path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load_workflow(self, filename: str) -> dict:
        if not filename.endswith(".json"):
            filename += ".json"
        path = WORKFLOWS_DIR / filename
        return json.loads(path.read_text(encoding="utf-8"))

    def list_workflows(self) -> list[dict]:
        result = []
        for p in sorted(WORKFLOWS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                wf = json.loads(p.read_text(encoding="utf-8"))
                result.append({
                    "filename": p.name,
                    "name": wf.get("name", p.stem),
                    "step_count": len(wf.get("steps", [])),
                    "created_at": wf.get("created_at", ""),
                    "modified": datetime.datetime.fromtimestamp(
                        p.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                })
            except Exception:
                pass
        return result

    def delete_workflow(self, filename: str) -> bool:
        if not filename.endswith(".json"):
            filename += ".json"
        path = WORKFLOWS_DIR / filename
        if path.exists():
            path.unlink()
            return True
        return False


if __name__ == "__main__":
    engine = LLOWEngine()
    all_elements = []
    for cat in engine.elements.get("categories", {}).values():
        all_elements.extend(cat.get("elements", []))
    print(f"LLOW Engine loaded. Elements: {len(all_elements)}, Arrow types: {len(engine.arrow_types)}")
