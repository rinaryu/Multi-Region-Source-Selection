import random
import json
import os
import logging
import math

logger = logging.getLogger("controller.api")

DEFAULT_ORIGINS = {
    "us-west-2": "http://localhost:8001",
    "us-east-1": "http://localhost:8002",
    "eu-central-1": "http://localhost:8003"
}

ORIGINS = DEFAULT_ORIGINS
origins_path = os.path.join(os.path.dirname(__file__), "..", "origins.json")
if os.path.exists(origins_path):
    try:
        with open(origins_path, "r") as f:
            data = json.load(f)
            ORIGINS = data
            logger.info("Loaded ORIGINS from origins.json")
    except Exception as e:
        logger.error(f"Failed to load origins.json: {e}")

REGION_COORDINATES = {
    "us-east-1": (39.0438, -77.4874),         # N. Virginia
    "us-east-2": (40.1906, -82.9071),         # Ohio
    "us-west-1": (37.7749, -122.4194),        # N. California
    "us-west-2": (45.8399, -119.7006),        # Oregon
    "ca-central-1": (45.5017, -73.5673),      # Montreal
    "sa-east-1": (-23.5505, -46.6333),        # Sao Paulo
    "eu-central-1": (50.1109, 8.6821),        # Frankfurt
    "eu-central-2": (47.3769, 8.5417),        # Zurich
    "eu-west-1": (53.3498, -6.2603),          # Ireland
    "eu-west-2": (51.5074, -0.1278),          # London
    "eu-west-3": (48.8566, 2.3522),           # Paris
    "eu-north-1": (59.3293, 18.0686),         # Stockholm
    "ap-southeast-1": (1.3521, 103.8198),     # Singapore
    "ap-southeast-2": (-33.8688, 151.2093),   # Sydney
    "ap-northeast-1": (35.6895, 139.6917),    # Tokyo
    "ap-northeast-2": (37.5665, 126.9780),    # Seoul
    "ap-northeast-3": (34.6937, 135.5023),    # Osaka
    "ap-south-1": (19.0760, 72.8777),         # Mumbai
    "af-south-1": (-33.9249, 18.4241),        # Cape Town
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes the Earth surface distance strictly in kilometers utilizing the absolute 
    Haversine trigonometric formula across the global latitude/longitude sphere.
    """
    R = 6371.0 # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2)**2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

_rr_index = 0

def select_sources(session_id: str, policy: str, client_region: str) -> dict:
    global _rr_index
    origin_keys = list(ORIGINS.keys())
    
    if not origin_keys:
        return {"origin": "unknown", "base_url": "http://localhost:8000"}

    if policy == "random":
        selected_key = random.choice(origin_keys)
    elif policy == "round_robin":
        selected_key = origin_keys[_rr_index % len(origin_keys)]
        _rr_index += 1
    else: # distance based
        # Safely fetch coordinates, default to N. Virginia if unknown
        client_coords = REGION_COORDINATES.get(client_region, REGION_COORDINATES["us-east-1"])
        
        min_distance = float('inf')
        selected_key = origin_keys[0]
        
        for origin in origin_keys:
            origin_coords = REGION_COORDINATES.get(origin, REGION_COORDINATES["us-east-1"])
            
            # Compute real spherical distance
            dist = haversine_distance(client_coords[0], client_coords[1], origin_coords[0], origin_coords[1])
            logger.info(f"    [Haversine] Evaluated Node {origin}: Discovered separation of {dist:.0f} km.")
            
            if dist < min_distance:
                min_distance = dist
                selected_key = origin

    base_url = ORIGINS[selected_key]
    if not base_url.endswith("/"):
        base_url += "/"
        
    return {
        "origin": selected_key,
        "base_url": base_url
    }
