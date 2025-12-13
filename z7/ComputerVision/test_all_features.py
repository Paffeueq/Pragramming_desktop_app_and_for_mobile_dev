import requests
import json

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'

# Try ALL possible combinations WITHOUT celebrities
test_cases = [
    ('Tags,Description', None),
    ('Objects', None),
    ('Faces', None),
    ('Brands', None),
    ('Color', None),
    ('ImageType', None),
    ('Tags,Description,Objects,Faces,Brands,Color,ImageType', None),
    ('Tags,Description', 'Landmarks'),
]

with open('honda.jpg', 'rb') as f:
    data = f.read()

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

for features, details in test_cases:
    query = f'features={features}'
    if details:
        query += f'&details={details}'
    url = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01&{query}'
    
    print(f"\n=== Features: {features}" + (f" | Details: {details}" if details else "") + " ===")
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        
        # Print only non-empty/new keys
        print(f"Keys: {list(result.keys())}")
        if 'tags' in result:
            print(f"✓ TAGS FOUND: {result['tags']}")
        if 'description' in result:
            print(f"✓ DESCRIPTION: {result['description']}")
        if 'objects' in result:
            print(f"✓ OBJECTS: {result['objects']}")
        if 'faces' in result:
            print(f"✓ FACES: {result['faces']}")
        if 'brands' in result:
            print(f"✓ BRANDS: {result['brands']}")
        if 'color' in result:
            print(f"✓ COLOR: {result['color']}")
        if 'imageType' in result:
            print(f"✓ IMAGE TYPE: {result['imageType']}")
            
        if result.get('code') == 'UnsupportedFeature':
            print(f"✗ UNSUPPORTED: {result['message']}")
            
    except Exception as e:
        print(f"Exception: {str(e)[:100]}")
