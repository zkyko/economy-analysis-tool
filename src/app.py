import streamlit as st
import sys
import os
import json
import pandas as pd
import subprocess
from datetime import datetime
import io
import plotly.express as px

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Modular imports
from tools.layout.app_layout import init_layout
from tools.ui.tab_browser import render_browser_tab
from tools.ui.tab_questions import render_qa_tab
from tools.ui.tab_compare import render_compare_tab
from tools.layout.theme_config import setup_theme
from tools.ui.tab_speech import render_speech_section

# --- Setup Theme and Layout ---
setup_theme()
left, right = init_layout()

# --- Load Indicator Metadata ---
with open(os.path.join('src', 'data', 'fred_keywords.json')) as f:
    data = json.load(f)
    indicators = pd.DataFrame.from_dict(data, orient='index')
    indicators = indicators.reset_index().rename(columns={'index': 'keyword'})
categories = sorted(indicators["type"].unique())
filtered = indicators.copy()

# --- Define Shared Utility Functions ---
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

# --- Terminal-Style Sidebar ---
with left:
    from tools.layout.terminal_panel import render_terminal_nav
    render_terminal_nav()

# --- Main App Tabs ---
with right:
    with st.expander("🧭 Getting Started (click to view help)", expanded=False):
        st.markdown("""
        - Use the left pane to **navigate** or **trigger actions**.
        - Start by selecting an indicator (e.g. GDP, CPI).
        - Ask follow-up questions in the Q&A panel.
        - Use Compare Series to analyze multiple indicators at once.
        """)
    from tools.ui.tab_tradingview import render_tradingview_tab
    tabs = st.tabs(["➜ Browse Indicators", "➜ Run Economic Q&A", "➜ Compare Series", "➜ TradingView Chart"])
    with tabs[0]:
        render_browser_tab(indicators, filtered, categories, get_fred_data, summarize_series)
    with tabs[1]:
        render_qa_tab(indicators, get_fred_data, summarize_series)
    with tabs[2]:
        render_compare_tab(indicators, get_fred_data)
    with tabs[3]:
        render_tradingview_tab()

# --- Speech Summary Section ---
render_speech_section()

# --- Final Test Card ---
from ui_query_panel import render_card
def test_card_content():
    st.write("✅ This is content inside the test card.")
render_card("🧪 Card Test", content_func=test_card_content)
