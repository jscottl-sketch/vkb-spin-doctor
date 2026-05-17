import json, re
from pathlib import Path
P = Path(r"C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor")

# Fix 2: Coder first in task_db.json
p = P/"task_db.json"
db = json.loads(p.read_text(encoding="utf-8"))
for t in db.get("task_types",{}).values():
    m = t.get("models",[])
    n = [x.get("name","") for x in m]
    c = "qwen2.5-coder-32b-instruct"
    if c in n and n[0]!=c:
        m.insert(0,m.pop(n.index(c)))
        t["models"]=m
p.write_text(json.dumps(db,indent=2),encoding="utf-8")
print("[OK] Fix 2 - Coder first")

# Fix 3: Unicode in model_router.py
p2 = P/"model_router.py"
t2 = p2.read_text(encoding="utf-8",errors="replace")
p2.write_text(re.sub(r"[\u2500-\u257F\u2550-\u256C]","-",t2),encoding="utf-8")
print("[OK] Fix 3 - Unicode cleaned")

# Fix 6: sfl_agent handover reference
p3 = P/"sfl_agent.py"
t3 = p3.read_text(encoding="utf-8")
p3.write_text(re.sub(r"VKB_SpinDoctor_Handover_v\d+\.md","VKB_SpinDoctor_Handover_v16.md",t3),encoding="utf-8")
print("[OK] Fix 6 - sfl_agent updated")
print("[DONE]")
