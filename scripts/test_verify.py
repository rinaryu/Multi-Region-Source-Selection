import sys
import os

# Append controller directory to path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(base_dir, 'controller'))

from source_selector import select_sources
from manifest_rewriter import rewrite_mpd

# test distance
sel = select_sources('s1', 'distance', 'eu-central-1')
print(f"Distance EU-Central-1: {sel}")
assert sel['origin'] == 'eu-central-1', "Distance Selection Failed"

# test random
sel2 = select_sources('s2', 'random', '')
print(f"Random: {sel2}")

# test rewrite
mpd_path = os.path.join(base_dir, 'dash', 'test_run', 'stream.mpd')
with open(mpd_path, 'r') as f:
    xml = f.read()

rewritten = rewrite_mpd(xml, sel['base_url'])
expected_tag = f"<BaseURL>{sel['base_url']}</BaseURL>"
print(f"Rewrite result contains BaseURL? {expected_tag in rewritten}")
assert expected_tag in rewritten, "XML Rewrite Failed to inject BaseURL"
print("System Verification Passed!")
