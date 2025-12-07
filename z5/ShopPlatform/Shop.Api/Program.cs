using System.Diagnostics;
using Shop.Api.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Diagnostics.HealthChecks;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.AddServiceDefaults();
builder.AddNpgsqlDbContext<ProductsContext>("productsdb");
builder.Services.AddOpenApi();

// Lokalny in-memory cache (bez Redisa)
builder.Services.AddOutputCache();

// Extend health checks: add DB readiness (no "live" tag = affects /health only)
builder.Services.AddHealthChecks()
    .AddDbContextCheck<ProductsContext>(name: "productsdb", failureStatus: HealthStatus.Unhealthy);

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

app.UseOutputCache();

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

app.MapGet("/weatherforecast", () =>
{
    // Simulate random failures for testing resilience/retry
    if (Random.Shared.Next(0, 4) == 0)
    {
        throw new InvalidOperationException("Simulated weather service failure");
    }
    
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
.WithName("GetWeatherForecast")
.CacheOutput(p => p.Expire(TimeSpan.FromSeconds(5)));

app.MapGet("/products", async (ProductsContext db) =>
    await db.Products.AsNoTracking().ToListAsync());

// Map /health (readiness) and /alive (liveness)
app.MapDefaultEndpoints();

app.Run();

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
