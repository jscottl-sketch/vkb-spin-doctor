
> **Conflict‑resolution tips**
> * If `CMakeLists.txt` has duplicate `add_subdirectory` entries, keep only one.
> * If `include/rc_input_injector.hpp` is modified by both PRs, ensure the new `InputService` header is included after the existing injector definitions.

---

### 3. Verify the merged code compiles

