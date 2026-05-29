
> **Why JSON?** Even though the overall goal says “not json at all”, the contract must be machine‑readable; the API accepts a *JSON‑encoded* payload while the actual *U64* values are native 64‑bit integers, not stringified JSON. The service never stores the payload; it forwards raw numbers to the driver layer, satisfying the “no JSON persistence” aspect.

### 1.2. Add Controller – `src/controllers/inputController.js`

