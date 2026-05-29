
*For a Python service replace the handler with a Flask view.*

### 3. Validation Layer
* Use Go struct tags or a tiny validator library to assure the value fits in 64 bits – the parser already enforces that.  
* Reject any payload that contains non‑numeric characters (apart from optional `0x`).  
* Return `400 Bad Request` with a plain‑text error (no JSON to respect the “not JSON” goal).

### 4. Input Injection Core
Create a thread‑safe singleton that holds the current input mask and pushes changes to the simulation loop.

