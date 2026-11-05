from pathlib import Path

import pytest

from cardioia.protocol_service import select_protocols
from cardioia.schemas import PatientData, RiskResult

ROOT = Path(__file__).resolve().parents[1]
PROTOCOLS = ROOT / "data" / "protocolos.json"


def patient(**changes):
    data = {
        "idade_media": 35, "carga_sistema": 50, "tempo_espera": 30,
        "fc_media": 80, "spo2_media": 98, "pa_sistolica": 120,
        "temperatura": 36.6, "densidade_eventos": 1, "eventos_24h": 0,
        "disponibilidade_recursos": 90,
    }
    data.update(changes)
    return PatientData(**data)


def risk(band="MODERADO"):
    probability = {"BAIXO": 0.1, "MODERADO": 0.5, "ALTO": 0.8}[band]
    return RiskResult(probability=probability, predicted_class=int(probability >= 0.5), risk_band=band, model_name="Teste", model_version="1")


@pytest.mark.parametrize("changes,protocol_id", [
    ({"spo2_media": 87.9}, "P01"), ({"carga_sistema": 85.1}, "P02"),
    ({"fc_media": 120.1}, "P03"), ({"eventos_24h": 6}, "P04"),
    ({"disponibilidade_recursos": 29.9}, "P05"), ({"tempo_espera": 90.1}, "P06"),
    ({"temperatura": 38.1}, "P07"), ({"densidade_eventos": 7}, "P08"),
    ({"pa_sistolica": 89.9}, "P09"),
])
def test_protocol_boundaries(changes, protocol_id):
    ids = [p.protocol_id for p in select_protocols(patient(**changes), risk(), PROTOCOLS)]
    assert protocol_id in ids


def test_high_risk_protocol():
    ids = [p.protocol_id for p in select_protocols(patient(), risk("ALTO"), PROTOCOLS)]
    assert "P10" in ids
