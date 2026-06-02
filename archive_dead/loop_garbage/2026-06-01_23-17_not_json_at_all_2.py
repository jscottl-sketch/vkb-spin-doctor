
1. **Locate the JSON schema** – Typically found under `src/joystick/mappings/` (e.g., `default_profiles.json`).  
2. **Identify all code paths** that read/write this file:  
   - `MappingLoader` (loads JSON at start‑up).  
   - UI mapper (reads JSON for UI generation).  
   - Auto‑load logic (searches `*.json` in a config directory).  

Document each reference in a spreadsheet or markdown table (`docs/json‑references.md`). This list will be required for the later code migration.

---

## 3. Decide on a Replacement Format  

Because the goal is “not JSON at all,” we will adopt **YAML** (human‑readable, fully supported by the existing Python/C++ ecosystem) as the new profile format.

*Advantages*:  
- Retains structure (maps → arrays → scalars).  
- Easy to edit without commas/quotes, aligning with the “no‑JSON” goal.  
- Existing libraries (`yaml-cpp` for C++, `PyYAML` for Python) parse it with minimal code changes.

Create a new directory `src/joystick/mappings_yaml/` for the YAML versions.

---

## 4. Convert Existing JSON Profiles to YAML  

