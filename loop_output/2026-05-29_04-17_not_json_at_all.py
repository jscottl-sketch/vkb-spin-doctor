
---

## 2️⃣  Design the Keyboard & Joystick REST API  

### 2.1 Data model  
- **`uint64_t`** (full 64‑bit) encodes all inputs.  
- **Bit layout (example, can be tweaked later)**  

| Bits | Meaning                     |
|------|----------------------------|
| 0‑31 | Keyboard – one‑hot per key (e.g., bit 0 = ‘A’, bit 1 = ‘B’, …) |
| 32‑63| Joystick – 8 axes (4 bits each) + 16 buttons (1 bit each)      |

### 2.2 API contract (OpenAPI 3.0) – saved as `api/v1/input.yaml`

