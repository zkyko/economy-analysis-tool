"""
Agent-like LLM interface for FRED Q&A, using modular tools and thread memory.
"""
import streamlit as st
import json
import os
import requests

from tools.llm import extract_fred_series, get_fred_data
from tools.llm.llm_tools import summarize_series
from tools.llm.utils import compare_series

def chat_agent(query: str, mode: str = "Analyst", history=None, dev_mode=False):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        st.warning("No OpenAI API key found.")
        return "OpenAI API key missing."

    OPENAI_URL = "https://api.openai.com/v1/chat/completions"
    personality_map = {
        "Analyst": "You are an economic analyst. Answer clearly and with data.",
        "Professor": "You are a patient economics professor. Explain in depth and clarify concepts.",
        "Journalist": "You are a financial journalist. Be concise and focus on real-world impact."
    }
    system_prompt = personality_map.get(mode, personality_map["Analyst"])

    thread = history[-3:] if history else st.session_state.get("qa_thread", [])[-3:]
    context = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in thread])

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_fred_data",
                "description": "Fetches economic time series data by ID from FRED",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "series_id": {"type": "string"},
                        "start_date": {"type": "string", "format": "date"}
                    },
                    "required": ["series_id"]
                }
            }
        }
    ]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "system", "content": f"Recent Q&A context:\n{context}"})
    messages.append({"role": "user", "content": query})

    body = {
        "model": "gpt-4-1106-preview",
        "messages": messages,
        "temperature": 0.3,
        "tools": tools
    }

    response = requests.post(OPENAI_URL, headers=headers, json=body)
    if response.status_code != 200:
        return f"OpenAI API error: {response.status_code} - {response.text[:200]}"
    result = response.json()

    tool_calls = result.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
    answer = result.get("choices", [{}])[0].get("message", {}).get("content", None)

    tool_outputs = {}
    tool_log = []

    if tool_calls and all("id" in call for call in tool_calls):
        for call in tool_calls:
            fn = call.get("function", {})
            fn_name = fn.get("name")
            tool_log.append(fn_name)
            try:
                fn_args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                fn_args = {}

            if fn_name == "get_fred_data" and "series_id" in fn_args:
                df = get_fred_data(fn_args["series_id"], fn_args.get("start_date"))
                if df is None or (hasattr(df, 'empty') and df.empty):
                    import logging
                    logging.warning(f"No data returned for series_id: {fn_args.get('series_id')}")
                    tool_outputs[call["id"]] = ""
                else:
                    tool_outputs[call["id"]] = df.to_json(orient="records") if hasattr(df, 'to_json') else str(df)

        tool_messages = messages.copy()
        for call in tool_calls:
            tool_messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "name": call["function"]["name"],
                "content": tool_outputs.get(call["id"], "")
            })

        body2 = {
            "model": "gpt-4-1106-preview",
            "messages": tool_messages,
            "temperature": 0.3
        }
        response2 = requests.post(OPENAI_URL, headers=headers, json=body2)
        if response2.status_code != 200:
            return f"OpenAI API error (2nd completion): {response2.status_code} - {response2.text[:200]}"
        result2 = response2.json()
        answer = result2.get("choices", [{}])[0].get("message", {}).get("content", None)

    fallback = "⚠️ I couldn't generate an answer. Try rephrasing or simplifying the question."
    if not answer or answer.strip().lower() == "none":
        # Optional: fallback to local tool use if LLM fails
        extract_result = extract_fred_series(query)
        series = extract_result.get("series") if isinstance(extract_result, dict) else None
        if series:
            dfs = [get_fred_data(s, start_date=None) for s in series]
            if len(series) == 1:
                df = dfs[0]
                desc = extract_result.get("series_description", "")
                time_range = f"{df['date'].min().date()} to {df['date'].max().date()}" if not df.empty else "N/A"
                answer = summarize_series(series[0], df, time_range=time_range, desc=desc)
            else:
                answer = compare_series(series, dfs)
        else:
            answer = fallback

    st.session_state.setdefault("qa_thread", []).append({"question": query, "answer": answer})
    if dev_mode:
        return {"answer": answer, "tools": tool_log, "tool_outputs": tool_outputs}
    return answer
