import os
import requests
from dotenv import load_dotenv

# Load your .env file
load_dotenv()
API_KEY = os.getenv("FRED_API_KEY")

def test_fred_connection():
    url = "https://api.stlouisfed.org/fred/series"
    params = {
        "series_id": "GDP",
        "api_key": API_KEY,
        "file_type": "json"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("✅ API Key works! Response received:")
        print(response.json().get("seriess", [{}])[0].get("title", "No title found"))
    else:
        print("❌ API failed. Status code:", response.status_code)
        print(response.text)

if __name__ == "__main__":
    test_fred_connection()
