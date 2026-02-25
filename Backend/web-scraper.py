import os
import re
import sys
import json
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://www.redfin.ca/on/ottawa/2083-Breezewood-St-K4A-4R7/home/149567261"


def fetch_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-CA,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def parse_description_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    lines = text.split("\n")
    cleaned_lines = []
    for ln in lines:
        stripped_line = ln.strip()
        if stripped_line:  
            cleaned_lines.append(stripped_line)
    lines = cleaned_lines

    start_idx = None

    start_idx = None
    i = 0
    while i < len(lines):
        lower_line = lines[i].lower()
        if lower_line == "about this home" or "about this home" in lower_line:
            start_idx = i + 1 
            break
        i += 1

    if start_idx is None:
        return ""

    end_idx = len(lines)

    for j in range(start_idx, len(lines)):
        lower_line = lines[j].lower()
        if lower_line in {
            "show more",
            "see this home in person",
            "property details",
            "around this home",
            "sale and tax history",
        } or lower_line.startswith("summary of"):
            end_idx = j
            break

    description = " ".join(lines[start_idx:end_idx])
    
    description = re.sub(r"\s+", " ", description).strip()
    description = description.replace(" * ", " ").replace("*", "").strip()
    return description


def parse_image_urls_from_html(html):
    urls = re.findall(r"https://ssl\.cdn-redfin\.com/photo/[^\s\"'>]+?\.jpg", html)

    seen = set()
    unique = []
    
    for u in urls:
        u = u.rstrip("),")
        if u not in seen:
            seen.add(u)
            unique.append(u)

    big = []

    for u in unique:
        if "/bigphoto/" in u:
            big.append(u)

    if len(big) > 0:
        rest = []

        for u in unique:
            if u not in big:
                rest.append(u)

        return big + rest

    return unique


def parse_sqft_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    ## Understand the Regex syntax
    pattern = re.compile(
        r"(?<!\d)"
        r"(\d{1,2}(?:[^\d]{0,6}\d{3})+|\d{3,5})"
        r"\s*(?:sq\.?\s*ft|sqft)"
        r"(?!\d)",
        re.IGNORECASE,
    )

    matches = pattern.findall(text)

    sqft_values = []
    for m in matches:
        cleaned = re.sub(r"[^\d]", "", m)
        if cleaned.isdigit():
            v = int(cleaned)
            if 200 <= v <= 20000:
                sqft_values.append(v)

    return max(sqft_values) if sqft_values else None



def parse_property_type_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    for i in ["townhouse", "row house", "detached", "semi-detached", "condo", "condominium", 
              "apartment", "stacked", "duplex", "triplex", "fourplex", "mobile", "manufactured",]:
        if i in text:
            return i.title()
    return None




## Realtor Stuff
def _iter_stingray_text_blobs(html: str):
    """
    The HTML contains cached API responses like:
      "text":"{}&&{\"version\":...\"payload\":{...}}"
    That "text" value is a JSON string, so quotes are escaped.

    This extracts each raw JSON-string value and decodes it.
    """
    for m in re.finditer(r'"text":"((?:\\.|[^"\\])*)"', html):
        raw = m.group(1)
        try:
            decoded = json.loads(f'"{raw}"')
        except Exception:
            continue
        yield decoded


def _extract_payload_json(decoded_text: str) -> dict | None:
    """
    decoded_text often looks like:
      {}&&{"version":...,"payload":{...}}
    We parse the JSON after the &&.
    """
    if "&&" not in decoded_text:
        return None
    _, after = decoded_text.split("&&", 1)
    after = after.strip()
    if not after.startswith("{"):
        return None
    try:
        return json.loads(after)
    except Exception:
        return None


def _collect_agents(obj, out: list[dict]) -> None:
    """
    Recursively walk payload dict/list and collect dicts that look like agents.
    """
    if isinstance(obj, dict):
        name = obj.get("fullName") or obj.get("name") or obj.get("agentDisplayName")
        brokerage = obj.get("brokerageName")
        phone = obj.get("phoneNumber") or obj.get("clientDisplayablePhoneNumber") or obj.get("phoneUrl")
        profile = obj.get("profileUrl") or obj.get("agentProfileUrl")

        if isinstance(name, str) and name.strip():
            agent = {}
            for k in [
                "fullName", "name", "firstName", "lastName",
                "brokerageName", "jobTitle", "teamName",
                "licenseNumber", "phoneNumber", "clientDisplayablePhoneNumber",
                "phoneUrl", "profileUrl",
                "photoUrl", "photoUrl74x110", "photoUrl120x120",
                "photoUrl150x150", "photoUrl270x360", "photoUrl500x500",
                "quote", "averageRating", "averageRatingForCustomerDisplay",
                "numReviews", "totalDealsInPastYear", "businessMarket",
                "officeCity", "officeState",
                "agentId", "agentFirstName", "agentDisplayName", "agentProfileUrl",
                "imgSrc", "dealCount", "hasPartnerSash", "isPartnerAgent",
            ]:
                if k in obj:
                    agent[k] = obj.get(k)
            if brokerage or phone or profile or ("licenseNumber" in agent) or ("quote" in agent):
                out.append(agent)

        for v in obj.values():
            _collect_agents(v, out)

    elif isinstance(obj, list):
        for item in obj:
            _collect_agents(item, out)


def parse_realtors_from_html(html: str) -> list[dict]:
    """
    Returns a list of agent dicts found in embedded stingray payloads.
    Dedupes by (fullName/name + brokerage + phone).
    """
    candidates: list[dict] = []

    for decoded in _iter_stingray_text_blobs(html):
        payload_obj = _extract_payload_json(decoded)
        if not payload_obj:
            continue
        _collect_agents(payload_obj, candidates)

    # Deduplicate
    seen = set()
    uniq = []
    for a in candidates:
        n = (a.get("fullName") or a.get("name") or a.get("agentDisplayName") or "").strip()
        b = (a.get("brokerageName") or "").strip()
        p = (a.get("clientDisplayablePhoneNumber") or a.get("phoneNumber") or a.get("phoneUrl") or "").strip()
        key = (n.lower(), b.lower(), p)
        if n and key not in seen:
            seen.add(key)
            uniq.append(a)

    return uniq


def pick_primary_realtor(agents: list[dict]) -> dict:
    """
    Heuristic: pick the 'most complete' agent (often has quote + phone + license).
    """
    def score(a: dict) -> int:
        s = 0
        for k in ["fullName", "name", "brokerageName", "clientDisplayablePhoneNumber", "phoneNumber", "licenseNumber", "quote", "profileUrl", "photoUrl150x150"]:
            if a.get(k):
                s += 1
        return s

    if not agents:
        return {}
    return max(agents, key=score)




def scrape_redfin_listing(url: str) -> dict:
    html = fetch_html(url)

    agents = parse_realtors_from_html(html)
    primary = pick_primary_realtor(agents)

    return {
        "url": url,
        "description": parse_description_from_html(html),
        "sqft": parse_sqft_from_html(html),
        "property_type": parse_property_type_from_html(html),
        "realtors": agents,          
        "primary_realtor": primary,  
        "image_urls": parse_image_urls_from_html(html),
    }


data = scrape_redfin_listing(DEFAULT_URL)

print("\nPROPERTY TYPE")
print(data["property_type"])

print("\nSQFT")
print(data["sqft"])

print("\nPRIMARY REALTOR")
print(json.dumps(data["primary_realtor"]))


print("\nALL REALTORS FOUND")
realtors = data["realtors"]
count = len(realtors)
print("Count:", count)

i = 0
for a in realtors:
    name = a.get("fullName") or a.get("name") or a.get("agentDisplayName")
    brokerage = a.get("brokerageName")
    phone = (a.get("clientDisplayablePhoneNumber") or a.get("phoneNumber") or a.get("phoneUrl"))

    index = str(i)

    print(index + ". " + str(name) + " | " + str(brokerage) + " | " + str(phone))

    i += 1 

print("\nDESCRIPTION")
print(data["description"])

print("\nIMAGE URLS")
print(f"Found {len(data['image_urls'])} images:")
for u in data["image_urls"]:
    print(u)
