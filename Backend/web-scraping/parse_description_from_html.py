from bs4 import BeautifulSoup
import re

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
