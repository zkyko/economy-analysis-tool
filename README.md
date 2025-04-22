
# 🧠 Macro Dashboard — Fed Speech + FRED AI Assistant

This is a Streamlit-based macroeconomic research assistant that brings together real-time data, speech summarization, and LLM-powered query interpretation for traders and economic researchers. Built by a developer interested in breaking into Quant Trading, this project is a work-in-progress playground for building smarter tools for understanding markets.

---

## ✨ Features

- 🔍 **LLM-Enhanced Natural Language Search**
  - Ask questions like "What’s the latest CPI data?" or "Show me unemployment trends."
  - Automatically maps your query to the correct FRED API ID using `keyword_mapper.py`.

- 🗣️ **Federal Reserve Speech Summarization**
  - Scrapes RSS feeds from the Fed site
  - Stores and summarizes speeches to `fed_rss_summaries.json`
  - Includes sentiment tagging (planned: better NLP + trend tracking)

- 📊 **FRED Data Access and Charting**
  - Supports key macro indicators like CPI, unemployment, interest rates, etc.
  - Uses `fred_keywords.json` to parse common finance terms into queryable FRED IDs

- 📆 **Calendar View for Macro Events**
  - Explore recent speeches by Fed members visually on a timeline via `calendar_view.py`

- ⚙️ **Modular Python Architecture**
  - Organized cleanly into scraping, data processing, UI, and LLM components
  - Makes it easy to iterate or plug in new modules (e.g., news scraping, sentiment, option chains)

- 📁 **Streamlit Frontend**
  - Fully interactive GUI hosted at: [https://zkyko-market.streamlit.app/](https://zkyko-market.streamlit.app/)
  - Planned upgrade: custom GUI using Vite + React

---

## 🗂️ Project Structure

```
📁 macro-dashboard/
│
├── app.py                  # Main Streamlit entry point
├── calendar_view.py        # Fed event calendar visualization
├── debug_fred.py           # Debug utility for FRED queries
├── fed_speech_scraper.py   # RSS scraper + speech summarizer
├── rss_scraper.py          # General RSS scraper for Fed
├── keyword_mapper.py       # Maps keywords → FRED API IDs
├── llm.py                  # Handles LLM calls and summarization
├── ui.py                   # Custom Streamlit components
├── utils.py                # Helper functions (API, time, etc.)
│
├── fed_rss_summaries.json  # Cached speech summaries
├── fred_keywords.json      # FRED keyword lookup mapping
├── requirements.txt        # Python dependencies
```

---

## 🚀 Running the App

### 1. Clone the project

```bash
git clone https://github.com/yourusername/macro-dashboard.git
cd macro-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root with:

```env
FRED_API_KEY=your_fred_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run Streamlit

```bash
streamlit run app.py
```

---

## 🔮 Future Plans

- Add frontend support via **Vite + React**, served as a hybrid or external UI layer
- Add **live data** feeds and cron-based auto-refresh
- Expand to **individual stocks**, **options data**, and **market heatmaps**
- Integrate **OpenBB Terminal–style modules** for deeper financial analytics
- Fine-tune LLMs to improve query understanding, summarization, and alerting
- Add **search + filter** in UI, and export to CSV/Markdown features

---

## 🧠 Why This Exists

This project is a learning ground and portfolio piece for exploring the intersection of:
- Quant trading
- Financial data engineering
- LLMs for macroeconomic interpretation

If you're a recruiter or engineer reading this — it's still evolving, and feedback is welcome!

---

## 📦 Requirements

See [`requirements.txt`](./requirements.txt)

- `streamlit`
- `requests`
- `pandas`
- `matplotlib`
- `openai` or `deepseek`
- `python-dotenv`

---

## 📌 Notes

- Hosted via [Streamlit Cloud](https://zkyko-market.streamlit.app/)
- If you're using Codex or ChatGPT, you can help build on top of this. Just keep iterating :)

---

## 🧑‍💻 Author

Built by Nischal Bhandari — CS student, coder, and aspiring quant.  
Portfolio & projects: coming soon...
