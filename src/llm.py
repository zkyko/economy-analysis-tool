import os
import json
import requests
import re

# ✅ Use st.secrets on Streamlit Cloud; fallback to .env locally
try:
    import streamlit as st
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def extract_fred_series(prompt):
    system_msg = """You are a helpful assistant that takes economic questions and returns relevant FRED series to query.
Respond ONLY in valid JSON format like this:
{
  "series": [{"id": "CPIAUCSL", "label": "Consumer Price Index"}],
  "start_date": "2018-01-01"
}
Do not include extra explanation, markdown, or text outside the JSON.
"""

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

        if text.startswith("```"):
            text = re.sub(r"```(json)?", "", text).strip()

        return json.loads(text)

    except requests.exceptions.RequestException as e:
        print("❌ DeepSeek request error:", e)
        return None
    except json.JSONDecodeError as e:
        print("⚠️ DeepSeek JSON parse error:", e)
        return None


def summarize_series(series_name, df):
    system_msg = f"""You are an economic analyst. Summarize the trend in the following data in simple, plain English.
Highlight major changes, turning points, and trends. Provide a short conclusion on what this might mean.

Series name: {series_name}
Time range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
"""

    recent_data = df.tail(12)[["date", "value"]].copy()
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
