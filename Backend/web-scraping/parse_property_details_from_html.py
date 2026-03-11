from bs4 import BeautifulSoup

def parse_property_details_from_html(html):
    # Initialize the parser
    soup = BeautifulSoup(html, 'html.parser')
    
    # Locate the specific preview section by ID
    details_section = soup.find('div', id='propertyDetails-preview')
    
    details_dict = {}
    
    if details_section:
        # Find all list items with the class 'entryItem'
        details = details_section.find_all('li', class_='entryItem')
        
        for item in details:
            # Extract text and clean it up
            text = item.get_text(strip=True)
            
            # Split by the colon to separate Key: Value
            if ':' in text:
                parts = text.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                details_dict[key] = value
                
    return details_dict