# moved from tools/compare_series.py
import streamlit as st
import pandas as pd
import json

def render_lightweight_chart(data):
    js_data = json.dumps(data)
    st.components.v1.html(f"""
    <div id=\"tvchart\" style=\"width:100%;height:500px;background:#0f1117;\"></div>
    <script src=\"https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js\"></script>
    <script>
      const chart = LightweightCharts.createChart(document.getElementById('tvchart'), {{
        width: Math.floor(window.innerWidth * 0.85),
        height: 500,
        layout: {{
          background: {{ color: '#0f1117' }},
          textColor: '#D9D9D9',
        }},
        grid: {{
          vertLines: {{ color: '#222' }},
          horzLines: {{ color: '#222' }},
        }},
        timeScale: {{
          borderColor: '#333',
        }},
        rightPriceScale: {{
          borderColor: '#333',
        }},
      }});
      const candleSeries = chart.addCandlestickSeries({{
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderUpColor: '#26a69a',
        borderDownColor: '#ef5350',
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      }});
      const pyData = {js_data};
      candleSeries.setData(pyData);
      window.addEventListener('resize', () => {{
        chart.applyOptions({{ width: Math.floor(window.innerWidth * 0.85) }});
      }});
    </script>
    """, height=520)

def render_tradingview_chart(symbol="NASDAQ:ES"):
    """
    Render a TradingView chart widget for the given symbol.
    """
    st.components.v1.html(f"""
    <div id=\"tradingview_chart\"></div>
    <script type=\"text/javascript\" src=\"https://s3.tradingview.com/tv.js\"></script>
    <script type=\"text/javascript\">
      new TradingView.widget({{
        "width": Math.floor(window.innerWidth * 0.85),
        "height": 500,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "hide_side_toolbar": false,
        "container_id": "tradingview_chart"
      }});
    </script>
    """, height=520)

def df_to_candlestick(df):
    """
    Convert a DataFrame with 'date' and 'value' columns into OHLC candlestick data for lightweight-charts.
    If you only have 'value', it will use it for open/high/low/close (flat candles).
    If you have 'open', 'high', 'low', 'close' columns, it will use those.
    """
    if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        # Already OHLC format
        return [
            {
                "time": row["date"].strftime("%Y-%m-%d"),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"])
            }
            for _, row in df.iterrows()
        ]
    elif "value" in df.columns:
        # Use 'value' as flat candle (open=high=low=close)
        return [
            {
                "time": row["date"].strftime("%Y-%m-%d"),
                "open": float(row["value"]),
                "high": float(row["value"]),
                "low": float(row["value"]),
                "close": float(row["value"])
            }
            for _, row in df.iterrows()
        ]
    else:
        raise ValueError("DataFrame must have either ['open','high','low','close'] or ['value'] columns.")

def render_compare_tab(indicators, get_fred_data):
    st.markdown('<div class="fadein">', unsafe_allow_html=True)
    st.markdown("<a name='compare-series'></a>", unsafe_allow_html=True)
    st.subheader("➜  Compare Series")
    multi_options = [f"{row['label']} ({row['keyword']})" for _, row in indicators.iterrows()]
    multi_map = {f"{row['label']} ({row['keyword']})": row for _, row in indicators.iterrows()}
    selected_multi = st.multiselect("Select indicators to compare:", multi_options)
    from datetime import date, timedelta
    today = date.today()
    default_start = today - timedelta(days=365)
    date_range = st.date_input(
        "Select date range:",
        value=(default_start, today)
    )
    st.caption(f"Filtering data from **{date_range[0]}** to **{date_range[1]}**")
    yoy_toggle = st.checkbox("Show YoY Change", value=False)
    use_lightweight = st.checkbox("Use Lightweight Chart (TradingView)", value=False, help="Switch to TradingView-style chart.")
    with st.spinner('Loading comparison chart...'):
        combined_df = None
        for sel in selected_multi:
            row = multi_map[sel]
            df = get_fred_data(row['id'])
            if not df.empty:
                df = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]
                if yoy_toggle and not df.empty:
                    df['value_yoy'] = df['value'].pct_change(periods=12) * 100
                    value_col = 'value_yoy'
                else:
                    value_col = 'value'
                df = df.rename(columns={value_col: sel})
                df = df[['date', sel]]
                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pd.merge(combined_df, df, on='date', how='outer')
        if combined_df is not None and not combined_df.empty:
            combined_df = combined_df.sort_values('date')
            if use_lightweight and len(selected_multi) == 1:
                # For now, use a default symbol; you can map sel to a TradingView symbol if desired
                render_tradingview_chart(symbol="NASDAQ:ES")
            elif len(selected_multi) > 0:
                from tools.ui.ui_helpers import build_comparison_chart
                norm_toggle = st.checkbox("Normalize to 100 at start", value=False, help="Set all series to 100 at the first date for easier comparison.")
                show_recession = st.checkbox("Show Recession Bands", value=True)
                show_inversion = st.checkbox("Show Yield Curve Inversions", value=True)
                show_fedfunds = st.checkbox("Show Fed Funds Rate", value=False)
                sentiment_options = ["None", "UMCSENT (Consumer Sentiment)", "GSCPI (Supply Chain Pressure)"]
                sentiment_choice = st.selectbox("Sentiment/Supply Overlay", sentiment_options, index=0)
                show_sentiment = st.checkbox("Show Selected Sentiment/Supply Overlay", value=False, disabled=sentiment_choice=="None")
                dev_mode = st.sidebar.checkbox("Developer Tools", value=False)
                overlays = []
                recession_df = get_fred_data("USREC")
                if not recession_df.empty:
                    recession_df = recession_df[(recession_df['date'] >= pd.to_datetime(date_range[0])) & (recession_df['date'] <= pd.to_datetime(date_range[1]))]
                if show_recession:
                    overlays.append({'type': 'recession', 'df': recession_df})
                t10y2y_df = get_fred_data("T10Y2Y")
                if not t10y2y_df.empty:
                    t10y2y_df = t10y2y_df[(t10y2y_df['date'] >= pd.to_datetime(date_range[0])) & (t10y2y_df['date'] <= pd.to_datetime(date_range[1]))]
                if show_inversion:
                    overlays.append({'type': 'inversion', 'df': t10y2y_df})
                fedfunds_df = get_fred_data("DFEDTAR")
                if not fedfunds_df.empty:
                    fedfunds_df = fedfunds_df[(fedfunds_df['date'] >= pd.to_datetime(date_range[0])) & (fedfunds_df['date'] <= pd.to_datetime(date_range[1]))]
                if show_fedfunds:
                    overlays.append({'type': 'fedfunds', 'df': fedfunds_df})
                sentiment_df = None
                sentiment_label = None
                sentiment_color = None
                if sentiment_choice.startswith("UMCSENT"):
                    sentiment_label = "Consumer Sentiment"
                    sentiment_color = "#a259ff"
                    sentiment_df = get_fred_data("UMCSENT")
                elif sentiment_choice.startswith("GSCPI"):
                    sentiment_label = "Supply Chain Pressure"
                    sentiment_color = "#ffb86b"
                    sentiment_df = get_fred_data("GSCPI")
                if sentiment_df is not None and not sentiment_df.empty:
                    sentiment_df = sentiment_df[(sentiment_df['date'] >= pd.to_datetime(date_range[0])) & (sentiment_df['date'] <= pd.to_datetime(date_range[1]))]
                    if show_sentiment:
                        overlays.append({'type': 'sentiment', 'df': sentiment_df, 'kwargs': {'label': sentiment_label, 'color': sentiment_color}})
                indicator_meta = {row['label'] + f" ({row['keyword']})": row for _, row in indicators.iterrows()}
                fig = build_comparison_chart(
                    combined_df, selected_multi,
                    yoy=yoy_toggle, normalize=norm_toggle,
                    overlays=overlays, indicator_meta=indicator_meta, dev_mode=dev_mode
                )
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("Download CSV", data=combined_df.to_csv(index=False), file_name="comparison.csv", mime="text/csv")
                md = combined_df.to_markdown(index=False)
                st.download_button("Download Markdown", data=md, file_name="comparison.md", mime="text/markdown")
        elif selected_multi:
            st.warning("No data found for selected indicators and date range.")
        else:
            st.info("Select at least one indicator to compare.")
    st.markdown('</div>', unsafe_allow_html=True)