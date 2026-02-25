from bs4 import BeautifulSoup

def parse_property_type_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    for i in ["townhouse", "row house", "detached", "semi-detached", "condo", "condominium", 
              "apartment", "stacked", "duplex", "triplex", "fourplex", "mobile", "manufactured",]:
        if i in text:
            return i.title()
    return None