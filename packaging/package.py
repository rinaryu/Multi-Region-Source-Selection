# create video segments and MPD
'''
IMPORTANT: Functions use Bento4 v1.6.0.640 (or higher), must have package installed on environment to be able to run. 
'''
import subprocess
from pathlib import Path
from typing import List, Optional

# helper function: run external bento4 commands to segment + package
def _run(cmd: List[str]):
  proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  if proc.returncode != 0:
    raise RuntimeError(proc.stderr.strip())
    
  return proc.stdout

# called by main pipeline (2)
# package renditions into DASH and return metadata about the package
# return: mpd_path(str), output_dir(str), renditions(list of dicts), files(str list), warnings(str list), error(str/None)
def package_for_dash(rendition_files: List[str],
                     output_dir: str,
                     segment_duration: int = 2,
                     packager: str = "bento4",
                     extra_args: Optional[List[str]] = None) -> dict:
  output = {
    "mpd_path": None,
    "output_dir": output_dir,
    "renditions": [],
    "files": [],
    "warnings": [],
    "error": None,
  }

  try:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # segment each rendition
    segmented = []
    for i in rendition_files:
      base = Path(i).stem
      seg_path = out_dir / f"{base}_seg.mp4"

      # segment the video into 2ms portions, export into new .mp4
      _run([
        "mp4fragment",
        "--fragment-duration", str(segment_duration * 1000), #ms
        i,
        str(seg_path),
      ])

      segmented.append(str(seg_path))
      output["renditions"].append({
        "input": i,
        "segmented": str(seg_path)
      })
    
    # package into DASH
    mpd_path = out_dir / "stream.mpd"
    output["mpd_path"] = str(mpd_path)

    # use segmented video to build manifest and write segments into output dir
    cmd = [
      "mp4dash",
      "--force",
      "--use-segment-timeline",
      "--mpd-name",
      "stream.mpd",
      "--output-dir",
      str(out_dir),
    ]

    if extra_args:
      cmd += extra_args

    cmd += segmented

    _run(cmd)

    # get output files
    for f in out_dir.iterdir():
      output["files"].append(str(f))

  except Exception as e:
    output["error"] = str(e)

  return output