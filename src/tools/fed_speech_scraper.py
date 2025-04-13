import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

FED_SPEECH_URL = "https://www.federalreserve.gov/newsevents/speeches.htm"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def get_fed_speech_links(limit=5):
    res = requests.get(FED_SPEECH_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    
    speeches = []
    for item in soup.select(".media-list li")[:limit]:
        anchor = item.find("a", href=True)
        if not anchor:
            continue

        title = anchor.text.strip()
        url = "https://www.federalreserve.gov" + anchor["href"]
        date = item.find("time").text.strip() if item.find("time") else "Unknown"
        speeches.append({"title": title, "url": url, "date": date})

    return speeches

def extract_speech_text(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    paragraphs = soup.select(".col-xs-12.col-sm-8.col-md-8 p")
    return "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

def summarize_text_with_sentiment(text):
    system_prompt = """You are a central bank analyst. Summarize this Fed speech and determine its tone:

- Hawkish: Focused on inflation, favors tightening
- Dovish: Focused on growth/employment, favors easing
- Neutral: Balanced or no clear signal

Respond with only JSON like:
{
  "summary": "...",
  "sentiment": "Hawkish"
}
"""

    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text[:4000]}
        ]
    }

    try:
        res = requests.post(DEEPSEEK_URL, headers=HEADERS, json=body)
        res.raise_for_status()
        raw = res.json()["choices"][0]["message"]["content"]
        return json.loads(raw)

    except Exception as e:
        print(f"❌ Error during summarization: {e}")
        return {"summary": "Could not summarize.", "sentiment": "Unknown"}

def save_summaries_to_file(data, file_path="src/data/fed_summaries.json"):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    speeches = get_fed_speech_links()
    print(f"📥 Found {len(speeches)} speeches")

    all_summaries = []

    for speech in speeches:
        print(f"\n🔗 Processing: {speech['title']} ({speech['date']})")
        full_text = extract_speech_text(speech["url"])[:4000]

        result = summarize_text_with_sentiment(full_text)

        all_summaries.append({
            "title": speech["title"],
            "date": speech["date"],
            "url": speech["url"],
            "summary": result["summary"],
            "sentiment": result["sentiment"],
            "raw": full_text
        })

    save_summaries_to_file(all_summaries)
    print("✅ Done. Saved to fed_summaries.json")

if __name__ == "__main__":
    main()
