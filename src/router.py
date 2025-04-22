# Handles tab routing and dashboard orchestration
import streamlit as st
from tools.layout.app_layout import init_layout
from tools.layout.theme_config import setup_theme
from tools.layout.terminal_panel import render_terminal_nav
from tools.ui.tab_browser import render_browser_tab
from tools.ui.tab_questions import render_qa_tab
from tools.ui.tab_compare import render_compare_tab
from tools.ui.ui_helpers import render_card
from tools.ui.tab_speech import render_speech_section
import pandas as pd
import json
import os

def get_fred_data(series_id, start_date="2000-01-01"):
    import requests
    API_KEY = os.getenv("FRED_API_KEY")
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "observation_start": start_date
    }
    res = requests.get(url, params=params)
    data = res.json()
    if "observations" not in data:
        return pd.DataFrame()
    df = pd.DataFrame(data["observations"])
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

def summarize_series(label, df):
    if df.empty:
        return "No data available."
    latest = df.iloc[-1]
    msg = f"**{label}**\n\nLatest value: **{latest['value']:.2f}** on {latest['date'].date()}"
    if len(df) > 12:
        prev = df.iloc[-13]
        pct = (latest['value'] - prev['value']) / abs(prev['value']) * 100 if prev['value'] != 0 else float('nan')
        msg += f"\nYoY change: **{pct:.2f}%**"
    msg += f"\n\nMin: {df['value'].min():.2f} | Max: {df['value'].max():.2f}"
    return msg

def run_dashboard():
    setup_theme()
    left, right = init_layout()
    # --- Load Indicator Metadata ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(BASE_DIR, 'data', 'fred_keywords.json')
    with open(data_path) as f:
        indicators_dict = json.load(f)
    indicators = pd.DataFrame([
        {**v, "keyword": k} for k, v in indicators_dict.items()
    ])
    categories = sorted(indicators["type"].unique())
    filtered = indicators.copy()
    with left:
        render_terminal_nav()
    with right:
        with st.expander("🧭 Getting Started (click to view help)", expanded=False):
            st.markdown("""
            - Use the left pane to **navigate** or **trigger actions**.
            - Start by selecting an indicator (e.g. GDP, CPI).
            - Ask follow-up questions in the Q&A panel.
            - Use Compare Series to analyze multiple indicators at once.
            """)
        tabs = st.tabs(["➜ Browse Indicators", "➜ Run Economic Q&A", "➜ Compare Series"])
        with tabs[0]:
            render_browser_tab(indicators, filtered, categories, get_fred_data, summarize_series)
        with tabs[1]:
            render_qa_tab(indicators, get_fred_data, summarize_series)
        with tabs[2]:
            render_compare_tab(indicators, get_fred_data)
    render_speech_section()
    def test_card_content():
        st.write("✅ This is content inside the test card.")
    render_card("🧪 Card Test", content_func=test_card_content)
