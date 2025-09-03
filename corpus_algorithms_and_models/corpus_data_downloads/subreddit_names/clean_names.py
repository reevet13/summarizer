import fileinput
import os
import re

def load_list_from_file(filename):
    """Load and sanitize the subreddit list from a file."""
    print(f"Loading file: {filename}")

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []

    try:
        with open(filename, 'r') as file:
            subreddit_list = [
                stripped_line for line in file
                if (stripped_line := line.strip()) and not re.search(r'[<>:"/\\|?*]', stripped_line)
            ]
        print(f"Loaded subreddits: {len(subreddit_list)}")
        return subreddit_list

    except Exception as e:
        print(f"Error loading file {filename}: {e}")
        return []

def main():
    profanity1 = load_list_from_file("./corpus_algorithms_and_models/corpus_data_downloads/profanity_lists/luis_von_ahn_profanity.txt")
    profanity2 = load_list_from_file("./corpus_algorithms_and_models/corpus_data_downloads/profanity_lists/profanity_wordlist.txt")
    profanity3 = load_list_from_file("./corpus_algorithms_and_models/corpus_data_downloads/profanity_lists/custom_profanity.txt")
    
    profanity_set = set(profanity1 + profanity2 + profanity3)

    print("Filtering subreddits...")
    for i in ["1", "2", "3"]:
        with fileinput.FileInput(f"./corpus_algorithms_and_models/corpus_data_downloads/subreddit_names/subreddits_{i}.txt", inplace=True) as file:
            for line in file:
                subreddit = line.strip().lower()
                if not any(bad_word in subreddit for bad_word in profanity_set):
                    print(line, end='')
    print("Done filtering.")

if __name__ == "__main__":
    main()