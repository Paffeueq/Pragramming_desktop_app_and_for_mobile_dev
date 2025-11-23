using System.ComponentModel.DataAnnotations;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

// In-memory user store for demo / development purposes
var users = new List<User>();

// POST /users - create a new user with validation
app.MapPost("/users", (CreateUserRequest req) =>
{
    var validationResults = new List<ValidationResult>();
    var validationContext = new ValidationContext(req);
    if (!Validator.TryValidateObject(req, validationContext, validationResults, true))
    {
        // Convert ValidationResult list into the shape accepted by Results.ValidationProblem
        var errors = new Dictionary<string, string[]>();
        foreach (var vr in validationResults)
        {
            var member = vr.MemberNames.FirstOrDefault() ?? string.Empty;
            if (!errors.TryGetValue(member, out var arr))
            {
                errors[member] = new[] { vr.ErrorMessage ?? "Invalid value" };
            }
            else
            {
                var list = arr.ToList();
                list.Add(vr.ErrorMessage ?? "Invalid value");
                errors[member] = list.ToArray();
            }
        }

        return Results.ValidationProblem(errors);
    }

    var user = new User(Guid.NewGuid(), req.Username, req.Email, req.FullName, DateTime.UtcNow);
    users.Add(user);

    return Results.Created($"/users/{user.Id}", user);
})
.WithName("CreateUser");

app.MapGet("/weatherforecast", () =>
{
    var forecast =  Enumerable.Range(1, 5).Select(index =>
        new WeatherForecast
        (
            DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            Random.Shared.Next(-20, 55),
            summaries[Random.Shared.Next(summaries.Length)]
        ))
        .ToArray();
    return forecast;
})
.WithName("GetWeatherForecast");

app.Run();

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}

// DTO used for incoming create-user requests
record CreateUserRequest(
    [property: Required]
    [property: StringLength(50, MinimumLength = 3)]
    string Username,

    [property: Required]
    [property: EmailAddress]
    string Email,

    [property: StringLength(100)]
    string? FullName);

// Stored user record
record User(Guid Id, string Username, string Email, string? FullName, DateTime CreatedAt);
