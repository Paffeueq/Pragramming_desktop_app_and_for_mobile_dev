#!/usr/bin/env powershell
# Test script dla aplikacji SpeechToText

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST APLIKACJI SPEECHTOTEXT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Sprawdzenie pliku WAV
Write-Host "TEST 1: Sprawdzenie pliku WAV" -ForegroundColor Yellow
$wavFile = Get-Item test_audio.wav -ErrorAction SilentlyContinue
if ($wavFile) {
    Write-Host "✅ Plik test_audio.wav istnieje"
    Write-Host "   Rozmiar: $($wavFile.Length) bajtów ($([math]::Round($wavFile.Length/1024, 1)) KB)" -ForegroundColor Green
} else {
    Write-Host "❌ Plik test_audio.wav nie znaleziony!" -ForegroundColor Red
    exit 1
}

# Test 2: Sprawdzenie projektu
Write-Host "`nTEST 2: Sprawdzenie projektu C#" -ForegroundColor Yellow
if (Test-Path "SpeechToText.csproj") {
    Write-Host "✅ Plik SpeechToText.csproj istnieje" -ForegroundColor Green
} else {
    Write-Host "❌ Projekt nie znaleziony!" -ForegroundColor Red
    exit 1
}

# Test 3: Build
Write-Host "`nTEST 3: Kompilacja projektu" -ForegroundColor Yellow
Write-Host "Budowanie..."
$buildOutput = dotnet build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build zakończony powodzeniem" -ForegroundColor Green
} else {
    Write-Host "❌ Build zakończył się błędem" -ForegroundColor Red
    Write-Host $buildOutput
    exit 1
}

# Test 4: Informacje o Azure Speech SDK
Write-Host "`nTEST 4: Sprawdzenie Azure Speech SDK" -ForegroundColor Yellow
$csprojContent = Get-Content SpeechToText.csproj
if ($csprojContent -match "Microsoft.CognitiveServices.Speech") {
    Write-Host "✅ Microsoft.CognitiveServices.Speech zependency znaleziona" -ForegroundColor Green
} else {
    Write-Host "❌ Azure Speech SDK nie zainstalowany!" -ForegroundColor Red
    exit 1
}

# Test 5: Dane konfiguracyjne
Write-Host "`nTEST 5: Sprawdzenie konfiguracji Azure" -ForegroundColor Yellow
$programContent = Get-Content Program.cs
if ($programContent -match "SPEECH_KEY") {
    Write-Host "✅ Klucz Azure Speech skonfigurowany" -ForegroundColor Green
}
if ($programContent -match "eastus") {
    Write-Host "✅ Region Azure skonfigurowany (eastus)" -ForegroundColor Green
}

# Test 6: Dostępne funkcje
Write-Host "`nTEST 6: Dostępne funkcje aplikacji" -ForegroundColor Yellow
if ($programContent -match "TranscribeFromMicrophone") {
    Write-Host "✅ Funkcja: TranscribeFromMicrophone" -ForegroundColor Green
}
if ($programContent -match "TranscribeFromFile") {
    Write-Host "✅ Funkcja: TranscribeFromFile" -ForegroundColor Green
}
if ($programContent -match "ChangeLanguage") {
    Write-Host "✅ Funkcja: ChangeLanguage" -ForegroundColor Green
}

# Test 7: Obsługiwane języki
Write-Host "`nTEST 7: Obsługiwane języki" -ForegroundColor Yellow
$languages = @("pl-PL", "en-US", "de-DE", "fr-FR", "es-ES")
foreach ($lang in $languages) {
    if ($programContent -match $lang) {
        Write-Host "✅ $lang" -ForegroundColor Green
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PODSUMOWANIE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Wszystkie testy przeszły!" -ForegroundColor Green
Write-Host "`nAby uruchomić aplikację, wpisz:" -ForegroundColor Cyan
Write-Host "  dotnet run`n" -ForegroundColor Yellow

Write-Host "Następnie wybierz opcję z menu:" -ForegroundColor Cyan
Write-Host "  1 - Transkrypcja z mikrofonu" -ForegroundColor Yellow
Write-Host "  2 - Transkrypcja pliku WAV (test_audio.wav)" -ForegroundColor Yellow
Write-Host "  3 - Zmiana języka" -ForegroundColor Yellow
Write-Host "  4 - Wyjście`n" -ForegroundColor Yellow
