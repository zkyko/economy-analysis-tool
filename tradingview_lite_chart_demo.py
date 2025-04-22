import streamlit as st
import streamlit.components.v1 as components

st.title("TradingView Lite Chart Demo")

# TradingView Lite Widget Embed (requires internet)
# For offline, you would need to download and inline the widget JS, which is not officially supported.
# This example uses the TradingView CDN for the Lite Chart widget.

html_content = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <style>
      #tradingview_chart {
        width: 600px;
        height: 400px;
      }
    </style>
  </head>
  <body>
    <div id="tradingview_chart"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
      new TradingView.widget({
        "width": 1920,
        "height": 1080,
        "symbol": "NASDAQ:ES",
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
      });
    </script>
  </body>
</html>
'''

components.html(html_content, height=420, width=620)
