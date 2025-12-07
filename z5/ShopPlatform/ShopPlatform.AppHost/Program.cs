var builder = DistributedApplication.CreateBuilder(args);

var productsDb = builder.AddConnectionString("productsdb");

var api = builder.AddProject("products", "../Shop.Api/Shop.Api.csproj")
    .WithReference(productsDb);

var frontend = builder.AddProject("frontend", "../ShopPlatform.Frontend/ShopPlatform.Frontend.csproj");

builder.Build().Run();
