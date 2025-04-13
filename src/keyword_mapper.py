import json
import os
import re

def load_keyword_map():
    path = os.path.join(os.path.dirname(__file__), "data", "fred_keywords.json")
    with open(path, "r") as f:
        return json.load(f)

def match_keywords_to_fred(query, keyword_dict):
    query = query.lower()

    matches = []
    for keyword, info in keyword_dict.items():
        # Match whole keyword (word-boundary based) so "rate" doesn't match "unemployment rate" accidentally
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query):
            matches.append(info)

    return matches
