from flask import Flask, request, jsonify, Response
from pathlib import Path
import time
import logging
from typing import Dict, Any

from manifest_rewriter import rewrite_mpd
from source_selector import select_sources

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("controller.api")

SESSIONS: Dict[str, Dict[str, Any]] = {}

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return response

@app.route("/stream.mpd", methods=["GET"])
def get_mpd():
    session = request.args.get("session")
    if not session:
        return jsonify({"error": "session is required"}), 400

    version = request.args.get("version", "test_run")
    policy = request.args.get("policy", "distance")
    client_region = request.args.get("client_region", "eu-central-1")

    # Assuming we run from the project root. If ran from controller/, then ../dash
    mpd_path = Path("dash") / version / "stream.mpd"
    if not mpd_path.exists():
        mpd_path = Path("../dash") / version / "stream.mpd"
        if not mpd_path.exists():
            return jsonify({"error": f"MPD not found"}), 404
  
    mpd_xml = mpd_path.read_text(encoding="utf-8")
    
    if session not in SESSIONS:
        SESSIONS[session] = {"started": time.time(), "metrics": []}
    
    selection = select_sources(session_id=session, policy=policy, client_region=client_region)
    rewrite = rewrite_mpd(mpd_xml, selection["base_url"])

    logger.info(f"[ROUTING] Session {session} | Policy: {policy} | Region: {client_region} -> Origin: {selection['origin']}")
    
    return Response(rewrite, mimetype="application/dash+xml")

@app.route("/init", methods=["GET"])
def get_init():
    return jsonify({"status": "deprecated, use stream.mpd instead"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)