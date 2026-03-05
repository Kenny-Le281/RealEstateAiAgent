import requests

url = "https://redfin-canada.p.rapidapi.com/properties/search-sale"

querystring = {"regionId":"33_2187"}

headers = {
	"x-rapidapi-key": "badc323e5bmsh826ec0db0007e04p1cff2ajsn459a448a40c0",
	"x-rapidapi-host": "redfin-canada.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())