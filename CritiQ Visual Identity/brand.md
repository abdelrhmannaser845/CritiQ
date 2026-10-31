# CritiQ: Brand Guidelines

> Read between the frames.

CritiQ is a movie review sentiment analysis web application that transforms raw written film criticism into a real-time polarity verdict and confidence score using TensorFlow and Flask.

## 1. Brand idea

**The Refracting Aperture:** Film criticism is more than a star rating—it is an emotional signal woven into language. CritiQ works like a precision cinema lens in reverse: it takes wide, unstructured paragraphs of critical prose, focuses their vocabulary into a single central point of meaning, and projects a sharp, unmistakable beam of sentiment polarity.

The visual identity balances **editorial cinema warmth** (archival celluloid paper, screening-room ink, marquee gold) with **analytical optical precision** (dichroic lens teal, exact circular geometry, monospace telemetry). It is incisive, cinematic, and lucid—never novelty theater kitsch (no popcorn or clapperboards), never generic AI-sparkle hype, and never sterile corporate SaaS.

## 2. Logo

| File | Use |
|---|---|
| `logo/critiq-mark.svg` | Mark alone, light backgrounds |
| `logo/critiq-mark-on-dark.svg` | Mark alone, dark backgrounds |
| `logo/critiq-mark-mono-ink.svg` / `-mono-white.svg` | One-color uses (stamps, embossing, watermarks) |
| `logo/critiq-logo.svg` / `-on-paper.svg` / `-on-dark.svg` | Horizontal lockups (transparent, light, and dark grounds) |
| `logo/critiq-app-icon.svg` | App icon, GitHub repo avatar, web favicon |
| `logo/critiq.ico` | Multi-size Windows & browser icon (16 to 256 px) |
| `social/critiq-social-banner.png` | Social preview & OpenGraph card, 1280×640 |

High-resolution PNG exports are included alongside every SVG. All typography in the SVG files is converted to vector outlines, so no installed font is required to render or view them.

**Construction:** The mark combines three optical primitives that form a monogram uniting **C** and **Q**:
1. **The C-Lens Ring:** A G1-smooth tapered circular aperture (`286°` sweep opening at `42°` in the lower-right quadrant).
2. **The Focal Core:** A circular node at the optical center representing pooled sequence embedding.
3. **The Q-Beam:** An expanding projector light cone emerging through the `42°` aperture that acts simultaneously as a spotlight beam, a sentiment needle, and the tail of the **Q**.

**Clear space:** Maintain a minimum clear margin around the mark equal to **2× the diameter of the central focal core** (`~10%` of the mark's total height) on all sides.
**Minimum size:** Mark alone `16 px` tall; horizontal lockup `96 px` wide.

**Don't:**
- Do not rotate the Q-beam to a different angle or connect the central focal dot to the beam (their separation keeps the mark legible at `16 px` and prevents it from reading as a speedometer dial).
- Do not recolor the projector beam in a cool/muted shade on multi-color lockups—it must always carry the warm accent (`#F04E2A` or `#FFC857` on teal tiles).
- Do not set the wordmark in all-uppercase (`CRITIQ`) or all-lowercase (`critiq`); always preserve the camel-capped **`CritiQ`** silhouette so the terminal **`Q`** echoes the mark.
- Do not add drop shadows, neon outer glows, or multi-stop rainbow gradients to the mark.

## 3. Color

| Name | Hex | Role |
|---|---|---|
| Dichroic Teal | `#0D6E82` | Primary brand color (lens ring on light, app icon tile) |
| Verdict Coral | `#F04E2A` | The one hot accent (projector beam, decisive callouts, used once per layout) |
| Marquee Gold | `#FFC857` | Highlight accent on Primary Dichroic Teal tiles & neutral/mixed band indicator |
| Projector Cyan | `#38BDF8` | Luminous primary for dark screening-room backgrounds |
| Screening Ink | `#09111E` | Dark ground and primary text on light surfaces |
| Celluloid Paper | `#F6F2EA` | Warm archival light ground and primary text on dark surfaces |
| Editorial Slate | `#475569` | Secondary body copy and metadata on light surfaces (`#94A3B8` Silver Halide on dark) |

**Proportions:** **60%** Ground (`#09111E` Screening Ink in dark UI or `#F6F2EA` Celluloid Paper in editorial/docs), **30%** Lens Primary (`#38BDF8` on dark / `#0D6E82` on light), **10%** Verdict Accent (`#F04E2A` / `#FFC857`).

**WCAG Contrast Checks:**
- `Screening Ink (#09111E)` on `Celluloid Paper (#F6F2EA)`: **16.94:1** (AAA text & graphics pass)
- `Projector Cyan (#38BDF8)` on `Screening Ink (#09111E)`: **8.83:1** (AAA text & graphics pass)
- `Silver Halide (#94A3B8)` on `Screening Ink (#09111E)`: **7.37:1** (AAA text pass)
- `Editorial Slate (#475569)` on `Celluloid Paper (#F6F2EA)`: **6.79:1** (AA text pass)
- `Dichroic Teal (#0D6E82)` on `Celluloid Paper (#F6F2EA)`: **5.27:1** (AA text & graphics pass)
- `Verdict Coral (#F04E2A)` on `Screening Ink (#09111E)`: **5.25:1** (AA text & graphics pass)
- `Marquee Gold (#FFC857)` on `Dichroic Teal (#0D6E82)`: **3.82:1** (AA large text & graphics pass)
- `Verdict Coral (#F04E2A)` on `Celluloid Paper (#F6F2EA)`: **3.23:1** (AA large text & graphics pass)

## 4. Typography

- **Space Grotesk Bold (700) & Medium (500):** Wordmark (`CritiQ`, tracked at `-0.03em`) and display headlines (`-0.02em` tracking). Its geometric circular bowls and distinctive stepped tail on the uppercase `Q` pair directly with the Refracting Aperture mark.
- **Plus Jakarta Sans Medium (500) & Bold (700):** Body copy, review input text, and UI controls. Warm, high-x-height legibility for long-form film reviews.
- **JetBrains Mono Medium (500):** Sentiment confidence percentages (`84.2%`), polarity labels, character counts, and API telemetry (`+0.04em` to `+0.08em` tracking in uppercase eyebrows).
- **Fallback:** `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`. All three fonts are open-source and available on Google Fonts.

## 5. Motion, pattern and icons

- **Motion language:** When a user submits a review (`is-loading`), the C-lens ring gently breathes in opacity while the central focal dot pulses; once the score returns, the projector beam expands outward along its `42°` axis with a brisk deceleration curve (`cubic-bezier(0.22, 1, 0.36, 1)`), mirroring the live sentiment meter bar.
- **Graphic device & pattern:** A subtle `44×44 px` optical calibration grid (`1 px` lines at `4.5%` opacity) paired with an oversized, low-contrast watermark crop (`8%` lighter than the ground) of the Refracting Aperture positioned at the right edge of hero banners.
- **Icon style:** Built from `2 px` rounded strokes with a single accent dot or `42°` angled cut, matching the geometry of the main mark.

## 6. Voice

CritiQ speaks like a sharp film editor with a signal analyzer: concise, observational, and grounded in what the text actually says.

1. **Describe the critical signal, not the neural plumbing.**
   - **Yes:** *"84% confidence — strong positive pulse across 142 words."*
   - **No:** *"Our revolutionary deep learning AI neural network processed your tokens!"*
2. **Pair editorial poise with exact numbers.**
   - **Yes:** *"Read between the frames. Paste any review to measure its critical weight."*
   - **No:** *"Super-fast sentiment checker tool for movie fans!"*
3. **Be direct and actionable when input falls short.**
   - **Yes:** *"Enter at least 3 words so CritiQ can catch the tone of your review."*
   - **No:** *"Invalid input error 400: minimum word threshold not met."*

## 7. Usage

- **GitHub Repository & Social Preview:** Upload `social/critiq-social-banner.png` (`1280×640`) under Repository Settings → Social Preview, and use `logo/critiq-app-icon.png` for organization/app avatars.
- **README Header:** Embed `logo/critiq-logo-on-dark.svg` (or `social/critiq-social-banner.png`) at the top of `readme.md` at `640 px` to `800 px` display width.
- **Flask Web App (`templates/index.html`):** Link `logo/critiq-app-icon.svg` and `logo/critiq.ico` as the page `<link rel="icon">`, and place `logo/critiq-mark-on-dark.svg` beside the `CritiQ` hero heading.
