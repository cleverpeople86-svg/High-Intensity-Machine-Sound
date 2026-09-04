---
title: Machine Sound Monitor
emoji: "🔊"
colorFrom: blue
colorTo: yellow
sdk: gradio
app_file: app.py
pinned: false
---

# Machine Sound Monitor

Machine Sound Monitor captures a short sample from a user's microphone, extracts FFT-based audio features in Python, and reports a transparent 0-100 screening score for unusually loud or high-frequency sound. The interface shows the score, confidence inputs, alert threshold, session event log, and CSV export.

**Live Space:** replace this line with your Hugging Face Space URL after deployment.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open the local URL shown by Gradio and allow microphone access. If permission is denied, the app remains usable and explains that a recording is required.

## Data and method

The app processes microphone samples in memory. It uses NumPy to calculate RMS loudness, dominant frequency, spectral centroid, and the ratio of energy above 2 kHz. Those features produce a heuristic risk score; this is not a certified acoustic exposure measurement or a trained classifier. Recordings are not persisted by the application.

## CI/CD and deployment

GitHub Actions runs the verification job on pushes and pull requests. A successful verification is required before the `deploy` job pushes the repository to Hugging Face Spaces. Add a repository secret named `HF_TOKEN` with write scope, then update the `HF_SPACE` environment variable in `.github/workflows/deploy-huggingface.yml` to your account and Space name.

The assignment also requires evidence of a failed workflow that was fixed. Capture the Actions run URL and a screenshot after intentionally testing a safe failure (for example, a temporary missing required-file check), then record both in `docs/ci-failure-evidence.md`.