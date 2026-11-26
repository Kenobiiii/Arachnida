import argparse
from pathlib import Path
import requests

def dowload_html(url: str) -> str | None:
    #the url is a str, and the func will return either an str or a None
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    }
    # we add a User-Agent in order to avoid the anti-bots blockades
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        # if the url didn't start with http/s the request library gives error 
    try:
        response = requests.get(url, headers=headers, timeout=5.0)
        # we add the timeout in order to avoid the script getting frozen because of a url not answering
        if response.status_code == 200:
            return response.text
        # status_code 200 in html means OK, 404: not found, 403: forbidden, 500: internal error
        else:
            print(f"[❌] Error HTTP {response.status_code} when accessing into: {url}")

    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        # If https fails, we try with http
        if url.startswith("https://"):
            url_http = url.replace("https://", "http://", 1)
            print(f"[❗] https failed, retrying with http: {url_http}")
            try:
                response = requests.get(url_http, headers=headers, timeout=5.0)
                if response.status_code == 200:
                    print(f"[✅] successful conection using http to: {url_http}")
                    return response.text
            except requests.exceptions.RequestException as e:
                print(f"[❌] Error trying to connect with http to: {url}")
                return None
        else:
            print(f"[❌] Error trying to connect with: {url}")
            return None
    
    except requests.exceptions.Timeout:
        print(f"[❌] Timeout ended for: {url}")
        return None
    
    except requests.exceptions.RequestException as e:
        # Invalid catch (Invalid URL, no contection, etc)
        print(f"[❌] Error trying to connect with: {url}")
        return None

def main():
    # 1. Analice arguments
    parser = argparse.ArgumentParser(description="Extractor e inspector de recursos web")
    parser.add_argument("url", type=str, help="Dir web")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enables recursive image download")
    parser.add_argument("-l", "--level", type=int, default=5, help="Max recursive level")
    parser.add_argument("-p", "--path", type=str, default="./data/", help="Path where the downloaded images will be stored")
    args = parser.parse_args()

    # 2. create directory
    directory = Path(args.path);
    directory.mkdir(parents=True, exist_ok=True)

    # 3. Dowload HTML
    print(f"url used {args.url}")
    html_content = dowload_html(args.url)

    if html_content:
        print(f"[✅]HTML dowloaded successful")

if __name__ == "__main__":
    main()