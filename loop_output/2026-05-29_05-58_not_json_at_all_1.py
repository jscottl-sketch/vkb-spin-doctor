
### 1.2 Design the payload (reference only – no JSON in this doc)
- **Root object** – `keyboard` (array of objects) and `joystick` (single object).  
- **Keyboard entry** – `{code: <int>, down: <bool>, ts: <epoch‑ms>}`  
- **Joystick object** – `{x: <float -1…1>, y: <float -1…1>, buttons: [<bool>, …], ts: <epoch‑ms>}`  
- Validation rules are enforced in code (see §1.5).

### 1.3 Add the REST controller

Create a new file `src/controllers/input.controller.ts` (or the equivalent for your language).

