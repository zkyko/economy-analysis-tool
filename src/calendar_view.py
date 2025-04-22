import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

def render_speech_timeline():
    st.markdown("### 🗓️ Fed Speech Timeline")

    filepath = "src/data/fed_rss_summaries.json"

    if not os.path.exists(filepath):
        st.error("Could not find `fed_rss_summaries.json`.")
        return

    with open(filepath) as f:
        data = json.load(f)

    if not data:
        st.warning("No speech data found.")
        return

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Filter out rows with invalid dates
    df = df[df["date"].notnull()]

    # --- Optional: Sentiment Filter ---
    sentiments = ["All"] + sorted(df["sentiment"].dropna().unique())
    selected_sentiment = st.selectbox("Filter by Sentiment", sentiments, index=0)

    if selected_sentiment != "All":
        df = df[df["sentiment"] == selected_sentiment]

    # Plotly timeline chart
    fig = px.timeline(
        df,
        x_start="date",
        x_end="date",
        y="speaker",
        color="sentiment",
        hover_data=["title", "summary", "location"],
        title="Fed Speeches by Date & Sentiment"
    )

    fig.update_layout(
        height=600,
        margin=dict(t=40, b=40),
        xaxis_title="Date",
        yaxis_title="Speaker",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)
