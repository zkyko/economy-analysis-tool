# src/tools/rss_scraper.py
import feedparser
import json
import os
from datetime import datetime

RSS_FEED_URL = "https://www.federalreserve.gov/feeds/speeches.xml"
OUTPUT_PATH = "src/data/fed_rss_summaries.json"

def parse_sentiment(text):
    if "inflation" in text.lower() or "rates" in text.lower():
        return "Hawkish"
    elif "growth" in text.lower() or "support" in text.lower():
        return "Dovish"
    return "Neutral"

def scrape_fed_speeches():
    feed = feedparser.parse(RSS_FEED_URL)
    speeches = []

    for entry in feed.entries:
        # Removed unnecessary filter: all entries are already speeches
        speech = {
            "title": entry.title,
            "date": datetime(*entry.published_parsed[:6]).strftime("%B %d, %Y"),
            "speaker": "Unknown",
            "summary": entry.summary.strip(),
            "location": "Unknown",
            "url": entry.link,
            "sentiment": parse_sentiment(entry.summary)
        }
        speeches.append(speech)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(speeches, f, indent=2)
    print(f"✅ Saved {len(speeches)} speeches to {OUTPUT_PATH}")

if __name__ == "__main__":
    scrape_fed_speeches()
