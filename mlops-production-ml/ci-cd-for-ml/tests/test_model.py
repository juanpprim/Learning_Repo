"""Model-quality gate: fails CI if accuracy drops below the threshold."""
from src.train import train

MIN_ACCURACY = 0.85


def test_model_quality_gate():
    _, accuracy = train()
    assert accuracy >= MIN_ACCURACY, f"accuracy {accuracy:.4f} below gate {MIN_ACCURACY}"
