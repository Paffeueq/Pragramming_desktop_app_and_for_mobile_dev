public class CityDto
{
    public string? Name { get; set; }
    public string? Country { get; set; }
}

public class CitiesClient
{
    private readonly HttpClient _httpClient;

    public CitiesClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    // get all cities
    public async Task<List<CityDto>> GetAllAsync()
    {
        return await _httpClient.GetFromJsonAsync<List<CityDto>>("/api/Cities");
    }

    // add new city
    public async Task<CityDto> CreateAsync(CityDto city)
    {
        var response = await _httpClient.PostAsJsonAsync("/api/Cities", city);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CityDto>();
    }
}
