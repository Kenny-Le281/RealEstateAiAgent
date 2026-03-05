from __future__ import annotations
from fetch_html import fetch_html
import json
from bs4 import BeautifulSoup
import re



def parse_parking_from_html(html):

    soup = BeautifulSoup(html, "html.parser")

    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = s.string or s.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue


        if isinstance(data, list):
            objs = data
        else:
            objs = [data]
             
        for obj in objs:
            if not isinstance(obj, dict):
                continue

            main = obj.get("mainEntity")
            if not isinstance(main, dict):
                continue

            features = main.get("amenityFeature")
            if not isinstance(feature, list):
                continue

            for feature in features:
                if not isinstance(feature, dict):
                    continue
                name = feature.get("name")
                if not (isinstance(name, str) and name.strip()):
                    continue

                name_clean = name.strip()
                if not name_clean.lower().startswith("parking:"):
                    continue

                # Extract spaces (digits) if present
                m = re.search(r"\b(\d+)\b", name_clean)
                if m:
                    spaces = int(m.group(1)) 
                else:
                    spaces = None

                return {
                    "has_parking": True,
                    "spaces": spaces,
                    "label": name_clean,
                }

    return {"has_parking": False, "spaces": None, "label": None}
