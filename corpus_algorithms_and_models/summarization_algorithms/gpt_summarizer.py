import os
import time
import sys
import pandas as pd
from rouge_score import rouge_scorer
from openai import OpenAI


# Handle command-line argument
if len(sys.argv) < 2:
    print("Usage: python summarize_gpt.py <subreddit>")
    sys.exit(1)

subreddit = sys.argv[1]


# Paths based on subreddit name
original_csv = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_data_downloads/data",
    subreddit,
    f"{subreddit}_conversations.csv"
)

summary_output_dir = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_summaries/gpt_conversation_summaries",
    f"{subreddit}_gpt"
)

gpt_scores_csv = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/rouge_scores",
    f"{subreddit}_scores",
    f"{subreddit}_rouge_scores_gpt_vs_original.csv"
)

os.makedirs(summary_output_dir, exist_ok=True)
os.makedirs(os.path.dirname(gpt_scores_csv), exist_ok=True)

print(f"  Summaries -> {summary_output_dir}")
print(f"  ROUGE scores -> {os.path.dirname(gpt_scores_csv)}")

# Load dataset
df = pd.read_csv(original_csv)
df = df[df["text"].notnull()]
conversation_ids = df["conversation_id"].dropna().unique().tolist()


# Setup
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
client = OpenAI()


# GPT summarization function
def summarize_with_chatgpt(text, convo_id):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an extractive summarizer. "
                "You must only select and return sentences copied verbatim from the original text. "
                "Do not rephrase or add any words. "
                "Return the selected sentences as they appear in the input, in order, separated by newlines."
            )
        },
        {
            "role": "user",
            "content": (
                "Extract a summary of about 10% of the text or up to 250 words "
                "by selecting only sentences from the original text exactly as written."
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error on convo {convo_id}: {e}")
        return None


# Loop through conversations
for convo_id in conversation_ids:
    convo_df = df[df["conversation_id"] == convo_id]
    if convo_df.empty:
        continue

    original_text = "\n".join(str(t).strip() for t in convo_df["text"] if isinstance(t, str))
    summary_path = os.path.join(summary_output_dir, f"gpt_{convo_id}.txt")

    # Load or generate summary
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            gpt_summary = f.read().strip()
        elapsed = None
    else:
        start_time = time.time()
        gpt_summary = summarize_with_chatgpt(original_text, convo_id)
        elapsed = time.time() - start_time

        if gpt_summary:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(gpt_summary)
        else:
            continue  # Skip on error

    # ROUGE scoring
    scores = scorer.score(original_text, gpt_summary)
    score_dict = {
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

    pd.DataFrame([score_dict]).to_csv(
        gpt_scores_csv,
        mode='a',
        index=False,
        header=not os.path.exists(gpt_scores_csv)
    )

    if elapsed is not None:
        print(f"✓ {convo_id} — ROUGE-1 F1: {scores['rouge1'].fmeasure:.3f} (took {elapsed:.2f}s)")
    else:
        print(f"✓ {convo_id} — ROUGE-1 F1: {scores['rouge1'].fmeasure:.3f} (summary loaded from file)")

    time.sleep(1.5)  # To respect rate limits
