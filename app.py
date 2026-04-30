import logging

from flask import Flask, render_template, request, jsonify

from api_client import (
    number_lookup,
    aadhar_lookup,
    freefire_lookup,
    bgmi_lookup,
    aadhar_family,
    snapchat_lookup,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/lookup", methods=["POST"])
def lookup():
    """Handle API lookup requests from the web UI."""
    data = request.json
    lookup_type = data.get("type", "")
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Please enter a valid input"}), 400

    try:
        if lookup_type == "number":
            result = number_lookup(query)
        elif lookup_type == "aadhar":
            result = aadhar_lookup(query)
        elif lookup_type == "family":
            result = aadhar_family(query)
        elif lookup_type == "ff":
            result = freefire_lookup(query)
        elif lookup_type == "bgmi":
            result = bgmi_lookup(query)
        elif lookup_type == "snap":
            result = snapchat_lookup(query)
        else:
            return jsonify({"error": "Invalid lookup type"}), 400

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Lookup error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "Call OSINT"})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
