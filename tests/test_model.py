from pathlib import Path

import pytest

from cardioia.model_service import classify_band, predict
from cardioia.schemas import PatientData

ROOT = Path(__file__).resolve().parents[1]


def patient_high():
    return PatientData.model_validate_json((ROOT / "examples" / "caso_alto.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("value,expected", [(0.0, "BAIXO"), (0.2999, "BAIXO"), (0.30, "MODERADO"), (0.6999, "MODERADO"), (0.70, "ALTO"), (1.0, "ALTO")])
def test_classify_boundaries(value, expected):
    assert classify_band(value) == expected


def test_real_artifact_prediction_is_valid():
    result = predict(patient_high(), ROOT / "artifacts")
    assert 0 <= result.probability <= 1
    assert result.predicted_class in (0, 1)
    assert result.risk_band in ("BAIXO", "MODERADO", "ALTO")
