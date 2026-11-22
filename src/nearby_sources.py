import math
from typing import Dict, List, Any, Optional

# Verified stationary and mobile point emission sources across Indian metros
KNOWN_POLLUTANT_SOURCES: List[Dict[str, Any]] = [
    # --- Delhi NCR ---
    {
        "id": "del-ghazipur",
        "name": "Ghazipur Landfill & Waste-to-Energy Cluster",
        "city": "Delhi",
        "category": "Landfill & Waste",
        "icon": "ph-fire",
        "color": "#8B5CF6",
        "lat": 28.6258,
        "lon": 77.3298,
        "key_pollutants": ["PM2.5", "PM10", "CO", "NH3", "Methane"],
        "severity": "Critical",
        "description": "Massive municipal waste mound with frequent spontaneous sub-surface smoldering and refuse processing."
    },
    {
        "id": "del-okhla",
        "name": "Okhla Industrial Estate (Phase I-III)",
        "city": "Delhi",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 28.5355,
        "lon": 77.2730,
        "key_pollutants": ["SO2", "NOx", "VOCs", "PM10"],
        "severity": "High",
        "description": "Extensive cluster of metal fabrication, polymer molding, printing presses, and electroplating units."
    },
    {
        "id": "del-wazirpur",
        "name": "Wazirpur Steel Rolling Industrial Area",
        "city": "Delhi",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 28.6980,
        "lon": 77.1650,
        "key_pollutants": ["PM2.5", "SO2", "NOx", "Acid Mists"],
        "severity": "Critical",
        "description": "Steel rolling mills, furnace annealing, and chemical pickling plants generating particulate and acidic vapors."
    },
    {
        "id": "del-anandvihar",
        "name": "Anand Vihar Interstate Transit Terminal",
        "city": "Delhi",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 28.6502,
        "lon": 77.3150,
        "key_pollutants": ["NO2", "NOx", "CO", "PM2.5"],
        "severity": "Critical",
        "description": "One of Northern India's densest interstate diesel bus terminals and railway freight convergence points."
    },
    {
        "id": "del-bawana",
        "name": "Bawana Industrial Complex",
        "city": "Delhi",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 28.7950,
        "lon": 77.0370,
        "key_pollutants": ["Benzene", "Toluene", "PM10", "CO"],
        "severity": "High",
        "description": "Large-scale industrial area featuring plastic recycling, rubber manufacturing, and resin production."
    },
    {
        "id": "del-noida-exp",
        "name": "Noida - Greater Noida Expressway Corridor",
        "city": "Delhi",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 28.5100,
        "lon": 77.3850,
        "key_pollutants": ["NO2", "CO", "PM2.5"],
        "severity": "Elevated",
        "description": "High-speed multi-lane transit artery with heavy daily commuter density and overnight commercial freight."
    },

    # --- Mumbai MMR ---
    {
        "id": "mum-deonar",
        "name": "Deonar Dumping Ground",
        "city": "Mumbai",
        "category": "Landfill & Waste",
        "icon": "ph-fire",
        "color": "#8B5CF6",
        "lat": 19.0728,
        "lon": 72.9342,
        "key_pollutants": ["PM2.5", "CO", "NH3", "VOCs"],
        "severity": "Critical",
        "description": "Mumbai's largest historical dumpsite; prone to smoldering fires generating dense particulate plumes."
    },
    {
        "id": "mum-mahul",
        "name": "Mahul - Trombay Petrochemical & Refinery Belt",
        "city": "Mumbai",
        "category": "Petrochemical & Power",
        "icon": "ph-fire",
        "color": "#F59E0B",
        "lat": 19.0135,
        "lon": 72.9050,
        "key_pollutants": ["SO2", "Benzene", "Toluene", "NOx"],
        "severity": "Critical",
        "description": "Concentration of BPCL/HPCL refineries, fertilizer complexes, and petrochemical storage depots."
    },
    {
        "id": "mum-sakinaka",
        "name": "Andheri-Kurla Road & Saki Naka Junction",
        "city": "Mumbai",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 19.1020,
        "lon": 72.8870,
        "key_pollutants": ["NO2", "CO", "PM2.5"],
        "severity": "High",
        "description": "Severe commercial bottleneck carrying mixed heavy vehicles, auto-rickshaws, and airport corridor traffic."
    },
    {
        "id": "mum-ttc",
        "name": "Thane-Belapur Trans-Thana Creek (TTC) Zone",
        "city": "Mumbai",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 19.1550,
        "lon": 73.0150,
        "key_pollutants": ["SO2", "NOx", "VOCs", "PM10"],
        "severity": "High",
        "description": "Major chemical manufacturing belt with bulk pharmaceutical, specialty dye, and textile processing units."
    },

    # --- Bengaluru ---
    {
        "id": "blr-peenya",
        "name": "Peenya Industrial Area",
        "city": "Bengaluru",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 13.0285,
        "lon": 77.5190,
        "key_pollutants": ["PM10", "PM2.5", "SO2", "VOCs"],
        "severity": "Critical",
        "description": "One of South Asia's largest industrial estates with thousands of precision tooling, casting, and chemical units."
    },
    {
        "id": "blr-silkboard",
        "name": "Silk Board - Outer Ring Road Transit Junction",
        "city": "Bengaluru",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 12.9176,
        "lon": 77.6238,
        "key_pollutants": ["NO2", "NOx", "CO", "PM2.5"],
        "severity": "Critical",
        "description": "Major traffic bottleneck with continuous stop-and-go congestion and diesel bus exhaust emissions."
    },
    {
        "id": "blr-whitefield",
        "name": "Whitefield Export & Metro Construction Belt",
        "city": "Bengaluru",
        "category": "Construction & Dust",
        "icon": "ph-hard-hat",
        "color": "#F59E0B",
        "lat": 12.9800,
        "lon": 77.7500,
        "key_pollutants": ["PM10", "PM2.5", "CO"],
        "severity": "High",
        "description": "Active infrastructure expansion, heavy commercial vehicle movement, and industrial diesel generator clusters."
    },
    {
        "id": "blr-hebbal",
        "name": "Hebbal Flyover North Highway Interchange",
        "city": "Bengaluru",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 13.0358,
        "lon": 77.5970,
        "key_pollutants": ["NO2", "CO", "PM2.5"],
        "severity": "Elevated",
        "description": "Northern gateway corridor connecting Bengaluru with Kempegowda International Airport and interstate freight."
    },

    # --- Kolkata ---
    {
        "id": "kol-taratala",
        "name": "Taratala - Hyde Road Industrial Belt",
        "city": "Kolkata",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 22.5180,
        "lon": 88.3150,
        "key_pollutants": ["PM2.5", "SO2", "Lead", "NOx"],
        "severity": "Critical",
        "description": "Heavy industrial zone featuring battery recycling, chemical warehousing, boiler units, and port logistics."
    },
    {
        "id": "kol-howrah",
        "name": "Howrah Terminal & Grand Foreshore Transit",
        "city": "Kolkata",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 22.5850,
        "lon": 88.3420,
        "key_pollutants": ["PM2.5", "NO2", "CO", "Black Carbon"],
        "severity": "Critical",
        "description": "High-density diesel locomotive, bus, and ferry staging areas creating intense localized black carbon."
    },
    {
        "id": "kol-dhapa",
        "name": "Dhapa Solid Waste Landfill",
        "city": "Kolkata",
        "category": "Landfill & Waste",
        "icon": "ph-fire",
        "color": "#8B5CF6",
        "lat": 22.5480,
        "lon": 88.4230,
        "key_pollutants": ["NH3", "CO", "PM2.5", "Methane"],
        "severity": "High",
        "description": "Kolkata's primary municipal solid waste site with active organic decomposition and intermittent fires."
    },

    # --- Chennai ---
    {
        "id": "chn-manali",
        "name": "Manali Petrochemical & Refinery Complex",
        "city": "Chennai",
        "category": "Petrochemical & Power",
        "icon": "ph-fire",
        "color": "#F59E0B",
        "lat": 13.1650,
        "lon": 80.2600,
        "key_pollutants": ["SO2", "NOx", "Benzene", "Toluene"],
        "severity": "Critical",
        "description": "Major cluster of oil refineries (CPCL), chemical synthesis, and synthetic rubber manufacturing."
    },
    {
        "id": "chn-ennore",
        "name": "Ennore Thermal Power & Ash Dyke Area",
        "city": "Chennai",
        "category": "Petrochemical & Power",
        "icon": "ph-lightning",
        "color": "#EAB308",
        "lat": 13.2050,
        "lon": 80.3200,
        "key_pollutants": ["SO2", "PM10", "PM2.5", "NOx"],
        "severity": "Critical",
        "description": "Coal-fired thermal generation complex with extensive ash ponds vulnerable to windblown particle lift."
    },
    {
        "id": "chn-kathipara",
        "name": "Kathipara Grade Separator (Guindy)",
        "city": "Chennai",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 13.0070,
        "lon": 80.2050,
        "key_pollutants": ["NO2", "CO", "PM2.5"],
        "severity": "High",
        "description": "Largest cloverleaf road interchange in Asia; handles constant convergence of 4 national arterial highways."
    },

    # --- Hyderabad ---
    {
        "id": "hyd-patancheru",
        "name": "Patancheru - Bollaram Bulk Drug Industrial Belt",
        "city": "Hyderabad",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 17.5300,
        "lon": 78.2600,
        "key_pollutants": ["VOCs", "Toluene", "SO2", "PM10"],
        "severity": "Critical",
        "description": "Globally renowned pharmaceutical manufacturing cluster with active organic solvent emissions."
    },
    {
        "id": "hyd-kukatpally",
        "name": "Kukatpally Y-Junction / NH 65",
        "city": "Hyderabad",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 17.4930,
        "lon": 78.4010,
        "key_pollutants": ["NO2", "CO", "PM2.5"],
        "severity": "High",
        "description": "Major commercial and transit bottleneck with continuous freight and commuter vehicular traffic."
    },

    # --- Ahmedabad ---
    {
        "id": "ahd-vatva",
        "name": "Vatva & Narol Textile & Chemical Cluster",
        "city": "Ahmedabad",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 22.9550,
        "lon": 72.6350,
        "key_pollutants": ["SO2", "NOx", "PM2.5", "CO"],
        "severity": "Critical",
        "description": "Dense concentration of textile bleaching, dyestuff production, and coal-fired industrial boiler stacks."
    },
    {
        "id": "ahd-pirana",
        "name": "Pirana Municipal Landfill Site",
        "city": "Ahmedabad",
        "category": "Landfill & Waste",
        "icon": "ph-fire",
        "color": "#8B5CF6",
        "lat": 22.9800,
        "lon": 72.5700,
        "key_pollutants": ["PM2.5", "CO", "NH3", "Methane"],
        "severity": "Critical",
        "description": "Major historic refuse mound with continuous smoldering, discharging smoke across the Sabarmati basin."
    },

    # --- Lucknow ---
    {
        "id": "lko-amausi",
        "name": "Amausi Industrial & Transport Hub",
        "city": "Lucknow",
        "category": "Industrial Cluster",
        "icon": "ph-factory",
        "color": "#EF4444",
        "lat": 26.7650,
        "lon": 80.8750,
        "key_pollutants": ["PM10", "PM2.5", "SO2"],
        "severity": "High",
        "description": "Manufacturing, railway siding, and freight logistics hub located on the southern city boundary."
    },
    {
        "id": "lko-charbagh",
        "name": "Charbagh Railway Terminal & Bus Staging Corridor",
        "city": "Lucknow",
        "category": "Vehicular Corridor",
        "icon": "ph-car",
        "color": "#3B82F6",
        "lat": 26.8320,
        "lon": 80.9200,
        "key_pollutants": ["NO2", "CO", "PM2.5"],
        "severity": "High",
        "description": "Extreme density of diesel locomotives, suburban commuter buses, and three-wheelers."
    }
]

# City Centers Coordinates
CITY_CENTERS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462}
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates in kilometers.
    """
    r = 6371.0  # Earth's mean radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates initial compass bearing (0-360 degrees) from point 1 to point 2.
    """
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    d_lon_r = math.radians(lon2 - lon1)

    y = math.sin(d_lon_r) * math.cos(lat2_r)
    x = (math.cos(lat1_r) * math.sin(lat2_r) -
         math.sin(lat1_r) * math.cos(lat2_r) * math.cos(d_lon_r))
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    return round(bearing, 1)


def evaluate_wind_alignment(source_bearing: float, wind_direction: Optional[float]) -> Dict[str, Any]:
    """
    Determines if emissions from a hotspot are blowing toward the user location.
    wind_direction is the direction the wind is blowing FROM (standard meteorological convention).
    """
    if wind_direction is None:
        return {"alignment": "Neutral", "level": "normal", "score": 1.0, "icon": "ph-wind"}

    # Bearing from source TO user is opposite of source_bearing
    source_to_user_bearing = (source_bearing + 180) % 360
    angle_diff = abs(source_to_user_bearing - wind_direction)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff

    # If angle_diff < 45 degrees, user is downwind of the source (maximum threat)
    if angle_diff <= 40:
        return {
            "alignment": "Directly Downwind (High Plume Threat)",
            "level": "downwind",
            "score": 1.8,
            "icon": "ph-arrow-down-right"
        }
    elif angle_diff <= 85:
        return {
            "alignment": "Partially Downwind (Moderate Threat)",
            "level": "crosswind",
            "score": 1.3,
            "icon": "ph-arrows-horizontal"
        }
    else:
        return {
            "alignment": "Upwind (Plume Dispersing Away)",
            "level": "upwind",
            "score": 0.8,
            "icon": "ph-arrow-up-right"
        }


def find_nearby_pollutant_sources(
    lat: float,
    lon: float,
    max_radius_km: float = 35.0,
    wind_direction: Optional[float] = None
) -> Dict[str, Any]:
    """
    Finds all verified pollutant sources within a specified radius,
    sorts them by proximity and wind dispersion alignment, and generates localized diagnostics.
    """
    sources_with_distance = []

    for src in KNOWN_POLLUTANT_SOURCES:
        dist = haversine_distance(lat, lon, src["lat"], src["lon"])
        if dist <= max_radius_km:
            bearing = calculate_bearing(src["lat"], src["lon"], lat, lon)
            wind_eval = evaluate_wind_alignment(bearing, wind_direction)

            # Categorize proximity impact zone
            if dist <= 4.0:
                proximity_zone = "Immediate Exposure Zone (<4 km)"
                zone_level = "immediate"
            elif dist <= 12.0:
                proximity_zone = "Nearby Urban Buffer (4-12 km)"
                zone_level = "nearby"
            else:
                proximity_zone = "Regional Airshed (12-35 km)"
                zone_level = "regional"

            sources_with_distance.append({
                **src,
                "distance_km": dist,
                "bearing_deg": bearing,
                "wind_alignment": wind_eval["alignment"],
                "wind_level": wind_eval["level"],
                "wind_multiplier": wind_eval["score"],
                "proximity_zone": proximity_zone,
                "zone_level": zone_level
            })

    # Sort primarily by distance, prioritizing downwind sources
    sources_with_distance.sort(key=lambda s: (s["distance_km"] / s["wind_multiplier"]))

    # Summary analysis
    immediate_count = sum(1 for s in sources_with_distance if s["zone_level"] == "immediate")
    downwind_threats = [s for s in sources_with_distance if s["wind_level"] == "downwind"]

    diagnostic_notes = []
    if sources_with_distance:
        closest = sources_with_distance[0]
        diagnostic_notes.append(
            f"Nearest: **{closest['name']}** (**{closest['distance_km']} km** • {closest['category']})."
        )
        if downwind_threats:
            diagnostic_notes.append(
                f"**{len(downwind_threats)} downwind plume(s)** active toward airshed."
            )
    else:
        diagnostic_notes.append(
            f"No major point sources within {max_radius_km} km."
        )

    return {
        "user_coordinates": {"lat": lat, "lon": lon},
        "search_radius_km": max_radius_km,
        "wind_direction_deg": wind_direction,
        "total_hotspots_found": len(sources_with_distance),
        "immediate_exposure_count": immediate_count,
        "downwind_threat_count": len(downwind_threats),
        "hotspots": sources_with_distance,
        "diagnostic_summary": " ".join(diagnostic_notes)
    }


def get_nearby_sources_for_city(
    city_name: str,
    max_radius_km: float = 35.0,
    wind_direction: Optional[float] = None
) -> Dict[str, Any]:
    """
    Convenience helper to retrieve nearby pollutant sources for a given city center name.
    """
    coords = CITY_CENTERS.get(city_name, CITY_CENTERS["Delhi"])
    return find_nearby_pollutant_sources(
        lat=coords["lat"],
        lon=coords["lon"],
        max_radius_km=max_radius_km,
        wind_direction=wind_direction
    )

