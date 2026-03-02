from fetch_html import fetch_html
import json
from bs4 import BeautifulSoup
from fetch_html import fetch_html

def parse_property_type_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    meta_script = soup.find("script", attrs={"id": "xdp-meta", "type": "application/json"})
    if meta_script:
        raw = meta_script.string or meta_script.get_text(strip=True)
        if raw:
            try:
                data = json.loads(raw)
                property_types = data.get("propertyType")
                if isinstance(property_types, str) and property_types.strip():
                    return property_types.strip()
            except json.JSONDecodeError:
                pass


    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = s.string or s.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict):
            continue
        main = data.get("mainEntity")
        if isinstance(main, dict):
            category = main.get("accommodationCategory")
            if isinstance(category, str) and category.strip():
                return category.strip()

    return None
