var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// OpenAPI nie jest dostępne w .NET 8 (tylko w .NET 9+)

// Konfiguruj URLs - tylko HTTP (bez HTTPS dla Linux)
builder.WebHost.UseUrls("http://0.0.0.0:5000");

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    // MapOpenApi() jest dostępne tylko w .NET 9+
}

// Wyłącz HTTPS redirect dla lokalnych testów
// app.UseHttpsRedirection();

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

// Endpoint zdrowia
app.MapGet("/", () => new { 
    status = "ok", 
    message = "HostingApp is running",
    version = "1.0.0",
    timestamp = DateTime.UtcNow
});

// Endpoint testowy
app.MapGet("/api/info", () => new {
    hostname = Environment.MachineName,
    osVersion = Environment.OSVersion.VersionString,
    runtime = ".NET 9.0",
    uptime = DateTime.UtcNow
});

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

// Słuchaj na wszystkich interfejsach sieciowych (0.0.0.0)
if (app.Environment.IsDevelopment())
{
    // MapOpenApi() jest dostępne tylko w .NET 9+
}

app.Run();

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
