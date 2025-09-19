import os
import pandas as pd

# Path where your rouge score CSVs are saved
base_path = "C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/rouge_scores"

# Define models and subreddits
models = ["gpt", "gpt5", "ollama", "mistral", "gemini", "tfidf"]
subreddits = ["askscience", "relationships", "worldnews"]

rows = []

for model in models:
    for subreddit in subreddits:
        csv_path = os.path.join(base_path, f"{subreddit}_scores/{subreddit}_{model}_scores.csv")
        if not os.path.exists(csv_path):
            print(f"⚠️ Missing file: {csv_path}")
            continue
        
        df = pd.read_csv(csv_path)
        
        # Compute averages
        avg = df.mean(numeric_only=True).to_dict()
        n_convos = len(df)
        
        rows.append({
            "Model": model,
            "Subreddit": subreddit,
            "#Convos": n_convos,
            "ROUGE-1 Precision": avg["rouge1_precision"],
            "ROUGE-1 Recall": avg["rouge1_recall"],
            "ROUGE-1 F1": avg["rouge1_f1"],
            "ROUGE-2 Precision": avg["rouge2_precision"],
            "ROUGE-2 Recall": avg["rouge2_recall"],
            "ROUGE-2 F1": avg["rouge2_f1"],
            "ROUGE-L Precision": avg["rougeL_precision"],
            "ROUGE-L Recall": avg["rougeL_recall"],
            "ROUGE-L F1": avg["rougeL_f1"],
            "Avg Summary Time (s)": avg.get("summary_time_seconds", None)
        })

# Make into summary DataFrame
summary_df = pd.DataFrame(rows)

# Save as CSV + Markdown
summary_csv = os.path.join(base_path, "rouge_summary.csv")
summary_md = os.path.join(base_path, "rouge_summary.md")

summary_df.to_csv(summary_csv, index=False)

# Pretty markdown table
with open(summary_md, "w", encoding="utf-8") as f:
    f.write(summary_df.to_markdown(index=False))

print(f"✅ Saved summary CSV: {summary_csv}")
print(f"✅ Saved summary MD: {summary_md}")
