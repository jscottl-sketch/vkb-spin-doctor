+----------------------+      +----------------------+      +----------------------+
|   Input Client(s)    | ---> |   gRPC Input Service | ---> |   PX4 / X‑Plane Core |
| (web UI, scripts…)   |      |   (C++/Python)       |      |   (C++, UDP Backend) |
+----------------------+      +----------------------+      +----------------------+

Key Points
- All traffic between client and service is protobuf‑encoded.
- The service exposes two RPCs:
    * `InjectInput(KeyboardJoystick)` – for one‑off injection.
    * `StreamInput(Empty)` – bidirectional stream for continuous joystick
      state updates and timeout monitoring.
- The service forwards the data to the existing PX4 input pipeline
  (unchanged) and to the X‑Plane SITL UDP backend.
