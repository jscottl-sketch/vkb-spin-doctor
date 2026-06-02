src/
├─ input/
│   ├─ api/
│   │   ├─ v1/
│   │   │   ├─ machine_input.h        # REST handlers
│   │   │   └─ machine_input.cpp
│   ├─ core/
│   │   ├─ injector.h                 # Public API for injection
│   │   ├─ injector.cpp               # Implements U64 mapping
│   │   ├─ joystick_monitor.h         # Timeout detection
│   │   └─ joystick_monitor.cpp
│   └─ utils/
│       └─ json_schema.h              # Validation helpers
├─ sim/
│   └─ xplane/
│       ├─ xplane_backend.h
│       └─ xplane_backend.cpp
└─ CMakeLists.txt
