import random
import json
import os
import logging

logger = logging.getLogger("controller.api")

DEFAULT_ORIGINS = {
    "us-west-1": "http://localhost:8001",
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

CLOSEST_MAP = {
    "us-west-1": "us-west-1",
    "us-east-1": "us-east-1",
    "eu-central-1": "eu-central-1",
    "ap-southeast-2": "us-west-1" 
}

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
        selected_key = CLOSEST_MAP.get(client_region, origin_keys[0])
        
    base_url = ORIGINS[selected_key]
    if not base_url.endswith("/"):
        base_url += "/"
        
    return {
        "origin": selected_key,
        "base_url": base_url
    }
