import requests
import json

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'

# Test 1: Only Tags
url1 = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01&features=Tags'
# Test 2: Tags and Description
url2 = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01&features=Tags,Description'
# Test 3: minimal analyze
url3 = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01'

with open('honda.jpg', 'rb') as f:
    data = f.read()

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

print("=== TEST 1: Features=Tags ===")
resp = requests.post(url1, headers=headers, data=data, timeout=30)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(json.dumps(result, indent=2)[:800])
    print(f"\nKeys in response: {list(result.keys())}")
else:
    print(resp.text[:300])

print("\n=== TEST 2: Features=Tags,Description ===")
resp = requests.post(url2, headers=headers, data=data, timeout=30)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(json.dumps(result, indent=2)[:800])
    print(f"\nKeys in response: {list(result.keys())}")
else:
    print(resp.text[:300])

print("\n=== TEST 3: No features param ===")
resp = requests.post(url3, headers=headers, data=data, timeout=30)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(json.dumps(result, indent=2)[:800])
    print(f"\nKeys in response: {list(result.keys())}")
else:
    print(resp.text[:300])
