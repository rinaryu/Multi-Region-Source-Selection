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

  if not rendition_files:
    rendition_files = ["360.mp4", "480.mp4", "720.mp4"]

  # ABR ladder configs mapped by height
  configs = {
    "360": {"b": "400k", "max": "450k", "buf": "800k"},
    "480": {"b": "800k", "max": "900k", "buf": "1600k"},
    "720": {"b": "1500k", "max": "1700k", "buf": "3000k"}
  }

  for r_file in rendition_files:
    height_str = Path(r_file).stem
    config = configs.get(height_str, configs["480"])
    
    out_path = out_dir / r_file 
    scale = f"scale=-2:{height_str}"
    
    cmd = [
      FFMPEG, "-y", "-hide_banner", "-loglevel", "warning",
      "-i", input_path,
      "-vf", scale,
      "-r", str(fps),
      "-g", str(gop),
      "-keyint_min", str(gop),
      "-sc_threshold", "0",
      "-c:v", "libx264",
      "-b:v", config["b"],
      "-maxrate", config["max"],
      "-bufsize", config["buf"],
      "-preset", "fast",
      "-profile:v", "main",
      "-x264-params", "nal-brd=cbr",
      "-c:a", "aac",
      "-b:a", "96k",
      str(out_path)
    ]

    _run(cmd)
    outputs.append(str(out_path))

  return outputs

# TODO: function that verifies that files exist
#  def verify_outputs(paths: List[str]) -> Dict: 

  
