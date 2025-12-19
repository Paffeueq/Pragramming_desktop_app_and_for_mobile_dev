#!/bin/bash

# Skrypt do deployment serwera MCP na Azure

set -e

echo "=========================================="
echo "Deployment MCP Server na Azure"
echo "=========================================="

# Konfiguracja
RESOURCE_GROUP="mcp-resource-group"
APP_SERVICE_NAME="mcp-server-app"
LOCATION="eastus"
REGISTRY_NAME="mcpregistry"

echo "[1] Sprawdzanie Azure CLI..."
az --version > /dev/null || { echo "Azure CLI nie zainstalowany!"; exit 1; }

echo "[2] Logowanie do Azure..."
az login

echo "[3] Tworzenie grupy zasobów..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "[4] Tworzenie Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic

echo "[5] Budowanie obrazu Docker..."
az acr build --registry $REGISTRY_NAME \
  --image mcpserver:latest \
  .

echo "[6] Tworzenie App Service Plan..."
az appservice plan create \
  --name "${APP_SERVICE_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

echo "[7] Tworzenie Web App..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "${APP_SERVICE_NAME}-plan" \
  --name $APP_SERVICE_NAME \
  --deployment-container-image-name-user "${REGISTRY_NAME}.azurecr.io/mcpserver:latest"

echo "[8] Konfiguracja Web App..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --settings \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
    DOCKER_REGISTRY_SERVER_URL="https://${REGISTRY_NAME}.azurecr.io" \
    DOCKER_ENABLE_CI=true

echo "[9] Pobranie adresu URL aplikacji..."
APP_URL=$(az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --query "defaultHostName" \
  -o tsv)

echo "=========================================="
echo "Deployment zakończony!"
echo "URL aplikacji: https://$APP_URL"
echo "=========================================="
