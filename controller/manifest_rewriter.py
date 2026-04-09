import re

def rewrite_mpd(mpd_xml: str, base_url: str) -> str:
    """
    Injects a <BaseURL> tag into the MPD XML.
    Dash.js will use this BaseURL to construct full paths for downloading segments.
    """
    match = re.search(r'(<MPD[^>]*>)', mpd_xml)
    if not match:
        return mpd_xml
    
    injection = f"\n  <BaseURL>{base_url}</BaseURL>"
    rewritten = mpd_xml[:match.end()] + injection + mpd_xml[match.end():]
    return rewritten