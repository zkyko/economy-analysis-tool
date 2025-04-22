import streamlit as st

def render_tradingview_tab():
    # Hide Streamlit UI (menu, header, footer, sidebar)
    st.markdown('''
        <style>
            #MainMenu, header, footer, .css-18e3th9, .css-1d391kg, .css-1v0mbdj {{ display: none !important; }}
            .block-container {{ padding: 0 !important; }}
            .css-1kyxreq {{ padding: 0 !important; }}
            body, html {{ margin: 0; padding: 0; overflow: hidden; }}
        </style>
    ''', unsafe_allow_html=True)
    # Symbol input (overlay style)
    symbol = st.text_input("Symbol (e.g. NASDAQ:AAPL, SPY, BTCUSD)", value="NASDAQ:AAPL", key="tv_symbol")
    # Square chart: size = min(viewport width, viewport height)
    st.components.v1.html(f'''
    <style>
      #tv-symbol-overlay {{
        position: fixed;
        top: 16px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        background: rgba(255,255,255,0.92);
        padding: 8px 24px;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.09);
        font-size: 1.2em;
      }}
    </style>
    <div id="tv-symbol-overlay">Symbol: <b>{symbol}</b></div>
    <div id="tradingview_chart" style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:9999;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
      function getSquareSize() {{
        return Math.min(window.innerWidth, window.innerHeight);
      }}
      function resizeChart() {{
        var size = getSquareSize();
        var chartDiv = document.getElementById('tradingview_chart');
        chartDiv.style.width = size + 'px';
        chartDiv.style.height = size + 'px';
        chartDiv.style.left = "calc(50vw - " + (size/2) + "px)";
        chartDiv.style.top = "calc(50vh - " + (size/2) + "px)";
      }}
      resizeChart();
      window.addEventListener('resize', resizeChart);
      new TradingView.widget({{
        "width": getSquareSize(),
        "height": getSquareSize(),
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
    ''', height=1200)
