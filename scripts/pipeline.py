import sys, json, time
from packaging.transcode import transcode
from packaging.package import package_for_dash

def run_pipeline(input_video, renditions, version_tag):
  start = time.time()

  try:
    # transcode
    renditions_dir = f"renditions/{version_tag}"
    files = transcode(input_video, renditions, renditions_dir)
    if not files:
      raise RuntimeError("transcode produced no files")
    print("successful transcode")


    # get segments
    package_dir = f"dash/{version_tag}"
    meta = package_for_dash(files, package_dir, segment_duration=2)
    if meta.get("error"):
      raise RuntimeError(meta["error"])
    print("successful segmentation")

  except Exception as e:
    # notify_failure({"error": str(e)})
    print("pipeline failed:", e, file=sys.stderr)
    return 1
  


if __name__ == "__main__":
  sys.exit(run_pipeline('video1.mp4', ['480.mp4'], 1))