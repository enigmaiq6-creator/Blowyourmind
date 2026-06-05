"""
Analyzes narration text for geopolitical keywords and generates
GeopoliticalData for the Remotion overlay.

Detects:
- Country names → extruded countries with flags
- Distance patterns → 3D distance arrows
- Years → year transitions
- Treaties/alliances → alliance icons
- Conflicts/tensions → conflict icons
- Colonial/imperial → colonial icons
- Boundaries/frontiers → boundary lines
- Historical territories → historical overlays
"""

import re
from typing import Any

# ─── Country database (name → iso3 + approximate center) ───

COUNTRIES: dict[str, dict[str, Any]] = {
    "united states": {"iso3": "USA", "lat": 39.8, "lng": -98.6},
    "usa": {"iso3": "USA", "lat": 39.8, "lng": -98.6},
    "america": {"iso3": "USA", "lat": 39.8, "lng": -98.6},
    "canada": {"iso3": "CAN", "lat": 56.1, "lng": -106.3},
    "mexico": {"iso3": "MEX", "lat": 23.6, "lng": -102.5},
    "brazil": {"iso3": "BRA", "lat": -14.2, "lng": -51.9},
    "brasil": {"iso3": "BRA", "lat": -14.2, "lng": -51.9},
    "argentina": {"iso3": "ARG", "lat": -38.4, "lng": -63.6},
    "colombia": {"iso3": "COL", "lat": 4.6, "lng": -74.3},
    "venezuela": {"iso3": "VEN", "lat": 7.0, "lng": -65.0},
    "peru": {"iso3": "PER", "lat": -9.2, "lng": -74.0},
    "chile": {"iso3": "CHL", "lat": -35.7, "lng": -71.5},
    "ecuador": {"iso3": "ECU", "lat": -1.8, "lng": -78.2},
    "bolivia": {"iso3": "BOL", "lat": -16.7, "lng": -64.7},
    "paraguay": {"iso3": "PRY", "lat": -23.4, "lng": -58.4},
    "uruguay": {"iso3": "URY", "lat": -32.5, "lng": -55.8},
    "united kingdom": {"iso3": "GBR", "lat": 55.4, "lng": -3.4},
    "uk": {"iso3": "GBR", "lat": 55.4, "lng": -3.4},
    "britain": {"iso3": "GBR", "lat": 55.4, "lng": -3.4},
    "england": {"iso3": "GBR", "lat": 52.4, "lng": -1.2},
    "france": {"iso3": "FRA", "lat": 46.6, "lng": 2.2},
    "germany": {"iso3": "DEU", "lat": 51.2, "lng": 10.5},
    "spain": {"iso3": "ESP", "lat": 40.2, "lng": -3.7},
    "portugal": {"iso3": "PRT", "lat": 39.4, "lng": -8.2},
    "italy": {"iso3": "ITA", "lat": 41.9, "lng": 12.6},
    "netherlands": {"iso3": "NLD", "lat": 52.1, "lng": 5.3},
    "holland": {"iso3": "NLD", "lat": 52.1, "lng": 5.3},
    "belgium": {"iso3": "BEL", "lat": 50.5, "lng": 4.5},
    "switzerland": {"iso3": "CHE", "lat": 46.8, "lng": 8.2},
    "austria": {"iso3": "AUT", "lat": 47.5, "lng": 14.5},
    "poland": {"iso3": "POL", "lat": 52.1, "lng": 19.4},
    "sweden": {"iso3": "SWE", "lat": 62.0, "lng": 15.0},
    "norway": {"iso3": "NOR", "lat": 64.5, "lng": 12.5},
    "denmark": {"iso3": "DNK", "lat": 56.2, "lng": 10.2},
    "finland": {"iso3": "FIN", "lat": 64.5, "lng": 26.0},
    "russia": {"iso3": "RUS", "lat": 61.5, "lng": 105.0},
    "ukraine": {"iso3": "UKR", "lat": 49.0, "lng": 31.0},
    "turkey": {"iso3": "TUR", "lat": 39.0, "lng": 35.0},
    "greece": {"iso3": "GRC", "lat": 39.1, "lng": 21.8},
    "egypt": {"iso3": "EGY", "lat": 26.8, "lng": 30.8},
    "morocco": {"iso3": "MAR", "lat": 31.8, "lng": -7.0},
    "south africa": {"iso3": "ZAF", "lat": -30.6, "lng": 22.9},
    "nigeria": {"iso3": "NGA", "lat": 9.1, "lng": 8.7},
    "kenya": {"iso3": "KEN", "lat": -0.0, "lng": 37.9},
    "ethiopia": {"iso3": "ETH", "lat": 9.1, "lng": 40.5},
    "india": {"iso3": "IND", "lat": 20.6, "lng": 78.9},
    "china": {"iso3": "CHN", "lat": 35.9, "lng": 104.2},
    "japan": {"iso3": "JPN", "lat": 36.2, "lng": 138.3},
    "south korea": {"iso3": "KOR", "lat": 36.0, "lng": 128.0},
    "north korea": {"iso3": "PRK", "lat": 40.0, "lng": 127.5},
    "australia": {"iso3": "AUS", "lat": -25.3, "lng": 134.0},
    "new zealand": {"iso3": "NZL", "lat": -41.3, "lng": 174.0},
    "indonesia": {"iso3": "IDN", "lat": -0.8, "lng": 117.8},
    "malaysia": {"iso3": "MYS", "lat": 4.2, "lng": 108.0},
    "thailand": {"iso3": "THA", "lat": 15.9, "lng": 101.0},
    "vietnam": {"iso3": "VNM", "lat": 16.0, "lng": 108.0},
    "philippines": {"iso3": "PHL", "lat": 12.9, "lng": 121.8},
    "iraq": {"iso3": "IRQ", "lat": 33.0, "lng": 44.0},
    "iran": {"iso3": "IRN", "lat": 32.0, "lng": 53.7},
    "syria": {"iso3": "SYR", "lat": 34.8, "lng": 39.0},
    "israel": {"iso3": "ISR", "lat": 31.0, "lng": 34.9},
    "palestine": {"iso3": "PSE", "lat": 31.9, "lng": 35.2},
    "saudi arabia": {"iso3": "SAU", "lat": 24.0, "lng": 45.0},
    "united arab emirates": {"iso3": "ARE", "lat": 24.0, "lng": 54.0},
    "uae": {"iso3": "ARE", "lat": 24.0, "lng": 54.0},
    "qatar": {"iso3": "QAT", "lat": 25.3, "lng": 51.2},
    "cuba": {"iso3": "CUB", "lat": 21.5, "lng": -79.5},
    "haiti": {"iso3": "HTI", "lat": 19.0, "lng": -72.4},
    "dominican republic": {"iso3": "DOM", "lat": 19.0, "lng": -70.7},
    "puerto rico": {"iso3": "PRI", "lat": 18.2, "lng": -66.4},
    "panama": {"iso3": "PAN", "lat": 8.6, "lng": -80.2},
    "costa rica": {"iso3": "CRI", "lat": 9.7, "lng": -84.0},
    "guatemala": {"iso3": "GTM", "lat": 15.8, "lng": -90.2},
    "honduras": {"iso3": "HND", "lat": 14.8, "lng": -86.8},
    "nicaragua": {"iso3": "NIC", "lat": 12.9, "lng": -85.0},
    "el salvador": {"iso3": "SLV", "lat": 13.8, "lng": -88.9},
    "bangladesh": {"iso3": "BGD", "lat": 23.7, "lng": 90.4},
    "pakistan": {"iso3": "PAK", "lat": 30.4, "lng": 69.3},
    "afghanistan": {"iso3": "AFG", "lat": 33.9, "lng": 67.7},
    "mongolia": {"iso3": "MNG", "lat": 46.9, "lng": 103.8},
    "kazakhstan": {"iso3": "KAZ", "lat": 48.0, "lng": 68.0},
    "congo": {"iso3": "COD", "lat": -2.9, "lng": 24.0},
    "angola": {"iso3": "AGO", "lat": -12.5, "lng": 18.5},
    "mozambique": {"iso3": "MOZ", "lat": -17.5, "lng": 35.5},
    "madagascar": {"iso3": "MDG", "lat": -19.4, "lng": 46.7},
    "sudan": {"iso3": "SDN", "lat": 15.6, "lng": 30.2},
    "libya": {"iso3": "LBY", "lat": 26.3, "lng": 17.2},
    "algeria": {"iso3": "DZA", "lat": 28.0, "lng": 3.0},
    "tunisia": {"iso3": "TUN", "lat": 34.0, "lng": 9.5},
    "romania": {"iso3": "ROU", "lat": 45.9, "lng": 25.0},
    "bulgaria": {"iso3": "BGR", "lat": 42.7, "lng": 25.5},
    "serbia": {"iso3": "SRB", "lat": 44.0, "lng": 21.0},
    "croatia": {"iso3": "HRV", "lat": 45.0, "lng": 15.5},
    "czech republic": {"iso3": "CZE", "lat": 49.7, "lng": 15.3},
    "czechia": {"iso3": "CZE", "lat": 49.7, "lng": 15.3},
    "hungary": {"iso3": "HUN", "lat": 47.2, "lng": 19.5},
    "slovakia": {"iso3": "SVK", "lat": 48.7, "lng": 19.5},
    "slovenia": {"iso3": "SVN", "lat": 46.1, "lng": 14.8},
    "lithuania": {"iso3": "LTU", "lat": 55.3, "lng": 24.0},
    "latvia": {"iso3": "LVA", "lat": 56.9, "lng": 24.6},
    "estonia": {"iso3": "EST", "lat": 58.6, "lng": 25.0},
    "ireland": {"iso3": "IRL", "lat": 53.1, "lng": -8.1},
    "iceland": {"iso3": "ISL", "lat": 64.9, "lng": -18.6},
    "cambodia": {"iso3": "KHM", "lat": 12.6, "lng": 104.9},
    "myanmar": {"iso3": "MMR", "lat": 21.9, "lng": 95.9},
    "burma": {"iso3": "MMR", "lat": 21.9, "lng": 95.9},
    "laos": {"iso3": "LAO", "lat": 19.9, "lng": 102.5},
    "taiwan": {"iso3": "TWN", "lat": 23.7, "lng": 121.0},
    "nepal": {"iso3": "NPL", "lat": 28.2, "lng": 84.0},
    "sri lanka": {"iso3": "LKA", "lat": 7.6, "lng": 80.7},
    "yemen": {"iso3": "YEM", "lat": 15.6, "lng": 48.5},
    "oman": {"iso3": "OMN", "lat": 21.0, "lng": 57.0},
    "kuwait": {"iso3": "KWT", "lat": 29.3, "lng": 47.7},
    "jordan": {"iso3": "JOR", "lat": 31.2, "lng": 36.8},
    "lebanon": {"iso3": "LBN", "lat": 33.9, "lng": 35.5},
    "ghana": {"iso3": "GHA", "lat": 7.9, "lng": -1.2},
    "ivory coast": {"iso3": "CIV", "lat": 7.5, "lng": -5.5},
    "cameroon": {"iso3": "CMR", "lat": 4.0, "lng": 12.5},
    "senegal": {"iso3": "SEN", "lat": 14.5, "lng": -14.5},
    "zimbabwe": {"iso3": "ZWE", "lat": -19.0, "lng": 29.5},
    "zambia": {"iso3": "ZMB", "lat": -14.5, "lng": 27.5},
    "tanzania": {"iso3": "TZA", "lat": -6.0, "lng": 35.0},
    "uganda": {"iso3": "UGA", "lat": 1.3, "lng": 32.4},
    "morocco": {"iso3": "MAR", "lat": 31.8, "lng": -7.0},
}


LOCATION_ALIASES: dict[str, str] = {
    "louisiana": "united states",
    "mississippi": "united states",
    "gulf coast": "united states",
    "atlantic coast": "united states",
    "pacific coast": "united states",
    "california": "united states",
    "florida": "united states",
    "alaska": "united states",
    "amazon": "brazil",
    "andes": "peru",
    "himalayas": "india",
    "sahara": "algeria",
    "mediterranean": "spain",
    "pacific islands": "indonesia",
    "caribbean": "cuba",
    "ganges": "india",
    "nile": "egypt",
    "danube": "romania",
    "patagonia": "argentina",
    "siberia": "russia",
    "scandinavia": "norway",
    "balkans": "greece",
    "middle east": "saudi arabia",
}

def _find_countries(text: str) -> list[dict[str, Any]]:
    """Find country mentions and location aliases in text."""
    found = []
    lower = text.lower()
    for name, data in COUNTRIES.items():
        if name in lower:
            found.append({"name": name.title(), "iso3": data["iso3"], "lat": data["lat"], "lng": data["lng"]})
    for alias, country in LOCATION_ALIASES.items():
        if alias in lower and country not in lower:
            data = COUNTRIES[country]
            found.append({"name": country.title(), "iso3": data["iso3"], "lat": data["lat"], "lng": data["lng"]})
    return found


def _find_year(text: str) -> int | None:
    """Find a 4-digit year (1500-2099) in text."""
    match = re.search(r'\b(1[5-9]\d{2}|20[0-2]\d{1})\b', text)
    if match:
        return int(match.group(0))
    return None


def _find_distance(text: str) -> str | None:
    """Find distance pattern like 'X km', 'X miles', 'X kilometers'."""
    match = re.search(r'(\d[\d,]*)\s*(km|kilometers|kilometres|miles)', text, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return None


def _has_keywords(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in keywords)


ALLIANCE_KW = ["treaty", "alliance", "agreement", "pact", "accord", "signed", "ally", "allies", "cooperation",
               "tratado", "alianza", "acuerdo", "pacto"]
CONFLICT_KW = ["war", "conflict", "dispute", "tension", "battle", "fight", "invasion", "attack",
               "guerra", "conflicto", "disputa", "tensión", "batalla"]
COLONIAL_KW = ["colony", "colonial", "empire", "imperial", "colonized", "colonization",
               "colonia", "colonial", "imperio", "colonizado"]
BOUNDARY_KW = ["border", "boundary", "frontier", "maritime", "territorial", "demarcation",
               "frontera", "limite", "límite", "marítimo"]
HISTORICAL_KW = ["former", "ancient", "historical", "old territory", "antiguo", "histórico"]


def analyze_narration(narration: str) -> dict[str, Any]:
    """
    Analyze narration text and return GeopoliticalData-compatible dict.
    """
    result: dict[str, Any] = {}

    # 1. Countries → extruded countries
    countries = _find_countries(narration)
    if countries:
        result["extrudedCountries"] = [
            {"name": c["name"], "iso3": c["iso3"]} for c in countries
        ]

    # 2. Distance → arrow (use first two countries, or offset from 1 country)
    dist = _find_distance(narration)
    if dist:
        from_lat, from_lng, to_lat, to_lng = 0, 0, 10, 10  # defaults
        if len(countries) >= 2:
            from_lat, from_lng = countries[0]["lat"], countries[0]["lng"]
            to_lat, to_lng = countries[1]["lat"], countries[1]["lng"]
        elif len(countries) == 1:
            from_lat, from_lng = countries[0]["lat"], countries[0]["lng"]
            to_lat, to_lng = from_lat + 10, from_lng + 10
        result["distanceArrows"] = [{
            "fromLat": from_lat,
            "fromLng": from_lng,
            "toLat": to_lat,
            "toLng": to_lng,
            "label": dist.upper(),
            "startMs": 0,
            "durationMs": 4000,
        }]

    # 3. Year → transition
    year = _find_year(narration)
    if year:
        result["yearTransitions"] = [{
            "year": year,
            "startMs": 500,
            "durationMs": 2000,
        }]

    # 4. Thematic icons
    icons = []
    if _has_keywords(narration, ALLIANCE_KW) and countries:
        icons.append({
            "type": "alliance",
            "lat": countries[0]["lat"],
            "lng": countries[0]["lng"],
            "label": "ALLIANCE",
            "startMs": 0,
        })
    if _has_keywords(narration, CONFLICT_KW) and countries:
        icons.append({
            "type": "conflict",
            "lat": countries[-1]["lat"] if countries else 0,
            "lng": countries[-1]["lng"] if countries else 0,
            "label": "CONFLICT",
            "startMs": 0,
        })
    if _has_keywords(narration, COLONIAL_KW) and countries:
        icons.append({
            "type": "colonial",
            "lat": countries[0]["lat"],
            "lng": countries[0]["lng"],
            "label": "COLONIAL",
            "startMs": 0,
        })
    if icons:
        result["thematicIcons"] = icons

    # 5. Boundary lines (boundary/coastline keywords + 1+ countries)
    if _has_keywords(narration, BOUNDARY_KW + ["coastline", "coast", "shore", "shoreline", "erosion", "disappear"]) and countries:
        c = countries[0]
        if len(countries) >= 2:
            waypoints = [
                {"lat": countries[0]["lat"], "lng": countries[0]["lng"]},
                {"lat": (countries[0]["lat"] + countries[1]["lat"]) / 2, "lng": (countries[0]["lng"] + countries[1]["lng"]) / 2},
                {"lat": countries[1]["lat"], "lng": countries[1]["lng"]},
            ]
        else:
            waypoints = [
                {"lat": c["lat"] - 5, "lng": c["lng"] - 5},
                {"lat": c["lat"] + 5, "lng": c["lng"] - 5},
                {"lat": c["lat"] + 5, "lng": c["lng"] + 5},
                {"lat": c["lat"] - 5, "lng": c["lng"] + 5},
            ]
        result["boundaryLines"] = [{
            "waypoints": waypoints,
            "colorA": "#FFD700",
            "colorB": "#000000",
            "startMs": 0,
            "durationMs": 4000,
        }]

    # 5b. Erosion/Coastline thematic icon
    if _has_keywords(narration, ["erosion", "coastline", "coast", "shore", "disappearing", "disappear", "sea level", "rising"]) and countries:
        c = countries[0]
        icons.append({
            "type": "erosion",
            "lat": c["lat"],
            "lng": c["lng"],
            "label": "EROSION",
            "startMs": 0,
        })

    # 6. Historical overlays
    if _has_keywords(narration, HISTORICAL_KW) and countries:
        result["historicalOverlays"] = [{
            "waypoints": [
                {"lat": c["lat"] - 5, "lng": c["lng"] - 5},
                {"lat": c["lat"] + 5, "lng": c["lng"] - 5},
                {"lat": c["lat"] + 5, "lng": c["lng"] + 5},
                {"lat": c["lat"] - 5, "lng": c["lng"] + 5},
            ],
            "color": "#D4A574",
            "opacity": 0.3,
            "label": f"HISTORICAL {countries[0]['name'].upper()}",
            "startMs": 0,
            "durationMs": 4000,
        } for c in countries[:1]]

    return result if result else {}
