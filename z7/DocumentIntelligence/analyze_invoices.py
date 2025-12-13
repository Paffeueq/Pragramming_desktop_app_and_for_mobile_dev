#!/usr/bin/env python3
"""
Azure Document Intelligence - Prebuilt Invoice Analysis
Przesyła faktury do Azure Document Intelligence API i analizuje wyniki JSON
"""

import json
import requests
import base64
from pathlib import Path
from datetime import datetime

# Konfiguracja Azure Document Intelligence
ENDPOINT = "https://azdocument.cognitiveservices.azure.com/"
API_KEY = "CrEjcF82i1NUGrurSkTNJNcOm2EttKH68Ahy7DLezzOMhI7ZRUFfJQQJ99BLACYeBjFXJ3w3AAALACOGwTPc"
API_VERSION = "2024-02-29-preview"

# Modele prebuilt
MODEL_ID = "prebuilt-invoice"


def analyze_invoice_file(file_path):
    """
    Wysyła plik faktury do Azure Document Intelligence API
    i zwraca wynik analizy
    """
    
    if not Path(file_path).exists():
        print(f"❌ Plik nie znaleziony: {file_path}")
        return None
    
    # Endpoint dla analizy dokumentu
    url = f"{ENDPOINT}documentintelligence/documentModels/{MODEL_ID}:analyze?api-version={API_VERSION}"
    
    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": API_KEY
    }
    
    # Odczytanie pliku
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    print(f"\n📤 Wysyłam: {Path(file_path).name} ({len(file_data)} bytes)")
    
    try:
        # Wysłanie do Azure
        response = requests.post(url, headers=headers, data=file_data)
        response.raise_for_status()
        
        # Pobranie operation-location do śledzenia zadania
        operation_location = response.headers.get("Operation-Location")
        
        if operation_location:
            print(f"⏳ Operation Location: {operation_location}")
            return poll_result(operation_location, headers)
        else:
            print("❌ Brak Operation-Location w nagłówkach")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd API: {e}")
        return None


def poll_result(operation_location, headers):
    """
    Czeka na wynik analizy dokumentu
    """
    import time
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(operation_location, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            status = result.get("status")
            
            if status == "succeeded":
                print("✅ Analiza zakończona pomyślnie")
                return result
            elif status == "failed":
                print(f"❌ Analiza nie powiodła się: {result.get('error')}")
                return None
            else:
                print(f"⏳ Status: {status} (spróba {retry_count + 1}/{max_retries})")
                retry_count += 1
                time.sleep(2)
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Błąd przy sprawdzeniu wyniku: {e}")
            return None
    
    print("❌ Upłynął limit czasu oczekiwania na wynik")
    return None


def extract_key_fields(document):
    """
    Wyodrębnia kluczowe pola z analizowanej faktury
    """
    
    if not document:
        return None
    
    fields = document.get("fields", {})
    
    extracted = {
        "invoice_number": fields.get("InvoiceNumber", {}),
        "invoice_date": fields.get("InvoiceDate", {}),
        "due_date": fields.get("DueDate", {}),
        "currency": fields.get("Currency", {}),
        "vendor_name": fields.get("VendorName", {}),
        "vendor_address": fields.get("VendorAddress", {}),
        "customer_name": fields.get("CustomerName", {}),
        "customer_address": fields.get("CustomerAddress", {}),
        "subtotal": fields.get("SubTotal", {}),
        "total_tax": fields.get("TotalTax", {}),
        "invoice_total": fields.get("InvoiceTotal", {}),
        "items": fields.get("Items", {}),
    }
    
    return extracted


def print_analysis_results(filename, result):
    """
    Wypisuje wyniki analizy w czytelnym formacie
    """
    
    print("\n" + "="*70)
    print(f"📋 WYNIKI ANALIZY: {filename}")
    print("="*70)
    
    if not result or result.get("status") != "succeeded":
        print("❌ Nie udało się przeanalizować dokumentu")
        return
    
    # Pobranie dokumentu z wynikami
    documents = result.get("analyzeResult", {}).get("documents", [])
    
    if not documents:
        print("❌ Brak dokumentów w wyniku")
        return
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    # Wyświetlanie kluczowych pól
    print("\n📌 POLA FAKTURY:")
    print("-" * 70)
    
    key_fields = [
        ("Numer faktury", "InvoiceNumber"),
        ("Data faktury", "InvoiceDate"),
        ("Data płatności", "DueDate"),
        ("Waluta", "Currency"),
        ("Nazwa sprzedawcy", "VendorName"),
        ("Adres sprzedawcy", "VendorAddress"),
        ("Nazwa kupującego", "CustomerName"),
        ("Adres kupującego", "CustomerAddress"),
        ("Razem netto", "SubTotal"),
        ("Razem podatek", "TotalTax"),
        ("Razem brutto", "InvoiceTotal"),
    ]
    
    for label, key in key_fields:
        if key in fields:
            field_data = fields[key]
            value = field_data.get("content", "N/A")
            confidence = field_data.get("confidence", 0.0)
            
            print(f"\n  {label}:")
            print(f"    Wartość: {value}")
            print(f"    Confidence: {confidence:.2%}")
    
    # Wyświetlanie tabeli przedmiotów
    print("\n\n📊 PRZEDMIOTY/POZYCJE:")
    print("-" * 70)
    
    if "Items" in fields:
        items_data = fields["Items"]
        
        if items_data.get("type") == "array":
            items = items_data.get("valueArray", [])
            
            print(f"\nIlość przedmiotów: {len(items)}")
            print(f"Confidence całej tabeli: {items_data.get('confidence', 0.0):.2%}\n")
            
            for idx, item in enumerate(items, 1):
                item_fields = item.get("valueObject", {})
                print(f"  Przedmiot #{idx}:")
                
                for item_key in ["Description", "Quantity", "UnitPrice", "Amount"]:
                    if item_key in item_fields:
                        item_field = item_fields[item_key]
                        content = item_field.get("content", "N/A")
                        conf = item_field.get("confidence", 0.0)
                        print(f"    {item_key}: {content} (conf: {conf:.2%})")
                print()
    
    # Informacje dodatkowe
    print("\n📈 PODSUMOWANIE:")
    print("-" * 70)
    print(f"Typ dokumentu: {doc.get('docType', 'N/A')}")
    print(f"Confidence dokumentu: {doc.get('confidence', 0.0):.2%}")
    print(f"Liczba stron: {len(doc.get('pages', []))}")
    
    print("\n" + "="*70 + "\n")
    
    return extract_key_fields(doc)


def save_json_results(filename, result):
    """
    Zapisuje pełny JSON rezultat do pliku
    """
    
    output_file = Path(filename).stem + "_analysis.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Wynik zapisany: {output_file}")
    return output_file


def main():
    """
    Główna funkcja - analiza wszystkich faktur
    """
    
    print("\n🔍 Azure Document Intelligence - Invoice Analysis")
    print("=" * 70)
    
    # Lista faktur do analizy
    invoices = [
        "invoice_acme_001.pdf",
        "invoice_globaltech_002.pdf",
        "invoice_techstartup_003.pdf",
    ]
    
    results_summary = []
    
    for invoice_file in invoices:
        invoice_path = Path(invoice_file)
        
        if not invoice_path.exists():
            print(f"⚠️  Plik nie znaleziony: {invoice_file}")
            continue
        
        # Analiza faktury
        result = analyze_invoice_file(invoice_file)
        
        if result:
            # Wyświetlenie wyników
            extracted = print_analysis_results(invoice_file, result)
            
            # Zapis JSON
            json_file = save_json_results(invoice_file, result)
            
            # Dodanie do podsumowania
            if extracted:
                results_summary.append({
                    "file": invoice_file,
                    "json": json_file,
                    "extracted": extracted
                })
    
    # Podsumowanie
    print("\n\n📋 PODSUMOWANIE ANALIZY")
    print("=" * 70)
    print(f"Przeanalizowanych faktur: {len(results_summary)}")
    
    for result in results_summary:
        print(f"\n  ✅ {result['file']}")
        print(f"     JSON: {result['json']}")
    
    print("\n" + "=" * 70)
    print("✅ Analiza zakończona!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
