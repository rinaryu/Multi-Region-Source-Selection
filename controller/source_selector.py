from typing Dict, Any, Optional

# temporary member names/links: CHANGE after implementing cloud vms
MEMBERS = [
  {"id": "cdn-west", "base_ur": "https://cdn-west.ss.net/dash/", "regions": ["CA-W", "US-W"], "health": True},
  {"id": "cdn-east", "base_ur": "https://cdn-east.ss.net/dash/", "regions": ["CA-E", "US-E"], "health": True},
  {"id": "cdn-central", "base_ur": "https://cdn-central.ss.net/dash/", "regions": ["CA-C", "US-C"], "health": True},
  {"id": "origin", "base_url": "https://origin.ss.net/dash/", "regions": ["GLOBAL"], "health": True},
]

# keep track of session state
SESSION_STATE: Dict[str, Dict[str, Any]] = {}

# idle time for a session
BUFFER = 60

# create a match score for the selector
def match_score(client: Optional[str], candidate: Dict[str, Any]) -> float:
  return 0.0


# selection logic for redirecting segments
# TODO: what exact metrics to use?
# tentative metric: geography
# output base URl for redirecting
# def select_sources(mpd_xml: Optional[str], 
#                    session_id: str, 
#                    metrics: Dict[str, Any], 
#                    client: Optional[str] = None) -> Dict[str, Any]:



          

