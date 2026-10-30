import json
import re
from pathlib import Path

import tensorflow as tf
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "sentiment_model.keras"
WORD_INDEX_PATH = BASE_DIR / "data" / "imdb_word_index.json"
NUM_WORDS = 10000
MAX_LEN = 200
MAX_REVIEW_CHARS = 5000
MIN_REVIEW_WORDS = 3


def load_word_index():
    if WORD_INDEX_PATH.exists():
        with open(WORD_INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    WORD_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    index = tf.keras.datasets.imdb.get_word_index()
    with open(WORD_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f)
    return index


model = tf.keras.models.load_model(MODEL_PATH, compile=False)
word_index = load_word_index()


def review_to_sequence(text):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    sequence = []

    for word in words:
        index = word_index.get(word)
        if index is None:
            sequence.append(2)
            continue

        encoded_index = index + 3
        sequence.append(encoded_index if encoded_index < NUM_WORDS else 2)

    return tf.keras.preprocessing.sequence.pad_sequences([sequence], maxlen=MAX_LEN)


def classify_review(text):
    padded = review_to_sequence(text)
    score = float(model.predict(padded, verbose=0)[0][0])
    label = "Positive" if score >= 0.5 else "Negative"
    confidence = score if label == "Positive" else 1 - score

    return {
        "label": label,
        "score": round(score, 4),
        "confidence": round(float(confidence), 4),
        "percent": round(score * 100, 1),
    }


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    if test_config:
        app.config.update(test_config)

    @app.after_request
    def add_local_development_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "model_loaded": model is not None,
                "vocab_size": NUM_WORDS,
                "max_len": MAX_LEN,
            }
        )

    @app.post("/predict")
    def predict():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}

        review = data.get("review") if isinstance(data.get("review"), str) else ""
        review = review.strip()

        if not review:
            return jsonify({"error": "Please enter a movie review."}), 400

        if len(review) > MAX_REVIEW_CHARS:
            return jsonify({"error": f"Review must not exceed {MAX_REVIEW_CHARS} characters."}), 413

        words = re.findall(r"[a-zA-Z']+", review)
        if len(words) < MIN_REVIEW_WORDS:
            return jsonify({"error": f"Please enter at least {MIN_REVIEW_WORDS} words."}), 400

        return jsonify(classify_review(review))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
