import os
import json
import requests
from dotenv import load_dotenv
import re
import pandas as pd

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def extract_fred_series(prompt):
    system_msg = """You are a helpful assistant that takes economic questions and returns relevant FRED series to query.\nRespond ONLY in valid JSON format like this:\n{\n  \"series\": [{\"id\": \"CPIAUCSL\", \"label\": \"Consumer Price Index\"}],\n  \"start_date\": \"2018-01-01\"\n}\nDo not include extra explanation, markdown, or text outside the JSON."""
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    try:
        res = requests.post(DEEPSEEK_URL, headers=HEADERS, json=body)
        res.raise_for_status()
        text = res.json()["choices"][0]["message"]["content"].strip()
        print("🧠 LLM Raw Output:\n", text)
        if text.startswith("```"):
            text = re.sub(r"```(json)?", "", text).strip()
        return json.loads(text)
    except requests.exceptions.RequestException as e:
        print("❌ Request error:", e)
        return None
    except json.JSONDecodeError as e:
        print("⚠️ JSON parse error:", e)
        return None

def summarize_series(series_name, df, time_range=None, desc=None):
    if df.empty:
        return f"No data available for {series_name}."
    latest = df.iloc[-1]
    msg = f"**{series_name}**\n\nLatest value: **{latest['value']:.2f}** on {latest['date'].date()}"
    if time_range:
        msg += f"\nTime range: {time_range}"
    if desc:
        msg += f"\nDescription: {desc}"
    if len(df) > 12:
        prev = df.iloc[-13]
        pct = (latest['value'] - prev['value']) / abs(prev['value']) * 100 if prev['value'] != 0 else float('nan')
        msg += f"\nYoY change: **{pct:.2f}%**"
    msg += f"\n\nMin: {df['value'].min():.2f} | Max: {df['value'].max():.2f}"
    return msg

def get_fred_data(series_id, start_date="2000-01-01", api_key=None):
    import requests
    import pandas as pd
    import os

    print(f"📡 Fetching FRED series: {series_id}")
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key or os.getenv("FRED_API_KEY"),
        "file_type": "json",
        "observation_start": start_date
    }

    res = requests.get(url, params=params)
    print("🔍 Response status:", res.status_code)
    print("🔍 Response body (short):", res.text[:200])

    data = res.json()
    if "observations" not in data:
        print("⚠️ No 'observations' in response.")
        return pd.DataFrame()
    df = pd.DataFrame(data["observations"])
    if df.empty:
        print("⚠️ No observations found.")
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def get_fred_metadata(series_id, api_key=None):
    """
    Fetch FRED series metadata (title, units, description, etc).
    Returns a dict.
    """
    import requests
    api_key = api_key or os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not set in environment.")
    url = "https://api.stlouisfed.org/fred/series"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"FRED metadata error: {r.status_code}")
        return {}
    data = r.json()
    series = data.get("seriess", [{}])[0]
    return series

