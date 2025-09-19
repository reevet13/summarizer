import os
import time
import sys
import pandas as pd
from rouge_score import rouge_scorer
from mistralai import Mistral

# Handle command-line argument
if len(sys.argv) < 2:
    print("Usage: python summarize_mistral.py <subreddit>")
    sys.exit(1)

subreddit = sys.argv[1]

# Paths based on subreddit name
original_csv = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_data_downloads/data",
    subreddit,
    f"{subreddit}_conversations.csv"
)

summary_output_dir = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/corpus_summaries/mistral_conversation_summaries",
    f"{subreddit}_mistral"
)

mistral_scores_csv = os.path.join(
    "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/rouge_scores",
    f"{subreddit}_scores",
    f"{subreddit}_rouge_scores_mistral_vs_original.csv"
)

# Create directories if they don't exist
os.makedirs(summary_output_dir, exist_ok=True)
os.makedirs(os.path.dirname(mistral_scores_csv), exist_ok=True)

print(f"Summaries -> {summary_output_dir}")
print(f"ROUGE scores -> {os.path.dirname(mistral_scores_csv)}")

# Load dataset
df = pd.read_csv(original_csv)
df = df[df["text"].notnull()]
conversation_ids = df["conversation_id"].dropna().unique().tolist()

# Setup ROUGE scorer and Mistral client
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Mistral summarization function
def summarize_with_mistral(text, convo_id):
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
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            max_tokens=8192
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error on convo {convo_id}: {e}")
        return None


# Loop through conversations
total_convos = len(conversation_ids)
for idx, convo_id in enumerate(conversation_ids, start=1):
    convo_df = df[df["conversation_id"] == convo_id]
    if convo_df.empty:
        continue

    original_text = "\n".join(str(t).strip() for t in convo_df["text"] if isinstance(t, str))
    summary_path = os.path.join(summary_output_dir, f"mistral_{convo_id}.txt")

    # Load or generate summary
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            mistral_summary = f.read().strip()
        elapsed = None
        print(f"[{idx}/{total_convos}] Loaded existing summary for {convo_id}")
    else:
        print(f"[{idx}/{total_convos}] Generating summary for {convo_id}...")
        start_time = time.time()
        mistral_summary = summarize_with_mistral(original_text, convo_id)
        elapsed = time.time() - start_time

        if mistral_summary:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(mistral_summary)
            print(f"[{idx}/{total_convos}] Saved summary for {convo_id} ({elapsed:.2f}s)")
        else:
            print(f"[{idx}/{total_convos}] Skipped {convo_id} (error generating summary)")
            continue  # Skip on error

    # ROUGE scoring
    scores = scorer.score(original_text, mistral_summary)
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

    # Append scores immediately
    pd.DataFrame([score_dict]).to_csv(
        mistral_scores_csv,
        mode='a',
        index=False,
        header=not os.path.exists(mistral_scores_csv)
    )

    # Print ROUGE results to console
    if elapsed is not None:
        print(f"[{idx}/{total_convos}] 📊 {convo_id} — ROUGE-1 F1: {scores['rouge1'].fmeasure:.3f}, "
              f"ROUGE-2 F1: {scores['rouge2'].fmeasure:.3f}, "
              f"ROUGE-L F1: {scores['rougeL'].fmeasure:.3f} (took {elapsed:.2f}s)")
    else:
        print(f"[{idx}/{total_convos}] 📊 {convo_id} — ROUGE-1 F1: {scores['rouge1'].fmeasure:.3f}, "
              f"ROUGE-2 F1: {scores['rouge2'].fmeasure:.3f}, "
              f"ROUGE-L F1: {scores['rougeL'].fmeasure:.3f} (loaded from file)")

    time.sleep(1.5)
