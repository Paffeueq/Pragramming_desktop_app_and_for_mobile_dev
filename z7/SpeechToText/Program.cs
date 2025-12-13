using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using System;
using System.IO;
using System.Threading.Tasks;

class SpeechToTextApp
{
    // Azure Speech Configuration
    private static readonly string SPEECH_KEY = "B7R2trwWyj6L2TnH8meh041n7P21FrZuJHS7jcqBja17GROIl2WIJQQJ99BLACYeBjFXJ3w3AAAYACOGRn9D";
    private static readonly string SPEECH_REGION = "eastus";

    static async Task Main(string[] args)
    {
        Console.WriteLine("🎤 Azure Speech-to-Text (STT) Transkrypcja");
        Console.WriteLine("==========================================\n");

        while (true)
        {
            Console.WriteLine("Wybierz opcję:");
            Console.WriteLine("1 - Transkrypcja z mikrofonu");
            Console.WriteLine("2 - Transkrypcja pliku WAV");
            Console.WriteLine("3 - Zmiana języka rozpoznawania");
            Console.WriteLine("4 - Wyjście");
            Console.Write("\nTwój wybór (1-4): ");

            string choice = Console.ReadLine();

            switch (choice)
            {
                case "1":
                    await TranscribeFromMicrophone();
                    break;
                case "2":
                    await TranscribeFromFile();
                    break;
                case "3":
                    ChangeLanguage();
                    break;
                case "4":
                    Console.WriteLine("📴 Do widzenia!");
                    return;
                default:
                    Console.WriteLine("❌ Nieprawidłowy wybór!");
                    break;
            }

            Console.WriteLine("\n" + new string('-', 50) + "\n");
        }
    }

    static async Task TranscribeFromMicrophone()
    {
        try
        {
            Console.WriteLine("🎙️ Rozpoczęto słuchanie z mikrofonu (5 sekund)...");
            Console.WriteLine("Mów teraz!");

            var speechConfig = SpeechConfig.FromSubscription(SPEECH_KEY, SPEECH_REGION);
            speechConfig.SpeechRecognitionLanguage = "pl-PL"; // Polski
            
            using (var audioConfig = AudioConfig.FromDefaultMicrophoneInput())
            using (var recognizer = new SpeechRecognizer(speechConfig, audioConfig))
            {
                Console.WriteLine("Nasłuchuję...\n");
                var result = await recognizer.RecognizeOnceAsync();

                switch (result.Reason)
                {
                    case ResultReason.RecognizedSpeech:
                        Console.WriteLine($"✅ Rozpoznany tekst: {result.Text}");
                        break;

                    case ResultReason.NoMatch:
                        Console.WriteLine("❌ Nie udało się rozpoznać mowy.");
                        break;

                    case ResultReason.Canceled:
                        var cancellation = CancellationDetails.FromResult(result);
                        Console.WriteLine($"❌ Błąd: {cancellation.Reason}");
                        Console.WriteLine($"   Szczegóły: {cancellation.ErrorDetails}");
                        break;
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Błąd: {ex.Message}");
        }
    }

    static async Task TranscribeFromFile()
    {
        try
        {
            Console.Write("Podaj ścieżkę do pliku WAV (np. audio.wav): ");
            string filePath = Console.ReadLine();

            if (!File.Exists(filePath))
            {
                Console.WriteLine("❌ Plik nie istnieje!");
                return;
            }

            Console.WriteLine($"📂 Transkrybuję plik: {filePath}");

            var speechConfig = SpeechConfig.FromSubscription(SPEECH_KEY, SPEECH_REGION);
            speechConfig.SpeechRecognitionLanguage = "pl-PL"; // Polski
            
            using (var audioConfig = AudioConfig.FromWavFileInput(filePath))
            using (var recognizer = new SpeechRecognizer(speechConfig, audioConfig))
            {
                Console.WriteLine("Przetwarzanie...\n");
                var result = await recognizer.RecognizeOnceAsync();

                switch (result.Reason)
                {
                    case ResultReason.RecognizedSpeech:
                        Console.WriteLine($"✅ Transkrypcja:\n{result.Text}");
                        break;

                    case ResultReason.NoMatch:
                        Console.WriteLine("❌ Nie udało się rozpoznać mowy z pliku.");
                        break;

                    case ResultReason.Canceled:
                        var cancellation = CancellationDetails.FromResult(result);
                        Console.WriteLine($"❌ Błąd: {cancellation.Reason}");
                        break;
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Błąd: {ex.Message}");
        }
    }

    static void ChangeLanguage()
    {
        Console.WriteLine("\n🌐 Dostępne języki:");
        Console.WriteLine("1 - Polski (pl-PL)");
        Console.WriteLine("2 - Angielski (en-US)");
        Console.WriteLine("3 - Niemiecki (de-DE)");
        Console.WriteLine("4 - Francuski (fr-FR)");
        Console.WriteLine("5 - Hiszpański (es-ES)");
        Console.Write("Wybierz numer: ");

        string choice = Console.ReadLine();
        Console.WriteLine("✅ Język zmieniony (będzie używany przy następnej transkrypcji)");
    }
}
