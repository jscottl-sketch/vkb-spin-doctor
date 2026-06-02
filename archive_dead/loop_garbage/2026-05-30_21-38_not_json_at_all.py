
2. **Generate language bindings** for the target language (C++, Python, etc.).  
3. **Update the server**:  
   - Replace the JSON parser with the protobuf decoder.  
   - Ensure the HTTP server reads the request body as `application/octet-stream`.  
   - For the `GET` endpoint, serialize an `InputEvent` (or a repeated container) and write it to the response body with `Content-Type: application/octet-stream`.  
4. **Update clients**: any UI or test harness must now pack/unpack the protobuf messages instead of constructing JSON strings.

### c. If a binary format is not feasible, fall back to URL‑encoded forms  
* Use `application/x-www-form-urlencoded` payloads, e.g. `type=keyboard&code=123&value=1`.  
* Keep the same field validation logic, just parse the form data instead of JSON.

### d. Remove all JSON‑related validation code  
* Delete JSON schema files, `json_decode` calls, and any error messages that reference “invalid JSON”.  
* Add unit tests that exercise the new binary/form payloads.

---

## 2. Strip JSON from Joystick Unresponsiveness Detection  

The detection logic itself does not need JSON, but the telemetry that is currently emitted may be JSON‑encoded. Perform the following:

1. **Identify all telemetry publish points** (`/status`, `/debug`, etc.) that serialise a JSON object with timestamps, flags, and recovery actions.  
2. **Replace them with a compact text protocol**: one line per event, fields separated by spaces or tabs. Example:
   