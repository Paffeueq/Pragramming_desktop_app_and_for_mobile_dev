# PowerShell Deploy Script dla Azure Functions

param(
    [string]$ResourceGroup = "myResourceGroup",
    [string]$FunctionAppName = "myFileUploadFunctionApp",
    [string]$Location = "eastus"
)

# Kolory dla output
$Green = "Green"
$Cyan = "Cyan"
$Yellow = "Yellow"

Write-Host "=== Azure Functions Deploy Script ===" -ForegroundColor $Cyan

# 1. Zaloguj się do Azure
Write-Host "1. Logging to Azure..." -ForegroundColor $Yellow
az login

# 2. Utwórz Resource Group
Write-Host "2. Creating resource group: $ResourceGroup..." -ForegroundColor $Yellow
az group create --name $ResourceGroup --location $Location

# 3. Utwórz Storage Account
$StorageAccount = "stg$(Get-Date -Format 'yyMMddHHmmss')"
Write-Host "3. Creating storage account: $StorageAccount..." -ForegroundColor $Yellow
az storage account create `
    --resource-group $ResourceGroup `
    --name $StorageAccount `
    --location $Location `
    --sku Standard_LRS

# 4. Utwórz kontener dla uploadów
Write-Host "4. Creating blob container 'uploads'..." -ForegroundColor $Yellow
az storage container create `
    --name uploads `
    --account-name $StorageAccount

# 5. Utwórz tabelę dla logów
Write-Host "5. Creating table 'FileUploadLogs'..." -ForegroundColor $Yellow
az storage table create `
    --name FileUploadLogs `
    --account-name $StorageAccount

# 6. Pobierz connection string
Write-Host "6. Getting connection string..." -ForegroundColor $Yellow
$StorageConnection = (az storage account show-connection-string `
    --resource-group $ResourceGroup `
    --name $StorageAccount `
    --query connectionString -o tsv)

# 7. Utwórz Function App
Write-Host "7. Creating function app: $FunctionAppName..." -ForegroundColor $Yellow
az functionapp create `
    --resource-group $ResourceGroup `
    --consumption-plan-location $Location `
    --runtime python `
    --runtime-version 3.11 `
    --functions-version 4 `
    --name $FunctionAppName `
    --storage-account $StorageAccount

# 8. Ustaw Application Settings
Write-Host "8. Setting application settings..." -ForegroundColor $Yellow
az functionapp config appsettings set `
    --name $FunctionAppName `
    --resource-group $ResourceGroup `
    --settings `
        "AzureWebJobsStorage=$StorageConnection" `
        "FUNCTIONS_WORKER_RUNTIME=python"

# 9. Deploy kod
Write-Host "9. Deploying function code..." -ForegroundColor $Yellow
func azure functionapp publish $FunctionAppName --build remote

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor $Green
Write-Host "Function App URL: https://$FunctionAppName.azurewebsites.net" -ForegroundColor $Green
Write-Host "Upload endpoint: https://$FunctionAppName.azurewebsites.net/api/UploadFile" -ForegroundColor $Green
Write-Host "List endpoint: https://$FunctionAppName.azurewebsites.net/api/ListFiles" -ForegroundColor $Green
Write-Host ""
Write-Host "Storage Account: $StorageAccount" -ForegroundColor $Green
Write-Host "Connection String saved" -ForegroundColor $Green
