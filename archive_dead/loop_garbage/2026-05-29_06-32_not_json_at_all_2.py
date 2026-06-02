# Fork and branch
git clone https://github.com/px4/px4.git
cd px4
git checkout -b feature/keyboard-joystick-api

# Add JSON dependency (nlohmann/json, header‑only)
# In CMakeLists.txt
target_include_directories(px4 PUBLIC external/nlohmann_json/include)

# Verify build
colcon build --packages-select px4
