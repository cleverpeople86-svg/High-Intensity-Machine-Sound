"""Live microphone analysis for high-intensity machine sound."""

import csv
import tempfile
from datetime import datetime, timezone

import gradio as gr
import numpy as np


APP_TITLE = "High Intensity Machine Sound Monitor"
DEFAULT_THRESHOLD = 70
EVENT_FIELDS = ["timestamp", "score", "severity", "dominant_frequency_hz", "rms_db", "spectral_centroid_hz"]


def _as_mono_float(samples: np.ndarray) -> np.ndarray:
    values = np.asarray(samples)
    if values.ndim > 1:
        values = values.mean(axis=1)
    if np.issubdtype(values.dtype, np.integer):
        values = values.astype(np.float32) / np.iinfo(values.dtype).max
    else:
        values = values.astype(np.float32)
    return np.nan_to_num(values)


def calculate_features(audio: tuple[int, np.ndarray]) -> dict[str, float]:
    """Extract stable, interpretable features from a Gradio numpy audio tuple."""
    sample_rate, samples = audio
    signal = _as_mono_float(samples)
    if signal.size == 0:
        raise ValueError("The recording contained no samples.")

    window = np.hanning(signal.size)
    spectrum = np.abs(np.fft.rfft(signal * window))
    frequencies = np.fft.rfftfreq(signal.size, 1 / sample_rate)
    magnitudes = spectrum[1:]
    frequency_bins = frequencies[1:]
    if magnitudes.size == 0 or not np.any(magnitudes):
        dominant_frequency = 0.0
        centroid = 0.0
    else:
        dominant_frequency = float(frequency_bins[int(np.argmax(magnitudes))])
        centroid = float(np.sum(frequency_bins * magnitudes) / np.sum(magnitudes))

    rms = float(np.sqrt(np.mean(signal**2)))
    rms_db = float(20 * np.log10(max(rms, 1e-6)))
    high_frequency_ratio = float(
        np.sum(magnitudes[frequency_bins >= 2000]) / max(np.sum(magnitudes), 1e-9)
    )
    return {
        "rms_db": rms_db,
        "dominant_frequency_hz": dominant_frequency,
        "spectral_centroid_hz": centroid,
        "high_frequency_ratio": high_frequency_ratio,
    }


def score_features(features: dict[str, float], threshold: int) -> tuple[int, str]:
    """Convert audio features into a heuristic alert score, 0-100."""
    loudness = np.clip((features["rms_db"] + 55) / 35 * 55, 0, 55)
    high_frequency = np.clip(features["high_frequency_ratio"] * 45, 0, 45)
    score = int(np.clip(round(loudness + high_frequency), 0, 100))
    severity = "ALERT" if score >= threshold else "NORMAL"
    return score, severity


def _write_csv(events: list[dict]) -> str | None:
    if not events:
        return None
    output = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", prefix="machine-sound-", delete=False, newline="")
    with output:
        writer = csv.DictWriter(output, fieldnames=EVENT_FIELDS)
        writer.writeheader()
        writer.writerows(events)
    return output.name


def analyze_audio(audio: tuple[int, np.ndarray] | None, threshold: int, events: list[dict] | None):
    events = list(events or [])
    if audio is None:
        return "### Waiting for microphone input\nRecord a short sample to begin analysis.", events, None, f"Events: {len(events)}", events

    try:
        features = calculate_features(audio)
        score, severity = score_features(features, int(threshold))
    except (TypeError, ValueError, IndexError) as error:
        return f"### Input error\n{error}", events, None, f"Events: {len(events)}", events

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "score": score,
        "severity": severity,
        "dominant_frequency_hz": round(features["dominant_frequency_hz"], 1),
        "rms_db": round(features["rms_db"], 1),
        "spectral_centroid_hz": round(features["spectral_centroid_hz"], 1),
    }
    events.append(event)
    color = "#b42318" if severity == "ALERT" else "#067647"
    summary = (
        f"### <span style='color:{color}'>{severity}</span>\n"
        f"**Risk score: {score}/100** (alert threshold: {int(threshold)})\n\n"
        f"Dominant frequency: **{event['dominant_frequency_hz']} Hz**  \n"
        f"Loudness: **{event['rms_db']} dBFS**  \n"
        f"Spectral centroid: **{event['spectral_centroid_hz']} Hz**"
    )
    return summary, events, _write_csv(events), f"Events: {len(events)}", events


def clear_events():
    return [], [], None, "Events: 0"


with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"# {APP_TITLE}\nLive microphone screening for unusually loud or high-frequency machine sound.")
    events_state = gr.State([])
    with gr.Row():
        with gr.Column(scale=1):
            microphone = gr.Audio(sources=["microphone"], type="numpy", label="Microphone sample")
            threshold = gr.Slider(20, 95, value=DEFAULT_THRESHOLD, step=1, label="Alert threshold")
            analyze = gr.Button("Analyze sample", variant="primary")
        with gr.Column(scale=1):
            result = gr.Markdown("### Waiting for microphone input\nRecord a short sample to begin analysis.")
            event_count = gr.Markdown("Events: 0")
    with gr.Row():
        event_log = gr.JSON(label="Session event log")
        export = gr.File(label="CSV export")
    clear = gr.Button("Clear session", variant="secondary")
    gr.Markdown(
        "### How it works\n"
        "The app applies a Hann window and FFT to each recording, then combines loudness and high-frequency energy into a 0-100 screening score. "
        "This is a lightweight DSP heuristic, not a calibrated safety instrument: microphone placement, room noise, and device hardware affect the result. "
        "No recordings are stored by this app."
    )

    analyze.click(analyze_audio, [microphone, threshold, events_state], [result, event_log, export, event_count, events_state])
    clear.click(clear_events, outputs=[events_state, event_log, export, event_count])


if __name__ == "__main__":
    demo.launch()