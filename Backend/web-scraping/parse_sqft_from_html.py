from fetch_html import fetch_html
import json
from bs4 import BeautifulSoup
import re

def parse_sqft_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = s.string or s.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        objs = walk(data)
        for obj in objs:
            fs = obj.get("floorSize")
            if isinstance(fs, dict):
                n = normalize(fs.get("value"))
                if n:
                    return n
            else:
                n = normalize(fs)
                if n:
                    return n
                
            keys = ["livingArea", "areaServed", "area", "size"]
            for key in keys:
                n = normalize(obj.get(key))
                if n:
                    return n


    for s in soup.find_all("script", attrs={"type": "application/json"}):
        raw = s.string or s.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        objs = walk(data)
        for obj in objs:
            options = ["sqft", "sqFt", "sqftTotal", "livingArea", "livingAreaValue", "finishedSqFt",
                       "finishedSqft", "aboveGradeFinishedArea", "homeSize", "areaValue", "totalSqFt", "floorSize"]
            for key in options:
                if key in obj:
                    n = normalize(obj.get(key))
                    if n:
                        return n


    text = soup.get_text(" ", strip=True)
    m = re.search(r"(\d[\d,]*)\s*(sq\.?\s*ft|sqft|square\s*feet)\b", text, flags=re.I)
    if m:
        return int(m.group(1).replace(",", ""))

    return None


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


def normalize(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        n = int(x)
        if n > 0:
            return n
        else:
            return None
        
    if isinstance(x, str):
        m = re.search(r"(\d[\d,]*)", x)
        if not m:
            return None
        n = int(m.group(1).replace(",", ""))
        if n > 0:
            return n
        else:
            return None
    return None