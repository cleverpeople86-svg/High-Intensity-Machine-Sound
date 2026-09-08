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

The app processes microphone samples in memory. It uses browser JavaScript in the Space and NumPy in the Python version to calculate RMS loudness, dominant frequency, spectral centroid, and the ratio of energy above 2 kHz. The main monitor supports user-controlled captures; the [automatic live stream](live.html) requests microphone access on page load and refreshes its rolling score and spectrum every 500 ms without a Record action. Each completed capture produces a 0-100 screening score and a signal-quality confidence value, updates the visible result, appends a timestamped detection event, and can be exported as CSV. These features produce a heuristic risk score; this is not a certified acoustic exposure measurement or a trained classifier. Recordings are not persisted or uploaded by the application.

## CI/CD and deployment

GitHub Actions runs the verification job on pushes and pull requests. A successful verification is required before the `deploy` job pushes the repository to `CleverPeople/HighIntensityMachine`. Add a repository secret named `HF_TOKEN` with write scope. The Space is configured as static so it does not request `cpu-basic`; Gradio and Docker Spaces require a paid Hugging Face plan for new compute-backed deployments.

The assignment also requires evidence of a failed workflow that was fixed. Capture the Actions run URL and a screenshot after intentionally testing a safe failure (for example, a temporary missing required-file check), then record both in `docs/ci-failure-evidence.md`.
