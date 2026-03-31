from typing import Dict, Any, Optional, List
import time

# temporary member names/links: CHANGE after implementing cloud vms
CANDIDATE = [
  {"id": "cdn-west", "base_url": "https://cdn-west.ss.net/dash/", "regions": ["CA-W", "US-W"], "health": True},
  {"id": "cdn-east", "base_url": "https://cdn-east.ss.net/dash/", "regions": ["CA-E", "US-E"], "health": True},
  {"id": "cdn-central", "base_url": "https://cdn-central.ss.net/dash/", "regions": ["CA-C", "US-C"], "health": True},
  {"id": "origin", "base_url": "https://origin.ss.net/dash/", "regions": ["GLOBAL"], "health": True},
]

# keep track of session state
SESSION_STATE: Dict[str, Dict[str, Any]] = {}

# idle time for a session
BUFFER = 60

# create a match score for the selector
# determines the match score a client against a single candidate region
'''
Scoring rules:
1.0 : exact region match
0.9 : country match (CA-BC -> CA-*)
0.8 : regional match (US-W -> US)
0.5 : GLOBAL
0.0 : no match
'''
def match_score(client: Optional[str], candidate: Dict[str, Any]) -> float:
  if not client:
    return 0.5 if "GLOBAL" in candidate.get("regions", []) else 0.0


  c_full = client.upper() # full country + region
  regions = [i.upper() for i in candidate.get("regions", [])]

  # if exact match
  if c_full in regions:
    return 1.0
  
  c_token = client.split("-")[0].upper() # parse: get country
  for i in regions:
    if i.split("-")[0] == c_token:
      if "-" not in i:
        return 0.8
      return 0.9
  
  if "GLOBAL" in regions:
    return 0.5
    
  # otherwise assume no match found
  return 0.0

# helper method to get the client score matched against all the CANADIDATEs 
# when called, would take the highest score in the resulting "scored" list
def score_all(client: Optional[str]) -> List[Dict[str, Any]]:
  scored = []
  for i in CANDIDATE:
    if not i.get("health", True):
      continue
    s = match_score(client, i)
    scored.append({"id": i["id"], "base_url": i["base_url"], "score": s})
  scored.sort(key=lambda x: x["score"], reverse=True)
  return scored


# selection logic for redirecting segments
# tentative metric: geography
# output base URl for redirecting and selected 
def select_sources(session_id: str,
                   metrics: Dict[str, Any],
                   client: Optional[str] = None) -> Dict[str, Any]:
  
  client_geo = (metrics or {}).get("geo")
  scored = score_all(client_geo)

  # session_id retreived from controller api
  state = SESSION_STATE.setdefault(session_id, {})
  last_choice = state.get("last_choice")
  last_change = state.get("last_change", 0) # timestamp of last change
  now = time.time()

  chosen = None

 # apply sticky logic: reuse the last choice if the session is still within the buffer window
  if last_choice and (now - last_change) < BUFFER:
    last_candidate = next((c for c in CANDIDATE if c.get("id") == last_choice), None)
    if last_candidate is not None:
        last_score = match_score(client_geo, last_candidate)
        if last_score > 0:
            chosen = {"id": last_candidate["id"],
                      "base_url": last_candidate["base_url"],
                      "score": last_score,
                      "sticky": True}

  # outside the window, so simply choose the highest scoring option
  if not chosen:
    chosen = scored[0] if scored else None
  
  # fallback to origin: there were no country or regional matches
  # pick global
  if not chosen:
    fallback = CANADIDATE[-1]
    chosen = {"id": fallback["id"], "base_url": fallback["base_url"], "score": 0.0}

  # update the session if the state has changed
  if state.get("last_choice") != chosen["id"]:
    state["last_choice"] = chosen["id"]
    state["last_change"] = now

  redirect_url = f"{chosen['base_url']}{session_id}/init.mp4"

  selection = {
    "selected_origin_id": chosen["id"],
    "redirect_url": redirect_url,
    "rewrite_map": {"base_url": chosen["base_url"]},

  }

  return selection

