# VisiDot

*[中文说明 →](README.zh-CN.md)*

An offline, single-file web app for **color vision self-testing** and **color-plate review**, built around Ishihara-style pseudoisochromatic plates. Pure HTML/CSS/JS — no build step, no framework, no backend.

VisiDot has two pages:

| Page | File | Purpose |
|------|------|---------|
| **Review Console** | `index.html` | Browse plates in a gallery, inspect each one full-screen, apply red/green filter masks, edit the recorded key figure, mark plates as reviewed, and export the answer key as JSON. |
| **Vision Quiz** | `quiz.html` | Take a quiz in **Practice** (untimed, instant feedback, filter-mask aids) or **Exam** mode (randomized, per-question timer, scored report with per-question review). |

Both pages share one calm "wellness-light" design system (cyan + health-green palette, Raleway/Lora typography) and adapt across desktop and mobile layouts.

## Features

- **Filter masks** — red/green multiply overlays with temperature / tint / opacity sliders, to aid plate discrimination.
- **Platform-adaptive UI** — the review console detects platform and switches between a web two-pane console and native-style iOS / Android shells. Preview any shell on desktop with `?platform=ios|android|web`.
- **Colorblind-safe UI** — categories are conveyed by icon + text, never color alone.
- **Accessibility** — keyboard shortcuts, focus states, `prefers-reduced-motion` support, AA-contrast text.
- **Offline-first** — everything runs from static files; no network calls, no tracking.

## Quick start

Requires **Python 3** (standard library only).

```bash
python serve.py
```

This starts a local static server on `http://127.0.0.1:8770/` and opens the quiz page in your browser.

Platform launchers:

- **Windows** — double-click `启动.bat`
- **Ubuntu / Linux** — run `./start.sh` (make it executable once with `chmod +x start.sh`)

Any static file server works too — e.g. `python -m http.server`.

## Plate images (not included)

The plate scans are **not distributed with this repository** — they are copyrighted medical test material. The app expects them under:

```
v5/v5-<page>-areal.webp
v6/v6-<page>-areal.webp
```

Supply your own plate images at those paths. The page-to-answer mappings the app reads live in:

- `data.js` — review-console plate list (`window.PLATE_DATA`)
- `quiz-data.js` — quiz answer key (`window.QUIZ_KEY`), which builds the quiz bank

See `reference/` for the answer-key JSON and page maps used to generate those data files.

## Project layout

```
index.html        Review console (single-page app)
quiz.html         Vision quiz (single-page app)
data.js           Review-console plate data
quiz-data.js      Quiz answer key + bank builder
app-icon.png      App icon / favicon
serve.py          Local static server (auto-opens browser, graceful shutdown)
启动.bat          Windows one-click launcher
start.sh          Ubuntu / Linux launcher
reference/        Answer-key JSON and page-map notes (not runtime dependencies)
v5/ v6/           Plate images — provide your own (git-ignored)
```

## Keyboard shortcuts

**Review console:** `←`/`→` prev/next plate · `G`/`R` toggle green/red mask · `F` jump to next flagged.
**Quiz:** `1`–`4` pick an option · `Enter` next question.

## Disclaimer

VisiDot is a self-testing and practice tool for fun and familiarization. **It is not a medical device and cannot replace a professional color vision examination.** Screen rendering alters colors; consult an eye-care professional for any color vision concerns.

## License

No license is granted for the bundled plate images (they are excluded from this repository). Application code (HTML/CSS/JS/Python) may be used under the terms you choose to add — add a `LICENSE` file before publishing.
