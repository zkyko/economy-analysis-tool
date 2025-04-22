import streamlit as st
st.write(f"📦 Running Streamlit v{st.__version__}")
from llm import extract_fred_series

def render_card(title, content_func=None, buttons=None):
    """
    Renders a consistent UI card with a title, optional body content, and optional buttons.
    """
    with st.container():
        st.markdown(
            f"""
            <div style='
                background-color: #1e1e1e;
                padding: 1.5rem;
                border-radius: 1rem;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                margin-bottom: 1.5rem;
            '>
                <h3 style='color:#ffffff; margin-bottom:1rem;'>{title}</h3>
            """,
            unsafe_allow_html=True
        )
        if content_func:
            content_func()
        if buttons:
            for btn in buttons:
                st.download_button(**btn)
        st.markdown("</div>", unsafe_allow_html=True)

def render_query_panel():
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    st.header("💬 Economic Q&A Chat")

    # Show chat history
    for msg in st.session_state["chat_history"]:
        st.chat_message("user").write(msg["question"])
        def show_llm_summary():
            st.write(msg["answer"])
        render_card("🧠 AI Summary", content_func=show_llm_summary)

    # Input for new question
    with st.form("query_form", clear_on_submit=True):
        user_query = st.text_input("Ask a question about the economy:")
        submitted = st.form_submit_button("Ask")

    if submitted and user_query:
        result = extract_fred_series(user_query)
        answer = str(result)
        st.session_state["chat_history"].append({"question": user_query, "answer": answer})
        st.rerun()

    # Button to clear chat
    if st.button("Clear Chat"):
        st.session_state["chat_history"] = []
        st.rerun()
