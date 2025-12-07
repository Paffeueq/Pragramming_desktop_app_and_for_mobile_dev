#!/bin/bash
# Deploy script dla Azure Functions - Przesyłanie plików

set -e

RESOURCE_GROUP="myResourceGroup"
FUNCTION_APP_NAME="myFileUploadFunctionApp"
STORAGE_ACCOUNT="mystorageacc$(date +%s)"
LOCATION="eastus"

echo "=== Azure Functions Deploy Script ===" 

# 1. Zaloguj się do Azure
echo "1. Logging to Azure..."
az login

# 2. Utwórz Resource Group
echo "2. Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Utwórz Storage Account
echo "3. Creating storage account..."
az storage account create \
  --resource-group $RESOURCE_GROUP \
  --name $STORAGE_ACCOUNT \
  --location $LOCATION \
  --sku Standard_LRS

# 4. Utwórz kontener dla uploadów
echo "4. Creating blob container..."
az storage container create \
  --name uploads \
  --account-name $STORAGE_ACCOUNT

# 5. Utwórz tabelę dla logów
echo "5. Creating table for logs..."
az storage table create \
  --name FileUploadLogs \
  --account-name $STORAGE_ACCOUNT

# 6. Pobierz connection string
echo "6. Getting connection string..."
STORAGE_CONNECTION=$(az storage account show-connection-string \
  --resource-group $RESOURCE_GROUP \
  --name $STORAGE_ACCOUNT \
  --query connectionString -o tsv)

# 7. Utwórz Function App
echo "7. Creating function app..."
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name $FUNCTION_APP_NAME \
  --storage-account $STORAGE_ACCOUNT

# 8. Ustaw Application Settings
echo "8. Setting application settings..."
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "AzureWebJobsStorage=$STORAGE_CONNECTION" \
    "FUNCTIONS_WORKER_RUNTIME=python"

# 9. Deploy kod
echo "9. Deploying function code..."
func azure functionapp publish $FUNCTION_APP_NAME --build remote

echo ""
echo "=== Deployment Complete ===" 
echo "Function App URL: https://$FUNCTION_APP_NAME.azurewebsites.net"
echo "Upload endpoint: https://$FUNCTION_APP_NAME.azurewebsites.net/api/UploadFile"
echo "List endpoint: https://$FUNCTION_APP_NAME.azurewebsites.net/api/ListFiles"
echo ""
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Connection String: $STORAGE_CONNECTION"
