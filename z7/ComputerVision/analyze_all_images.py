import requests
import json
import os

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'
url = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01'

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

# Analyze all 5 images
images = [f for f in os.listdir('.') if f.endswith('.jpg')]
images.sort()

results = {}

for img_file in images:
    print(f"\nAnalyzing {img_file}...")
    
    # Get file size
    file_size = os.path.getsize(img_file)
    
    # Read image
    with open(img_file, 'rb') as f:
        data = f.read()
    
    # Call API
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            
            # Store result
            results[img_file] = {
                'status': 'success',
                'file_size_bytes': file_size,
                'categories': result.get('categories', []),
                'metadata': result.get('metadata', {}),
                'requestId': result.get('requestId', '')
            }
            
            # Print result
            print(f"✓ Status: 200 OK")
            print(f"  File Size: {file_size:,} bytes")
            print(f"  Image Dimensions: {result.get('metadata', {}).get('width')}x{result.get('metadata', {}).get('height')}")
            print(f"  Categories: {[cat['name'] for cat in result.get('categories', [])]}")
            
        else:
            print(f"✗ Status: {resp.status_code}")
            results[img_file] = {'status': 'error', 'code': resp.status_code, 'error': resp.text[:100]}
            
    except Exception as e:
        print(f"✗ Exception: {str(e)[:100]}")
        results[img_file] = {'status': 'exception', 'error': str(e)[:100]}

# Save all results
with open('all_analyses.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*50}")
print(f"Analyzed {len(images)} images. Results saved to all_analyses.json")
print(json.dumps(results, indent=2))
