# This file initally calls fetch__html to get the HTML content of the page, then calls all the individual parsing functions to extract the relevant information. 
# Finally...

import json
from pathlib import Path

from fetch_html import fetch_html
from parse_description_from_html import parse_description_from_html
from parse_image_urls_from_html import parse_image_urls_from_html
from parse_parking_from_html import parse_parking_from_html
from parse_property_type_from_html import parse_property_type_from_html
from parse_property_details_from_html import parse_property_details_from_html
from parse_sqft_from_html import parse_sqft_from_html
# Missing Realtor info parsing for now, will add later when we have a better idea of the structure of the HTML and the data we want to extract from it.


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = BASE_DIR / "Ottawa" / "ottawa_selected.json"
OUTPUT_PATH = INPUT_PATH


def main(input_path: Path | str = INPUT_PATH, output_path: Path | str = OUTPUT_PATH):
    base_url = "https://www.redfin.ca"

    # Open the JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        properties = json.load(file)

    # Determine total count for progress output
    total = len(properties) # Will change this logic later

    index = 0
    for property in properties:
        print(f"Processing property {index + 1}/{total} (ID: {property.get('propertyId')})")
        index += 1

        url = property.get("url")
        
        if not url:
            print("No URL found for property, skipping.")
            continue

        full_url = base_url + url

        html_content = fetch_html(full_url)

        # Parse the data and update the property dict
        property['parsed_description'] = parse_description_from_html(html_content)
        property['parsed_image_urls'] = parse_image_urls_from_html(html_content)
        property['parsed_parking'] = parse_parking_from_html(html_content)
        property['parsed_property_type'] = parse_property_type_from_html(html_content)
        property['parsed_property_details'] = parse_property_details_from_html(html_content)
        property['parsed_sqft'] = parse_sqft_from_html(html_content)

    # Save the updated properties back to the JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(properties, file, indent=2)

    print(f"Updated {output_path} with parsed data.")

if __name__ == "__main__":
    main()

    