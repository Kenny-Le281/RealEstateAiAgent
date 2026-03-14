import http.client
import json
import os

conn = http.client.HTTPSConnection("redfin-canada.p.rapidapi.com")

headers = {
    "x-rapidapi-key": "190a6ed5b8mshbe58323ae965f75p10774djsnde2c1a93eb6b",
    "x-rapidapi-host": "redfin-canada.p.rapidapi.com"
}

conn.request(
    "GET",
    "/properties/search-sale?regionId=33_2187",
    headers=headers
)

res = conn.getresponse()
data = res.read()

# Convert to JSON
parsed = json.loads(data.decode("utf-8"))

# Pretty print to terminal
print(json.dumps(parsed, indent=4))

# Ensure output directory exists (placed in the repo root)
output_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "Ottawa"))
os.makedirs(output_dir, exist_ok=True)

# Save to file
output_path = os.path.join(output_dir, "Ottawa.json")
with open(output_path, "w") as f:
    json.dump(parsed, f, indent=4)

print(f"Saved to {output_path}")
