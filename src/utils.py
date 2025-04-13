import os
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 🌐 Use st.secrets for Streamlit Cloud (fallback to .env locally)
try:
    import streamlit as st
    API_KEY = st.secrets["FRED_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("FRED_API_KEY")


def get_fred_data(series_id, start_date="2000-01-01"):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "observation_start": start_date
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        if "observations" not in data:
            print(f"❌ FRED API Error for {series_id}: {data}")
            return pd.DataFrame()

        df = pd.DataFrame(data["observations"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])
        return df

    except Exception as e:
        print("❌ get_fred_data() failed:", e)
        return pd.DataFrame()


def detect_start_date(query: str, default="2010-01-01"):
    now = datetime.now()
    query = query.lower()

    if "last 2 months" in query:
        return (now - relativedelta(months=2)).strftime("%Y-%m-%d")
    if "last 6 months" in query:
        return (now - relativedelta(months=6)).strftime("%Y-%m-%d")
    if "past year" in query or "last year" in query:
        return (now - relativedelta(years=1)).strftime("%Y-%m-%d")

    return default


def filter_recent_data(df, start_date):
    return df[df["date"] >= pd.to_datetime(start_date)].copy()
