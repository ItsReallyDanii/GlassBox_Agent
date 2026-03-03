import os
import json
import base64
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)
MODEL_ID = "gemini-2.5-pro"

@app.route("/", methods=["POST"])
def analyze_ui():
    data = request.get_json()
    if not data or 'image_b64' not in data or 'user_issue' not in data:
        return jsonify({"error": "Missing image_b64 or user_issue"}), 400

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"error": "Server missing API key"}), 500

    client = genai.Client(api_key=api_key)
    image_part = types.Part.from_bytes(data=base64.b64decode(data['image_b64']), mime_type="image/png")

    prompt = f"""Analyze this screenshot. The user is reporting the following issue: "{data['user_issue']}"
    Identify the single most relevant UI element the user should interact with to resolve their issue.
    Return ONLY a raw JSON object using this exact schema:
    {{
      "x": integer,
      "y": integer,
      "width": integer,
      "height": integer,
      "element_description": "short string",
      "rationale": "short string"
    }}"""

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=[image_part, prompt])
        text_response = response.text.strip()
        if text_response.startswith("```"):
            lines = text_response.splitlines()
            start = 1 if lines[0].startswith("```") else 0
            end = -1 if lines[-1].strip() == "```" else len(lines)
            text_response = "\n".join(lines[start:end]).strip()
        return jsonify(json.loads(text_response))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
