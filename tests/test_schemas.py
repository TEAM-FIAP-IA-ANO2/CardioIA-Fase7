import pytest
from pydantic import ValidationError

from cardioia.schemas import FinalResponse, PatientData, ProtocolRecommendation, RiskResult


def valid_patient(**changes):
    data = {
        "idade_media": 45, "carga_sistema": 50, "tempo_espera": 30,
        "fc_media": 80, "spo2_media": 98, "pa_sistolica": 120,
        "temperatura": 36.5, "densidade_eventos": 2, "eventos_24h": 1,
        "disponibilidade_recursos": 80,
    }
    data.update(changes)
    return PatientData(**data)


def test_rejects_extra_field():
    with pytest.raises(ValidationError):
        valid_patient(campo_extra=1)


@pytest.mark.parametrize("field,value", [("idade_media", 17), ("spo2_media", 101), ("fc_media", 251)])
def test_rejects_ranges(field, value):
    with pytest.raises(ValidationError):
        valid_patient(**{field: value})


def test_risk_class_must_match_threshold():
    with pytest.raises(ValidationError):
        RiskResult(probability=0.8, predicted_class=0, risk_band="ALTO", model_name="X", model_version="1")


def test_final_response_deduplicates_protocols():
    protocol = ProtocolRecommendation(protocol_id="P01", action="Ação", reason="Motivo", severity="critica")
    response = FinalResponse(
        execution_id="x", probability=0.8, predicted_class=1, risk_band="ALTO",
        protocols=[protocol, protocol], evidence=["evidência"],
        rationale="Justificativa acadêmica suficientemente detalhada para validação.",
        disclaimer="Aviso acadêmico suficientemente claro e completo para validação.",
    )
    assert len(response.protocols) == 1
