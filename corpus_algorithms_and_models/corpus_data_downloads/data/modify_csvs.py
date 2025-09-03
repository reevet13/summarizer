import pandas as pd
import os
import re

def load_list_from_file(filename):
    """Load and sanitize the profanity list from a file."""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [
                line.strip().lower()
                for line in file
                if line.strip() and not re.search(r'[<>:"/\\|?*]', line)
            ]
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def create_cleaned_csv(input_file, output_file, profanity_set):
    df = pd.read_csv(input_file)

    def contains_profanity(text):
        text = str(text).lower()
        return any(bad_word in text for bad_word in profanity_set)

    df['has_profanity'] = df['answer_text'].apply(contains_profanity)
    bad_conv_ids = set(df[df['has_profanity']]['conv_id'])
    df_cleaned = df[~df['conv_id'].isin(bad_conv_ids)].drop(columns=['has_profanity'])
    df_cleaned.to_csv(output_file, index=False)

def create_filtered_csv(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)
    df_filtered = df.dropna(subset=['answer_text']).query("answer_text.str.strip() != ''")
    df_filtered.to_csv(output_csv_path, index=False)

def create_excel(input_csv_path, output_excel_path):
    df_cleaned = pd.read_csv(input_csv_path)
    df_cleaned.to_excel(output_excel_path, index=False)

def main():
    original_csv_path = "./corpus_algorithms_and_models/corpus_data_downloads/data/master_corpus.csv"
    filtered_csv_path = "./corpus_algorithms_and_models/corpus_data_downloads/data/filtered_master_corpus.csv"
    cleaned_csv_path = "./corpus_algorithms_and_models/corpus_data_downloads/data/cleaned_master_corpus.csv"
    excel_path = "./corpus_algorithms_and_models/corpus_data_downloads/data/master_corpus.xlsx"

    profanity1 = load_list_from_file("./corpus_algorithms_and_models/corpus_data_downloads/profanity_lists/luis_von_ahn_profanity.txt")
    profanity2 = load_list_from_file("./corpus_algorithms_and_models/corpus_data_downloads/profanity_lists/profanity_wordlist.txt")
    profanity3 = load_list_from_file("./corpus_algorithms_and_models/corpus_data_downloads/profanity_lists/custom_profanity.txt")
    profanity_set = set(profanity1 + profanity2 + profanity3)

    create_filtered_csv(original_csv_path, filtered_csv_path)
    create_cleaned_csv(filtered_csv_path, cleaned_csv_path, profanity_set)
    create_excel(cleaned_csv_path, excel_path)

if __name__ == "__main__":
    main()