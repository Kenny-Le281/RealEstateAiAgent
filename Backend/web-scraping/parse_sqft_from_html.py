from bs4 import BeautifulSoup
import re

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