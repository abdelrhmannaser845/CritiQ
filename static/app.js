const form = document.querySelector("#reviewForm");
const textarea = document.querySelector("#reviewText");
const submitButton = document.querySelector("#submitButton");
const clearButton = document.querySelector("#clearButton");
const message = document.querySelector("#message");

const scorePanel = document.querySelector(".score-panel");
const resultLabel = document.querySelector("#resultLabel");
const resultPercent = document.querySelector("#resultPercent");
const verdictBadge = document.querySelector("#verdictBadge");
const resultDetail = document.querySelector("#resultDetail");
const resultMeta = document.querySelector("#resultMeta");
const meterFill = document.querySelector("#meterFill");

const charCount = document.querySelector("#charCount");
const driverChips = document.querySelector("#driverChips");

const teleLabel = document.querySelector("#teleLabel");
const teleConfidence = document.querySelector("#teleConfidence");
const teleScore = document.querySelector("#teleScore");
const telePadding = document.querySelector("#telePadding");

const themeToggle = document.querySelector("#themeToggle");
const themeLabel = document.querySelector("#themeLabel");
const brandMarkImg = document.querySelector("#brandMarkImg");
const footerCopy = document.querySelector("#footerCopy");

const sampleCards = document.querySelectorAll(".sample-card");
const glassPanels = document.querySelectorAll(".score-panel, .analyzer, .examples");

const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:5000" : "";

const POSITIVE_VOCAB = new Set([
  "excellent", "confident", "moving", "brilliant", "fantastic", "wonderful",
  "warm", "sharp", "gorgeous", "strong", "masterpiece", "great", "love",
  "best", "superb", "emotional", "earned", "earns", "stays", "beautiful",
  "compelling", "engaging", "remarkable", "stunning", "triumph", "promising",
  "talented", "masterful", "sublime", "vivid", "captivating", "terrific",
  "impressive", "powerful", "good", "fine", "rich", "solid", "fun", "fresh"
]);

const NEGATIVE_VOCAB = new Set([
  "dull", "missed", "unfinished", "lifeless", "boring", "terrible", "worst",
  "awful", "weak", "flat", "waste", "poor", "bad", "loses", "mess", "slow",
  "disappointing", "predictable", "pointless", "flawed", "tedious", "unresolved",
  "clunky", "shallow", "tired", "cheap", "forgettable", "hollow", "wooden",
  "stale", "failed", "drags", "messy", "lacks", "ruined"
]);

function countWords(text) {
  if (!text) return 0;
  const matches = text.match(/[a-zA-Z']+/g);
  return matches ? matches.length : 0;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function updateCharacterCount() {
  const length = textarea.value.length;
  const words = countWords(textarea.value);
  charCount.textContent = `${length.toLocaleString()} CHARACTERS // ${words} WORDS`;
}

function extractFallbackDrivers(text, isPositive) {
  if (!text) return [];

  const rawWords = text.toLowerCase().match(/[a-zA-Z']+/g) || [];
  const seen = new Set();
  const uniqueWords = [];

  for (const w of rawWords) {
    const clean = w.replace(/^'+|'+$/g, "");
    if (clean.length >= 2 && !seen.has(clean)) {
      seen.add(clean);
      uniqueWords.push(clean);
    }
  }

  const primaryVocab = isPositive ? POSITIVE_VOCAB : NEGATIVE_VOCAB;
  const secondaryVocab = isPositive ? NEGATIVE_VOCAB : POSITIVE_VOCAB;
  const primaryPolarity = isPositive ? "positive" : "negative";
  const secondaryPolarity = isPositive ? "negative" : "positive";

  const drivers = [];
  const picked = new Set();

  // 1. Primary vocabulary matches
  for (const w of uniqueWords) {
    if (primaryVocab.has(w) && !picked.has(w)) {
      picked.add(w);
      drivers.push({ word: w, polarity: primaryPolarity });
      if (drivers.length >= 4) return drivers;
    }
  }

  // 2. Secondary vocabulary matches
  for (const w of uniqueWords) {
    if (secondaryVocab.has(w) && !picked.has(w)) {
      picked.add(w);
      drivers.push({ word: w, polarity: secondaryPolarity });
      if (drivers.length >= 4) return drivers;
    }
  }

  // 3. Fallback: longest words >= 5 characters from review
  const longWords = uniqueWords
    .filter((w) => w.length >= 5 && !picked.has(w))
    .sort((a, b) => b.length - a.length);

  for (const w of longWords) {
    picked.add(w);
    drivers.push({ word: w, polarity: primaryPolarity });
    if (drivers.length >= 4) return drivers;
  }

  // 4. Any remaining words >= 3 chars
  for (const w of uniqueWords) {
    if (w.length >= 3 && !picked.has(w)) {
      picked.add(w);
      drivers.push({ word: w, polarity: primaryPolarity });
      if (drivers.length >= 4) return drivers;
    }
  }

  return drivers;
}

function renderDrivers(drivers, text, isPositive) {
  let list = drivers;
  if (!Array.isArray(list) || list.length === 0) {
    list = extractFallbackDrivers(text, isPositive);
  }

  if (!list || list.length === 0) {
    driverChips.innerHTML = '<span class="driver-chip is-muted">awaiting review input</span>';
    return;
  }

  const html = list.slice(0, 4).map((d) => {
    const polarity = d.polarity === "positive" ? "positive" : "negative";
    const sign = polarity === "positive" ? "+" : "-";
    return `<span class="driver-chip is-${polarity}">${sign} ${escapeHtml(d.word)}</span>`;
  }).join("");

  driverChips.innerHTML = html;
}

function setResult(result, elapsedMs) {
  scorePanel.classList.remove("is-loading", "is-positive", "is-negative", "is-mixed");

  const rawLabel = result.label || (result.score >= 0.5 ? "Positive" : "Negative");
  const isPositive = rawLabel.toLowerCase() === "positive";
  const isNegative = rawLabel.toLowerCase() === "negative";
  const isMixed = rawLabel.toLowerCase() === "mixed";

  if (isMixed) {
    scorePanel.classList.add("is-mixed");
    verdictBadge.textContent = "MIXED SIGNAL";
  } else if (isPositive) {
    scorePanel.classList.add("is-positive");
    verdictBadge.textContent = "POSITIVE SIGNAL";
  } else {
    scorePanel.classList.add("is-negative");
    verdictBadge.textContent = "NEGATIVE SIGNAL";
  }

  resultLabel.textContent = rawLabel;
  resultPercent.textContent = `${result.percent}%`;
  meterFill.style.width = `${result.percent}%`;

  const confNum = typeof result.confidence === "number" ? result.confidence : parseFloat(result.confidence || 0);
  const confPct = Math.round(confNum * 100);
  const words = result.word_count !== undefined ? result.word_count : countWords(textarea.value);

  if (isMixed) {
    resultDetail.textContent = `${confPct}% confidence — balanced critical signal across ${words} words (${result.percent}% positive score).`;
  } else if (isPositive) {
    resultDetail.textContent = `${confPct}% confidence — strong positive pulse across ${words} words (${result.percent}% positive score).`;
  } else {
    resultDetail.textContent = `${confPct}% confidence — sharp negative verdict across ${words} words (${result.percent}% positive score).`;
  }

  const scoreNum = typeof result.score === "number" ? result.score : parseFloat(result.score || 0);
  const latencyMs = result.latency_ms !== undefined ? result.latency_ms : (elapsedMs !== undefined ? Math.round(elapsedMs) : 0);
  resultMeta.textContent = `SCORE: ${scoreNum.toFixed(4)} // THRESHOLD: >= 0.50 // LATENCY: ${latencyMs}ms`;

  teleLabel.textContent = rawLabel;
  teleConfidence.textContent = `${confNum.toFixed(4)} (${confPct}%)`;
  teleScore.textContent = scoreNum.toFixed(4);

  if (result.tokens_mapped !== undefined) {
    telePadding.textContent = `200 TOKENS (${result.tokens_mapped} MAPPED)`;
  } else {
    telePadding.textContent = "200 TOKENS (IMDB_WORD_INDEX)";
  }

  message.className = "message is-ok";
  message.textContent = `STATUS: 200 OK — ${isMixed ? "Mixed" : (isPositive ? "Positive" : "Negative")} sentiment classification complete.`;

  renderDrivers(result.drivers, textarea.value, isPositive);
}

function resetResult() {
  scorePanel.classList.remove("is-loading", "is-positive", "is-negative", "is-mixed");
  resultLabel.textContent = "Waiting";
  resultPercent.textContent = "0.0%";
  verdictBadge.textContent = "WAITING";
  resultDetail.textContent = "Submit a review to measure its critical weight.";
  resultMeta.textContent = "SCORE: — // THRESHOLD: >= 0.50 // LATENCY: —";
  meterFill.style.width = "0%";
  driverChips.innerHTML = '<span class="driver-chip is-muted">awaiting review input</span>';

  teleLabel.textContent = "Waiting";
  teleConfidence.textContent = "—";
  teleScore.textContent = "—";
  telePadding.textContent = "200 TOKENS (IMDB_WORD_INDEX)";

  message.textContent = "";
  message.className = "message";

  sampleCards.forEach((card) => card.classList.remove("is-active"));
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;

  const isDark = next === "dark";

  if (themeLabel) {
    themeLabel.textContent = isDark ? "PAPER LIGHT" : "SCREENING DARK";
  }

  if (brandMarkImg) {
    const src = isDark ? brandMarkImg.dataset.darkSrc : brandMarkImg.dataset.lightSrc;
    if (src) {
      brandMarkImg.src = src;
    }
  }

  if (footerCopy) {
    footerCopy.textContent = isDark
      ? "CRITIQ VISUAL IDENTITY // 60% SCREENING INK (#09111E) • 30% LENS CYAN/TEAL (#38BDF8) • 10% VERDICT CORAL (#F04E2A)"
      : "CRITIQ EDITORIAL LIGHT // 60% CELLULOID PAPER (#F6F2EA) • 30% DICHROIC TEAL (#0D6E82) • 10% VERDICT CORAL (#F04E2A)";
  }
}

if (themeToggle) {
  themeToggle.addEventListener("click", toggleTheme);
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

textarea.addEventListener("input", () => {
  updateCharacterCount();
  sampleCards.forEach((card) => card.classList.remove("is-active"));
});

textarea.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    if (!submitButton.disabled) {
      if (typeof form.requestSubmit === "function") {
        form.requestSubmit();
      } else {
        submitButton.click();
      }
    }
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  message.className = "message";
  scorePanel.classList.remove("is-positive", "is-negative", "is-mixed");
  scorePanel.classList.add("is-loading");
  submitButton.disabled = true;
  submitButton.textContent = "Analyzing...";

  const startTime = performance.now();
  let response;
  let payload;

  try {
    response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ review: textarea.value }),
    });
  } catch (networkError) {
    scorePanel.classList.remove("is-loading");
    message.className = "message is-error";
    message.textContent = "Could not reach Flask. Run python app.py and open http://127.0.0.1:5000.";
    submitButton.disabled = false;
    submitButton.textContent = "Analyze Review";
    return;
  }

  const elapsedMs = performance.now() - startTime;

  try {
    payload = await response.json();
  } catch (parseError) {
    payload = { error: `HTTP ${response.status}: Failed to parse server response.` };
  }

  scorePanel.classList.remove("is-loading");
  submitButton.disabled = false;
  submitButton.textContent = "Analyze Review";

  if (!response.ok) {
    message.className = "message is-error";
    message.textContent = (payload && payload.error) || "Could not analyze this review.";
    return;
  }

  setResult(payload, elapsedMs);
});

clearButton.addEventListener("click", () => {
  textarea.value = "";
  resetResult();
  updateCharacterCount();
  textarea.focus();
});

sampleCards.forEach((button) => {
  button.addEventListener("click", () => {
    sampleCards.forEach((card) => card.classList.remove("is-active"));
    button.classList.add("is-active");
    textarea.value = button.dataset.review || "";
    resetResult();
    button.classList.add("is-active");
    updateCharacterCount();
    textarea.focus();
  });
});

updateCharacterCount();
