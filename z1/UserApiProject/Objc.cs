using System;

namespace MyApp
{
    public class Obiekt
    {
        public string Name { get; set; }
        public int Age { get; set; }

        public Obiekt(string name, int age)
        {
            Name = name;
            Age = age;
        }

        public void przedstawSie()
        {
            Console.WriteLine($"Cześć, mam na imię {Name} i mam {Age} lat.");
        }

        class Program
        {
            static void Main(string[] args)
            {
                Obiekt obiekt = new Obiekt("Jan", 30);
                obiekt.przedstawSie();
            }
        }
    }
}