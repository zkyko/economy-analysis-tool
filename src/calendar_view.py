# src/calendar_view.py

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

def parse_date(d):
    try:
        return datetime.strptime(d, "%B %d, %Y")
    except:
        return None

def render_calendar(speeches):
    if not speeches:
        st.info("No speeches available for calendar view.")
        return

    st.markdown("---")
    st.subheader("📅 Speech Calendar (Timeline View)")

    # Prepare data
    timeline_data = []
    for s in speeches:
        date_obj = parse_date(s.get("date", ""))
        if date_obj:
            timeline_data.append({
                "Title": s.get("title", "Unknown Title"),
                "Speaker": s.get("speaker", "Unknown"),
                "Date": date_obj,
                "Sentiment": s.get("sentiment", "Unknown"),
                "URL": s.get("url", "#")
            })

    if not timeline_data:
        st.warning("No valid dates found in speeches.")
        return

    df = pd.DataFrame(timeline_data)

    fig = px.timeline(
        df,
        x_start="Date",
        x_end="Date",
        y="Speaker",
        color="Sentiment",
        hover_name="Title",
        hover_data={"Date": True, "Speaker": True, "Sentiment": True},
        title="Federal Reserve Speech Timeline",
        color_discrete_map={
            "Hawkish": "red",
            "Dovish": "green",
            "Neutral": "gray",
            "Unknown": "lightgray"
        }
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=40),
        hoverlabel=dict(bgcolor="white")
    )

    st.plotly_chart(fig, use_container_width=True)
