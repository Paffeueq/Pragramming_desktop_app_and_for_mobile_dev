import requests
import json

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'

# Try v4.0 with different api versions
test_urls = [
    ('vision/v4.0/analyze', '2024-02-01'),  # Latest
    ('vision/v4.0/analyze', '2023-10-01'),
    ('computervision:analyze', '2024-02-01'),  # Alternative path
]

with open('honda.jpg', 'rb') as f:
    data = f.read()

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

for path, api_version in test_urls:
    url = f'{endpoint}{path}?api-version={api_version}&features=Tags,Description,DenseCaptions'
    print(f"\n=== Testing: {path} (api-version={api_version}) ===")
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"SUCCESS! Keys: {list(result.keys())}")
            print(json.dumps(result, indent=2)[:500])
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text[:300])
    except Exception as e:
        print(f"Exception: {str(e)[:150]}")
