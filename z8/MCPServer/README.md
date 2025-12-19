# Prosty Serwer MCP w C#

## Opis
Projekt demonstracyjny implementującego serwer **Model Context Protocol (MCP)** w C#.

## Wymagania
- .NET SDK 9.0+
- Visual Studio Code lub Visual Studio

## Struktura projektu
```
MCPServer/
├── Program.cs           # Główny serwer MCP
├── MCPServer.csproj     # Konfiguracja projektu
├── README.md            # Ta dokumentacja
└── bin/Debug/           # Zbudowane artefakty
```

## Funkcjonalności
- ✅ Serwer nasłuchujący na stdin/stdout
- ✅ Obsługa wiadomości inicjalizacji
- ✅ Zwracanie informacji o serwerze
- ✅ Listowanie dostępnych narzędzi
- ✅ Obsługa zdarzeń z klienta

## Budowanie projektu

```bash
cd MCPServer
dotnet build
```

## Uruchamianie serwera

```bash
dotnet run
```

## Komunikacja z serwerem

Serwer oczekuje wiadomości tekstowych na wejściu (stdin):

```
> init
< {"status": "initialized", "name": "SimpleMCPServer", "version": "1.0.0"}

> list_tools
< {"tools": [{"name": "calculator", "description": "Prosty kalkulator"}]}

> info
< {"capabilities": ["tools", "resources", "prompts"]}
```

## Obsługiwane komendy
- `init` - inicjalizacja serwera
- `info` - informacje o serwerze
- `list_tools` - lista dostępnych narzędzi
- Dowolne inne - echo odpowiedzi

## Protokół MCP
MCP (Model Context Protocol) definiuje standardową komunikację między:
- **Klientem** - aplikacją AI lub agentem
- **Serwerem** - serwisem udostępniającym funkcjonalność

Wersja protokołu: 2024-11-05

## Rozszerzenia
Możesz rozszerzyć serwer o:
- JSON message parsing
- Tool execution logic
- Resource management
- Prompt handling

## Autor
Laboratorium AI MCP - grudzień 2025
