# Deployment MCP Server na Azure

## Szybki Start

### Wymagania
- Azure Subscription
- Azure CLI (`az` command)
- .NET 9.0 SDK

### Instalacja Azure CLI
```powershell
# Windows
choco install azure-cli

# lub pobrać z: https://aka.ms/installazurecliwindows
```

## Deployment - Opcja 1: Azure App Service (Rekomendowana)

### Krok 1: Logowanie
```powershell
az login
```

### Krok 2: Tworzenie grupy zasobów
```powershell
az group create --name mcp-resource-group --location eastus
```

### Krok 3: Tworzenie App Service Plan
```powershell
az appservice plan create `
  --name mcp-app-plan `
  --resource-group mcp-resource-group `
  --sku B1 `
  --is-linux
```

### Krok 4: Tworzenie Web App
```powershell
az webapp create `
  --resource-group mcp-resource-group `
  --plan mcp-app-plan `
  --name mcp-server-app `
  --runtime "DOTNETCORE|9.0"
```

### Krok 5: Publikowanie aplikacji
```powershell
dotnet publish -c Release -o ./publish
cd publish
az webapp deployment source config-zip `
  --resource-group mcp-resource-group `
  --name mcp-server-app `
  --src-path ..\publish.zip
```

## Deployment - Opcja 2: Docker Container

### Krok 1: Tworzenie Container Registry
```powershell
$registryName = "mcpregistry"
$resourceGroup = "mcp-resource-group"

az acr create `
  --resource-group $resourceGroup `
  --name $registryName `
  --sku Basic
```

### Krok 2: Budowanie obrazu
```powershell
az acr build --registry $registryName `
  --image mcpserver:latest `
  .
```

### Krok 3: Wdrożenie na App Service
```powershell
az webapp create `
  --resource-group $resourceGroup `
  --plan mcp-app-plan `
  --name mcp-server-app `
  --deployment-container-image-name-user "$registryName.azurecr.io/mcpserver:latest"
```

## Konfiguracja Aplikacji

### Ustawianie zmiennych środowiskowych
```powershell
az webapp config appsettings set `
  --resource-group mcp-resource-group `
  --name mcp-server-app `
  --settings `
    GROQ_API_KEY="gsk_Your_Key_Here" `
    WEBSITE_ENABLE_APP_SERVICE_STORAGE=false
```

## Monitoring

### Podgląd logów
```powershell
az webapp log tail `
  --resource-group mcp-resource-group `
  --name mcp-server-app
```

### Status aplikacji
```powershell
az webapp show `
  --resource-group mcp-resource-group `
  --name mcp-server-app
```

## Uruchomiona aplikacja

Po deployment, aplikacja będzie dostępna pod:
```
https://mcp-server-app.azurewebsites.net
```

## Wyczyszczenie Zasobów

```powershell
az group delete `
  --name mcp-resource-group `
  --yes `
  --no-wait
```

## Koszty

- **Azure App Service B1**: ~$55/miesiąc
- **Darmowy tier**: dostępny dla nowych użytkowników (12 miesięcy)
- **Pay-as-you-go**: ~$0.013/godzinę

## Troubleshooting

### Aplikacja nie uruchamia się
```powershell
az webapp log config `
  --name mcp-server-app `
  --resource-group mcp-resource-group `
  --web-server-logging filesystem

az webapp log download `
  --name mcp-server-app `
  --resource-group mcp-resource-group
```

### Błędy przy deployment
- Sprawdzić czy .NET 9.0 runtime jest dostępny na Azure
- Weryfikować zmienne środowiskowe
- Sprawdzić logi w Azure Portal
