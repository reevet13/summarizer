<<<<<<< HEAD
# Multi-Document Summarizer

This project leverages Cornell's ConvoKit library to download and preprocess subreddit conversation corpora. Once retrieved, these corpora undergo profanity filtering and structural formatting to prepare them for natural language processing tasks.

The cleaned conversations are then summarized using several variations of Kullback-Leibler (KL) Divergence-based algorithms. These include techniques such as KL-Diversity and KL-TFIDF, designed to extract the most informative and representative responses within a conversation thread...

Each generated summary is then scored...

## Reddit Corpus Downloading/Processing Pipeline

This portion of the pipeline is designed to **download**, **clean**, and **process conversation corpora** from the [ConvoKit subreddit collection](https://zissou.infosci.cornell.edu/convokit/datasets/subreddit-corpus/corpus-zipped/). It extracts and sanitizes dialogue data for further analysis by filtering profanity, removing malformed conversations, and saving results in both CSV and Excel formats.

---

### Directory Structure

```
corpus_algorithms_and_models/
├── corpus_data_downloads/
│   ├── data/
│   │   ├── master_corpus.csv
│   │   ├── cleaned_master_corpus.csv
│   │   ├── filtered_master_corpus.csv
│   │   ├── master_corpus.xlsx
│   ├── profanity_lists/
│   │   ├── luis_von_ahn_profanity.txt
│   │   ├── profanity_wordlist.txt
│   │   ├── custom_profanity.txt
│   ├── subreddit_names/
│   │   ├── subreddits_1.txt
│   │   ├── subreddits_2.txt
│   │   ├── subreddits_3.txt
│   │   ├── clean_names.py
│   ├── corpus_download_logs/
│   │   ├── corpus_downloader_1.log
│   ├── name_collection/
│   │   ├── requestguard.py
│   │   ├── name_collection.py
│   ├── data_download.py
│   ├── validate_downloaded_list.py
```
---
### Project Libraries
These are the libraries that will need to be downloaded in your local environment to run this portion of the project.
#### Data Download Libraries
```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait, TimeoutError
import shutil
from convokit import Corpus, download
from multiprocessing import Lock
import os
import re
import pickle
import multiprocessing
import logging
import pandas as pd
import fileinput
```
#### Clean Names Libraries
```python
import fileinput
import os
import re
```
#### Name Collection Libraries
```python
from corpus_algorithms_and_models.corpus_data_downloads.name_collection.requestguard import RequestGuard, requests, urllib
from bs4 import BeautifulSoup
```
#### Request Guard Libraries
```python
import requests
import urllib
```
#### Modify CSVS
```python
import pandas as pd
import os
import re
```
---

### How to Run the Pipeline

#### Main Batch Downloader

```bash
python data_download.py
```

This will:
- Load all subreddit names
- Download and validate each corpus
- Append content from approved corpora
- Save output into: `master_corpus.csv`

---

### Output Format

Each row in the final dataset represents one utterance in a conversation:

| corpus_name      | conv_id    | res_id | question_text | answer_text          |
|------------------|------------|--------|----------------|-----------------------|
| subreddit-askmen | t3_abcd123 | 1      | DUMMY DATA     | I think you're right. |

Conversations with profanity are removed entirely based on `answer_text`.

---

### Error Handling

- Logs are stored in `corpus_download_logs/`
- Malformed lines in the downloaded corpus index file can be detected by running `validate_downloaded_list.py` manually. The path should be changed for each local environment. The malformed lines need to be changed manually to start download process again.
- Errors during downloads are logged and cleaned up automatically.

---

### Cleaning Logic

- Removes all non-printable and control characters
- Drops rows with missing or empty `answer_text`
- Uses a `profanity_set` to eliminate entire conversations that contain flagged words

---


### Project Features

- **Scrapes .zip corpora links** from ConvoKit dataset index which checks `robots.txt` compliance before crawling pages for subreddit names to download.
- **Downloads corpora concurrently** using threads and processes using the names scrapped previously if those corpora meet minimum text size and conversation count standards.
- **Filters and Cleans** the downloaded csv file so it doesn't include profanity, empty rows, or extraneous characters.
- **Logs all download activity** and gives resources to detect malformed entries

---

## Summarization Algorithms

## Summaries and ROUGE Scores
=======
# Summarizer

## Overview

Summarizer is a Python-based project designed to [provide a brief description of the project's purpose and functionality].

## Features

- [Feature 1]
- [Feature 2]
- [Feature 3]

## Installation

To get started with Summarizer, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/cnesbit1/summarizer.git
   cd summarizer
   ```
2. **Set up a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. **Install the required dependencies listed in `requirements.txt`**
    ```bash
    pip install -r requirements.txt
    ```
>>>>>>> origin/tanner
