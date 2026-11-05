"""Motor determinístico para a base estruturada de protocolos sintéticos."""

import json
from functools import lru_cache
from pathlib import Path

from .schemas import PatientData, ProtocolRecommendation, RiskResult


@lru_cache(maxsize=4)
def load_protocols(path: str) -> list[dict]:
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(content, list) or len(content) < 10:
        raise ValueError("protocolos.json deve conter ao menos dez regras estruturadas.")
    return content


def _active_rules(patient: PatientData, risk: RiskResult) -> dict[str, bool]:
    return {
        "P01": patient.spo2_media < 88,
        "P02": patient.carga_sistema > 85,
        "P03": patient.fc_media > 120,
        "P04": patient.eventos_24h > 5,
        "P05": patient.disponibilidade_recursos < 30,
        "P06": patient.tempo_espera > 90,
        "P07": patient.temperatura > 38,
        "P08": patient.densidade_eventos > 6,
        "P09": patient.pa_sistolica < 90,
        "P10": risk.risk_band == "ALTO",
    }


def select_protocols(
    patient: PatientData,
    risk: RiskResult,
    protocols_path: Path,
) -> list[ProtocolRecommendation]:
    rules = load_protocols(str(protocols_path.resolve()))
    active = _active_rules(patient, risk)
    selected = [ProtocolRecommendation.model_validate(rule) for rule in rules if active.get(rule["protocol_id"], False)]
    return selected
