import requests
import json

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'

# Test different API versions
versions = [
    ('v3.0', '2021-04-01'),
    ('v3.1', '2021-04-01'),
    ('v3.2', '2021-04-01'),
]

with open('honda.jpg', 'rb') as f:
    data = f.read()

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

for vision_version, api_version in versions:
    url = f'{endpoint}vision/{vision_version}/analyze?api-version={api_version}&features=Tags,Description'
    print(f"\n=== Testing: vision/{vision_version} (api-version={api_version}) ===")
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"Keys in response: {list(result.keys())}")
            if 'tags' in result:
                print(f"Tags found: {result['tags'][:100]}")
            if 'description' in result:
                print(f"Description found: {result['description']['captions']}")
        else:
            print(f"Error: {resp.text[:200]}")
    except Exception as e:
        print(f"Exception: {str(e)[:100]}")
