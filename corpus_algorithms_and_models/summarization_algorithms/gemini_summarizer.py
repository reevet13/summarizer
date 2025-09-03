import os
import time
import sys
import pandas as pd
from rouge_score import rouge_scorer
from google import genai
from google.genai.types import GenerateContentConfig, ThinkingConfig

if len(sys.argv) < 2:
    print("Usage: python summarize_gemini.py <subreddit>")
    sys.exit(1)
subreddit = sys.argv[1]

original_csv = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_data_downloads/data", subreddit, f"{subreddit}_conversations.csv")
summary_output_dir = os.path.join("C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_summaries/gemini_conversation_summaries", f"{subreddit}_gemini")
gpt_scores_csv = os.path.join("C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/rouge_scores",
                              f"{subreddit}_scores", f"{subreddit}_rouge_scores_gemini_vs_original.csv")

os.makedirs(summary_output_dir, exist_ok=True)
os.makedirs(os.path.dirname(gpt_scores_csv), exist_ok=True)

print(f"Summaries -> {summary_output_dir}")
print(f"ROUGE scores -> {os.path.dirname(gpt_scores_csv)}")

df = pd.read_csv(original_csv)
df = df[df["text"].notnull()]
conversation_ids = df["conversation_id"].dropna().unique().tolist()

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
client = genai.Client()

def summarize_with_gemini(text, convo_id):
    prompt = (
        "You are an extractive summarizer. "
        "Select ~10% of the sentences from the input, **verbatim**, in order, separated by newlines."
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, text],
            config=GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=1024,
                thinking_config=ThinkingConfig(thinking_budget=0)
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error on convo {convo_id}: {e}")
        return None

for convo_id in conversation_ids:
    convo_df = df[df["conversation_id"] == convo_id]
    if convo_df.empty:
        continue
    original_text = "\n".join(str(t).strip() for t in convo_df["text"])
    summary_path = os.path.join(summary_output_dir, f"gemini_{convo_id}.txt")

    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            gem_summary = f.read().strip()
        elapsed = None
    else:
        start = time.time()
        gem_summary = summarize_with_gemini(original_text, convo_id)
        elapsed = time.time() - start
        if gem_summary:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(gem_summary)
        else:
            continue

    scores = scorer.score(original_text, gem_summary)
    d = {
        "conversation_id": convo_id,
        "rouge1_precision": scores["rouge1"].precision,
        "rouge1_recall": scores["rouge1"].recall,
        "rouge1_f1": scores["rouge1"].fmeasure,
        "rouge2_precision": scores["rouge2"].precision,
        "rouge2_recall": scores["rouge2"].recall,
        "rouge2_f1": scores["rouge2"].fmeasure,
        "rougeL_precision": scores["rougeL"].precision,
        "rougeL_recall": scores["rougeL"].recall,
        "rougeL_f1": scores["rougeL"].fmeasure,
        "summary_time_seconds": elapsed
    }
    pd.DataFrame([d]).to_csv(
        gpt_scores_csv, mode='a', index=False,
        header=not os.path.exists(gpt_scores_csv)
    )
    note = f"(took {elapsed:.2f}s)" if elapsed is not None else "(loaded from file)"
    print(f"✓ {convo_id} — ROUGE-1 F1: {scores['rouge1'].fmeasure:.3f} {note}")
    time.sleep(1.5)
