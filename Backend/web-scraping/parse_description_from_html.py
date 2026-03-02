import json
import html
from bs4 import BeautifulSoup
from fetch_html import fetch_html

def parse_description_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    for s in scripts:
        raw = s.string or s.get_text(strip=True)
        if not raw:
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue


        if isinstance(data, dict):
            desc = data.get("description")
            if isinstance(desc, str) and desc.strip():
                return html.unescape(desc).strip()

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    desc = item.get("description")
                    if isinstance(desc, str) and desc.strip():
                        return html.unescape(desc).strip()

    return None
