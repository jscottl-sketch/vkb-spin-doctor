
### 1.2 New files / modifications  

| File | Purpose | Summary of changes |
|------|---------|--------------------|
| `src/input_manager.hpp` | Header for the new singleton | • `class InputManager` with thread‑safe `std::atomic<uint64_t> keyboard_state_` and a `struct JoystickState { uint64_t buttons; float axes[4]; };` <br>• Public static `instance()` accessor <br>• Methods: `setKeyboard(uint64_t)`, `getKeyboard()`, `setJoystick(uint64_t buttons, const std::array<float,4>&)`, `getJoystick()` |
| `src/input_manager.cpp` | Implementation | • Initialize the atomic members. <br>• Use a `std::mutex` for joystick struct updates. |
| `include/rest_api.hpp` | Extend existing HTTP wrapper (assumed Boost.Beast) | • Add route registration for `/v1/machine:input` (GET & POST). |
| `src/rest_input.cpp` | REST handlers | 