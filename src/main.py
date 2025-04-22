import streamlit as st
st.set_page_config(page_title="Macro Dashboard", layout="wide", page_icon="📊")
from router import run_dashboard

if __name__ == "__main__":
    run_dashboard()
