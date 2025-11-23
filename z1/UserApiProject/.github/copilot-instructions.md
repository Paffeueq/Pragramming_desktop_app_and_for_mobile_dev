
# Copilot instructions for UserApiProject

These are short, actionable rules to help an AI agent be productive in this repository.

## Quick summary (big picture)
- This is a single-project ASP.NET Core minimal Web API (see `Program.cs`).
- Target framework: .NET 9.0 (`UserApiProject.csproj`).
- OpenAPI support is added via `Microsoft.AspNetCore.OpenApi` and enabled only in Development via `app.MapOpenApi()`.
- The app uses the minimal hosting model (all route mappings live in `Program.cs`) and uses C# 11 language features like `record` types and `implicit usings`.

## Key files to reference
- `Program.cs` — entry point and all HTTP endpoint mappings (example: `app.MapGet("/weatherforecast", ...)`).
- `UserApiProject.csproj` — project SDK, target framework, and NuGet references.
- `Properties/launchSettings.json` — local debug profiles used by IDEs and `dotnet run` in development.

## Naming & coding conventions (preserve existing rules)
- Classes and public methods: PascalCase.
- Local variables and parameters: camelCase.
- DTOs: PascalCase; small immutable DTOs often implemented as `record` types (see `WeatherForecast` in `Program.cs`).
- Use async/await for asynchronous operations.
- Add XML doc comments for public surfaces when appropriate.

## Project-specific patterns & examples
- Endpoints are mapped directly on `app` using `MapGet`/`MapPost` etc. Example: `app.MapGet("/weatherforecast", () => { ... })`.
- Use `builder.Services` to register services before `var app = builder.Build();`.
- OpenAPI is configured via `builder.Services.AddOpenApi()` and only mapped in Development: `if (app.Environment.IsDevelopment()) { app.MapOpenApi(); }`.
- HTTPS redirection is enabled by `app.UseHttpsRedirection();` — local development uses the launch profile which contains the application URL.
- Project enables `Nullable` and `ImplicitUsings`; account for nullable reference types and fewer explicit using directives.

## Build / run / debug (developer workflows)
- Build: `dotnet build` (run from repo root or specify project file).
- Run locally: `dotnet run --project .` (PowerShell example). This uses the `launchSettings.json` environment in Development.
- Debug in VS/VS Code: use the `launchSettings.json` profiles under `Properties/` — the IDE will pick up the HTTPS URL and environment.
- There are currently no test projects in the repository (no Tests/ folder). If you add tests, place them under a `tests/` or `Tests/` folder and reference the main project.

## Integration points & external dependencies
- OpenAPI (via `Microsoft.AspNetCore.OpenApi`) — exposes Swagger UI in Development.
- No external databases or third-party services are present in the repo. If you add integrations, register them in `builder.Services` and inject via constructor or delegate handlers.

## What to avoid / repository constraints
- Do not modify generated build artifacts under `bin/` or `obj/`.
- Keep the single-project minimal API pattern consistent; prefer adding services and small endpoint handlers in `Program.cs` unless the change justifies creating controllers or additional files.

## Small examples to follow
- Adding a service:
	- `builder.Services.AddSingleton<IMyService, MyService>();`
	- Inject into endpoints: `app.MapGet("/ping", (IMyService svc) => svc.Ping());`
- Return JSON-friendly DTOs (use `record` for simple immutable shapes):
	- `record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary);`

## Questions for maintainers (if unclear)
- There are no test projects — should new features include unit/integration tests and a test project layout?
- Any preferred folder structure for expanding the API (e.g., `Endpoints/`, `Controllers/`, `Services/`)?

If any section is unclear or you want more detail (example code patterns, tests scaffold, or CI commands), say which area and I will iterate.

## Order Class Guidelines

## Order Class Guidelines
- Location: `Models/Order.cs` (POCO model using DataAnnotations).
- Class name: `Order` — PascalCase, `UserApiProject.Models` namespace.

- Properties and discovery (do not change types without coordination):
	- `int Id` — integer primary identifier (positive). Keep as int for now.
	- `string ProductName` — required. Use `[Required]` and consider adding a `StringLength` limit when needed.
	- `int Quantity` — required-ish and must be > 0. Use `[Range(1, int.MaxValue, ErrorMessage = "Quantity must be greater than 0")]`.
	- `string CustomerName` — required.
	- `DateTime CreatedAt` — default to `DateTime.UtcNow` on creation; store as UTC.

- Validation and endpoints:
	- Prefer using DataAnnotations on the model (already present). Validate inputs at the API boundary.
	- In minimal APIs, either:
		- Run `Validator.TryValidateObject(...)` and return `Results.ValidationProblem(...)` (explicit validation), or
		- Map a DTO for create/update and validate it with DataAnnotations before mapping to the `Order` model.
	- Always return HTTP 400 with a validation-problem style body for validation errors (field -> string[] map).
	- For successful creates return 201 Created with Location header pointing to `/api/orders/{id}` and the created resource in the body.

- API routing and naming:
	- Use `/api/orders` for collection endpoints and `/api/orders/{id}` for single resources.
	- Endpoints to expect/implement:
		- POST `/api/orders` — create an order (validate request, set `CreatedAt`, return 201).
		- GET `/api/orders/{id}` — fetch a single order (return 404 if not found).
		- GET `/api/orders` — optional list with pagination/filtering if volume increases.

- Examples
	- Example POST body (JSON):
		{
			"productName": "Widget A",
			"quantity": 3,
			"customerName": "ACME Corp"
		}

	- Example validation error response (400):
		{
			"type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
			"title": "One or more validation errors occurred.",
			"status": 400,
			"errors": {
				"Quantity": ["Quantity must be greater than 0"]
			}
		}

- Testing and maintainability notes
	- Add a small unit test for the Order validation rules (happy path + quantity=0). Place tests under `tests/` if you add a test project.
	- If persistence is added, prefer a repository/service layer and register it via `builder.Services` (do not access DB directly from `Program.cs`).

If you want, I can add a sample POST `/api/orders` endpoint (with the same validation style used for `/users`) and tests — tell me if you prefer an in-memory store or EF Core-backed persistence.
