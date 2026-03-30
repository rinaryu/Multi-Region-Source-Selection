from typing import Dict, Any
import xml.etree.ElementTree as ET

from pathlib import Path # temp for testing

MPD_NS = "urn:mpeg:dash:schema:mpd:2011"
ET.register_namespace("", MPD_NS)
ns = {"mpd": MPD_NS}

# helper method
def parse_mpd(xml: str) -> ET.ElementTree:
  return ET.ElementTree(ET.fromstring(xml))

# helper method
def serialize_mpd(tree: ET.ElementTree) -> str:
  return ET.tostring(tree.getroot(), encoding="utf-8", method="xml").decode("utf-8")

# mpd is the generated manifest from packaging after segmenting the video file
# decisions are the outcomes of source selector
def rewrite_mpd(mpd: str, decisions: Dict[str, Any]) -> str:
  tree = parse_mpd(mpd)
  root = tree.getroot()

  base_url = decisions.get("rewrite_map", {}).get("base_url")
  if not base_url:
    return mpd

  # remove any existing instances of BaseURL (there shouldn't be any but do anyway for sanity)
  for i in root.findall("mpd:BaseURL", ns):
    root.remove(i)
    
  # inject redirect
  # create BaseURL namespace
  base_elem = ET.Element(f'{{{MPD_NS}}}BaseURL')
  base_elem.text = base_url
  root.insert(0, base_elem)

  # turn mpd tree back into xml and return mpd
  return serialize_mpd(tree)

#   print(root)

def main():
  mpd_root = Path("dash")
  mpd_path = mpd_root / "1" / "stream.mpd"
  mpd_xml = mpd_path.read_text(encoding="utf-8")

  print(mpd_xml)

  selection = {
    "selected_origin_id": "cdn-west",
    "redirect_url": "https://cdn-west.ss.net/dash/s1/init.mp4",
    "rewrite_map": {
      "base_url": "https://cdn-west.ss.net/dash/"
    }
  }
  print("spacer----------------")

  mpd = rewrite_mpd(mpd_xml, selection)

  print(mpd)

if __name__ == "__main__":
  main()