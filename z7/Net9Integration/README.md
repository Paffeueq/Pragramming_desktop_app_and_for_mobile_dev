# VisionIntegrationApi - .NET 9 Minimal API

## Opis

Aplikacja .NET 9 z Minimal API integrującą Azure Computer Vision REST API.

### Funkcjonalności:
- ✅ Minimal API endpoint `/analyze-image`
- ✅ Obsługa URL i Base64 obrazów
- ✅ Konfiguracja przez IOptions pattern
- ✅ Integracja Azure Key Vault (opcjonalna)
- ✅ Swagger/OpenAPI dokumentacja
- ✅ Logging diagnostyki

## Architektura

```
Program.cs
├── Services
│   └── VisionService.cs (implementacja REST API call)
├── Models
│   ├── VisionOptions.cs (IOptions configuration)
│   └── AnalyzeImageRequest/Response
└── Controllers (Minimal API endpoints)
    ├── /health
    ├── /analyze-image (POST)
    ├── /analyze-image/test (GET)
    └── /config (GET)
```

## Konfiguracja

### appsettings.json (produkcja)
```json
{
  "VisionService": {
    "Endpoint": "https://eastus.api.cognitive.microsoft.com",
    "Key": "YOUR_VISION_KEY"
  }
}
```

### appsettings.Development.json (development)
```json
{
  "VisionService": {
    "Endpoint": "https://eastus.api.cognitive.microsoft.com",
    "Key": "YOUR_VISION_KEY"
  }
}
```

## Konfiguracja Key Vault

Aby dodać Azure Key Vault:

1. **Utwórz Key Vault w Azure**
```bash
az keyvault create --name mykeyvault --resource-group mygroup
az keyvault secret set --vault-name mykeyvault --name VisionKey --value "your-key"
```

2. **Dodaj do appsettings.json**
```json
{
  "KeyVault": {
    "VaultUrl": "https://mykeyvault.vault.azure.net/",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "ClientSecret": "your-client-secret"
  }
}
```

3. **Aktywuj w Program.cs** (już jest zakomentowany)
```csharp
var keyVaultUrl = builder.Configuration["KeyVault:VaultUrl"];
if (!string.IsNullOrEmpty(keyVaultUrl))
{
    var credential = new DefaultAzureCredential();
    builder.Configuration.AddAzureKeyVault(
        new Uri(keyVaultUrl),
        credential);
}
```

## Endpoints

### 1. Health Check
```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2025-12-13T17:07:26.4232247Z"
}
```

### 2. Analiza obrazu z URL
```
POST /analyze-image
Content-Type: application/json

Request:
{
  "imageUrl": "https://example.com/image.jpg"
}

Response: 200 OK / 400 BadRequest
{
  "status": "Success|Error",
  "imageFile": "https://example.com/image.jpg",
  "analysisResults": {
    "description": {...},
    "tags": [...],
    "objects": [...]
  },
  "processingTimeMs": 354,
  "error": null
}
```

### 3. Analiza obrazu z Base64
```
POST /analyze-image
Content-Type: application/json

Request:
{
  "imageBase64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
}

Response: jak wyżej
```

### 4. Test endpoint
```
GET /analyze-image/test
Response: Analiza publicznego obrazu testowego (landmark.jpg)
```

### 5. Pokaż konfigurację
```
GET /config
Response: 200 OK
{
  "visionService": {
    "endpoint": "https://eastus.api.cognitive.microsoft.com",
    "keyConfigured": true
  }
}
```

## Testowanie

### Test 1: Health Check
```powershell
curl http://localhost:5000/health
```

### Test 2: Analiza obrazu
```powershell
$body = @{
    imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/analyze-image" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Test 3: Test endpoint
```powershell
curl http://localhost:5000/analyze-image/test
```

## Pakiety NuGet

```xml
<PackageReference Include="Microsoft.Extensions.Azure" Version="1.7.0" />
<PackageReference Include="Azure.Identity" Version="1.10.0" />
<PackageReference Include="Azure.Security.KeyVault.Secrets" Version="4.7.0" />
<PackageReference Include="Azure.Extensions.AspNetCore.Configuration.Secrets" Version="1.3.0" />
<PackageReference Include="Swashbuckle.AspNetCore" Version="6.0.0" />
```

## Build i Run

```bash
# Build
dotnet build

# Run (development)
dotnet run --launch-profile http

# Run (production)
dotnet publish -c Release
dotnet VisionIntegrationApi.dll
```

## Struktura kodu

### Program.cs
- Konfiguracja dependency injection
- Rejestracja serwisów
- Definicja Minimal API endpoints
- Middleware pipeline

### Services/VisionService.cs
- Implementacja interfejsu IVisionService
- HTTP call do Vision REST API
- Obsługa URL i Base64
- Logging i error handling
- Pomiar czasu wykonania

### Models/VisionOptions.cs
- VisionServiceOptions (IOptions pattern)
- KeyVaultOptions
- AnalyzeImageRequest
- AnalyzeImageResponse

## Bezpieczeństwo

### Rekomendacje:
1. **Nikdy nie przechowuj kluczy w kodzie** - użyj:
   - appsettings.json dla production
   - Azure Key Vault dla secrets
   - Environment variables

2. **HTTPS w produkcji** - zawsze
3. **CORS** - ograniczam do zaufanych domen w produkcji
4. **Rate limiting** - dla chronienia API
5. **Authentication** - dodać jeśli public API

## Monitoring

### Logging dostępny dla:
- Parametrów request'u (bez sekretów)
- Statusu odpowiedzi API
- Czasu wykonania
- Błędów i wyjątków

### Aktywuj debug logging:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug"
    }
  }
}
```

## Rozszerzenia

Możliwe ullepszenia:
- [ ] Integracja rate limiting (AspNetCore.RateLimit)
- [ ] API Key authentication
- [ ] JWT Bearer authentication
- [ ] Caching wyników
- [ ] Batch processing wielu obrazów
- [ ] Support dla Computer Vision v4.0 API
- [ ] Custom Vision integration
- [ ] Database do przechowywania historii analiz

## Troubleshooting

### Błąd: "Access denied due to invalid subscription key"
- Sprawdź klucz w appsettings.json
- Sprawdź czy klucz jest dla poprawnego regionu

### Błąd: "Connection refused"
- Sprawdź czy aplikacja jest uruchomiona
- Sprawdź port (default: 5000)

### Błąd: "Invalid imageUrl"
- Sprawdź czy URL jest dostępny
- Sprawdź czy format obsługiwany (JPG, PNG, GIF, BMP)

## Test Results

```
✅ /health - Status 200 OK
✅ /config - Status 200 OK
✅ /analyze-image POST - Status 200 OK (z URL)
✅ /analyze-image POST - Status 200 OK (z Base64)
✅ /analyze-image/test GET - Status 200 OK
```

## Podsumowanie

- ✅ .NET 9 Minimal API zbudowana
- ✅ Vision REST API integration
- ✅ IOptions configuration pattern
- ✅ Key Vault ready (commented)
- ✅ Swagger documentation
- ✅ Error handling i logging
- ✅ Testowana i działająca
