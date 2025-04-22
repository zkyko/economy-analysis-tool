import os
import json
import pandas as pd
import io

def render_speech_summaries():
    render_card("🗣️ Federal Reserve Speech Summaries")

    file_path = "src/data/fed_rss_summaries.json"

    if not os.path.exists(file_path):
        st.error("❌ Summary file not found at `src/data/fed_rss_summaries.json`.")
        return

    with open(file_path) as f:
        data = json.load(f)

    if not data:
        st.warning("No Fed speech data available.")
        return

    df = pd.DataFrame(data)

    # --- Filters ---
    st.markdown("#### 🔎 Filters")

    sentiments = ["All"] + sorted(df["sentiment"].dropna().unique())
    selected_sentiment = st.selectbox("Sentiment", sentiments)

    speakers = ["All"] + sorted(df["speaker"].dropna().unique())
    selected_speaker = st.selectbox("Speaker", speakers)

    search_query = st.text_input("Search in Title/Summary").lower()

    def apply_filters(row):
        sentiment_ok = (selected_sentiment == "All") or (row["sentiment"] == selected_sentiment)
        speaker_ok = (selected_speaker == "All") or (row["speaker"] == selected_speaker)
        search_ok = search_query in row["title"].lower() or search_query in row["summary"].lower()
        return sentiment_ok and speaker_ok and search_ok

    df_filtered = df[df.apply(apply_filters, axis=1)]

    # --- Pagination ---
    PAGE_SIZE = 5
    page_count = max(1, (len(df_filtered) - 1) // PAGE_SIZE + 1)
    page = st.number_input("Page", min_value=1, max_value=page_count, step=1)
    start_idx = (page - 1) * PAGE_SIZE
    page_df = df_filtered.iloc[start_idx:start_idx + PAGE_SIZE]

    # --- Sentiment Badge Map ---
    badge = {
        "Hawkish": "🔴",
        "Dovish": "🟢",
        "Neutral": "⚪",
        "Unknown": "❓"
    }

    # --- Render Each Speech ---
    def render_speech_card(row):
        sentiment_colors = {
            "Hawkish": "🔴", "Dovish": "🟢", "Neutral": "⚪", "Unknown": "❓"
        }
        emoji = sentiment_colors.get(row["sentiment"], "❓")
        def content():
            st.caption(f"[🔗 View Full Speech]({row['url']})")
            st.markdown(f"**Speaker:** {row.get('speaker', 'Unknown')}")
            st.markdown(f"**Location:** {row.get('location', 'Unknown')}")
            st.markdown(f"**Sentiment:** {emoji} `{row.get('sentiment', 'Unknown')}`")
            st.markdown(f"**Summary:** {row.get('summary', '')}")
        render_card(title=f"{row['title']} ({row['date']})", content_func=content)

    for _, row in page_df.iterrows():
        render_speech_card(row)

    # --- Export Section ---
    st.subheader("📤 Export Filtered Speeches")

    csv_buffer = io.StringIO()
    df_filtered.to_csv(csv_buffer, index=False)

    md_buffer = io.StringIO()

# -----------------------------
# Card UI Helper (for import)
# -----------------------------
def render_card(title, content_func=None, buttons=None):
    import streamlit as st
    st.markdown(
        f"""
        <div style='
            background-color: #2a2a2a;
            padding: 1.5rem;
            border-radius: 1rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            border: 1px solid #444;
        '>
            <h3 style='color: #fff; font-size: 1.2rem;'>{title}</h3>
        """,
        unsafe_allow_html=True
    )
    if content_func:
        content_func()
    if buttons:
        for btn in buttons:
            st.download_button(**btn)
    st.markdown("</div>", unsafe_allow_html=True)

    for _, row in df_filtered.iterrows():
        md_buffer.write(f"### {row['title']} ({row['date']})\n")
        md_buffer.write(f"[View Full Speech]({row['url']})\n\n")
        md_buffer.write(f"**Speaker:** {row.get('speaker', 'Unknown')}\n\n")
        md_buffer.write(f"**Location:** {row.get('location', 'Unknown')}\n\n")
        md_buffer.write(f"**Sentiment:** {row.get('sentiment', 'Unknown')}\n\n")
        md_buffer.write(f"**Summary:**\n{row['summary']}\n\n---\n")

    st.download_button("📄 Download CSV", data=csv_buffer.getvalue(), file_name="fed_summaries.csv", mime="text/csv")
    st.download_button("📝 Download Markdown", data=md_buffer.getvalue(), file_name="fed_summaries.md", mime="text/markdown")
