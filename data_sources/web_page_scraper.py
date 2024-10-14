import os
import pickle
import requests
from bs4 import BeautifulSoup

class WebPageScraper:
    def __init__(self, cache_dir="web_cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_filename(self, url):
        return os.path.join(self.cache_dir, url.replace('/', '_') + '.pkl')

    def _fetch_and_cache(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        cache_file = self._get_cache_filename(url)
        with open(cache_file, 'wb') as f:
            pickle.dump(response.content, f)
            
    def get_links_from_url(self, url):
        cache_file = self._get_cache_filename(url)

        if os.path.exists(cache_file):
            # Load from cache
            with open(cache_file, 'rb') as f:
                content = pickle.load(f)
        else:
            # Fetch and save to cache
            self._fetch_and_cache(url)
            content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            links.append(link.get('href'))
        return links

    def get_text_from_url(self, url, text_selectors=['p', 'h1', 'h2', 'h3', 'li', 'td', 'th']):
        cache_file = self._get_cache_filename(url)

        if os.path.exists(cache_file):
            # Load from cache
            with open(cache_file, 'rb') as f:
                content = pickle.load(f)
                print("Using cache" + url)
        else:
            # Fetch and save to cache
            self._fetch_and_cache(url)
            content = requests.get(url).content  # Reload after caching

        soup = BeautifulSoup(content, 'html.parser')

        extracted_text = []
        for selector in text_selectors:
            elements = soup.find_all(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    extracted_text.append(text)

        return '\n'.join(extracted_text)
    
    def recursive_scrape(self, url, filter, max_depth=2, text_selectors=['p', 'h1', 'h2', 'h3', 'li', 'td', 'th']):
        visited_urls = set()
        current_depth = 0
        results = []
        def process_page(url, depth):
            if depth <= max_depth and url not in visited_urls:
                visited_urls.add(url)
                try:
                    # Check for url in cache
                    cache_file = self._get_cache_filename(url)
                    if os.path.exists(cache_file):
                        # Load from cache
                        with open(cache_file, 'rb') as f:
                            content = pickle.load(f)
                            print("Using cache" + url)
                    else:
                        # Fetch and save to cache
                        self._fetch_and_cache(url)
                        content = requests.get(url).content  # Reload after caching

                    soup = BeautifulSoup(content, 'html.parser')

                    # Extract text 
                    print("Starting URL: ", url)
                    print("========\n")
                    for selector in text_selectors:
                        for tag in soup.find_all(selector):
                            text = tag.get_text(strip=True)
                            if text:
                                results.append(text)
                    print("=======\n")

                    # Find and process links
                    links = soup.find_all('a', href=True)
                    for link in links:
                        next_url = link['href']    
                        if next_url.startswith(filter):
                            process_page(next_url, depth + 1)

                except requests.exceptions.RequestException as e:
                    print(f"Error processing {url}: {e}")

        process_page(url, current_depth)
        return results