import pandas as pd
import os
import sys


if len(sys.argv) < 2:
    print("Usage: python summarize_gpt.py <subreddit>")
    sys.exit(1)

subreddit = sys.argv[1]

base_dir = f"C:/Users/Tanner/Desktop/summarizer/corpus_algorithms_and_models/rouge_scores/{subreddit}_scores"

models = ["gemini", "tfidf", "ollama", "gpt"]
dfs = []

for model in models:
    path = os.path.join(base_dir, f"{subreddit}_rouge_scores_{model}_vs_original.csv")
    df = pd.read_csv(path)
    
    # Rename columns to include model name
    rename_map = {col: f"{model}_{col}" for col in df.columns if col != "conversation_id"}
    df = df.rename(columns=rename_map)
    dfs.append(df)

# Merge all dataframes on conversation_id
final_df = dfs[0]
for df in dfs[1:]:
    final_df = pd.merge(final_df, df, on="conversation_id", how="outer")

final_df = final_df.fillna("N/A")

# Interleave columns: conversation_id first, then by metric type
id_col = ["conversation_id"]
other_cols = [col for col in final_df.columns if col != "conversation_id"]

# Extract the metric names without model prefix
metrics = sorted({col.split("_", 1)[1] for col in other_cols})

# Build new column order
new_order = id_col + [f"{model}_{metric}" for metric in metrics for model in models]

# Reorder columns
final_df = final_df[new_order]

# Save combined CSV
output_path = os.path.join(base_dir, f"{subreddit}_rouge_scores_combined.csv")
final_df.to_csv(output_path, index=False)

print(f"✅ Combined file saved to {output_path}")
