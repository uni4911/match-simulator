import time
from typing import Optional
from curl_cffi import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def fetch_html(url: str, delay: float = 1.0, retries: int = 3) -> Optional[str]:
    if delay > 0:
        time.sleep(delay)

    for attempt in range(retries):
        try:
            session = requests.Session(impersonate="chrome124")
            response = session.get(url, headers=HEADERS, timeout=12)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt + 1}/{retries}] Error fetching {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    test_html = fetch_html("https://sofifa.com/teams")
    if test_html:
        print(f"Successfully fetched test page ({len(test_html)} bytes)")
    else:
        print("Failed to fetch test page")