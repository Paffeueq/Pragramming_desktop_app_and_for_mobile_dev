using System.ComponentModel.DataAnnotations;

namespace UserApiProject.Models
{
    public class Order
    {
        public int Id { get; set; }

        [Required]
        public string ProductName { get; set; }

        [Range(1, int.MaxValue, ErrorMessage = "Quantity must be greater than 0")]
        public int Quantity { get; set; }

        [Required]
        public string CustomerName { get; set; }

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}
