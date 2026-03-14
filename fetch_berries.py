"""
fetch_berries.py
----------------
Fetches wild berry sighting data from the iNaturalist API
and saves it as berries.json for the map to read.

Run this script whenever you want to refresh the data:
    python fetch_berries.py

Requirements:
    pip install requests
"""

import requests
import json

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

# Add or remove berry species here using their iNaturalist taxon IDs
# You can find taxon IDs by searching https://www.inaturalist.org/taxa
BERRY_SPECIES = {
    "Strawberry":       57423,
    "Blueberry":        52833,
    "Blackberry":       47153,
    "Raspberry":        61699,
    "Elderberry":       55512,
    "Serviceberry":     55934,
    "Gooseberry":       76489,
    "Huckleberry":      53912,
}

# How many sightings to fetch per species (max 200 per API call)
RESULTS_PER_SPECIES = 100

# Only fetch observations from the US
PLACE_ID = 1  # iNaturalist place ID for United States

# ─── FETCH FUNCTION ───────────────────────────────────────────────────────────

def fetch_sightings(name, taxon_id):
    """Fetch verified sightings for a single berry species."""
    print(f"Fetching {name} sightings...")

    url = "https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_id": taxon_id,
        "place_id": PLACE_ID,
        "quality_grade": "research",   # only verified sightings
        "geo": True,                   # must have coordinates
        "per_page": RESULTS_PER_SPECIES,
        "order": "desc",
        "order_by": "observed_on",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"  Error fetching {name}: HTTP {response.status_code}")
        return []

    data = response.json()
    sightings = []

    for obs in data.get("results", []):
        coords = obs.get("location")
        if not coords:
            continue

        lat, lng = coords.split(",")

        sightings.append({
            "name": name,
            "lat": float(lat),
            "lng": float(lng),
            "date": obs.get("observed_on", "Unknown"),
            "place": obs.get("place_guess", "Unknown location"),
            "photo": (
                obs["photos"][0]["url"].replace("square", "medium")
                if obs.get("photos") else None
            ),
            "url": f"https://www.inaturalist.org/observations/{obs['id']}",
        })

    print(f"  Found {len(sightings)} sightings for {name}")
    return sightings


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    all_sightings = []

    for name, taxon_id in BERRY_SPECIES.items():
        sightings = fetch_sightings(name, taxon_id)
        all_sightings.extend(sightings)

    # Save to berries.json
    with open("berries.json", "w") as f:
        json.dump(all_sightings, f, indent=2)

    print(f"\nDone! Saved {len(all_sightings)} total sightings to berries.json")


if __name__ == "__main__":
    main()
