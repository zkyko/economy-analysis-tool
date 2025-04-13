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

from utils import get_fred_data, detect_start_date, filter_recent_data
from llm import extract_fred_series, summarize_series
from keyword_mapper import load_keyword_map, match_keywords_to_fred
from ui import render_data_and_summary

st.set_page_config(page_title="Economic Dashboard", layout="wide")
st.title("📊 AI-Powered Economic Dashboard")

# -----------------------------
# 📤 Economic Data Section
# -----------------------------
query = st.text_input("Ask a question about the economy:", "Show me GDP and inflation since 2010")

def compute_yoy(df):
    df = df.copy()
    df["value_yoy"] = df["value"].pct_change(periods=12) * 100
    return df

if st.button("Run Query"):
    keyword_dict = load_keyword_map()
    matched_series = match_keywords_to_fred(query, keyword_dict)
    start_date = detect_start_date(query, default="2010-01-01")

    if matched_series:
        st.info("🎯 Matched series using keyword map (no LLM needed)")
        for series in matched_series:
            df = get_fred_data(series["id"], start_date)
            df = filter_recent_data(df, start_date)
            if not df.empty:
                if series.get("yoy"):
                    df = compute_yoy(df)
                    summary = summarize_series(f"{series['label']} (YoY)", df)
                    render_data_and_summary(df, summary, f"{series['label']} (YoY)", use_yoy=True)
                else:
                    summary = summarize_series(series["label"], df)
                    render_data_and_summary(df, summary, series["label"])
            else:
                st.warning(f"No data found for {series['label']}")
        st.stop()

    st.info("🤖 No keyword matched — sending prompt to DeepSeek...")
    result = extract_fred_series(query)
    st.subheader("🔍 LLM Response (Raw)")
    st.code(json.dumps(result, indent=2), language="json")

    if not result or "series" not in result:
        st.error("❌ Sorry, I couldn't interpret that request.")
        st.stop()

    start_date = result.get("start_date", "2000-01-01")
    for series in result["series"]:
        df = get_fred_data(series["id"], start_date)
        df = filter_recent_data(df, start_date)
        if not df.empty:
            if series.get("yoy"):
                df = compute_yoy(df)
                summary = summarize_series(f"{series['label']} (YoY)", df)
                render_data_and_summary(df, summary, f"{series['label']} (YoY)", use_yoy=True)
            else:
                summary = summarize_series(series["label"], df)
                render_data_and_summary(df, summary, series["label"])
        else:
            st.warning(f"No data found for {series['label']}")

# -----------------------------
# 🎤 Fed Speech Summaries Section
# -----------------------------
st.markdown("---")
st.header("🎤 Federal Reserve Speech Summaries")

@st.cache_data
def load_or_scrape_speeches():
    filepath = "src/data/fed_rss_summaries.json"
    if not os.path.exists(filepath):
        st.warning("🔄 No speech file found. Running scraper...")
        result = subprocess.run(["python", "src/tools/rss_scraper.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("❌ Failed to scrape Fed speeches.")
            return []
    with open(filepath) as f:
        return json.load(f)

# Load and preprocess data
speeches = load_or_scrape_speeches()

if speeches:
    def parse_date(d):
        try:
            return datetime.strptime(d, "%B %d, %Y")
        except:
            return datetime.min

    speeches = sorted(speeches, key=lambda x: parse_date(x["date"]), reverse=True)
    df_all = pd.DataFrame(speeches)

    # 🧠 Filter UI
    sentiment_options = sorted(set(df_all["sentiment"].fillna("Unknown")))
    speaker_options = sorted(set(df_all["speaker"].fillna("Unknown")))
    selected_sentiment = st.selectbox("🗣️ Filter by Sentiment", ["All"] + sentiment_options)
    selected_speaker = st.selectbox("🧑 Filter by Speaker", ["All"] + speaker_options)
    search_query = st.text_input("🔍 Search title or summary").lower()

    # 🧹 Filter Logic
    def apply_filters():
        return df_all[
            ((df_all["sentiment"] == selected_sentiment) | (selected_sentiment == "All")) &
            ((df_all["speaker"] == selected_speaker) | (selected_speaker == "All")) &
            (df_all["title"].str.lower().str.contains(search_query) | df_all["summary"].str.lower().str.contains(search_query))
        ]

    filtered_df = apply_filters()

    # 📆 Plotly Timeline View
    if not filtered_df.empty:
        fig = px.timeline(
            filtered_df,
            x_start=pd.to_datetime(filtered_df["date"], errors="coerce"),
            x_end=pd.to_datetime(filtered_df["date"], errors="coerce"),
            y="speaker",
            color="sentiment",
            hover_data=["title", "summary"]
        )
        fig.update_layout(title="🗓️ Fed Speeches Timeline", xaxis_title="Date", yaxis_title="Speaker", height=500)
        st.plotly_chart(fig, use_container_width=True)

    # 📜 Pagination for Long Lists
    PAGE_SIZE = 5
    page = st.number_input("📄 Page", min_value=1, max_value=(len(filtered_df) // PAGE_SIZE + 1), step=1)
    start_idx = (page - 1) * PAGE_SIZE
    page_df = filtered_df.iloc[start_idx:start_idx + PAGE_SIZE]

    sentiment_colors = {
        "Hawkish": "🔴", "Dovish": "🟢", "Neutral": "⚪", "Unknown": "❓"
    }

    for _, speech in page_df.iterrows():
        color = sentiment_colors.get(speech.get("sentiment", "Unknown"), "❓")
        st.subheader(f"{speech['title']} ({speech['date']})")
        st.caption(f"[📄 View Full Speech]({speech['url']})")
        st.markdown(f"🧑 **Speaker:** {speech.get('speaker', 'Unknown')}")
        st.markdown(f"📍 **Location:** {speech.get('location', 'Unknown')}")
        st.markdown(f"🧠 **Summary:** {speech.get('summary', '')}")
        st.markdown(f"{color} **Sentiment:** `{speech.get('sentiment', 'Unknown')}`")

    # 📤 Export Section
    st.markdown("---")
    st.subheader("📤 Export Speech Summaries")

    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)

    md_buffer = io.StringIO()
    for _, s in filtered_df.iterrows():
        md_buffer.write(f"### {s['title']} ({s['date']})\n")
        md_buffer.write(f"[View Full Speech]({s['url']})\n\n")
        md_buffer.write(f"**Speaker:** {s.get('speaker', 'Unknown')}\n\n")
        md_buffer.write(f"**Location:** {s.get('location', 'Unknown')}\n\n")
        md_buffer.write(f"**Sentiment:** {s.get('sentiment', 'Unknown')}\n\n")
        md_buffer.write(f"**Summary:**\n{s['summary']}\n\n---\n")

    st.download_button("📄 Download CSV", data=csv_buffer.getvalue(), file_name="fed_summaries.csv", mime="text/csv")
    st.download_button("📝 Download Markdown", data=md_buffer.getvalue(), file_name="fed_summaries.md", mime="text/markdown")
else:
    st.warning("No Fed speech data available.")
