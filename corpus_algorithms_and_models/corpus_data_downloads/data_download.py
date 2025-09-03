import sys
import json
import os
from collections import defaultdict
from convokit import download
import zipfile

MIN_WORDS = 1000
MAX_WORDS = 2000
MAX_CONVOS = 500

def stream_and_filter(subreddit):
    print(f"📥 Downloading subreddit '{subreddit}' corpus archive (if needed)...")
    archive_path = download(f"subreddit-{subreddit}")
    print(f"✅ Archive downloaded at: {archive_path}")

    qualifying_convos = []
    convo_utterances = defaultdict(list)
    convo_word_counts = defaultdict(int)

    print("📂 Opening archive and streaming utterances.jsonl...")
    with zipfile.ZipFile(archive_path, 'r') as z:
        with z.open('utterances.jsonl') as f:
            for line_num, line_bytes in enumerate(f, 1):
                line = line_bytes.decode('utf-8')
                utt = json.loads(line)

                convo_id = utt["root"]
                text = utt.get("text") or ""
                word_count = len(text.split())

                convo_word_counts[convo_id] += word_count
                convo_utterances[convo_id].append(utt)

                if (convo_id not in qualifying_convos
                        and MIN_WORDS <= convo_word_counts[convo_id] <= MAX_WORDS):
                    qualifying_convos.append(convo_id)

                    if len(qualifying_convos) >= MAX_CONVOS:
                        print(f"✅ Found {MAX_CONVOS} qualifying conversations. Stopping at line {line_num}.")
                        break

                if line_num % 100000 == 0:
                    print(f"Processed {line_num} lines, found {len(qualifying_convos)} qualifying conversations so far...")

    print(f"📊 Total qualifying conversations found: {len(qualifying_convos)}")

    filtered = {cid: convo_utterances[cid] for cid in qualifying_convos}
    output_file = f"{subreddit}_filtered_conversations.json"
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(filtered, out, indent=2)

    print(f"💾 Saved filtered conversations to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_subreddit.py <subreddit>")
        sys.exit(1)

    subreddit = sys.argv[1]
    stream_and_filter(subreddit)
