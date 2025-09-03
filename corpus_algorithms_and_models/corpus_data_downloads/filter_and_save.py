import os
import sys
import json
import pandas as pd
from collections import defaultdict

MIN_WORDS = 1000
MAX_WORDS = 2000
MAX_CONVOS = 500

def filter_conversations(utterances_path, output_dir):
    convo_utterances = defaultdict(list)
    convo_word_counts = defaultdict(int)
    qualifying_convos = []

    print(f"📂 Reading utterances from {utterances_path} ...")

    with open(utterances_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            utt = json.loads(line)
            convo_id = utt["root"]
            text = utt.get("text") or ""
            word_count = len(text.split())

            convo_word_counts[convo_id] += word_count
            convo_utterances[convo_id].append(utt)

            # Check if conversation qualifies and not yet added
            if (convo_id not in qualifying_convos
                    and MIN_WORDS <= convo_word_counts[convo_id] <= MAX_WORDS):
                qualifying_convos.append(convo_id)

                if len(qualifying_convos) >= MAX_CONVOS:
                    print(f"✅ Found {MAX_CONVOS} qualifying conversations. Stopping at line {line_num}.")
                    break

            if line_num % 100000 == 0:
                print(f"Processed {line_num} lines, found {len(qualifying_convos)} qualifying conversations so far...")

    print(f"📊 Total qualifying conversations found: {len(qualifying_convos)}")

    # Gather utterances for qualifying conversations
    filtered_utterances = []
    for cid in qualifying_convos:
        filtered_utterances.extend(convo_utterances[cid])

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
            "meta": json.dumps(u.get("meta", {}))
        }
        for u in sorted(filtered_utterances, key=lambda x: (x.get("root"), x.get("timestamp")))
    ])

    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, f"{subreddit}_conversations.csv")
    xlsx_path = os.path.join(output_dir, f"{subreddit}_conversations.xlsx")

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_excel(xlsx_path, index=False)

    print(f"💾 Saved filtered conversations to:")
    print(f"  CSV: {csv_path}")
    print(f"  XLSX: {xlsx_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python filter_and_save.py <subreddit_name> <output_directory>")
        sys.exit(1)

    subreddit = sys.argv[1]
    output_dir = f"C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_data_downloads/data/{subreddit}"

    utterances_path = os.path.expanduser(f"C:/Users/Tanner/.convokit/saved-corpora/subreddit-{subreddit}/utterances.jsonl")
    if not os.path.exists(utterances_path):
        print(f"❌ Could not find utterances.jsonl at: {utterances_path}")
        print(f"Run `download_subreddit.py {subreddit}` first.")
        sys.exit(1)

    filter_conversations(utterances_path, output_dir)
