
*Key points*  

* **U64 format** – enforced by regex `^0x[0-9a-fA-F]{16}$`.  
* **Security** – JWT‑Bearer token, TLS mandatory (enforced by the reverse proxy).  
* **Error handling** – 422 for out‑of‑range values, 400 for malformed JSON, 401 for auth failures.

---

### 1.2 Service implementation (Go)

> **File:** `internal/api/input_handler.go`

