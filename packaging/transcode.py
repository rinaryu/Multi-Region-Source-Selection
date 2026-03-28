from pathlib import Path
from typing import List, Dict
import logging
import json
import subprocess

# run ffmpeg to produce video rendition
logging.basicConfig(level=logging.INFO)
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

def _run(cmd: List[str]):
  logging.info("Running: %s", " ".join(cmd))
  proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  if proc.returncode != 0:
    logging.error("Command failed: %s", proc.stderr.strip())
    raise RuntimeError(proc.stderr.strip())
  return proc.stdout

# called by main pipeline (1)
# Produce 480p MP4 rendition. Returns list of output file paths.
# gop: keyframe interval in frames
# fps: target frame rate
def transcode(input_path: str, 
              rendition_files: List[str],
              out_dir: str,
              gop: int = 48,
              fps: int = 24) -> List[str]:

  out_dir = Path(out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  outputs = []

  out_name = rendition_files[0] if rendition_files else "480.mp4"
  out_path = out_dir / out_name 

  scale = "scale=-2:480"
  cmd = [
    FFMPEG, "-y", "-hide_banner", "-loglevel", "info",
    "-i", input_path,
    "-vf", scale,
    "-r", str(fps),
    "-g", str(gop),
    "-keyint_min", str(gop),
    "-sc_threshold", "0",
    "-c:v", "libx264",
    "-b:v", "800k",
    "-maxrate", "900k",
    "-bufsize", "1600k",
    "-preset", "fast",
    "-profile:v", "main",
    "-x264-params", "nal-brd=cbr",
    "-c:a", "aac",
    "-b:a", "96k",
    str(out_path)
  ]

  _run(cmd)
  return [str(out_path)]

# TODO: function that verifies that files exist
#  def verify_outputs(paths: List[str]) -> Dict: 

  
