using System;
using System.Threading.Tasks;

Console.WriteLine("╔════════════════════════════════════════════════╗");
Console.WriteLine("║   Klient MCP + Groq + Azure MCPServer         ║");
Console.WriteLine("╚════════════════════════════════════════════════╝\n");

// Konfiguracja
string groqApiKey = Environment.GetEnvironmentVariable("GROQ_API_KEY") ?? "";

if (string.IsNullOrEmpty(groqApiKey))
{
    Console.WriteLine("[ERROR] Brak API klucza Groq!\n");
    Console.WriteLine("Aby użyć tego klienta:\n");
    Console.WriteLine("  1. Zarejestruj się na https://console.groq.com");
    Console.WriteLine("  2. Skopiuj swój API key");
    Console.WriteLine("  3. Ustaw zmienną: $env:GROQ_API_KEY='gsk_xxx'\n");
    return;
}

// Inicjalizacja integratora
var integrator = new MCPIntegratorAzure(groqApiKey);

try
{
    // Uruchomienie (połączenie z Azure)
    integrator.StartMCPServer();

    // Sesja interaktywna
    await integrator.InteractiveSession();
}
finally
{
    integrator.StopMCPServer();
}
