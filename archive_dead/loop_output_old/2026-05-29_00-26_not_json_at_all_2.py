src/
├─ Controllers/
│  └─ InputController.cs                ← new REST controller
├─ Models/
│  └─ InputPayloadDto.cs                ← DTO and validation attributes
├─ Services/
│  └─ InputInjectionService.cs          ← thin wrapper around U64 injection API
├─ Security/
│  └─ InputInjectorRequirement.cs       ← custom policy requirement
├─ Middleware/
│  └─ RateLimitingMiddleware.cs         ← per‑token limiter
└─ Tests/
   ├─ Unit/
   │  └─ InputPayloadDtoTests.cs
   └─ Integration/
      └─ InputApiIntegrationTests.cs

Docs/
 └─ openapi.yaml                         ← OpenAPI fragment
README.md                                 ← API usage examples added
CHANGELOG.md                               ← entry for v1.23.0‑input‑api
