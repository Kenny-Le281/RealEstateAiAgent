from __future__ import annotations
from fetch_html import fetch_html
import json
from bs4 import BeautifulSoup
import re



def parse_parking_from_html(html_content):

    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue
        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue


        if isinstance(data, list):
            data_objects = data
        else:
            data_objects = [data]
             
        for data_obj in data_objects:
            if not isinstance(data_obj, dict):
                continue

            main_entity = data_obj.get("mainEntity")
            if not isinstance(main_entity, dict):
                continue

            amenity_features = main_entity.get("amenityFeature")
            if not isinstance(amenity_features, list):
                continue

            for amenity_feature in amenity_features:
                if not isinstance(amenity_feature, dict):
                    continue
                name = amenity_feature.get("name")
                if not (isinstance(name, str) and name.strip()):
                    continue

                name_clean = name.strip()
                if not name_clean.lower().startswith("parking:"):
                    continue

                # Extract spaces (digits) if present
                match = re.search(r"\b(\d+)\b", name_clean)
                if match:
                    parking_spaces = int(match.group(1)) 
                else:
                    parking_spaces = None

                return {
                    "has_parking": True,
                    "spaces": parking_spaces,
                    "label": name_clean,
                }

    return {"has_parking": False, "spaces": None, "label": None}
