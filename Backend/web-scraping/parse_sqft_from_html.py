from fetch_html import fetch_html
import json
from bs4 import BeautifulSoup
import re

def parse_sqft_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue
        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue

        data_objects = walk(data)
        for data_obj in data_objects:
            floor_size = data_obj.get("floorSize")
            if isinstance(floor_size, dict):
                square_feet = normalize(floor_size.get("value"))
                if square_feet:
                    return square_feet
            else:
                square_feet = normalize(floor_size)
                if square_feet:
                    return square_feet
                
            keys = ["livingArea", "areaServed", "area", "size"]
            for key in keys:
                square_feet = normalize(data_obj.get(key))
                if square_feet:
                    return square_feet


    for script in soup.find_all("script", attrs={"type": "application/json"}):
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue
        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue

        data_objects = walk(data)
        for data_obj in data_objects:
            options = ["sqft", "sqFt", "sqftTotal", "livingArea", "livingAreaValue", "finishedSqFt",
                       "finishedSqft", "aboveGradeFinishedArea", "homeSize", "areaValue", "totalSqFt", "floorSize"]
            for key in options:
                if key in data_obj:
                    square_feet = normalize(data_obj.get(key))
                    if square_feet:
                        return square_feet


    text = soup.get_text(" ", strip=True)
    match = re.search(r"(\d[\d,]*)\s*(sq\.?\s*ft|sqft|square\s*feet)\b", text, flags=re.I)
    if match:
        return int(match.group(1).replace(",", ""))

    return None


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


def normalize(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        normalized = int(value)
        if normalized > 0:
            return normalized
        else:
            return None
        
    if isinstance(value, str):
        match = re.search(r"(\d[\d,]*)", value)
        if not match:
            return None
        normalized = int(match.group(1).replace(",", ""))
        if normalized > 0:
            return normalized
        else:
            return None
    return None