# Dockerfile dla serwera MCP

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

COPY ["MCPServer.csproj", "."]
RUN dotnet restore "MCPServer.csproj"

COPY . .
RUN dotnet build "MCPServer.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "MCPServer.csproj" -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/runtime:9.0
WORKDIR /app
COPY --from=publish /app/publish .

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["dotnet", "MCPServer.dll"]
