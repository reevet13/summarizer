from corpus_algorithms_and_models.corpus_data_downloads.name_collection.requestguard import RequestGuard, requests, urllib
from bs4 import BeautifulSoup


def save_list_to_file(subreddit_list, filename="subreddits.txt"):
    """Save the subreddit list to a file."""
    print(f"Saving subreddit list to {filename}...")
    with open(filename, 'w') as file:
        for subreddit in subreddit_list:
            file.write(f"{subreddit}\n")
    print("Subreddit list saved successfully.")

def save_zip_links(url, subreddit_list):
    zip_links = []
    try:
        guard = RequestGuard(url)

        print(f"Visiting main URL: {url}...")
        response = guard.make_get_request(url)
        if response is None:
            print(f"Cannot access {url} as per robots.txt.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True)[1:]:
            href = link['href']
            if href.startswith('/'):
                href = url.rstrip('/') + href
            href = urllib.parse.unquote(href)
            print(f"Visiting link: {href}...")
            try:
                sub_response = guard.make_get_request(f"{url}{href}")
                if sub_response is None:
                    print(f"Cannot access {href} as per robots.txt.")
                    continue

                sub_soup = BeautifulSoup(sub_response.text, 'html.parser')

                for sub_link in sub_soup.find_all('a', href=True)[1:]:
                    sub_href = sub_link['href']
                    if sub_href.endswith('.zip'):
                        full_zip_href = urllib.parse.urljoin(href, sub_href)
                        decoded_zip_href = urllib.parse.unquote(full_zip_href)
                        proper_name = decoded_zip_href[len(href):decoded_zip_href.rfind('.corpus.zip')]
                        zip_links.append(f"subreddit-{proper_name}")

                        print(f"Found .zip link: {proper_name}")

            except requests.RequestException as sub_e:
                print(f"Failed to visit {href}: {sub_e}")
    except requests.RequestException as e:
        print(f"Failed to visit {url}: {e}")

    subreddit_list.extend(zip_links)
    print("All .zip links collected:", zip_links)


if __name__ == "__main__":
    url = "https://zissou.infosci.cornell.edu/convokit/datasets/subreddit-corpus/corpus-zipped/"
    subreddit_list = []
    save_zip_links(url, subreddit_list)
    save_list_to_file(subreddit_list)