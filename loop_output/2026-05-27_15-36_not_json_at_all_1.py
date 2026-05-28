
### 1.2. Locate the existing input engine  

*File:* `src/Emulator/Core/InputHandler.cs`  
*Key method:* `public void InjectU64(uint64_t eventMask)` – this is the entry point used by the emulator to receive raw U64‑class input events.

The class `U64InputEvent` (in `src/Emulator/Models/U64InputEvent.cs`) defines the bit‑field layout:

| Bits | Meaning                      |
|------|------------------------------|
| 0‑7  | Keyboard scan‑code           |
| 8    | Keyboard press/release flag  |
| 9‑15 | Reserved                      |
| 16‑23| Joystick axis X (signed)      |
| 24‑31| Joystick axis Y (signed)      |
| 32‑39| Joystick button mask (bits)   |
| 40‑63| Reserved for future extensions|

### 1.3. API design (no JSON in the plan)

| Verb | Route                     | Purpose                     |
|------|---------------------------|-----------------------------|
| GET  | `/v1/machine:input`       | Return the current snapshot of the input state. |
| POST | `/v1/machine:input`       | Accept a payload that describes a keyboard or joystick action and inject it into the emulator. |

**Payload description (plain‑text, application/json)**  

