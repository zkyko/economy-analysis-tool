# moved from tools/app_layout.py
from tools.layout import theme_config
import streamlit as st

def init_layout():
    # Global CSS/JS (fonts, background, hotkeys, cursor)
    st.markdown("""
    <style>
    * { font-family: monospace !important; }
    .ascii-box {border: 1px solid #555; border-radius: 6px; background: #191919; padding: 1em; margin-bottom: 1em;}
    .blinking-cursor {font-weight: bold; color: #39ff14; animation: blink 1s steps(2, start) infinite;}
    .terminal-prompt-cursor {font-weight: bold; color: #39ff14; font-size: 1.25em; animation: blink 1s steps(2, start) infinite; vertical-align: middle;}
    @keyframes blink {to {visibility: hidden;}}
    .fadein {animation: fadeIn 0.8s;}
    @keyframes fadeIn {from {opacity: 0;} to {opacity: 1;}}
    </style>
    <script>
    document.addEventListener('keydown', function(e) {
        if(e.key==='1'){window.location.hash='#browse-indicators';}
        if(e.key==='2'){window.location.hash='#run-economic-q-a';}
        if(e.key==='3'){window.location.hash='#compare-series';}
        if(e.ctrlKey && e.key==='e'){window.location.search='?export=1';}
        if(e.ctrlKey && e.key==='r'){window.location.search='?run_query=1';}
        if(e.ctrlKey && e.key==='c'){window.location.search='?clear_chat=1';}
    });
    </script>
    """, unsafe_allow_html=True)
    left, right = st.columns([1, 3], gap="medium")
    return left, right
