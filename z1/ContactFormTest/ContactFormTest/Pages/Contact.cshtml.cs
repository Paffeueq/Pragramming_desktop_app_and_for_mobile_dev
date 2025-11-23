using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace ContactFormTest.Pages
{
    public class ContactModel : PageModel
    {
        [BindProperty]
        public InputModel Input { get; set; } = new InputModel();

        public bool Submitted { get; set; }

        public void OnGet()
        {
        }

        public IActionResult OnPost()
        {
            if (!ModelState.IsValid)
            {
                return Page();
            }

            // Here you could send the message by email or store it.
            // For now, just mark as submitted.
            Submitted = true;
            ModelState.Clear();
            return Page();
        }

        public class InputModel
        {
            [Required(ErrorMessage = "Imię jest wymagane")]
            public string? Name { get; set; }

            [Required(ErrorMessage = "Email jest wymagany")]
            [EmailAddress(ErrorMessage = "Nieprawidłowy adres email")]
            public string? Email { get; set; }

            [Required(ErrorMessage = "Wiadomość jest wymagana")]
            public string? Message { get; set; }
        }
    }
}
