*These three branches will host the three PRs described in the plan.*

### 1.3 Install Required Tooling (one‑time per developer)

| Tool | Installation Command (Windows) | Installation Command (Linux/macOS) |
|------|--------------------------------|------------------------------------|
| .NET SDK 8.0 | `winget install Microsoft.DotNet.SDK.8` | `sudo apt-get install dotnet-sdk-8.0` (or `brew install --cask dotnet-sdk` ) |
| Avalonia Templates | `dotnet new --install Avalonia.Templates` | same command |
| SDL2 (runtime) | download the latest `SDL2.dll` and place it in `src/YourApp/bin/Debug/net8.0/` | `sudo apt-get install libsdl2-dev` |
| SharpOSC (OSC lib) | `dotnet add package SharpOSC` | same command |
| OpenAPI / Swagger UI (optional) | `dotnet add package Swashbuckle.AspNetCore` | same command |

*Run the commands inside each feature branch when you start working on that branch.*

### 1.4 Draft a Design Brief (single markdown file)

Create `docs/INPUT_CONTROL_DESIGN.md` with the following headings:

