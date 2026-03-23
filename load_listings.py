from dotenv import load_dotenv
import json
import os
import psycopg2


load_dotenv()

# 1. Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres.uajcmeseaipjrplvndrp",
    password=os.getenv("SUPABASE_DB_PASSWORD"),
    host="aws-1-ca-central-1.pooler.supabase.com",
    port=5432,
    sslmode="require"
)


conn.autocommit = True
cur = conn.cursor()

def normalize_listing(raw):
    return {
        "listing_id": raw.get("listingId"),
        "property_id": raw.get("propertyId"),
        "address_name": raw.get("address-name"),
        "city": raw.get("city"),
        "state": raw.get("state"),
        "zip": raw.get("zip"),
        "location": raw.get("location"),
        "url": raw.get("url"),
        "property_type": raw.get("propertyType"),
        "beds": raw.get("beds"),
        "baths": raw.get("baths"),
        "price": int(raw["price"]) if raw.get("price") else None,
        "days_on_market": raw.get("daysOnMarket"),
        "time_on_redfin": raw.get("timeOnRedfin"),
        "listing_added_date": raw.get("listingAddedDate"),
        "hoa_amount": int(raw["hoa-amount"]) if raw.get("hoa-amount") else None,
        "brokers": json.dumps(raw.get("brokers")),
        "last_sold_date": raw.get("lastSoldDate"),
        "partial_baths": raw.get("partialBaths"),
        "full_baths": raw.get("fullBaths"),
        "total_baths": raw.get("totalBaths"),
        "latitude": raw.get("latitude"),
        "longitude": raw.get("longitude"),
        "raw": json.dumps(raw)
    }


def upsert_listing(listing):
    sql = """
    INSERT INTO listings (
        listing_id, property_id, address_name, city, state, zip, location,
        url, property_type, beds, baths, price, days_on_market, time_on_redfin,
        listing_added_date, hoa_amount, brokers, last_sold_date, partial_baths,
        full_baths, total_baths, latitude, longitude, raw
    )
    VALUES (
        %(listing_id)s, %(property_id)s, %(address_name)s, %(city)s, %(state)s, %(zip)s, %(location)s,
        %(url)s, %(property_type)s, %(beds)s, %(baths)s, %(price)s, %(days_on_market)s, %(time_on_redfin)s,
        %(listing_added_date)s, %(hoa_amount)s, %(brokers)s, %(last_sold_date)s, %(partial_baths)s,
        %(full_baths)s, %(total_baths)s, %(latitude)s, %(longitude)s, %(raw)s
    )
    ON CONFLICT (listing_id)
    DO UPDATE SET
        property_id = EXCLUDED.property_id,
        address_name = EXCLUDED.address_name,
        city = EXCLUDED.city,
        state = EXCLUDED.state,
        zip = EXCLUDED.zip,
        location = EXCLUDED.location,
        url = EXCLUDED.url,
        property_type = EXCLUDED.property_type,
        beds = EXCLUDED.beds,
        baths = EXCLUDED.baths,
        price = EXCLUDED.price,
        days_on_market = EXCLUDED.days_on_market,
        time_on_redfin = EXCLUDED.time_on_redfin,
        listing_added_date = EXCLUDED.listing_added_date,
        hoa_amount = EXCLUDED.hoa_amount,
        brokers = EXCLUDED.brokers,
        last_sold_date = EXCLUDED.last_sold_date,
        partial_baths = EXCLUDED.partial_baths,
        full_baths = EXCLUDED.full_baths,
        total_baths = EXCLUDED.total_baths,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        raw = EXCLUDED.raw,
        last_updated = NOW();
    """

    cur.execute(sql, listing)

def load_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # If the file contains a single object, wrap it in a list
    if isinstance(data, dict):
        data = [data]

    for raw in data:
        listing = normalize_listing(raw)
        if not listing["listing_id"]:
            print("Skipping listing without listing_id:", raw)
            continue
        upsert_listing(listing)

if __name__ == "__main__":
    load_from_file("Ottawa/ottawa_selected.json")
    cur.close()
    conn.close()
