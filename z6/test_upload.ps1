
# Script do testowania Azure Functions Upload

$UploadURL = "http://localhost:7071/api/UploadFile"
$ListURL = "http://localhost:7071/api/ListFiles"

# Test 1: Przesłanie pliku jako multipart/form-data
Write-Host "=== TEST 1: Multipart Upload ===" -ForegroundColor Cyan

# Tworzymy plik testowy
$testFile = "C:\temp\test.txt"
New-Item -Path "C:\temp" -ItemType Directory -Force | Out-Null
"Hello from Azure Functions!" | Out-File -FilePath $testFile -Encoding UTF8

# Przesyłamy plik
$response = Invoke-WebRequest -Uri $UploadURL `
    -Method POST `
    -InFile $testFile `
    -ContentType "multipart/form-data" `
    -ErrorAction SilentlyContinue

Write-Host "Status: $($response.StatusCode)"
Write-Host "Response:" 
$response.Content | ConvertFrom-Json | Format-List

# Test 2: Przesłanie pliku jako base64 w JSON
Write-Host "`n=== TEST 2: Base64 JSON Upload ===" -ForegroundColor Cyan

$fileContent = Get-Content $testFile -Raw
$base64Content = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($fileContent))

$body = @{
    filename = "test-base64.txt"
    content = $base64Content
} | ConvertTo-Json

$response2 = Invoke-WebRequest -Uri $UploadURL `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -ErrorAction SilentlyContinue

Write-Host "Status: $($response2.StatusCode)"
Write-Host "Response:"
$response2.Content | ConvertFrom-Json | Format-List

# Test 3: Lista plików
Write-Host "`n=== TEST 3: List Files ===" -ForegroundColor Cyan

$response3 = Invoke-WebRequest -Uri $ListURL `
    -Method GET `
    -ContentType "application/json" `
    -ErrorAction SilentlyContinue

Write-Host "Status: $($response3.StatusCode)"
Write-Host "Response:"
$response3.Content | ConvertFrom-Json | Format-List

# Czyszczenie
Remove-Item -Path $testFile -Force
Write-Host "`nTesty zakończone!" -ForegroundColor Green
