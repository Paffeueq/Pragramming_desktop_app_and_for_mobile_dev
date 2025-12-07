# Azure Functions - Przesyłanie Plików do Azure Storage

## Opis projektu

System do przesyłania plików do Azure Blob Storage z Azure Functions. Aplikacja obsługuje:

1. **Upload pliku** - HTTP POST z plikiem (multipart/form-data lub base64)
2. **Zapis do Blob Storage** - Automatyczne przechowywanie plików
3. **Generowanie SAS URL** - Bezpieczny dostęp do pliku
4. **Logowanie** - Blob Trigger loguje uploady do Table Storage
5. **Listing plików** - Wylistowanie wszystkich przesłanych plików

## Architektura

```
Klient (Postman/Browser)
    ↓ POST /api/UploadFile
Azure Functions (HTTP Trigger)
    ↓
Azure Blob Storage (Container: 'uploads')
    ↓ (Blob Trigger - file changed)
Table Storage (Logging)
    + GET /api/ListFiles
```

## Funkcje dostępne

### 1. POST /api/UploadFile
**Przesyłanie pliku do Blob Storage**

**Metody:**

**a) Multipart Form-Data:**
```bash
curl -X POST http://localhost:7071/api/UploadFile \
  -F "file=@/path/to/file.txt"
```

**b) Base64 JSON:**
```bash
curl -X POST http://localhost:7071/api/UploadFile \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "content": "SGVsbG8gV29ybGQh"
  }'
```

**Odpowiedź:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "filename": "test.txt",
  "blob_name": "20251204_173500_test.txt",
  "file_size": 1024,
  "blob_url": "https://account.blob.core.windows.net/uploads/...",
  "timestamp": "2025-12-04T17:35:00.123456"
}
```

### 2. GET /api/ListFiles
**Wylistowanie wszystkich plików w Blob Storage**

```bash
curl -X GET http://localhost:7071/api/ListFiles
```

**Odpowiedź:**
```json
{
  "success": true,
  "count": 5,
  "files": [
    {
      "name": "20251204_173500_test.txt",
      "size": 1024,
      "created": "2025-12-04T17:35:00.123456"
    }
  ]
}
```

### 3. Blob Trigger (event-driven)
**Automatyczne logowanie uploadów do Table Storage**

- Aktywuje się, gdy plik pojawia się w kontenerze `uploads`
- Zapisuje metadane do tabeli `FileUploadLogs`
- Loguje timestamp, rozmiar, status

## Konfiguracja

### local.settings.json
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=xxx;AccountKey=xxx;",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsSecretStorageType": "Files"
  }
}
```

### requirements.txt
```
azure-functions
azure-storage-blob
azure-data-tables
```

## Uruchomienie

### 1. Zainstaluj zależności
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Uruchom Azure Functions
```bash
func host start
```

Server będzie dostępny na: **http://localhost:7071**

### 3. Testuj w Postmanie
- Importuj `Postman_Collection.json` do Postmana
- Wykonaj testy dla każdej funkcji

## Testing

### PowerShell Script
```bash
.\test_upload.ps1
```

Wykonuje 3 testy:
1. Multipart upload
2. Base64 JSON upload
3. List files

### Manual Tests
```bash
# Upload
curl -X POST http://localhost:7071/api/UploadFile -F "file=@test.txt"

# List
curl -X GET http://localhost:7071/api/ListFiles
```

## Struktura plików

```
z6/
├── function_app.py           # Główna aplikacja Azure Functions
├── requirements.txt          # Zależności Python
├── local.settings.json       # Konfiguracja lokalna
├── host.json                 # Konfiguracja hosta
├── Postman_Collection.json   # Testy w Postmanie
├── test_upload.ps1           # PowerShell test script
└── README.md                 # Niniejsza dokumentacja
```

## Błędy i rozwiązania

### 1. "Port 7071 is unavailable"
```bash
# Zabij proces na porcie 7071
netstat -ano | findstr 7071
Stop-Process -Id <PID> -Force
```

### 2. "No valid combination of account information found"
- Sprawdź `AzureWebJobsStorage` w `local.settings.json`
- Upewnij się, że connection string jest prawidłowy

### 3. "Module 'azure' not found"
```bash
pip install azure-storage-blob azure-data-tables
```

## Wdrożenie na Azure

### 1. Utwórz Function App
```bash
az functionapp create --resource-group myGroup --consumption-plan-location eastus \
  --runtime python --functions-version 4 --name myFunctionApp
```

### 2. Deploy
```bash
func azure functionapp publish myFunctionApp
```

### 3. Ustaw Connection String
```bash
az functionapp config appsettings set --name myFunctionApp --resource-group myGroup \
  --settings "AzureWebJobsStorage=<connection_string>"
```

## Kody błędów

| Kod | Opis |
|-----|------|
| 200 | OK - Operacja udana |
| 400 | Bad Request - Brakujący plik lub dane |
| 500 | Server Error - Błąd przy przesyłaniu |

## ToDo (Enhancements)

- [ ] Uwierzytelnianie (OAuth, API Key)
- [ ] Limity rozmiaru pliku
- [ ] Skanowanie wirusów (ClamAV)
- [ ] Kompresja plików
- [ ] Synchronizacja z bazy danych
- [ ] Thumbnail generation dla obrazów

## Autor

Z6 - Projekt Azure Functions

## Licencja

MIT
