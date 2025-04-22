# moved from tools/terminal_panel.py (if present)
import streamlit as st

def render_terminal_nav():
    st.markdown('''
    <style>
    .ascii-box {border: 1px solid #555; border-radius: 6px; background: #191919; padding: 1em; margin-bottom: 1em;}
    .blinking-cursor {font-weight: bold; color: #39ff14; animation: blink 1s steps(2, start) infinite;}
    .terminal-prompt-cursor {font-weight: bold; color: #39ff14; font-size: 1.25em; animation: blink 1s steps(2, start) infinite; vertical-align: middle;}
    @keyframes blink {to {visibility: hidden;}}
    .fadein {animation: fadeIn 0.8s;}
    @keyframes fadeIn {from {opacity: 0;} to {opacity: 1;}}
    </style>
    <div class="ascii-box">
    <span class="blinking-cursor">➜</span> <b>Terminal</b>
    <span class="terminal-prompt-cursor">▊</span>
    <br>
    <a href="#browse-indicators" style="color:#fff; text-decoration:none">[1] Browse Indicators</a><br>
    <a href="#run-economic-q-a" style="color:#fff; text-decoration:none">[2] Run Economic Q&A</a><br>
    <a href="#compare-series" style="color:#fff; text-decoration:none">[3] Compare Series</a><br>
    <br>
    <b>Quick Commands:</b><br>
    <div style="margin-top: 0.5em; margin-bottom: 0.5em;">
    <form>
    <button style="background:#181818;color:#39ff14;border:none;padding:0.3em 1.2em;font-family:monospace;font-size:1em;cursor:pointer;">▶ Run Query</button>
    </form>
    </div>
    <a href="?clear_chat=1" style="color:#39ff14; text-decoration:none">[🧼 Clear Chat]</a>
    <a href="?export=1" style="color:#39ff14; text-decoration:none">[⬇ Export]</a>
    <br>---
    <br><span style="color:#888">&gt; show cpi<br>&gt; compare gdp inflation</span>
    </div>
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
    ''', unsafe_allow_html=True)
