import requests
import json

endpoint = 'https://eastus.api.cognitive.microsoft.com/'
api_key = 'F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV'

# Try with URL instead of binary
# First - test if language parameter helps
url = f'{endpoint}vision/v3.1/analyze?api-version=2021-04-01&features=Tags,Description,Objects,Faces,Brands,Color,ImageType&details=Celebrities&language=en'

with open('honda.jpg', 'rb') as f:
    data = f.read()

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/octet-stream'
}

print(f"URL: {url}\n")
resp = requests.post(url, headers=headers, data=data, timeout=30)
print(f"Status: {resp.status_code}")
result = resp.json()
print(f"Keys: {list(result.keys())}")
print(json.dumps(result, indent=2))
