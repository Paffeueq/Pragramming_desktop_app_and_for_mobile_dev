using System;
using System.Data;
using Microsoft.Data.Sqlite;
using System.Collections.Generic;

/// <summary>
/// Serwer MCP z obsługą SQLite bazy danych
/// </summary>
public class DatabaseServer
{
    private readonly string _dbPath;
    private readonly string _connectionString;

    public DatabaseServer(string dbPath = "mcp_database.db")
    {
        _dbPath = dbPath;
        _connectionString = $"Data Source={dbPath};";
        InitializeDatabase();
    }

    /// <summary>
    /// Inicjalizacja bazy danych z przykładowymi tabelami
    /// </summary>
    private void InitializeDatabase()
    {
        using (var connection = new SqliteConnection(_connectionString))
        {
            connection.Open();

            // Tworzenie tabeli użytkowników
            string createUsersTable = @"
                CREATE TABLE IF NOT EXISTS Users (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Email TEXT UNIQUE,
                    Created DATETIME DEFAULT CURRENT_TIMESTAMP
                );";

            // Tworzenie tabeli produktów
            string createProductsTable = @"
                CREATE TABLE IF NOT EXISTS Products (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Price REAL,
                    Stock INTEGER DEFAULT 0
                );";

            using (var cmd = new SqliteCommand(createUsersTable, connection))
                cmd.ExecuteNonQuery();

            using (var cmd = new SqliteCommand(createProductsTable, connection))
                cmd.ExecuteNonQuery();

            // Dodaj przykładowe dane jeśli tabela jest pusta
            string checkUsersCount = "SELECT COUNT(*) FROM Users;";
            using (var cmd = new SqliteCommand(checkUsersCount, connection))
            {
                int count = (int)(long)cmd.ExecuteScalar();
                if (count == 0)
                {
                    InsertSampleData(connection);
                }
            }

            connection.Close();
        }

        Console.WriteLine("[DB] Baza danych zainicjalizowana");
    }

    /// <summary>
    /// Wstawianie przykładowych danych
    /// </summary>
    private void InsertSampleData(SqliteConnection connection)
    {
        string[] insertUsers = new[]
        {
            "INSERT INTO Users (Name, Email) VALUES ('Jan Kowalski', 'jan@example.com');",
            "INSERT INTO Users (Name, Email) VALUES ('Maria Nowak', 'maria@example.com');",
            "INSERT INTO Users (Name, Email) VALUES ('Piotr Lewandowski', 'piotr@example.com');"
        };

        string[] insertProducts = new[]
        {
            "INSERT INTO Products (Name, Price, Stock) VALUES ('Laptop', 2999.99, 5);",
            "INSERT INTO Products (Name, Price, Stock) VALUES ('Mysz', 49.99, 50);",
            "INSERT INTO Products (Name, Price, Stock) VALUES ('Klawiatura', 199.99, 20);"
        };

        foreach (var query in insertUsers)
        {
            using (var cmd = new SqliteCommand(query, connection))
                cmd.ExecuteNonQuery();
        }

        foreach (var query in insertProducts)
        {
            using (var cmd = new SqliteCommand(query, connection))
                cmd.ExecuteNonQuery();
        }
    }

    /// <summary>
    /// Wykonanie zapytania SELECT
    /// </summary>
    public string QueryDatabase(string tableName, string whereClause = "")
    {
        try
        {
            using (var connection = new SqliteConnection(_connectionString))
            {
                connection.Open();

                string query = $"SELECT * FROM {tableName}";
                if (!string.IsNullOrEmpty(whereClause))
                    query += $" WHERE {whereClause}";
                query += ";";

                using (var cmd = new SqliteCommand(query, connection))
                using (var reader = cmd.ExecuteReader())
                {
                    return ReadResults(reader);
                }
            }
        }
        catch (Exception ex)
        {
            return $"ERROR: {ex.Message}";
        }
    }

    /// <summary>
    /// Wstawienie nowego rekordu
    /// </summary>
    public string InsertData(string tableName, Dictionary<string, string> values)
    {
        try
        {
            using (var connection = new SqliteConnection(_connectionString))
            {
                connection.Open();

                var columns = string.Join(", ", values.Keys);
                var paramValues = string.Join(", ", values.Keys.Select(k => "@" + k));

                string query = $"INSERT INTO {tableName} ({columns}) VALUES ({paramValues});";

                using (var cmd = new SqliteCommand(query, connection))
                {
                    foreach (var kvp in values)
                    {
                        cmd.Parameters.AddWithValue("@" + kvp.Key, kvp.Value);
                    }

                    int rowsAffected = cmd.ExecuteNonQuery();
                    return $"SUCCESS: Wstawiono {rowsAffected} rekord(y)";
                }
            }
        }
        catch (Exception ex)
        {
            return $"ERROR: {ex.Message}";
        }
    }

    /// <summary>
    /// Aktualizacja rekordu
    /// </summary>
    public string UpdateData(string tableName, Dictionary<string, string> setValues, string whereClause)
    {
        try
        {
            using (var connection = new SqliteConnection(_connectionString))
            {
                connection.Open();

                var setClause = string.Join(", ", setValues.Keys.Select(k => $"{k}=@{k}"));
                string query = $"UPDATE {tableName} SET {setClause} WHERE {whereClause};";

                using (var cmd = new SqliteCommand(query, connection))
                {
                    foreach (var kvp in setValues)
                    {
                        cmd.Parameters.AddWithValue("@" + kvp.Key, kvp.Value);
                    }

                    int rowsAffected = cmd.ExecuteNonQuery();
                    return $"SUCCESS: Zaktualizowano {rowsAffected} rekord(y)";
                }
            }
        }
        catch (Exception ex)
        {
            return $"ERROR: {ex.Message}";
        }
    }

    /// <summary>
    /// Usunięcie rekordu
    /// </summary>
    public string DeleteData(string tableName, string whereClause)
    {
        try
        {
            using (var connection = new SqliteConnection(_connectionString))
            {
                connection.Open();

                string query = $"DELETE FROM {tableName} WHERE {whereClause};";

                using (var cmd = new SqliteCommand(query, connection))
                {
                    int rowsAffected = cmd.ExecuteNonQuery();
                    return $"SUCCESS: Usunięto {rowsAffected} rekord(y)";
                }
            }
        }
        catch (Exception ex)
        {
            return $"ERROR: {ex.Message}";
        }
    }

    /// <summary>
    /// Odczyt wyników zapytania
    /// </summary>
    private string ReadResults(SqliteDataReader reader)
    {
        var results = new List<string>();
        results.Add("Wyniki:");

        if (!reader.HasRows)
        {
            results.Add("Brak wyników");
            return string.Join("\n", results);
        }

        // Nagłówki kolumn
        var headers = new List<string>();
        for (int i = 0; i < reader.FieldCount; i++)
        {
            headers.Add(reader.GetName(i));
        }
        results.Add(string.Join(" | ", headers));
        results.Add(new string('-', 50));

        // Wiersze danych
        while (reader.Read())
        {
            var row = new List<string>();
            for (int i = 0; i < reader.FieldCount; i++)
            {
                row.Add(reader.GetValue(i)?.ToString() ?? "NULL");
            }
            results.Add(string.Join(" | ", row));
        }

        return string.Join("\n", results);
    }

    /// <summary>
    /// Lista dostępnych tabel
    /// </summary>
    public string ListTables()
    {
        try
        {
            using (var connection = new SqliteConnection(_connectionString))
            {
                connection.Open();

                string query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';";
                using (var cmd = new SqliteCommand(query, connection))
                using (var reader = cmd.ExecuteReader())
                {
                    var tables = new List<string>();
                    while (reader.Read())
                    {
                        tables.Add(reader.GetString(0));
                    }
                    return $"Tabele: {string.Join(", ", tables)}";
                }
            }
        }
        catch (Exception ex)
        {
            return $"ERROR: {ex.Message}";
        }
    }
}
