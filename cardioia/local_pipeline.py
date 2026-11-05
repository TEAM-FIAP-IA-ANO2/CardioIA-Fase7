"""Pipeline local reproduzível, sem dependência de LLM ou de chave externa."""

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
import uuid

from .audit import append_record, fingerprint
from .model_service import predict
from .protocol_service import select_protocols
from .schemas import AuditRecord, FinalResponse, PatientData


DISCLAIMER = (
    "Protótipo acadêmico com dados e protocolos sintéticos, sem validação clínica. "
    "Não utilizar para diagnóstico, triagem, prescrição ou decisão médica real."
)


def run_local(
    patient: PatientData,
    project_root: Path,
    audit_path: Path | None = None,
    execution_id: str | None = None,
) -> FinalResponse:
    started = perf_counter()
    execution_id = execution_id or f"local-{uuid.uuid4().hex[:12]}"
    artifacts_dir = project_root / "artifacts"
    risk = predict(patient, artifacts_dir)
    protocols = select_protocols(patient, risk, project_root / "data" / "protocolos.json")

    evidence = [
        f"Modelo {risk.model_name} ({risk.model_version}) retornou probabilidade {risk.probability:.4f}.",
        f"Faixa {risk.risk_band} calculada pelos limites acadêmicos 0,30 e 0,70.",
        f"{len(protocols)} regra(s) objetiva(s) da base sintética foram acionadas.",
    ]
    response = FinalResponse(
        execution_id=execution_id,
        probability=risk.probability,
        predicted_class=risk.predicted_class,
        risk_band=risk.risk_band,
        protocols=protocols,
        evidence=evidence,
        rationale=(
            "O resultado combina a inferência do classificador treinado com dados sintéticos "
            "e regras determinísticas de protocolo. A IA conversacional não altera a probabilidade "
            "nem cria protocolos; a revisão humana continua obrigatória."
        ),
        human_review_required=True,
        disclaimer=DISCLAIMER,
    )

    duration_ms = int((perf_counter() - started) * 1000)
    record = AuditRecord(
        execution_id=execution_id,
        timestamp_utc=datetime.now(timezone.utc),
        mode="local",
        input_fingerprint=fingerprint(patient),
        risk=risk,
        protocol_ids=[item.protocol_id for item in protocols],
        output_validated=True,
        duration_ms=duration_ms,
    )
    append_record(audit_path or project_root / ".runtime" / "decisoes_cardioia.jsonl", record)
    return response
