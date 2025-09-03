import os
import pandas as pd
import json

# Paths
input_json = os.path.expanduser("~/.convokit/saved-corpora/reddit-corpus-small/utterances.json")
output_csv = "./corpus_algorithms_and_models/corpus_data_downloads/data/reddit_corpus_small.csv"
output_xlsx = "./corpus_algorithms_and_models/corpus_data_downloads/data/reddit_corpus_small.xlsx"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# Read the entire file as a single JSON array
with open(input_json, 'r', encoding='utf-8') as f:
    utterances_list = json.load(f)

# Convert to DataFrame
df = pd.DataFrame([
    {
        "id": u.get("id"),
        "conversation_id": u.get("root"),
        "speaker": u.get("user"),
        "reply_to": u.get("reply_to"),
        "text": u.get("text"),
        "timestamp": u.get("timestamp"),
        "subreddit": u.get("meta", {}).get("subreddit"),
        "score": u.get("meta", {}).get("score"),
        "permalink": u.get("meta", {}).get("permalink"),
        "meta": json.dumps(u.get("meta", {}))  # optional: full meta as JSON string
    }
    for u in utterances_list
])

# Write to CSV
df.to_csv(output_csv, index=False, encoding="utf-8")
print(f"Saved CSV to: {output_csv}")

# Write to XLSX
df.to_excel(output_xlsx, index=False)
print(f"Saved XLSX to: {output_xlsx}")
