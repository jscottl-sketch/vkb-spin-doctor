
### 1.2 Shared “input‑core” Library  

| Folder | Purpose |
|--------|---------|
| `src/InputCore` | Core abstractions (interfaces, event queue, state snapshot). |
| `src/InputCore/Models` | POCOs for keyboard, joystick, OSC events. |
| `src/InputCore/Services` | Thread‑safe queue, event dispatcher, state manager. |
| `src/InputCore/Providers` | SDL provider, OSC provider, future platform providers. |

#### 1.2.1 Example `IInputEvent`  

