# moved from tools/utils_ui.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Card UI Helper ---
def render_card(title, content_func=None, download_buttons=None):
    st.markdown(f"<div style='border:1px solid #444; border-radius:6px; padding:1em; margin-bottom:1em; background:#232323;'>"
                f"<b>{title}</b>", unsafe_allow_html=True)
    if content_func:
        content_func()
    if download_buttons:
        for btn in download_buttons:
            btn()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Export Q&A to Markdown ---
def export_to_markdown(chat_history):
    md_export = ""
    for i, msg in enumerate(chat_history):
        md_export += f"### Q{i+1}: {msg['question']}\n\nA{i+1}: {msg['answer']}\n\nIndicator: {msg['indicator']}\n\n---\n"
    return md_export

# --- Fed Speech Card ---
def render_speech_card(speech):
    st.subheader(f"{speech['title']} ({speech['date']})")
    st.caption(f"[📄 View Full Speech]({speech['url']})")
    st.markdown(f"**Speaker:** {speech.get('speaker', 'Unknown')}")
    st.markdown(f"**Location:** {speech.get('location', 'Unknown')}")
    st.markdown(f"**Sentiment:** {speech.get('sentiment', 'Unknown')}")
    st.markdown(f"**Summary:**\n{speech['summary']}")
    st.markdown("---")

# --- Overlay Add-on ---
def add_overlay(fig, overlay_type, overlay_df, **kwargs):
    if overlay_type == 'recession' and overlay_df is not None and not overlay_df.empty:
        in_recession = False
        rec_start = None
        for idx, row in overlay_df.iterrows():
            if row['value'] == 1 and not in_recession:
                rec_start = row['date']
                in_recession = True
            elif row['value'] == 0 and in_recession:
                rec_end = row['date']
                fig.add_vrect(
                    x0=rec_start - pd.Timedelta(days=2),
                    x1=rec_end + pd.Timedelta(days=2),
                    fillcolor="rgba(100,100,200,0.15)",
                    line_width=0,
                    layer="below",
                    annotation_text="Recession Period",
                    annotation_position="top left",
                    annotation=dict(font=dict(size=10, color="#aaa")),
                    opacity=0.3
                )
                in_recession = False
        if in_recession:
            rec_end = overlay_df['date'].iloc[-1]
            fig.add_vrect(
                x0=rec_start - pd.Timedelta(days=2),
                x1=rec_end + pd.Timedelta(days=2),
                fillcolor="rgba(100,100,200,0.15)",
                line_width=0,
                layer="below",
                annotation_text="Recession Period",
                annotation_position="top left",
                annotation=dict(font=dict(size=10, color="#aaa")),
                opacity=0.3
            )
    elif overlay_type == 'inversion' and overlay_df is not None and not overlay_df.empty:
        inv_dates = overlay_df[overlay_df['value'] < 0]['date']
        for d in inv_dates:
            fig.add_vline(
                x=pd.to_datetime(d).to_pydatetime(),
                line_dash="dash",
                line_color="#ff4b82",
                opacity=0.7,
                annotation_text="Inversion",
                annotation_position="top right",
                annotation=dict(font=dict(size=10, color="#ff4b82"))
            )
    elif overlay_type == 'fedfunds' and overlay_df is not None and not overlay_df.empty:
        fig.add_trace(go.Scatter(
            x=overlay_df['date'], y=overlay_df['value'],
            name="Fed Funds Rate",
            yaxis="y2",
            mode="lines",
            line=dict(color="#ffe156", width=2, dash="dot"),
            opacity=0.7,
            hovertemplate="Fed Funds: %{y:.2f}<br>Date: %{x|%b %Y}"
        ))
    elif overlay_type == 'sentiment' and overlay_df is not None and not overlay_df.empty:
        label = kwargs.get('label', 'Sentiment')
        color = kwargs.get('color', '#1faaff')
        fig.add_trace(go.Scatter(
            x=overlay_df['date'], y=overlay_df['value'],
            name=label,
            mode="lines",
            line=dict(color=color, width=2, dash="dot"),
            opacity=0.6,
            hovertemplate=f"{label}: %{{y:.2f}}<br>Date: %{{x|%b %Y}}"
        ))
    return fig

# --- Chart Builder ---
def build_comparison_chart(combined_df, selected_multi, yoy=False, normalize=False, overlays=None, indicator_meta=None, dev_mode=False):
    fig = go.Figure()
    colors = ["#39ff14", "#ff4b82", "#1faaff", "#ffe156", "#a259ff", "#ffb86b"]
    for i, sel in enumerate(selected_multi):
        y = combined_df[sel]
        if y.dropna().empty:
            continue  # Skip this series if no data is present
        if normalize:
            y = (y / y.dropna().iloc[0]) * 100
        pct_change = (y / y.dropna().iloc[0] - 1) * 100
        yoy_avg = y.mean() if yoy else None
        customdata = pct_change.values.reshape(-1, 1)
        hovertemplate = (
            f"<b>Value:</b> %{{y:.2f}}<br>"
            f"<b>% Change:</b> %{{customdata[0]:+.2f}}%<br>"
            f"<b>Date:</b> %{{x|%b %Y}}"
        )
        if yoy:
            hovertemplate += f"<br><b>YoY Avg:</b> {yoy_avg:.2f}"
        if indicator_meta and sel in indicator_meta:
            hovertemplate += f"<br><span style='font-size:10px'>Desc: {indicator_meta[sel]['label']}</span>"
        fig.add_trace(go.Scatter(
            x=combined_df['date'],
            y=y,
            mode='lines',
            name=sel,
            line=dict(width=2, color=colors[i % len(colors)], dash='solid' if i == 0 else 'dash'),
            customdata=customdata,
            hovertemplate=hovertemplate,
            connectgaps=True
        ))
    if overlays:
        for overlay in overlays:
            fig = add_overlay(fig, overlay['type'], overlay['df'], **overlay.get('kwargs', {}))

    chart_title = f"YoY Comparison: {', '.join(selected_multi)}" if yoy else f"Comparison: {', '.join(selected_multi)}"
    yaxis_title = "YoY % Change" if yoy else ("Normalized Value (100=start)" if normalize else "Value")
    layout = dict(
        title=chart_title,
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font=dict(family="monospace", color="#DDDDDD", size=14),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#222", tickformat="%Y-%m", zeroline=False),
        yaxis=dict(title=yaxis_title, gridcolor="#333", zeroline=False),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=13)),
        hovermode="x unified",
        margin=dict(b=80)
    )
    if overlays and any(ov['type'] == 'fedfunds' for ov in overlays):
        layout['yaxis2'] = dict(
            title="Fed Funds Rate",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#ffe156"),
            titlefont=dict(color="#ffe156")
        )
    fig.update_layout(**layout)
    if dev_mode and overlays:
        st.markdown("#### [Dev] Overlay Debug Info")
        for ov in overlays:
            st.write(f"Overlay: {ov['type']}")
            st.dataframe(ov['df'].head())
    return fig
