using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

public class CityDto
{
    public string? Name { get; set; }
    public string? Country { get; set; }
}

class Program
{
    static async Task Main(string[] args)
    {
        var client = new HttpClient();
        client.BaseAddress = new Uri("https://localhost:7221");

        // GET
        var cities = await client.GetFromJsonAsync<List<CityDto>>("/api/cities");
        Console.WriteLine($"Miasta: {string.Join(", ", cities.Select(c => c.Name))}");

        // POST
        var newCity = new CityDto { Name = "Ilza", Country = "Poland" };
        var response = await client.PostAsJsonAsync("/api/cities", newCity);
        Console.WriteLine($"Dodano miasto, status: {response.StatusCode}");
    }
}
