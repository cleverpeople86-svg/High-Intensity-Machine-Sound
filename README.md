---
title: Machine Sound Monitor
emoji: "🔊"
colorFrom: blue
colorTo: yellow
sdk: static
app_file: index.html
pinned: false
---
# Machine Sound Monitor

Machine Sound Monitor captures a short sample from a user's microphone, extracts FFT-based audio features in the browser, and reports a transparent 0-100 screening score for unusually loud or high-frequency sound. The static Space version runs entirely in the browser, so it does not require paid Hugging Face compute.

**Live Space:** https://huggingface.co/spaces/CleverPeople/HighIntensityMachine

## Run the Python version locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open the local URL shown by Gradio and allow microphone access. The deployed Space uses `index.html` because Hugging Face static Spaces are available on free accounts; `app.py` remains the Python reference implementation used by CI.

## Data and method

The app processes microphone samples in memory. The root page contains the automatic live stream, which requests microphone access on page load and calculates level (dBFS), dominant frequency, spectral centroid, spectral spread, spectral flatness, crest factor, 85% spectral rolloff, and baseline deviation from a saved healthy spectrum. It adds a report row every 15 seconds, exports up to 50 feature records as CSV, and keeps a timestamped five-minute WAV recording buffer for download. Audio remains in the browser and is not uploaded or persisted; the results are a transparent DSP heuristic, not a certified acoustic safety measurement or trained classifier.

## CI/CD and deployment

GitHub Actions runs the verification job on pushes and pull requests. A successful verification is required before the `deploy` job pushes the repository to `CleverPeople/HighIntensityMachine`. Add a repository secret named `HF_TOKEN` with write scope. The Space is configured as static so it does not request `cpu-basic`; Gradio and Docker Spaces require a paid Hugging Face plan for new compute-backed deployments.

The assignment also requires evidence of a failed workflow that was fixed. Capture the Actions run URL and a screenshot after intentionally testing a safe failure (for example, a temporary missing required-file check), then record both in `docs/ci-failure-evidence.md`.
