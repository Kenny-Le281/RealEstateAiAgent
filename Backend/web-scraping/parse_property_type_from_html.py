from fetch_html import fetch_html
import json
from bs4 import BeautifulSoup
from fetch_html import fetch_html

def parse_property_type_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    meta_script = soup.find("script", attrs={"id": "xdp-meta", "type": "application/json"})
    if meta_script:
        script_content = meta_script.string or meta_script.get_text(strip=True)
        if script_content:
            try:
                data = json.loads(script_content)
                property_types = data.get("propertyType")
                if isinstance(property_types, str) and property_types.strip():
                    return property_types.strip()
            except json.JSONDecodeError:
                pass


    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue
        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict):
            continue
        main_entity = data.get("mainEntity")
        if isinstance(main_entity, dict):
            accommodation_category = main_entity.get("accommodationCategory")
            if isinstance(accommodation_category, str) and accommodation_category.strip():
                return accommodation_category.strip()

    return None
