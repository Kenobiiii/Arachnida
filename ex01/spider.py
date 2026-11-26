import argparse
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}
# we add a User-Agent in order to avoid the anti-bots blockades

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def download_html(url: str) -> tuple[str, str] | None:
    #the url is a str, and the func will return either a tuple (html, final url after redirects) or a None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        # if the url didn't start with http/s the request library gives error
    try:
        response = requests.get(url, headers=HEADERS, timeout=5.0)
        # we add the timeout in order to avoid the script getting frozen because of a url not answering
        if response.status_code == 200:
            # response.url is the url we ended in after following the redirects
            return response.text, response.url
        # status_code 200 in html means OK, 404: not found, 403: forbidden, 500: internal error
        else:
            print(f"[❌] Error HTTP {response.status_code} when accessing into: {url}")
            return None

    except requests.exceptions.Timeout:
        # it goes before ConnectionError because ConnectTimeout inherits from ConnectionError
        print(f"[❌] Timeout ended for: {url}")
        return None

    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        # If https fails, we try with http
        if url.startswith("https://"):
            url_http = url.replace("https://", "http://", 1)
            print(f"[❗] https failed, retrying with http: {url_http}")
            try:
                response = requests.get(url_http, headers=HEADERS, timeout=5.0)
                if response.status_code == 200:
                    print(f"[✅] successful conection using http to: {url_http}")
                    return response.text, response.url
                return None
            except requests.exceptions.RequestException as e:
                print(f"[❌] Error trying to connect with http to: {url}, error: {e}")
                return None
        else:
            print(f"[❌] Error trying to connect with: {url}")
            return None

    except requests.exceptions.RequestException as e:
        # Invalid catch (Invalid URL, no contection, etc)
        print(f"[❌] Error trying to connect with: {url}, error: {e}")
        return None

def extract_images_from_url(html_content: str, base_url: str) -> set[str]:
    images_url = set()

    # 1. We create a BeautifulSoup object in order to parse
    soup = BeautifulSoup(html_content, 'html.parser')
    # 2. We search for all <img> labels
    img_label = soup.find_all('img')
    print(f"[❕] we found {len(img_label)} <img> labels")

    # 3. We parse each img label
    for img in img_label:
        # we extract the src attribute
        src = img.get('src')
        if not src:
            continue
        # 4. we transform the relative url into the absolute using urljoin
        absolute_url = urljoin(base_url, src)

        # we check if the url end in a valid extension (only the path, so foto.jpg?width=300 is valid too)
        if urlparse(absolute_url).path.lower().endswith(VALID_EXTENSIONS):
            images_url.add(absolute_url)
    return images_url

def extract_page_links(html_content: str, base_url: str, base_domain: str) -> set[str]:
    links = set()
    soup = BeautifulSoup(html_content, 'html.parser')

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if not href:
            continue

        absolute_url = urljoin(base_url, href)
        clean_url = absolute_url.split('#')[0]
        parsed = urlparse(clean_url)
        if parsed.scheme in ('http', 'https') and parsed.netloc == base_domain:
            links.add(clean_url)

    return links

def download_img(image_url: str, destination_path: Path):
    try:
        # 1. we get the name for the file from the url
        file_name = Path(urlparse(image_url).path).name

        # if invalid name
        if not file_name:
            print(f"[❌] Invalid name for: {image_url}")
            return

        # 2. we keep the path to the directory
        file_path = destination_path / file_name

        # 3. http get to the img
        response = requests.get(image_url, headers=HEADERS, timeout=10.0)
        if response.status_code == 200:
            # 4. we write the bytes in binary writing (wb)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"[✅] Downloaded: {file_name} -> {file_path}")
        else:
            print(f"[❌] HTTP error {response.status_code} when downloading:  {image_url}")

    except requests.exceptions.RequestException as e:
        print(f"[❌] Error downloading {image_url}: {e}")
    except OSError as e:
        print(f"[❌] Error in disk writing for {file_name}: {e}")

def spider_bfs(start_url: str, max_level: int, visited_urls: set[str], output_dir: Path):
    # BFS: we use a queue of (url, level) so we crawl level by level
    queue = deque([(start_url, 0)])
    # urls of the images already downloaded, so we don't download the same one twice
    downloaded_images = set()
    # it's set with the final url of the first page (after redirects)
    base_domain = None

    while queue:
        # popleft takes the OLDEST element -> lower levels go first
        current_url, current_level = queue.popleft()
        if current_url in visited_urls:
            continue

        print(f"[❕] [Level {current_level}/{max_level}] Crawling: {current_url}")
        visited_urls.add(current_url)

        result = download_html(current_url)
        if not result:
            continue
        html_content, final_url = result

        # if it redirected to a page we already crawled, skip it
        if final_url != current_url and final_url in visited_urls:
            continue
        visited_urls.add(final_url)

        # the base domain is taken from the FINAL url of the first page (example.com -> www.example.com)
        if base_domain is None:
            base_domain = urlparse(final_url).netloc

        image_urls = extract_images_from_url(html_content, final_url)
        print(f"[✅] Found {len(image_urls)} valid images at this level")

        for img_url in image_urls:
            if img_url in downloaded_images:
                continue
            downloaded_images.add(img_url)
            download_img(img_url, output_dir)
        if current_level < max_level:
            child_links = extract_page_links(html_content, final_url, base_domain)
            for link in child_links:
                if link not in visited_urls:
                    # append adds at the END of the queue
                    queue.append((link, current_level + 1))

def main():
    # 1. Analice arguments
    parser = argparse.ArgumentParser(description="Extractor e inspector de recursos web")
    parser.add_argument("url", type=str, help="Dir web")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enables recursive image download")
    parser.add_argument("-l", "--level", type=int, default=5, help="Max recursive level")
    parser.add_argument("-p", "--path", type=str, default="./data/", help="Path where the downloaded images will be stored")
    args = parser.parse_args()

    # 2. create directory
    directory = Path(args.path)
    directory.mkdir(parents=True, exist_ok=True)

    # 3. Normalize URL (the base domain is calculated inside spider_bfs, after redirects)
    initial_url = args.url if args.url.startswith(("http://", "https://")) else "https://" + args.url

    # 4. Recursive level (0 if -r is not used)
    max_level = args.level if args.recursive else 0
    visited_urls = set()

    # 5. Start crawling
    print(f"[⌛] Starting spider on: {initial_url} | Max depth: {max_level}")
    spider_bfs(initial_url, max_level, visited_urls, directory)
    print(f"[✅] Finished. Pages visited: {len(visited_urls)}")


if __name__ == "__main__":
    main()
