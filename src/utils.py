import os
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

    res = requests.get(url, params=params)
    data = res.json()
    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

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
