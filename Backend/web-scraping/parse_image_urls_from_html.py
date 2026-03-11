import json
from bs4 import BeautifulSoup
from fetch_html import fetch_html

def parse_image_urls_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    urls = []
    seen = set()

    def add_url(url):
        if isinstance(url, str) and url.startswith("http") and url not in seen:
            seen.add(url)
            urls.append(url)

    def collect_from_image_field(image_data):
        if isinstance(image_data, str):
            add_url(image_data)

        elif isinstance(image_data, dict):
            add_url(image_data.get("url"))

        elif isinstance(image_data, list):
            for item in image_data:
                if isinstance(item, str):
                    add_url(item)
                elif isinstance(item, dict):
                    add_url(item.get("url"))

    for script in scripts:
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue

        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue

        data_objects = walk(data)
        for data_obj in data_objects:
            if "image" in data_obj:
                collect_from_image_field(data_obj["image"])
    
    print(len(urls))
    return urls

def walk(node):
    collected_nodes = []
    if isinstance(node, dict):
        collected_nodes.append(node)
        for value in node.values():
            collected_nodes.extend(walk(value))

    elif isinstance(node, list):
        for item in node:
            collected_nodes.extend(walk(item))

    return collected_nodes