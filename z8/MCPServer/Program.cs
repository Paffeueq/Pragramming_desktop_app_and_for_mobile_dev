using System;
using System.Text.Json;
using System.Collections.Generic;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Inicjalizacja bazy danych
var dbServer = new DatabaseServer("mcp_database.db");

Console.WriteLine("╔═══════════════════════════════════════════════╗");
Console.WriteLine("║  Serwer MCP z bazą danych SQLite             ║");
Console.WriteLine("║  Wersja 3.0.0 (ASP.NET Core)                 ║");
Console.WriteLine("╚═══════════════════════════════════════════════╝\n");

// Health check endpoint
app.MapGet("/", () => new { status = "ok", message = "MCP Server running", version = "3.0.0" });
app.MapGet("/health", () => new { status = "ok", timestamp = DateTime.UtcNow });

// MCP API endpoint
app.MapPost("/mcp", async (HttpContext context) =>
{
    try
    {
        using var reader = new StreamReader(context.Request.Body);
        var line = await reader.ReadToEndAsync();

        if (string.IsNullOrWhiteSpace(line))
        {
            context.Response.StatusCode = 400;
            await context.Response.WriteAsJsonAsync(new { error = "Empty request" });
            return;
        }

        var json = JsonDocument.Parse(line);
        var root = json.RootElement;

        string command = root.GetProperty("command").GetString() ?? "";
        
        string response = command switch
        {
            "init" => JsonSerializer.Serialize(new
            {
                status = "initialized",
                name = "MCPServerWithDatabase",
                version = "3.0.0"
            }),

            "list_tables" => JsonSerializer.Serialize(new
            {
                status = "ok",
                data = dbServer.ListTables()
            }),

            "query_database" => HandleQueryDatabase(root, dbServer),
            "insert_data" => HandleInsertData(root, dbServer),
            "update_data" => HandleUpdateData(root, dbServer),
            "delete_data" => HandleDeleteData(root, dbServer),

            _ => JsonSerializer.Serialize(new { error = "Unknown command" })
        };

        context.Response.ContentType = "application/json";
        await context.Response.WriteAsync(response);
    }
    catch (JsonException ex)
    {
        context.Response.StatusCode = 400;
        await context.Response.WriteAsJsonAsync(new { error = "Invalid JSON: " + ex.Message });
    }
    catch (Exception ex)
    {
        context.Response.StatusCode = 500;
        await context.Response.WriteAsJsonAsync(new { error = "Server error: " + ex.Message });
    }
});

app.Run();

string HandleQueryDatabase(JsonElement root, DatabaseServer db)
{
    try
    {
        var queryObj = root.GetProperty("query");
        string table = queryObj.GetProperty("table").GetString() ?? "";
        string where = queryObj.TryGetProperty("where", out var w) ? w.GetString() ?? "" : "";

        string result = db.QueryDatabase(table, where);

        return JsonSerializer.Serialize(new
        {
            status = "ok",
            data = result
        });
    }
    catch (Exception ex)
    {
        return JsonSerializer.Serialize(new { error = ex.Message });
    }
}

string HandleInsertData(JsonElement root, DatabaseServer db)
{
    try
    {
        var insertObj = root.GetProperty("insert");
        string table = insertObj.GetProperty("table").GetString() ?? "";
        
        var values = new Dictionary<string, string>();
        var valuesObj = insertObj.GetProperty("values");
        foreach (var prop in valuesObj.EnumerateObject())
        {
            values[prop.Name] = prop.Value.GetString() ?? "";
        }

        string result = db.InsertData(table, values);

        return JsonSerializer.Serialize(new
        {
            status = "ok",
            data = result
        });
    }
    catch (Exception ex)
    {
        return JsonSerializer.Serialize(new { error = ex.Message });
    }
}

string HandleUpdateData(JsonElement root, DatabaseServer db)
{
    try
    {
        var updateObj = root.GetProperty("update");
        string table = updateObj.GetProperty("table").GetString() ?? "";
        
        var values = new Dictionary<string, string>();
        var valuesObj = updateObj.GetProperty("set");
        foreach (var prop in valuesObj.EnumerateObject())
        {
            values[prop.Name] = prop.Value.GetString() ?? "";
        }

        string where = updateObj.GetProperty("where").GetString() ?? "";

        string result = db.UpdateData(table, values, where);

        return JsonSerializer.Serialize(new
        {
            status = "ok",
            data = result
        });
    }
    catch (Exception ex)
    {
        return JsonSerializer.Serialize(new { error = ex.Message });
    }
}

string HandleDeleteData(JsonElement root, DatabaseServer db)
{
    try
    {
        var deleteObj = root.GetProperty("delete");
        string table = deleteObj.GetProperty("table").GetString() ?? "";
        string where = deleteObj.GetProperty("where").GetString() ?? "";

        string result = db.DeleteData(table, where);

        return JsonSerializer.Serialize(new
        {
            status = "ok",
            data = result
        });
    }
    catch (Exception ex)
    {
        return JsonSerializer.Serialize(new { error = ex.Message });
    }
}
