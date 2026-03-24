import json
import html
from bs4 import BeautifulSoup
from fetch_html import fetch_html

def parse_description_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    for script in scripts:
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue

        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue


        if isinstance(data, dict):
            description = data.get("description")
            if isinstance(description, str) and description.strip():
                return html.unescape(description).strip()

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    description = item.get("description")
                    if isinstance(description, str) and description.strip():
                        return html.unescape(description).strip()

    return None
