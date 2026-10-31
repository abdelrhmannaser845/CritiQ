# CritiQ — Movie Review AI

![CritiQ Social Banner](CritiQ%20Visual%20Identity/social/critiq-social-banner.png)

> **Read between the frames.**

CritiQ predicts whether a movie review sounds positive or negative, returning a live sentiment polarity verdict, confidence score, and detected sentiment signal chips. It runs in **two modes** out of the box:

1. **GitHub Pages (Serverless Browser Mode):** Serves [`index.html`](index.html) directly from the repository root and runs the exact 4-layer Keras neural network (`Embedding -> GlobalAveragePooling1D -> Dense(16, relu) -> Dense(1, sigmoid)`) in pure JavaScript using [`static/model_bundle.json`](static/model_bundle.json).
2. **Local Flask + TensorFlow Mode:** Runs [`app.py`](app.py) on `http://127.0.0.1:5000` and serves predictions from [`sentiment_model.keras`](sentiment_model.keras) via `POST /predict`.

---

## Visual Identity & FigCraft UI

### Screening Room Dark (`#09111E`)
![CritiQ Desktop Dark UI](CritiQ%20Visual%20Identity/ui/exports/01_Desktop_Screening_Room_Dark.png)

### Celluloid Paper Light (`#F6F2EA`)
![CritiQ Desktop Light UI](CritiQ%20Visual%20Identity/ui/exports/02_Desktop_Celluloid_Paper_Light.png)

---

## Hosting on GitHub Pages

This repository is structured to work immediately on **GitHub Pages** without requiring a Python backend server:

- **Option A (GitHub Actions — Automatic):**
  1. Push this repository to GitHub.
  2. Go to **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions**.
  3. The included workflow ([`.github/workflows/pages.yml`](.github/workflows/pages.yml)) automatically deploys the site on push.
- **Option B (Deploy from Branch):**
  1. Go to **Settings → Pages → Build and deployment**.
  2. Set **Source** to **Deploy from a branch**, select your branch (`main` / `phase-1-foundation`) and folder **`/ (root)`**, and click **Save**.
  3. GitHub Pages will serve [`index.html`](index.html), [`static/styles.css`](static/styles.css), [`static/app.js`](static/app.js), and [`static/model_bundle.json`](static/model_bundle.json) directly.

---

## Project Structure

```text
CritiQ/
  index.html                      # Root entry point for GitHub Pages
  .nojekyll                       # Disables Jekyll processing on GitHub Pages
  .github/
    workflows/
      pages.yml                   # Automatic GitHub Pages deployment workflow
  app.py                          # Flask backend (/predict and /health endpoints)
  model.py                        # Keras training script for sentiment_model.keras
  sentiment_model.keras           # Trained TensorFlow/Keras model
  requirements.txt                # Production Python dependencies
  requirements-dev.txt            # Development & test dependencies (pytest, ruff)
  static/
    app.js                        # Interactive UI + in-browser Keras inference fallback
    styles.css                    # CritiQ Visual Identity stylesheet (Dark & Light themes)
    model_bundle.json             # Exported Keras weights & 10K IMDB vocabulary for GitHub Pages
    critiq-app-icon.svg           # Vector app icon & favicon
    critiq-mark-on-dark.svg       # Refracting Aperture mark (Dark theme)
    critiq-mark.svg               # Refracting Aperture mark (Light theme)
    critiq.ico                    # Multi-size favicon
  templates/
    index.html                    # Flask Jinja template
  tests/
    test_app.py                   # Automated pytest unit & integration suite
  CritiQ Visual Identity/         # Brand guidelines, logos, social banner, and FigCraft UI
```

---

## Run Locally with Flask

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

Open in your browser:

```text
http://127.0.0.1:5000
```

---

## Run Tests

```bash
pytest -v
```
