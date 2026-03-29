from flask import Flask, request, jsonify, redirect
from pathlib import Path
import time
import logging
from typing import Dict, Any

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("controller.api")

# keep track of sessions
SESSIONS: Dict[str, Dict[str, Any]] = {}

# configuration: outputs packager root path
MPD_ROOT = Path("dash")

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
  # TODO: redirect

  # TODO: redirect user to selected source (based on member metrics)
  # code 302=found
  return redirect(default_init, code=302)

if __name__ == "__main__":
  # For development. Use a WSGI server for production.
  app.run(host="0.0.0.0", port=8000, debug=True)