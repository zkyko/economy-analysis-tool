# Speech summary tab logic, migrated from app.py
import streamlit as st
import pandas as pd
import json, os, io
from datetime import datetime

def render_speech_section():
    st.markdown("---")
    st.header("🎤 Federal Reserve Speech Summaries")
    @st.cache_data
    def load_or_scrape_speeches():
        filepath = "src/data/fed_rss_summaries.json"
        if not os.path.exists(filepath):
            st.warning("🔄 No speech file found. Please run the scraper.")
            return []
        with open(filepath) as f:
            return json.load(f)
    speeches = load_or_scrape_speeches()
    if speeches:
        def parse_date(d):
            try:
                return datetime.strptime(d, "%B %d, %Y")
            except:
                return datetime.min
        speeches = sorted(speeches, key=lambda x: parse_date(x["date"]), reverse=True)
        df_all = pd.DataFrame(speeches)
        sentiment_options = sorted(set(df_all["sentiment"].fillna("Unknown")))
        speaker_options = sorted(set(df_all["speaker"].fillna("Unknown")))
        selected_sentiment = st.selectbox("🗣️ Filter by Sentiment", ["All"] + sentiment_options)
        selected_speaker = st.selectbox("🧑 Filter by Speaker", ["All"] + speaker_options)
        search_query = st.text_input("🔍 Search title or summary").lower()
        def apply_filters():
            return df_all[
                ((df_all["sentiment"] == selected_sentiment) | (selected_sentiment == "All")) &
                ((df_all["speaker"] == selected_speaker) | (selected_speaker == "All")) &
                (df_all["title"].str.lower().str.contains(search_query) | df_all["summary"].str.lower().str.contains(search_query))
            ]
        filtered_df = apply_filters()
        if not filtered_df.empty:
            import plotly.express as px
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
        PAGE_SIZE = 5
        page = st.number_input("📄 Page", min_value=1, max_value=(len(filtered_df) // PAGE_SIZE + 1), step=1)
        start_idx = (page - 1) * PAGE_SIZE
        page_df = filtered_df.iloc[start_idx:start_idx + PAGE_SIZE]
        sentiment_colors = {"Hawkish": "🔴", "Dovish": "🟢", "Neutral": "⚪", "Unknown": "❓"}
        for _, speech in page_df.iterrows():
            color = sentiment_colors.get(speech.get("sentiment", "Unknown"), "❓")
            st.subheader(f"{speech['title']} ({speech['date']})")
            st.caption(f"[📄 View Full Speech]({speech['url']})")
            st.markdown(f"🧑 **Speaker:** {speech.get('speaker', 'Unknown')}")
            st.markdown(f"📍 **Location:** {speech.get('location', 'Unknown')}")
            st.markdown(f"🧠 **Summary:** {speech.get('summary', '')}")
            st.markdown(f"{color} **Sentiment:** `{speech.get('sentiment', 'Unknown')}`")
            st.markdown("---")
        # Export Section
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
