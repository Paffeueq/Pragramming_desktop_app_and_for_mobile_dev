var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddConnectionString("cache");

var api = builder.AddProject("products", "../Shop.Api/Shop.Api.csproj");

var frontend = builder.AddProject("frontend", "../ShopPlatform.Frontend/ShopPlatform.Frontend.csproj");

builder.Build().Run();
