import requests

def fetch_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-CA,en;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text
