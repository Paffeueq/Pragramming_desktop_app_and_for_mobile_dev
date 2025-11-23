var builder = WebApplication.CreateBuilder(args);

// Add Razor Pages services
builder.Services.AddRazorPages();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
	app.UseDeveloperExceptionPage();
}

app.UseStaticFiles();

// Map Razor Pages
app.MapRazorPages();

// Redirect root to the contact page
app.MapGet("/", ctx =>
{
	ctx.Response.Redirect("/Contact");
	return System.Threading.Tasks.Task.CompletedTask;
});

app.Run();
