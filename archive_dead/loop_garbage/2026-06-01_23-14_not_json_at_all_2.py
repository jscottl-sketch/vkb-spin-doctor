
---

## 2. Integrate the **X‑Plane SITL backend** (PX4 PR #27472)

| Action | Command / Detail |
|--------|------------------|
| **Fetch the PR** | `git fetch origin pull/27472/head:pr_27472` |
| **Merge** | `git merge pr_27472` (resolve any conflicts, especially in `src/modules/simulator/` and `msg/` definitions) |
| **Review key files** | - `src/modules/simulator/sim_xplane.cpp` – new UDP handling code<br>- `msg/simulator_status.msg` – status fields for RREF/DREF<br>- `CMakeLists.txt` additions for the new module |
| **Update build configuration** | Ensure the `sim_xplane` target is added to `px4_sitl_default.cmake` and that the `PX4_SIM_MODEL` flag can select `xplane`.<br>