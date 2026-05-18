# Morning Report — 2026-05-18 22:01

**Goal:** Add Star Citizen full support to Spin Doctor
**Stop reason:** goal_met
**Iterations completed:** 1
**Total cost:** £0.003425

## Best Attempt

**ID:** fafb5f77-50ed-4bfe-abf2-74f3ba8e506c
**Score:** 9.17

### Plan

To add full Star Citizen support to Spin Doctor, follow this step-by-step plan, focusing on robust game file management, configuration control, and user experience.

**Phase 1

### Work

**Objective:** Integrate full Star Citizen support into the Spin Doctor application, providing seamless import, real‑time monitoring, backup, and restoration of the game’s configuration and save data. The implementation must be reliable, secure, and user‑friendly, and it should respect the game’s frequent updates and the user’s environment (Windows 10/11, Steam/RSI Launcher, optional cloud‑sync).

---

## 1. Architecture Overview

| Component | Responsibility | Technologies |
|-----------|----------------|--------------|
| **SpinDoctor Core** | Existing UI, logging, backup engine | C# /.NET 6, WPF/WinForms |
| **StarCitizen Plugin** | Detects installation, parses game files, provides API for backup/restore | C# /.NET 6, JSON, XML, optional native DLLs |
| **Configuration Manager** | Centralizes per‑game settings (paths, exclusions, schedule) | JSON schema + validation (Newtonsoft.Json) |
| **Update Monitor** | Listens for RSI/Steam patch events and triggers re‑scan | Windows Registry watcher, file‑system watcher, Steam Web API |
| **User Experience Layer** | Wizard‑style UI, status icons, error handling | WPF MVVM, MahApps.Metro for modern look |
| **Testing Suite** | Unit, integration, UI automation | xUnit, MSTest, Selenium/WinAppDriver |

All new code will be placed under `SpinDoctor.Plugins.StarCitizen` namespace and compiled as a separate DLL (`StarCitizen.dll`) that can be loaded/unloaded at runtime, ensuring the core remains untouched.

---

## 2. Phase‑by‑Phase Implementation

### **Phase 1 – Discovery & Baseline Integration**

| Step | Action | Detail | Acceptance Criteria |
|------|--------|--------|----------------------|
| 1.1 | **Add Plugin Infrastructure** | Create `IPlugin` interface (`Initialize`, `Shutdown`, `GetSupportedGames`). Refactor core to load plugins via reflection from `Plugins` folder. | SpinDoctor starts with no plugins, loads any DLL that implements `IPlugin`. |
| 1.2 | **Create StarCitizen Plugin Skeleton** | Add new project `SpinDoctor.Plugins.StarCitizen`. Implement `IPlugin`. Register supported game id = `"StarCitizen"`. | Plugin loads, `GetSupportedGames` returns correct id. |
| 1.3 | **Detect Installation** | Implement `InstallationDetector` that: <br>• Checks the registry keys: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StarCitizen` (Steam) and `HKCU\Software\RobertsSpaceIndustries\StarCitizen` (RSI Launcher). <br>• Falls back to reading `%USERPROFILE%\AppData\Local\StarCitizen` and the default Steam folder `%ProgramFiles(x86)%\Steam\steamapps\common\StarCitizen`. | Detector returns a fully‑qualified root path (e.g., `C:\Program Files\Roberts Space Industries\StarCitizen`) or `null` if not found. |
| 1.4 | **Map Game‑Specific Folders** | From the root path, expose the following directories via a `GameFileLayout` object: <br>• `GameRoot` <br>• `Packages` (`StarCitizen\Packages`) <br>• `SavedGames` (`StarCitizen\SavedGames`) <br>• `UserConfig` (`StarCitizen\UserConfig`) <br>• `Logs` (`StarCitizen\Logs`). | All paths resolve correctly on a test machine with both launchers installed. |
| 1.5 | **Add Configuration Schema** | Extend `SpinDoctor.Config.json` with a `StarCitizen` section: <br>```json { "StarCitizen": { "Backup": { "Enabled": true, "Folders": ["SavedGames","UserConfig"], "ExcludePatterns": ["*.tmp","*.log"]
