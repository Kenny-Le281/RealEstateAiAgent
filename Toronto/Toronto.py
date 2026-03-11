import http.client
import json

conn = http.client.HTTPSConnection("redfin-canada.p.rapidapi.com")

headers = {
    "x-rapidapi-key": "190a6ed5b8mshbe58323ae965f75p10774djsnde2c1a93eb6b",
    "x-rapidapi-host": "redfin-canada.p.rapidapi.com"
}

conn.request(
    "GET",
    "/properties/search-sale?regionId=33_2924",
    headers=headers
)

res = conn.getresponse()
data = res.read()

# Convert to JSON
parsed = json.loads(data.decode("utf-8"))

# Pretty print to terminal
print(json.dumps(parsed, indent=4))

# Save to file
with open("output.json", "w") as f:
    json.dump(parsed, f, indent=4)

print("Saved to output.json")
