#!/usr/bin/env python3
import requests
import json

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'
url = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01&features=Tags,Description,Faces,ImageType,Objects,Brands,Categories,Color'

print("Testing Vision API...")

with open('honda.jpg', 'rb') as f:
    data = f.read()

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

resp = requests.post(url, headers=headers, data=data, timeout=30)
print(f'HTTP Status: {resp.status_code}')

if resp.status_code == 200:
    print('✅ SUCCESS! API jest dostępny!')
    result = resp.json()
    print(f'Tags znalezione: {len(result.get("tags", []))}')
    print(f'Description: {result.get("description", {}).get("captions", [{}])[0].get("text", "N/A")}')
    
    # Zapisz wynik
    with open('honda_analysis.json', 'w') as f:
        json.dump(result, f, indent=2)
    print('Wynik zapisany do honda_analysis.json')
else:
    print(f'❌ Error: {resp.status_code}')
    print(f'Response: {resp.text[:500]}')
