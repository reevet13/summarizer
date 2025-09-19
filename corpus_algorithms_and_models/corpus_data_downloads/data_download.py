import os
import sys
from convokit import download
import zipfile

def download_and_extract(subreddit):
    print(f"📥 Downloading subreddit '{subreddit}' corpus archive...")
    archive_path = download(f"subreddit-{subreddit}")
    print(f"✅ Archive downloaded at: {archive_path}")

    extract_dir = os.path.join(os.path.dirname(archive_path), f"subreddit-{subreddit}")
    if not os.path.exists(extract_dir):
        print(f"📂 Extracting archive to {extract_dir} ...")
        with zipfile.ZipFile(archive_path, 'r') as z:
            z.extractall(extract_dir)
        print("✅ Extraction complete.")
    else:
        print(f"ℹ️ Already extracted at: {extract_dir}")

    return extract_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_subreddit.py <subreddit_name>")
        sys.exit(1)

    subreddit = sys.argv[1]
    extract_dir = download_and_extract(subreddit)
    print(f"📁 You can now access utterances at: {os.path.join(extract_dir, 'utterances.jsonl')}")
