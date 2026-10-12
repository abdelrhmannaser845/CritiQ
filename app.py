import re
from pathlib import Path

import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "sentiment_model.keras"
NUM_WORDS = 10000
MAX_LEN = 200

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

model = tf.keras.models.load_model(MODEL_PATH, compile=False)
word_index = tf.keras.datasets.imdb.get_word_index()


@app.after_request
def add_local_development_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


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


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    review = (data.get("review") or "").strip()

    if not review:
        return jsonify({"error": "Please enter a movie review."}), 400

    return jsonify(classify_review(review))


if __name__ == "__main__":
    app.run(debug=True)
