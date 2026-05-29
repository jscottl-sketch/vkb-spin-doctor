src/
├─ api/
│  ├─ __init__.py
│  ├─ input_routes.py          # New FastAPI router
│  └─ schemas.py               # Pydantic models (no JSON in the diff)
├─ core/
│  ├─ __init__.py
│  └─ injector.py              # Thin wrapper around the low‑level driver
├─ tests/
│  ├─ test_input_api.py
│  └─ test_injector.py
└─ openapi.yaml                # Updated OpenAPI description
