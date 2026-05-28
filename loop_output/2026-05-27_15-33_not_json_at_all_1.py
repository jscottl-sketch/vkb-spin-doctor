MachineInput.Api/
│
├─ Controllers/
│   └─ InputController.cs
│
├─ Models/
│   ├─ InputState.cs
│   └─ InputCommand.cs
│
├─ Services/
│   └─ IInputInjectionService.cs
│   └─ InputInjectionService.cs   // wrapper around the existing U64 class
│
├─ Filters/
│   └─ ValidateModelAttribute.cs
│
└─ MachineInput.Api.csproj
