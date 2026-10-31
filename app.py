import json
import re
import time
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

POSITIVE_WORDS = {
    "excellent", "confident", "moving", "brilliant", "fantastic", "wonderful",
    "warm", "sharp", "gorgeous", "strong", "masterpiece", "great", "love",
    "best", "superb", "emotional", "earned", "earns", "stays", "beautiful",
    "compelling", "engaging", "remarkable", "stunning", "triumph", "promising",
    "talented", "masterful", "sublime", "vivid", "captivating", "terrific",
    "impressive", "powerful", "good", "fine", "rich", "solid", "fun", "fresh",
}

NEGATIVE_WORDS = {
    "dull", "missed", "unfinished", "lifeless", "boring", "terrible", "worst",
    "awful", "weak", "flat", "waste", "poor", "bad", "loses", "mess", "slow",
    "disappointing", "predictable", "pointless", "flawed", "tedious", "unresolved",
    "clunky", "shallow", "tired", "cheap", "forgettable", "hollow", "wooden",
    "stale", "failed", "drags", "messy", "lacks", "ruined",
}

STOP_WORDS = {
    "about", "after", "again", "also", "been", "before", "being", "between",
    "both", "came", "come", "could", "does", "done", "down", "even", "from",
    "have", "having", "here", "into", "just", "like", "made", "make", "many",
    "more", "most", "much", "must", "only", "other", "over", "said", "same",
    "should", "some", "such", "than", "that", "the", "their", "them", "then",
    "there", "these", "they", "this", "those", "through", "very", "were",
    "what", "when", "where", "which", "while", "will", "with", "would",
}


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


def extract_drivers(words, predicted_label):
    unique_words = []
    seen = set()
    for w in words:
        clean = w.strip("'")
        if len(clean) >= 2 and clean not in seen:
            seen.add(clean)
            unique_words.append(clean)

    is_positive = predicted_label == "Positive"
    primary_vocab = POSITIVE_WORDS if is_positive else NEGATIVE_WORDS
    secondary_vocab = NEGATIVE_WORDS if is_positive else POSITIVE_WORDS
    primary_polarity = "positive" if is_positive else "negative"
    secondary_polarity = "negative" if is_positive else "positive"

    drivers = []
    picked = set()

    # 1. Primary vocabulary matches (aligned with predicted sentiment)
    for w in unique_words:
        if w in primary_vocab and w not in picked:
            picked.add(w)
            drivers.append({"word": w, "polarity": primary_polarity})
            if len(drivers) >= 4:
                return drivers

    # 2. Secondary vocabulary matches (opposing sentiment nuances)
    for w in unique_words:
        if w in secondary_vocab and w not in picked:
            picked.add(w)
            drivers.append({"word": w, "polarity": secondary_polarity})
            if len(drivers) >= 4:
                return drivers

    # 3. Fallback to known IMDB vocabulary words >= 4 chars (excluding stop words)
    for w in unique_words:
        if len(w) >= 4 and w not in picked and w not in STOP_WORDS:
            idx = word_index.get(w)
            if idx is not None and (idx + 3 < NUM_WORDS):
                picked.add(w)
                drivers.append({"word": w, "polarity": primary_polarity})
                if len(drivers) >= 4:
                    return drivers

    # 4. Fallback to any known IMDB vocabulary words >= 3 chars
    for w in unique_words:
        if len(w) >= 3 and w not in picked:
            idx = word_index.get(w)
            if idx is not None and (idx + 3 < NUM_WORDS):
                picked.add(w)
                drivers.append({"word": w, "polarity": primary_polarity})
                if len(drivers) >= 4:
                    return drivers

    # 5. Last fallback: any remaining unique review words
    for w in unique_words:
        if w not in picked:
            picked.add(w)
            drivers.append({"word": w, "polarity": primary_polarity})
            if len(drivers) >= 4:
                return drivers

    return drivers


def classify_review(text):
    raw_words = re.findall(r"[a-zA-Z']+", text.lower())
    word_count = len(raw_words)
    tokens_mapped = sum(
        1
        for w in raw_words
        if word_index.get(w) is not None and (word_index.get(w) + 3 < NUM_WORDS)
    )

    padded = review_to_sequence(text)

    t0 = time.perf_counter()
    score = float(model.predict(padded, verbose=0)[0][0])
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    label = "Positive" if score >= 0.5 else "Negative"
    confidence = score if label == "Positive" else 1 - score
    drivers = extract_drivers(raw_words, label)

    return {
        "label": label,
        "score": round(score, 4),
        "confidence": round(float(confidence), 4),
        "percent": round(score * 100, 1),
        "word_count": word_count,
        "tokens_mapped": tokens_mapped,
        "latency_ms": latency_ms,
        "drivers": drivers,
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
