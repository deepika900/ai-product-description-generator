"""Flask API that turns product details into SEO-friendly fashion copy using the OpenAI API."""
import json
import os
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

load_dotenv()

TONES = {"professional", "playful", "luxury", "casual"}
SYSTEM_PROMPT = (
    "You are an e-commerce copywriter for a fashion brand. Write SEO-friendly product copy. "
    "Only use facts present in the input: never invent materials, sizes, prices or claims. "
    'Reply with JSON only, in this shape: {"title": string (max 70 chars), '
    '"description": string (60-90 words), "bullets": [3 to 5 short strings]}.'
)


def clean_list(value, limit=10):
    """Accept a list or a comma/newline separated string and return a clean list of strings."""
    if isinstance(value, str):
        value = value.replace("\n", ",").split(",")
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()][:limit]


def create_app(client=None):
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    state = {"client": client}

    def get_client():
        if state["client"] is None:
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY is not set")
            state["client"] = OpenAI(api_key=key)
        return state["client"]

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", model=model)

    @app.post("/api/generate")
    def generate():
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        if not name:
            return jsonify(error="'name' is required"), 400
        if len(name) > 120:
            return jsonify(error="'name' must be 120 characters or fewer"), 400

        tone = str(data.get("tone", "professional")).lower()
        if tone not in TONES:
            return jsonify(error=f"'tone' must be one of {sorted(TONES)}"), 400

        payload = {
            "name": name,
            "category": str(data.get("category", "")).strip()[:60],
            "features": clean_list(data.get("features")),
            "keywords": clean_list(data.get("keywords"), limit=8),
            "tone": tone,
        }

        started = time.perf_counter()
        try:
            response = get_client().chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(payload)},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=400,
                timeout=20,
            )
            result = json.loads(response.choices[0].message.content)
            if not all(k in result for k in ("title", "description", "bullets")):
                raise ValueError("model response missing fields")
        except RuntimeError as exc:  # missing API key
            return jsonify(error=str(exc)), 500
        except (ValueError, json.JSONDecodeError):
            return jsonify(error="The model returned an unexpected response. Please try again."), 502
        except Exception as exc:  # network / API errors
            app.logger.exception("OpenAI request failed: %s", exc)
            return jsonify(error="Could not reach the AI service. Please try again."), 502

        elapsed_ms = round((time.perf_counter() - started) * 1000)
        return jsonify(
            title=result["title"],
            description=result["description"],
            bullets=result["bullets"],
            elapsed_ms=elapsed_ms,
        )

    return app


if __name__ == "__main__":
    create_app().run(port=int(os.getenv("PORT", 5001)), debug=True)
