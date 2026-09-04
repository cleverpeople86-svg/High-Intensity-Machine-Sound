import numpy as np

from app import calculate_features, score_features


def test_calculate_features_finds_dominant_frequency():
    sample_rate = 16_000
    time = np.arange(sample_rate) / sample_rate
    audio = (sample_rate, (0.5 * np.sin(2 * np.pi * 1000 * time)).astype(np.float32))

    features = calculate_features(audio)

    assert 990 <= features["dominant_frequency_hz"] <= 1010
    assert features["rms_db"] < 0


def test_score_marks_loud_high_frequency_signal_as_alert():
    score, severity = score_features(
        {"rms_db": -10, "high_frequency_ratio": 0.9}, threshold=70
    )

    assert score >= 70
    assert severity == "ALERT"