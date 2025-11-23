# Instrukcje — CopilotTest

Ten plik zawiera krótkie instrukcje, jak zbudować, uruchomić, przetestować i opublikować konsolowy projekt .NET 9 o nazwie `CopilotTest`.

Co zrobić dalej
- Upewnij się, że masz zainstalowane wymagane narzędzia (znajdują się niżej).
- (Opcjonalnie) przywróć zależności, zbuduj projekt, uruchom i przetestuj.
- Opublikuj, gdy chcesz uzyskać wyjście gotowe do wdrożenia.

Wymagania
- Zainstalowany .NET 9 SDK i dostępny `dotnet` w PATH. Sprawdź wersję:

```powershell
dotnet --version
```

Najczęściej używane polecenia (PowerShell)
Uruchom je z katalogu głównego projektu (tam, gdzie znajdują się `CopilotTest.sln` i `CopilotTest.csproj`).

Przywracanie (opcjonalne):

```powershell
dotnet restore
```

Budowanie (Debug):

```powershell
dotnet build
```

Uruchomienie (z pliku projektu):

```powershell
dotnet run
```

Uruchomienie skompilowanego DLL bezpośrednio:

```powershell
dotnet .\bin\Debug\net9.0\CopilotTest.dll
```

Sprzątanie (clean):

```powershell
dotnet clean
```

Publikacja (Release, framework-dependent):

```powershell
dotnet publish -c Release -o .\publish
```

Testy (na poziomie solution):

```powershell
dotnet test .\CopilotTest.sln
```

Uruchomienie testów i zapis wyników (TRX):

```powershell
dotnet test .\CopilotTest.sln --logger "trx;LogFileName=TestResults.trx" --results-directory .\TestResults
```

Uwagi edytora
- W Visual Studio otwórz `CopilotTest.sln`.
- W VS Code zainstaluj rozszerzenie C# (OmniSharp). Użyj debuggera (F5) do uruchomienia i debugowania.

Pliki wynikowe i artefakty
- Pliki wynikowe (DLL itp.): `./bin/Debug/net9.0/`
- Artefakty kompilacji: `./obj/`
- Wyjście po publikacji: `./publish/`

Dodatkowe uwagi
- Aplikacja używa top-level statements — główna logika startowa znajduje się w `Program.cs`.
- Logika kalkulatora (jeśli potrzebna) jest w `Calculator.cs`.
- W chwili obecnej w repozytorium nie ma projektu testowego — `dotnet test` zbuduje rozwiązanie, ale nie uruchomi testów jednostkowych dopóki nie dodasz projektu testowego.

Weryfikacja
- Uruchomiono `dotnet test` na tej solucji podczas przygotowania instrukcji; polecenie zakończyło się pomyślnie (kod wyjścia 0) i projekt się kompiluje.

Co mogę dodać dalej
- Mały projekt testowy (xUnit) z kilkoma testami dla `Calculator` (np. test pozytywny + test przypadku brzegowego).
- Plik workflow dla GitHub Actions, który buduje projekt i uruchamia testy przy push/PR.

Powiedz, co chcesz, a zaktualizuję plik dalej lub dodam testy/CI.

Tell me which of those you'd like next.