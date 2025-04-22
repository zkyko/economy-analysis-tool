import os
import json
import requests
from dotenv import load_dotenv
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

if not OPENAI_API_KEY:
    import streamlit as st
    st.warning("No OpenAI API key found.")


def extract_fred_series(prompt, fallback=False):
    fallback_result = {
        "series": [
            {"id": "CPIAUCSL", "label": "Consumer Price Index"},
            {"id": "PPIACO", "label": "Producer Price Index"}
        ],
        "start_date": "2023-01-01"
    }
    if fallback:
        print("🧪 Using fallback series for test mode.")
        return fallback_result

    system_msg = """
You are an assistant that maps economic questions to FRED series.
Return valid JSON with this structure:

{
  "series": [
    {"id": "CPIAUCSL", "label": "Consumer Price Index"}
  ],
  "start_date": "2023-01-01"
}

Don't return anything else.
"""

    body = {
        "model": "gpt-4-1106-preview",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        res = requests.post(OPENAI_URL, headers=HEADERS, json=body)
        res.raise_for_status()
        raw = res.json()["choices"][0]["message"]["content"].strip()
        print("🧠 LLM Raw Output:\n", raw)
        # Remove code block markdown if present
        if raw.startswith("```"):
            raw = raw.strip("` ").replace("json", "")
        try:
            data = json.loads(raw)
            print("✅ JSON parsed:", data)
            if "series" in data:
                print("✅ Extracted FRED series:", [s["id"] for s in data["series"]])
            else:
                print("⚠️ No 'series' key found in response.")
            return data
        except Exception as e:
            print("❌ JSON Error:", e)
            print("🔎 Raw text that failed to parse:\n", raw)
            return fallback_result
    except Exception as e:
        print("❌ LLM API Error:", e)
        return fallback_result


def summarize_series(series_name, df, time_range=None, desc=None):
    if df.empty:
        return f"No data available for {series_name}."
    # Convert df to CSV for LLM context (handle up to 100 rows for turbo context window)
    csv_data = df.tail(100).to_csv(index=False)
    system_msg = f"""You are an economic analyst. Summarize the trend in the following time series data in simple, plain English.
Highlight major changes, turning points, and trends. Provide a short conclusion on what this might mean.
Series: {series_name}
Time range: {time_range or 'N/A'}
Description: {desc or ''}
CSV data:
{csv_data}
"""
    recent_data["date"] = recent_data["date"].dt.strftime("%Y-%m-%d")
    recent_data = recent_data.to_dict(orient="records")

    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Here is the most recent data:\n{json.dumps(recent_data, indent=2)}"}
        ],
        "temperature": 0.4
    }

    try:
        res = requests.post(DEEPSEEK_URL, headers=HEADERS, json=body)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("❌ Summary generation error:", e)
        return "⚠️ Summary could not be generated."
