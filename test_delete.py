import requests
import json

# Testar DELETE endpoint
url = "http://localhost:8000/api/v1/presione1/campanhas/1"
headers = {"Content-Type": "application/json"}

print(f"Testing DELETE request to: {url}")

try:
    response = requests.delete(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Content: {response.text}")
except Exception as e:
    print(f"Error: {e}")