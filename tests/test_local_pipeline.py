import json
from pathlib import Path

from cardioia.audit import read_records
from cardioia.local_pipeline import run_local
from cardioia.schemas import FinalResponse, PatientData

ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_local(tmp_path):
    patient = PatientData.model_validate_json((ROOT / "examples" / "caso_alto.json").read_text(encoding="utf-8"))
    audit = tmp_path / "audit.jsonl"
    response = run_local(patient, ROOT, audit_path=audit, execution_id="test-e2e")
    assert isinstance(response, FinalResponse)
    assert response.execution_id == "test-e2e"
    assert response.human_review_required is True
    assert response.protocols
    records = read_records(audit)
    assert len(records) == 1
    assert records[0]["output_validated"] is True
    assert len(records[0]["input_fingerprint"]) == 64


def test_low_case_has_no_objective_protocol(tmp_path):
    patient = PatientData.model_validate_json((ROOT / "examples" / "caso_baixo.json").read_text(encoding="utf-8"))
    response = run_local(patient, ROOT, audit_path=tmp_path / "audit.jsonl", execution_id="test-low")
    assert response.risk_band == "BAIXO"
    assert response.protocols == []
