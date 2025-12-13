using VisionIntegrationApi.Models;
using VisionIntegrationApi.Services;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

// === KONFIGURACJA KEY VAULT ===
// Jeśli używasz Key Vault, dodaj:
// var keyVaultUrl = builder.Configuration["KeyVault:VaultUrl"];
// if (!string.IsNullOrEmpty(keyVaultUrl))
// {
//     var credential = new DefaultAzureCredential();
//     builder.Configuration.AddAzureKeyVault(
//         new Uri(keyVaultUrl),
//         credential);
// }

// === KONFIGURACJA IPTIONS ===
builder.Services.Configure<VisionServiceOptions>(
    builder.Configuration.GetSection(VisionServiceOptions.SectionName));

// === REJESTRACJA SERWISÓW ===
builder.Services.AddScoped<IVisionService, VisionService>();
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll",
        policy =>
        {
            policy.AllowAnyOrigin()
                  .AllowAnyMethod()
                  .AllowAnyHeader();
        });
});

builder.Services.AddLogging();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// === MIDDLEWARE ===
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("AllowAll");

// === MINIMAL API ENDPOINTS ===

/// <summary>
/// GET /health - Health check
/// </summary>
app.MapGet("/health", () =>
{
    return Results.Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
})
.WithName("HealthCheck")
.Produces<object>(StatusCodes.Status200OK);

/// <summary>
/// POST /analyze-image - Analiza obrazu (URL lub Base64)
/// </summary>
app.MapPost("/analyze-image", async (
    AnalyzeImageRequest request,
    IVisionService visionService) =>
{
    if (request == null)
        return Results.BadRequest(new { error = "Request nie może być pusty" });

    if (string.IsNullOrEmpty(request.ImageUrl) && string.IsNullOrEmpty(request.ImageBase64))
        return Results.BadRequest(new { error = "Wymagane: ImageUrl lub ImageBase64" });

    AnalyzeImageResponse result;

    if (!string.IsNullOrEmpty(request.ImageUrl))
    {
        // Analiza z URL
        result = await visionService.AnalyzeImageFromUrlAsync(request.ImageUrl);
    }
    else
    {
        // Analiza z Base64
        result = await visionService.AnalyzeImageFromBase64Async(request.ImageBase64!);
    }

    return result.Status == "Success" 
        ? Results.Ok(result) 
        : Results.BadRequest(result);
})
.WithName("AnalyzeImage")
.Produces<AnalyzeImageResponse>(StatusCodes.Status200OK)
.Produces<AnalyzeImageResponse>(StatusCodes.Status400BadRequest)
.WithDescription("Analiza obrazu z użyciem Azure Computer Vision REST API");

/// <summary>
/// GET /analyze-image/test - Test endpoint z obrazem testowym
/// </summary>
app.MapGet("/analyze-image/test", async (IVisionService visionService) =>
{
    // Użyj publicznego obrazu testowego z Microsoftu
    var testImageUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg";
    
    var result = await visionService.AnalyzeImageFromUrlAsync(testImageUrl);
    return Results.Ok(result);
})
.WithName("TestAnalysis")
.Produces<AnalyzeImageResponse>(StatusCodes.Status200OK);

/// <summary>
/// GET /config - Pokaż bieżącą konfigurację (bez sekretów)
/// </summary>
app.MapGet("/config", (IOptions<VisionServiceOptions> options) =>
{
    var config = options.Value;
    return Results.Ok(new
    {
        visionService = new
        {
            endpoint = config.Endpoint,
            keyConfigured = !string.IsNullOrEmpty(config.Key)
        }
    });
})
.WithName("ShowConfig");

app.Run();
