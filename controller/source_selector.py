from typing import Dict, Any, Optional, List

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
# TODO: what exact metrics to use?
# tentative metric: geography
# output base URl for redirecting
# def select_sources(mpd_xml: Optional[str], 
#                    session_id: str, 
#                    metrics: Dict[str, Any], 
#                    client: Optional[str] = None) -> Dict[str, Any]:


# def main():
#   client = "CA-BC"
#   scored = score_all(client)

#   print(scored)



# if __name__ == "__main__":
#   main()

          

