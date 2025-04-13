# src/ui.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def plot_interactive_chart(df, title="Economic Data", use_yoy=False):
    if df is None or df.empty:
        st.warning("No data to display.")
        return

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    y_col = "value_yoy" if use_yoy else "value"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df[y_col],
        mode='lines+markers',
        line=dict(width=2, color="#00bfff"),
        name=title
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_dark",
        height=400,
        margin=dict(t=40, b=40, l=20, r=20),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_data_and_summary(df, summary, title, use_yoy=False):
    col1, col2 = st.columns([2, 1])

    with col1:
        plot_interactive_chart(df, title=title, use_yoy=use_yoy)

    with col2:
        st.markdown("### 🧠 AI Summary")
        st.write(summary)

    st.markdown("### 📄 Raw Data")
    with st.expander("View full table"):
        st.dataframe(df.head(20))
