using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using System.Collections.Generic;
using System.Linq;

namespace CopilotTest.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    // In-memory storage
    private static readonly List<User> Users = new()
    {
        new User { Id = 1, Name = "Alice", Email = "alice@example.com" },
        new User { Id = 2, Name = "Bob", Email = "bob@example.com" }
    };

    private static int NextId = Users.Max(u => u.Id) + 1;

    // GET /api/users
    [HttpGet]
    public ActionResult<IEnumerable<User>> GetAll()
    {
        return Ok(Users);
    }

    // GET /api/users/{id}
    [HttpGet("{id:int}")]
    public ActionResult<User> Get(int id)
    {
        var user = Users.FirstOrDefault(u => u.Id == id);
        if (user == null) return NotFound();
        return Ok(user);
    }

    // POST /api/users
    [HttpPost]
    public ActionResult<User> Create([FromBody] UserCreateDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);

        var user = new User { Id = NextId++, Name = dto.Name, Email = dto.Email };
        Users.Add(user);

        return CreatedAtAction(nameof(Get), new { id = user.Id }, user);
    }

    // PUT /api/users/{id}
    [HttpPut("{id:int}")]
    public ActionResult Update(int id, [FromBody] UserUpdateDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);

        var user = Users.FirstOrDefault(u => u.Id == id);
        if (user == null) return NotFound();

        user.Name = dto.Name;
        user.Email = dto.Email;

        return Ok(user);
    }

    // DELETE /api/users/{id}
    [HttpDelete("{id:int}")]
    public ActionResult Delete(int id)
    {
        var user = Users.FirstOrDefault(u => u.Id == id);
        if (user == null) return NotFound();

        Users.Remove(user);
        return NoContent();
    }

    // DTOs
    public record UserCreateDto([Required] string Name, [Required][EmailAddress] string Email);
    public record UserUpdateDto([Required] string Name, [Required][EmailAddress] string Email);
}
