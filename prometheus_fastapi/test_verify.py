import requests
import json

url = "http://localhost:8001/verify"

payload = {
    "land_id": "PLOT-000099",
    "owner_name": "Atim",
    "national_id": "UG099",
    "amount": 25000000,
    "date": "2024-01-01"
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))