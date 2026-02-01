import requests
import os

url = "http://127.0.0.1:8000/analyze"
file_path = "sleep_edf_data/SC4201E0-PSG.edf"

if not os.path.exists(file_path):
    print("File not found")
    exit(1)

print(f"Uploading {file_path} to {url}...")
with open(file_path, 'rb') as f:
    files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
    # We skip auth for now to see if the upload itself works
    response = requests.post(url, files=files)

print(f"Status: {response.status_code}")
try:
    print(f"Response: {response.json()}")
except:
    print(f"Response: {response.text}")
