namespace VisionIntegrationApi.Models
{
    /// <summary>
    /// Konfiguracja Azure Computer Vision
    /// </summary>
    public class VisionServiceOptions
    {
        public const string SectionName = "VisionService";
        
        public string? Endpoint { get; set; }
        public string? Key { get; set; }
    }

    /// <summary>
    /// Konfiguracja Key Vault
    /// </summary>
    public class KeyVaultOptions
    {
        public const string SectionName = "KeyVault";
        
        public string? VaultUrl { get; set; }
        public string? TenantId { get; set; }
        public string? ClientId { get; set; }
        public string? ClientSecret { get; set; }
    }

    /// <summary>
    /// Request do analizy obrazu
    /// </summary>
    public class AnalyzeImageRequest
    {
        public string? ImageUrl { get; set; }
        public string? ImageBase64 { get; set; }
    }

    /// <summary>
    /// Response z wynikami analizy
    /// </summary>
    public class AnalyzeImageResponse
    {
        public string? Status { get; set; }
        public string? Description { get; set; }
        public string? ImageFile { get; set; }
        public Dictionary<string, object>? AnalysisResults { get; set; }
        public string? Error { get; set; }
        public long ProcessingTimeMs { get; set; }
    }
}
