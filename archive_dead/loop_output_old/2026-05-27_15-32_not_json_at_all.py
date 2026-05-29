
*The schema lives in `src/api/input_schema.json` and is loaded at service start‑up.*

#### 1.1.2. REST endpoints  

| Method | Path                     | Description                                    |
|--------|--------------------------|------------------------------------------------|
| GET    | `/v1/machine:input`      | Returns the current aggregated U64 input state |
| POST   | `/v1/machine:input`      | Accepts a payload matching the schema and injects it into the driver |

Both endpoints are secured with a bearer token (see **Security** below).

### 1.2. Code – “input‑api” module (Python Flask example)

