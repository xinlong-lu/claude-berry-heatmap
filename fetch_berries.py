"""
fetch_berries.py
----------------
Fetches wild berry sighting data from the iNaturalist API
and saves it as berries.json for the map to read.

Run this script whenever you want to refresh the data:
    python3 fetch_berries.py

Requirements:
    pip3 install requests

NOTE: iNaturalist is a crowd-sourced database. All sightings
are user-submitted and verified by the community ("research grade"),
but location accuracy depends on the observer.
"""

import requests
import json

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

# Verified iNaturalist taxon IDs for US wild berry species
BERRY_SPECIES = {
    "Blueberry":    55882,   # Vaccinium corymbosum (Highbush Blueberry)
    "Blackberry":   61358,   # Rubus allegheniensis (Common Blackberry)
    "Raspberry":    55906,   # Rubus idaeus (Red Raspberry)
    "Strawberry":   55777,   # Fragaria virginiana (Wild Strawberry)
    "Elderberry":   56041,   # Sambucus canadensis (American Elderberry)
    "Huckleberry":  55889,   # Vaccinium membranaceum (Mountain Huckleberry)
    "Serviceberry": 47732,   # Amelanchier (Serviceberry genus)
    "Gooseberry":   55911,   # Ribes uva-crispa (Gooseberry)
}

RESULTS_PER_SPECIES = 150

# Strict US bounding box
US_BOUNDS = {
    "nelat":  49.4,
    "nelng": -66.9,
    "swlat":  24.4,
    "swlng": -124.8,
}

# ─── FETCH FUNCTION ───────────────────────────────────────────────────────────

def fetch_sightings(name, taxon_id):
    print(f"Fetching {name} (taxon {taxon_id})...")

    url = "https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_id":      taxon_id,
        "quality_grade": "research",
        "geo":           True,
        "per_page":      RESULTS_PER_SPECIES,
        "order":         "desc",
        "order_by":      "observed_on",
        "nelat":  US_BOUNDS["nelat"],
        "nelng":  US_BOUNDS["nelng"],
        "swlat":  US_BOUNDS["swlat"],
        "swlng":  US_BOUNDS["swlng"],
    }

    try:
        response = requests.get(url, params=params, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"  Network error for {name}: {e}")
        return []

    if response.status_code != 200:
        print(f"  Error fetching {name}: HTTP {response.status_code}")
        return []

    data = response.json()
    sightings = []

    for obs in data.get("results", []):
        coords = obs.get("location")
        if not coords:
            continue

        lat, lng = map(float, coords.split(","))

        if not (US_BOUNDS["swlat"] <= lat <= US_BOUNDS["nelat"] and
                US_BOUNDS["swlng"] <= lng <= US_BOUNDS["nelng"]):
            continue

        taxon_name = obs.get("taxon", {}).get("name", "")

        sightings.append({
            "name":       name,
            "scientific": taxon_name,
            "lat":        lat,
            "lng":        lng,
            "date":       obs.get("observed_on", "Unknown"),
            "place":      obs.get("place_guess", "Unknown location"),
            "photo": (
                obs["photos"][0]["url"].replace("square", "medium")
                if obs.get("photos") else None
            ),
            "url": f"https://www.inaturalist.org/observations/{obs['id']}",
        })

    print(f"  {len(sightings)} verified US sightings for {name}")
    return sightings


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    all_sightings = []

    for name, taxon_id in BERRY_SPECIES.items():
        sightings = fetch_sightings(name, taxon_id)
        all_sightings.extend(sightings)

    with open("berries.json", "w") as f:
        json.dump(all_sightings, f, indent=2)

    print(f"\nDone! Saved {len(all_sightings)} total US sightings to berries.json")

if __name__ == "__main__":
    main()
