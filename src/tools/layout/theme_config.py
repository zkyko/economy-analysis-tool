# moved from tools/theme_config.py
import streamlit as st

def setup_theme():
    st.sidebar.markdown("## Theme")
    st.sidebar.checkbox("🌙 Dark Mode", key="dark_mode_toggle")
    st.sidebar.checkbox("🔴 Live Mode", key="live_mode_toggle")
    if st.sidebar.button("Clear Cache"):
        st.cache_data.clear()
        st.rerun()
