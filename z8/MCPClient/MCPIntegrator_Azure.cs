using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

/// <summary>
/// Integrator MCP dla Azure - łączy LLM (Groq) z Azure MCPServer
/// </summary>
public class MCPIntegratorAzure
{
    private readonly string _apiKey;
    private readonly HttpClient _httpClient;
    private const string AZURE_SERVER_URL = "https://mcp-server-app-pms.azurewebsites.net";
    private const string GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions";

    public MCPIntegratorAzure(string apiKey)
    {
        _apiKey = apiKey;
        _httpClient = new HttpClient();
    }

    /// <summary>
    /// Uruchomienie (połączenie z Azure MCPServer)
    /// </summary>
    public void StartMCPServer()
    {
        Console.WriteLine("[INTEGRATOR] Łączenie z Azure MCPServer...");
        Console.WriteLine($"[INTEGRATOR] URL: {AZURE_SERVER_URL}\n");
    }

    /// <summary>
    /// Wysyłanie komendy do Azure MCPServer via HTTP (już w formacie JSON)
    /// </summary>
    public string SendToMCPServer(string jsonCommand)
    {
        try
        {
            Console.WriteLine($"[MCP CLIENT] Wysyłanie: {jsonCommand}");

            var jsonContent = new StringContent(
                jsonCommand,
                Encoding.UTF8,
                "application/json"
            );

            var response = _httpClient.PostAsync(
                $"{AZURE_SERVER_URL}/mcp",
                jsonContent
            ).Result;

            string content = response.Content.ReadAsStringAsync().Result;
            Console.WriteLine($"[MCP SERVER] Odpowiedź: {content}\n");
            return content;
        }
        catch (Exception ex)
        {
            return $"ERROR: {ex.Message}";
        }
    }

    /// <summary>
    /// Wysyłanie żądania do Groq LLM
    /// </summary>
    public async Task<string> CallGroqLLM(string userMessage)
    {
        try
        {
            var request = new
            {
                model = "meta-llama/llama-4-scout-17b-16e-instruct",
                messages = new[]
                {
                    new { role = "system", content = "Jesteś asystentem mogącym wywoływać narzędzia MCP do zarządzania bazą danych." },
                    new { role = "user", content = userMessage }
                },
                temperature = 0.7,
                max_tokens = 500
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(request),
                Encoding.UTF8,
                "application/json"
            );

            var requestMsg = new HttpRequestMessage(HttpMethod.Post, GROQ_API_URL)
            {
                Content = jsonContent,
                Headers = { { "Authorization", $"Bearer {_apiKey}" } }
            };

            var response = await _httpClient.SendAsync(requestMsg);
            string responseContent = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return $"GROQ ERROR: {responseContent}";
            }

            var jsonDoc = JsonDocument.Parse(responseContent);
            string assistantMessage = jsonDoc.RootElement
                .GetProperty("choices")[0]
                .GetProperty("message")
                .GetProperty("content")
                .GetString() ?? "";

            return assistantMessage;
        }
        catch (Exception ex)
        {
            return $"GROQ ERROR: {ex.Message}";
        }
    }

    /// <summary>
    /// Sesja interaktywna: User → Groq → MCP → DB
    /// </summary>
    public async Task InteractiveSession()
    {
        Console.WriteLine("\n╔═══════════════════════════════════════════╗");
        Console.WriteLine("║  SESJA INTERAKTYWNA: Groq + MCP + Azure   ║");
        Console.WriteLine("╚═══════════════════════════════════════════╝\n");

        // Scenariusz 1: Inicjalizuj serwer
        Console.WriteLine("[SCENARIUSZ 1] Inicjalizacja serwera MCP\n");
        string initResponse = SendToMCPServer("{\"command\": \"init\"}");
        Console.WriteLine($"[USER] Uruchom serwer MCP");
        string llmResponse1 = await CallGroqLLM(
            $"Serwer odpowiedział: {initResponse}\nPodsumuj co się stało."
        );
        Console.WriteLine($"[ASYSTENT] {llmResponse1}\n");

        // Scenariusz 2: Sprawdzenie dostępnych tabel
        Console.WriteLine("\n[SCENARIUSZ 2] Jakie tabele są w bazie?\n");
        string tablesResponse = SendToMCPServer("{\"command\": \"list_tables\"}");
        Console.WriteLine("[USER] Jakie tabele masz w bazie danych?");
        string llmResponse2 = await CallGroqLLM(
            $"Dane z bazy: {tablesResponse}\nJakie tabele są dostępne?"
        );
        Console.WriteLine($"[ASYSTENT] {llmResponse2}\n");

        // Scenariusz 3: Zapytaj o użytkowników
        Console.WriteLine("\n[SCENARIUSZ 3] Dane z tabeli Users\n");
        string queryResponse = SendToMCPServer("{\"command\": \"query_database\", \"query\": {\"table\": \"Users\"}}");
        Console.WriteLine("[USER] Pokaż mi wszystkich użytkowników z bazy danych");
        string llmResponse3 = await CallGroqLLM(
            $"Dane z bazy Users:\n{queryResponse}\n\nPodsumuj te użytkowników dla mnie w polskim języku."
        );
        Console.WriteLine($"[ASYSTENT] {llmResponse3}\n");

        // Scenariusz 4: Dane z tabeli Products
        Console.WriteLine("\n[SCENARIUSZ 4] Produkty w magazynie\n");
        string productsResponse = SendToMCPServer("{\"command\": \"query_database\", \"query\": {\"table\": \"Products\"}}");
        Console.WriteLine("[USER] Jakie produkty mamy w magazynie?");
        string llmResponse4 = await CallGroqLLM(
            $"Produkty w bazie:\n{productsResponse}\n\nPodsumuj dostępne produkty i ich ceny."
        );
        Console.WriteLine($"[ASYSTENT] {llmResponse4}\n");
    }

    /// <summary>
    /// Zamknięcie
    /// </summary>
    public void StopMCPServer()
    {
        Console.WriteLine("[INTEGRATOR] Zamykanie sesji...");
    }
}
