const form = document.querySelector("#reviewForm");
const textarea = document.querySelector("#reviewText");
const submitButton = document.querySelector("#submitButton");
const clearButton = document.querySelector("#clearButton");
const message = document.querySelector("#message");
const resultLabel = document.querySelector("#resultLabel");
const resultDetail = document.querySelector("#resultDetail");
const meterFill = document.querySelector("#meterFill");
const scorePanel = document.querySelector(".score-panel");
const charCount = document.querySelector("#charCount");
const glassPanels = document.querySelectorAll(".score-panel, .analyzer, .examples");
const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:5000" : "";

function updateCharacterCount() {
  const length = textarea.value.length;
  charCount.textContent = `${length.toLocaleString()} ${length === 1 ? "character" : "characters"}`;
}

function setResult(result) {
  scorePanel.classList.remove("is-loading", "is-positive", "is-negative");
  scorePanel.classList.add(result.label === "Positive" ? "is-positive" : "is-negative");
  resultLabel.textContent = result.label;
  resultDetail.textContent = `${Math.round(result.confidence * 100)}% confidence, ${result.percent}% positive score`;
  meterFill.style.width = `${result.percent}%`;
}

function resetResult() {
  message.textContent = "";
  scorePanel.classList.remove("is-loading", "is-positive", "is-negative");
  resultLabel.textContent = "Waiting";
  resultDetail.textContent = "Submit a review to analyze it.";
  meterFill.style.width = "0%";
}

glassPanels.forEach((panel) => {
  panel.addEventListener("pointermove", (event) => {
    const rect = panel.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;

    panel.style.setProperty("--tilt-x", `${y * -4}deg`);
    panel.style.setProperty("--tilt-y", `${x * 4}deg`);
  });

  panel.addEventListener("pointerleave", () => {
    panel.style.setProperty("--tilt-x", "0deg");
    panel.style.setProperty("--tilt-y", "0deg");
  });
});

textarea.addEventListener("input", updateCharacterCount);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  scorePanel.classList.add("is-loading");
  submitButton.disabled = true;
  submitButton.textContent = "Analyzing...";

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ review: textarea.value }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Could not analyze this review.");
    }

    setResult(payload);
  } catch (error) {
    scorePanel.classList.remove("is-loading");
    message.textContent = "Could not reach Flask. Run python app.py and open http://127.0.0.1:5000.";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Analyze Review";
  }
});

clearButton.addEventListener("click", () => {
  textarea.value = "";
  resetResult();
  updateCharacterCount();
  textarea.focus();
});

document.querySelectorAll("[data-review]").forEach((button) => {
  button.addEventListener("click", () => {
    textarea.value = button.dataset.review;
    resetResult();
    updateCharacterCount();
    textarea.focus();
  });
});

updateCharacterCount();
