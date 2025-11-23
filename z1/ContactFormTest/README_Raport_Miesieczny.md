Instrukcja: jak wypełnić `Raport_Miesieczny.md`

1. Otwórz plik `Raport_Miesieczny.md` w edytorze tekstu (np. VS Code).
2. Uzupełnij nagłówek (Miesiąc, Rok, Przygotował(a)).
3. Uzupełnij sekcję KPI danymi z faktycznych źródeł. Skorzystaj z plików logów, baz danych lub narzędzi analitycznych.
4. W sekcji „Najważniejsze wydarzenia” opisz zdarzenia, które miały największy wpływ na wyniki.
5. Dodaj zadania i przypisz właścicieli. Wprowadź realistyczne terminy.
6. Dołącz załączniki (wykresy, zrzuty ekranów) do sekcji 9 lub umieść je w katalogu `Reports/attachments/` i podaj linki.

Sugestie i opcje rozszerzenia:
- Jeśli chcesz, mogę wygenerować wersję PDF lub DOCX z tego szablonu.
- Mogę również przygotować skrypt (PowerShell / .NET) który wypełni szablon na podstawie pliku JSON lub danych z aplikacji.

Dodano automatyzację (PowerShell):

- Skrypt: `Reports\fill_report.ps1` — czyta plik JSON i tworzy wypełniony Markdown oraz (jeśli zainstalowany) generuje PDF i DOCX przez Pandoc.
- Przykładowe dane: `Reports\sample_data.json`.

Jak uruchomić (PowerShell / pwsh):

1. Otwórz terminal w katalogu projektu.
2. Uruchom:

```powershell
# przykład
pwsh -NoProfile -ExecutionPolicy Bypass -File .\Reports\fill_report.ps1 -InputJson .\Reports\sample_data.json -OutDir .\Reports\output
```

3. Jeśli chcesz PDF/DOCX, zainstaluj Pandoc (https://pandoc.org/) i upewnij się, że `pandoc` jest w PATH — skrypt wtedy wygeneruje pliki automatycznie.

Powiedz, czy chcesz, bym uruchomił skrypt teraz i wygenerował pliki (Markdown i PDF/DOCX jeśli pandoc jest dostępny).
