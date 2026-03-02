import json
from bs4 import BeautifulSoup
from fetch_html import fetch_html

def parse_image_urls_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    urls = []
    seen = set()

    for s in scripts:
        raw = s.string or s.get_text(strip=True)
        if not raw:
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        dicts = walk(data)
        for obj in dicts:
            if "image" in obj:
                collect_from_image_field(obj["image"])
    print(len(urls))

    def add_url(u):
        if isinstance(u, str) and u.startswith("http") and u not in seen:
            seen.add(u)
            urls.append(u)

    def collect_from_image_field(img):
        if isinstance(img, str):
            add_url(img)

        elif isinstance(img, dict):
            add_url(img.get("url"))

        elif isinstance(img, list):
            for item in img:
                if isinstance(item, str):
                    add_url(item)
                elif isinstance(item, dict):
                    add_url(item.get("url"))

    return urls

def walk(node):
    results = []
    if isinstance(node, dict):
        results.append(node)
        for v in node.values():
            results.extend(walk(v))

    elif isinstance(node, list):
        for item in node:
            results.extend(walk(item))

    return results