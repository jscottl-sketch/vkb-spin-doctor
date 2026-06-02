
### B. API design (OpenAPI / Swagger)

Create a file named `api/v1/input.yaml` in the repo (or `docs/openapi.yaml`).  
The spec defines two endpoints:

| Method | Path                     | Purpose |
|--------|--------------------------|-------------------------------------------------------------------|
| GET    | `/v1/machine:input`      | Returns the current input state (pressed keys, joystick axes/buttons). |
| POST   | `/v1/machine:input`      | Accepts a payload that describes a set of key‑presses or joystick actions to be injected into the input pipeline. |

**Key points to embed in the spec (written as comments in the YAML):**  

* **Allowed key codes** – use the U64‑class enumeration (`Key.A`, `Key.Shift`, …).  
* **Joystick IDs** – numeric IDs starting at `0`.  
* **Axes** – floating‑point values in the range `[-1.0, +1.0]`.  
* **Buttons** – binary (0/1) per button index.  

You can later generate client stubs with `swagger-codegen` or `openapi-generator`.

### C. Server stub (example in C# ASP.NET Core)

Create a new controller under `src/YourProject.Api/Controllers/InputController.cs`:

