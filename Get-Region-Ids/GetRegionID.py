import http.client
import json

API_HOST = "redfin-canada.p.rapidapi.com"
API_KEY = "190a6ed5b8mshbe58323ae965f75p10774djsnde2c1a93eb6b"

def get_region_ids(city_name):
    conn = http.client.HTTPSConnection(API_HOST)
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    path = f"/properties/auto-complete?query={city_name}"
    conn.request("GET", path, headers=headers)

    res = conn.getresponse()
    data = res.read()
    parsed = json.loads(data.decode("utf-8"))

    print("\nRAW RESPONSE:")
    print(json.dumps(parsed, indent=4))

    if parsed.get("data") is None:
        print("\n❌ API returned no data.")
        return

    # Find the "Places" section
    places_section = None
    for section in parsed["data"]:
        if section.get("name") == "Places":
            places_section = section
            break

    if not places_section:
        print("\n❌ No 'Places' section found.")
        return

    rows = places_section["rows"]

    print(f"\n=== Region IDs for '{city_name}' ===\n")
    for r in rows:
        name = r.get("name", "Unknown")
        region_id = r.get("id", "Unknown")
        print(f"{name} → {region_id}")


# Try it
get_region_ids("Ottawa")
