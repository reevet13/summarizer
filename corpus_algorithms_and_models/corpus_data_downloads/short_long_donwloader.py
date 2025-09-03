import os
import pandas as pd
import json

# Paths
input_jsonl = os.path.expanduser("~/.convokit/saved-corpora/subreddit-askscience/utterances.jsonl")
output_csv_short = "./corpus_algorithms_and_models/corpus_data_downloads/data/askscience_short_convos.csv"
output_csv_long = "./corpus_algorithms_and_models/corpus_data_downloads/data/askscience_long_convos.csv"
output_xlsx_short = "./corpus_algorithms_and_models/corpus_data_downloads/data/askscience_short_convos.xlsx"
output_xlsx_long = "./corpus_algorithms_and_models/corpus_data_downloads/data/askscience_long_convos.xlsx"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_csv_short), exist_ok=True)

# Load utterances.jsonl
print("Loading utterances...")
utterance_dict = {}
with open(input_jsonl, 'r', encoding='utf-8') as f:
    for line in f:
        u = json.loads(line)
        root_id = u.get("root")
        if root_id not in utterance_dict:
            utterance_dict[root_id] = []
        utterance_dict[root_id].append(u)

print(f"Loaded {len(utterance_dict)} conversations.")

# Filter conversations
short_convos, long_convos = [], []
short_ids, long_ids = set(), set()

for convo_id, utterances in utterance_dict.items():
    total_words = sum(len(u.get("text", "").split()) for u in utterances)

    if 100 <= total_words <= 200 and len(short_ids) < 100:
        short_convos.extend(utterances)
        short_ids.add(convo_id)
    elif 1000 <= total_words <= 2000 and len(long_ids) < 100:
        long_convos.extend(utterances)
        long_ids.add(convo_id)

    if len(short_ids) >= 100 and len(long_ids) >= 100:
        break

print(f"Selected {len(short_ids)} short and {len(long_ids)} long conversations.")

# Convert to DataFrames
def to_dataframe(utterances):
    return pd.DataFrame([
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
            "meta": json.dumps(u.get("meta", {}))
        }
        for u in sorted(utterances, key=lambda x: (x.get("root"), x.get("timestamp")))
    ])

df_short = to_dataframe(short_convos)
df_long = to_dataframe(long_convos)

# Write to CSV
df_short.to_csv(output_csv_short, index=False, encoding="utf-8")
df_long.to_csv(output_csv_long, index=False, encoding="utf-8")
print(f"Saved short conversations CSV to: {output_csv_short}")
print(f"Saved long conversations CSV to: {output_csv_long}")

# Write to XLSX
df_short.to_excel(output_xlsx_short, index=False)
df_long.to_excel(output_xlsx_long, index=False)
print(f"Saved short conversations XLSX to: {output_xlsx_short}")
print(f"Saved long conversations XLSX to: {output_xlsx_long}")
