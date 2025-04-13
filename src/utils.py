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
    import requests

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": API_KEY,  # This uses st.secrets or .env based on how you configured above
        "file_type": "json",
        "observation_start": start_date
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        # ✅ Check for 'observations' key first
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
    