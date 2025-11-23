using Microsoft.AspNetCore.Mvc;
using ShopAPI.Api.Dtos;

namespace ShopAPI.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CitiesController : ControllerBase
    {
        private static List<City> Cities = new()
        {
            new City { Id = 1, Name = "Warsaw", Country = "Poland" },
            new City { Id = 2, Name = "Berlin", Country = "Germany" },
            new City { Id = 3, Name = "Paris", Country = "France" },
            new City { Id = 4, Name = "Madrid", Country = "Spain" }
        };

        [HttpGet]
        public ActionResult<List<City>> GetAll() => Cities;

        [HttpGet("{id}")]
        public ActionResult<City> Get(int id)
        {
            var city = Cities.FirstOrDefault(c => c.Id == id);
            return city == null ? NotFound() : city;
        }

        [HttpPost]
        public ActionResult<City> Create(CityDto cityDto)
        {
            if (string.IsNullOrWhiteSpace(cityDto.Name))
                return BadRequest("Name is required.");

            var city = new City
            {
                Id = Cities.Any() ? Cities.Max(c => c.Id) + 1 : 1,
                Name = cityDto.Name,
                Country = cityDto.Country
            };

            Cities.Add(city);
            return CreatedAtAction(nameof(Get), new { id = city.Id }, city);
        }

        [HttpPut("{id}")]
        public ActionResult Update(int id, CityDto cityDto)
        {
            var city = Cities.FirstOrDefault(c => c.Id == id);
            if (city == null) return NotFound();

            city.Name = cityDto.Name;
            city.Country = cityDto.Country;
            return NoContent();
        }

        [HttpPatch("{id}")]
        public ActionResult Patch(int id, [FromBody] Dictionary<string, string> fields)
        {
            var city = Cities.FirstOrDefault(c => c.Id == id);
            if (city == null) return NotFound();

            if (fields.ContainsKey("Name") && Cities.Any(c => c.Name == fields["Name"] && c.Id != id))
                return Conflict("City with this name already exists.");

            if (fields.ContainsKey("Country"))
                city.Country = fields["Country"];
            if (fields.ContainsKey("Name"))
                city.Name = fields["Name"];

            return NoContent();
        }

        [HttpDelete("{id}")]
        public ActionResult Delete(int id)
        {
            var city = Cities.FirstOrDefault(c => c.Id == id);
            if (city == null) return NotFound();

            Cities.Remove(city);
            return NoContent();
        }

        [HttpHead("{id}")]
        public ActionResult Head(int id)
        {
            var city = Cities.FirstOrDefault(c => c.Id == id);
            return city == null ? NotFound() : Ok();
        }

        [HttpOptions]
        public IActionResult Options()
        {
            Response.Headers.Add("Allow", "GET,POST,PUT,PATCH,DELETE,HEAD,OPTIONS");
            return Ok();
        }
    }
}
