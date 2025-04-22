# moved from tools/ask_questions.py
import streamlit as st
from tools.ui.ui_helpers import render_card, export_to_markdown

from keyword_mapper import match_keywords_to_fred, load_keyword_map

from tools.llm.llm_agent import chat_agent

def render_qa_tab(indicators, get_fred_data, summarize_series):
    st.markdown('<div class="fadein">', unsafe_allow_html=True)
    st.markdown("<a name='run-economic-q-a'></a>", unsafe_allow_html=True)
    st.subheader("➜  Run Economic Q&A")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    # --- Agent Mode Toggle and Personality ---
    st.markdown("<b>⚡ Agent Mode (LLM-powered)</b>", unsafe_allow_html=True)
    agent_mode = st.checkbox("Use Agent Mode", value=True)
    personality = st.selectbox("Agent Personality", ["Analyst", "Professor", "Journalist"], key="qa_agent_personality")
    dev_mode = st.checkbox("Dev Mode (Show Tool Usage)", value=False)

    # --- Prompt Input ---
    user_q = st.text_input("Ask a question about economic indicators:", key="qa_tab_input")
    if st.button("Ask", key="qa_tab_btn") and user_q:
        with st.spinner('Generating answer...'):
            if agent_mode:
                result = chat_agent(user_q, mode=personality, history=st.session_state.get("qa_thread", []), dev_mode=dev_mode)
                if isinstance(result, dict):
                    answer = result["answer"]
                    tools = result["tools"]
                else:
                    answer = result
                    tools = []
                st.session_state.setdefault("qa_thread", []).append({"question": user_q, "answer": answer, "tools": tools})
            else:
                # Fallback: legacy logic
                keyword_dict = {row['keyword']: row for _, row in indicators.iterrows()}
                override_match = match_keywords_to_fred(user_q, keyword_dict)
                if override_match:
                    fred_id = override_match[0]["id"]
                    label = override_match[0]["label"]
                else:
                    selected_indicator = st.selectbox("Choose an indicator for Q&A:", indicator_options, key="qa_indicator_select")
                    indicator_row = indicator_map[selected_indicator]
                    fred_id = indicator_row['id']
                    label = indicator_row['label']
                df = get_fred_data(fred_id)
                answer = summarize_series(label, df) if not df.empty else "No data available."
                st.session_state.setdefault("chat_history", []).append({"indicator": label, "question": user_q, "answer": answer})
        st.rerun()
    # --- Prompt History Viewer (Agent Mode) ---
    if agent_mode:
        with st.expander("Show Prompt History (last 10)"):
            qa_thread = st.session_state.get("qa_thread", [])[-10:]
            for i, msg in enumerate(qa_thread):
                st.markdown(f"**Q{i+1}:** {msg['question']}")
                st.markdown(f"**A{i+1}:** {msg['answer']}")
                if dev_mode and msg.get("tools"):
                    st.caption(f"Tools used: {', '.join(msg['tools'])}")
                st.markdown("---")
    # --- Card Rendering (Legacy and Agent) ---
    md_export = ""
    chat_data = st.session_state.get("qa_thread" if agent_mode else "chat_history", [])
    for i, msg in enumerate(chat_data):
        def qa_content():
            st.markdown(f"**Q:** {msg['question']}")
            answer = msg['answer']
            fallback = "⚠️ I couldn't generate an answer. Try rephrasing or simplifying the question."
            if not answer or answer.strip().lower() == 'none':
                st.warning(fallback)
            else:
                st.markdown(f"**A:** {answer}")
            charted = False
            # --- Chart It button logic ---
            # Try to extract FRED series from tools or indicator
            series_id = None
            if msg.get('tools') and any(t in msg['tools'] for t in ['extract_fred_series', 'get_fred_data']):
                # Try to extract FRED series from the question or indicator
                import re
                fred_matches = re.findall(r'([A-Z0-9_]{3,})', msg['question'])
                if fred_matches:
                    series_id = fred_matches[0]
                elif msg.get('indicator'):
                    # Try to use indicator keyword as fallback
                    series_id = msg['indicator']
            elif msg.get('indicator'):
                series_id = msg['indicator']
            if series_id and st.button("📈 Chart It", key=f"chart_{i}"):
                df = get_fred_data(series_id)
                if not df.empty:
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines', name=series_id))
                    fig.update_layout(title=f"{series_id} - Latest Data", xaxis_title="Date", yaxis_title="Value", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                    charted = True
                else:
                    st.warning("No data available for charting.")
            if dev_mode and msg.get("tools"):
                st.caption(f"Tools used: {', '.join(msg['tools'])}")
            if msg.get("indicator"):
                st.caption(f"Indicator: {msg['indicator']}")
            if st.button("📌 Save this insight", key=f"save_{i}"):
                with open("insights_log.md", "a") as f:
                    f.write(f"### Q: {msg['question']}\nA: {msg['answer']}\n---\n")
                st.success("Insight saved!")
        render_card(f"💬 Q&A", content_func=qa_content)
        md_export += f"### Q{i+1}: {msg['question']}\n\nA{i+1}: {msg['answer']}\n\n---\n"
    st.download_button("Download All Q&A as Markdown", data=md_export, file_name="qa_chat.md", mime="text/markdown")
    if st.button("Clear Chat", key="clear_chat_btn"):
        if agent_mode:
            st.session_state["qa_thread"] = []
        else:
            st.session_state["chat_history"] = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
