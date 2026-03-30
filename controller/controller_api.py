from flask import Flask, request, jsonify, redirect
from pathlib import Path
import time
import logging
from typing import Dict, Any

import manifest_rewriter, source_selector

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("controller.api")

# keep track of sessions
SESSIONS: Dict[str, Dict[str, Any]] = {}

# configuration: outputs packager root path
MPD_ROOT = Path("dash")

# TODO: get metrics of the session (telemetry)

# get the initially generated manifest, get the source selection, inject the redirect base url into the manifest (mpd) and return it (as a Response)
# Key attributes: session, version ("1" is the default if not found), client
@app.route("/stream.mpd", methods=["GET"])
def get_mpd():
  session = request.args.get("session")
  if not session:
    return jsonify({"error": "session is required"}), 400

  version = request.args.get("version", "1")
  client = request.args.get("client")

  mpd_path = MPD_ROOT / version / "stream.mpd"
  if not mpd_path.exists():
    return jsonify({"error": f"MPD not found: {mpd_path}"}), 404
  
  mpd_xml = mpd_path.read_text(encoding="utf-8")
  session_state = SESSIONS.get(session, {}) # problem? 
  metrics = session_state.get("metrics", {})

  selection = select_sources(mpd_xml, session_id=session, metrics=metrics, client=client)
  mpd = rewrite_mpd(mpd_xml, selection)

  return Response(mpd, mimetype="application/dash+xml")




# Gets the redirect url for chosen segment of the session
@app.route("/init", methods=["GET"])
def get_init():
  session = request.args.get("session")
  if not session:
    return jsonify({"error": "session is required"}), 400

  version = request.args.get("version", "1")
  default_init = f"/dash/{version}/init.mp4"

  session_state = SESSION.get(session, {})
  metrics = session_state.get("metrics", {})

  # TODO: source selection
  selection = select_sources(None, session_id=session, metrics=metrics, client=session_state.get("client"))
  # TODO: redirect
  redirect_url = selection.get("redirect_url")

  # TODO: redirect user to selected source (based on member metrics)
  # code 302=found
  if redirect_url:
    return redirect(redirect_url, code=302)

  return redirect(default_init, code=302)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000, debug=True)