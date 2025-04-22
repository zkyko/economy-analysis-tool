# moved from tools/indicator_browser.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os, json
from tools.ui.ui_helpers import render_card

def render_browser_tab(indicators, filtered, categories, get_fred_data, summarize_series=None):
    st.markdown('<div class="fadein">', unsafe_allow_html=True)
    st.markdown("<a name='browse-indicators'></a>", unsafe_allow_html=True)
    st.subheader("➜  Browse Indicators")
    selected_category = st.selectbox("Category", ["All"] + categories, label_visibility="collapsed")
    search = st.text_input("Search indicators", label_visibility="collapsed")
    filtered = indicators.copy()
    if selected_category != "All":
        filtered = filtered[filtered["type"] == selected_category]
    if search:
        filtered = filtered[filtered["label"].str.lower().str.contains(search.lower()) | filtered["keyword"].str.lower().str.contains(search.lower())]
    st.markdown(f"**{len(filtered)} indicators found**")
    if not filtered.empty:
        st.markdown("**Indicators:**", unsafe_allow_html=True)
        # --- Mini summary cache ---
        if 'indicator_summaries' not in st.session_state:
            st.session_state['indicator_summaries'] = {}
        for k in filtered["keyword"]:
            row = filtered.loc[filtered['keyword']==k].iloc[0]
            desc = row.get('description', '')
            fred_url = f"https://fred.stlouisfed.org/series/{row['id']}"
            checked = "<b>&#x25B6;</b> " if st.session_state.get('indicator_browser_radio') == k else ""
            # --- Mini summary ---
            summary = st.session_state['indicator_summaries'].get(k)
            if not summary and summarize_series:
                df = get_fred_data(row['id'])
                summary = summarize_series(row['label'], df)
                st.session_state['indicator_summaries'][k] = summary
            preview = summary.split('\n')[0] if summary else ''
            with st.expander(f'{checked}{row["label"]} (<code>{k}</code>)  📖', expanded=False):
                st.markdown(f"{preview}")
                if summary and len(summary.split('\n')) > 1:
                    st.caption(summary)
                st.markdown(f'<a href="{fred_url}" target="_blank" style="text-decoration:none;">Open in FRED</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
