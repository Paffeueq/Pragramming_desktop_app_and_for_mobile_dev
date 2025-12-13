using Azure;
using VisionIntegrationApi.Models;
using Microsoft.Extensions.Options;

namespace VisionIntegrationApi.Services
{
    /// <summary>
    /// Serwis do komunikacji z Azure Computer Vision REST API
    /// </summary>
    public interface IVisionService
    {
        Task<AnalyzeImageResponse> AnalyzeImageFromUrlAsync(string imageUrl);
        Task<AnalyzeImageResponse> AnalyzeImageFromBase64Async(string base64Image);
    }

    public class VisionService : IVisionService
    {
        private readonly IOptions<VisionServiceOptions> _visionOptions;
        private readonly ILogger<VisionService> _logger;

        public VisionService(
            IOptions<VisionServiceOptions> visionOptions,
            ILogger<VisionService> logger)
        {
            _visionOptions = visionOptions;
            _logger = logger;
        }

        /// <summary>
        /// Analiza obrazu z URL
        /// </summary>
        public async Task<AnalyzeImageResponse> AnalyzeImageFromUrlAsync(string imageUrl)
        {
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();

            try
            {
                _logger.LogInformation("Analizowanie obrazu z URL: {ImageUrl}", imageUrl);

                var client = new HttpClient();
                var subscriptionKey = _visionOptions.Value.Key;
                var endpoint = _visionOptions.Value.Endpoint;

                if (string.IsNullOrEmpty(subscriptionKey) || string.IsNullOrEmpty(endpoint))
                {
                    return new AnalyzeImageResponse
                    {
                        Status = "Error",
                        Error = "Brakuje konfiguracji Vision Service (Key lub Endpoint)",
                        ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                    };
                }

                // Przygotowanie request'u
                var requestUrl = $"{endpoint}/vision/v3.2/analyze?visualFeatures=Description,Tags,Objects,Color";
                
                var request = new HttpRequestMessage(HttpMethod.Post, requestUrl);
                request.Headers.Add("Ocp-Apim-Subscription-Key", subscriptionKey);
                request.Content = new StringContent($"{{\"url\":\"{imageUrl}\"}}", 
                    System.Text.Encoding.UTF8, "application/json");

                // Wysłanie request'u
                var response = await client.SendAsync(request);
                var responseContent = await response.Content.ReadAsStringAsync();

                stopwatch.Stop();

                if (response.IsSuccessStatusCode)
                {
                    _logger.LogInformation("Analiza zakończona pomyślnie w {Ms}ms", stopwatch.ElapsedMilliseconds);

                    // Parsowanie wyników
                    var analysisResults = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent);

                    return new AnalyzeImageResponse
                    {
                        Status = "Success",
                        ImageFile = imageUrl,
                        AnalysisResults = analysisResults,
                        ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                    };
                }
                else
                {
                    _logger.LogError("Błąd przy analizie: {StatusCode} - {Content}", 
                        response.StatusCode, responseContent);

                    return new AnalyzeImageResponse
                    {
                        Status = "Error",
                        ImageFile = imageUrl,
                        Error = $"Vision API returned {response.StatusCode}: {responseContent}",
                        ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                    };
                }
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Wyjątek podczas analizy obrazu");

                return new AnalyzeImageResponse
                {
                    Status = "Error",
                    Error = $"Exception: {ex.Message}",
                    ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                };
            }
        }

        /// <summary>
        /// Analiza obrazu z Base64
        /// </summary>
        public async Task<AnalyzeImageResponse> AnalyzeImageFromBase64Async(string base64Image)
        {
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();

            try
            {
                _logger.LogInformation("Analizowanie obrazu z Base64 ({Length} chars)", base64Image.Length);

                var client = new HttpClient();
                var subscriptionKey = _visionOptions.Value.Key;
                var endpoint = _visionOptions.Value.Endpoint;

                if (string.IsNullOrEmpty(subscriptionKey) || string.IsNullOrEmpty(endpoint))
                {
                    return new AnalyzeImageResponse
                    {
                        Status = "Error",
                        Error = "Brakuje konfiguracji Vision Service (Key lub Endpoint)",
                        ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                    };
                }

                // Przygotowanie request'u
                var requestUrl = $"{endpoint}/vision/v3.2/analyze?visualFeatures=Description,Tags,Objects,Color";
                
                var request = new HttpRequestMessage(HttpMethod.Post, requestUrl);
                request.Headers.Add("Ocp-Apim-Subscription-Key", subscriptionKey);
                request.Content = new ByteArrayContent(Convert.FromBase64String(base64Image));
                request.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");

                // Wysłanie request'u
                var response = await client.SendAsync(request);
                var responseContent = await response.Content.ReadAsStringAsync();

                stopwatch.Stop();

                if (response.IsSuccessStatusCode)
                {
                    _logger.LogInformation("Analiza zakończona pomyślnie w {Ms}ms", stopwatch.ElapsedMilliseconds);

                    // Parsowanie wyników
                    var analysisResults = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent);

                    return new AnalyzeImageResponse
                    {
                        Status = "Success",
                        ImageFile = $"Base64 ({base64Image.Length} chars)",
                        AnalysisResults = analysisResults,
                        ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                    };
                }
                else
                {
                    _logger.LogError("Błąd przy analizie: {StatusCode} - {Content}", 
                        response.StatusCode, responseContent);

                    return new AnalyzeImageResponse
                    {
                        Status = "Error",
                        Error = $"Vision API returned {response.StatusCode}: {responseContent}",
                        ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                    };
                }
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Wyjątek podczas analizy obrazu");

                return new AnalyzeImageResponse
                {
                    Status = "Error",
                    Error = $"Exception: {ex.Message}",
                    ProcessingTimeMs = stopwatch.ElapsedMilliseconds
                };
            }
        }
    }
}
