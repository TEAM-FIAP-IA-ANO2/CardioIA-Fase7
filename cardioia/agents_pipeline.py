"""Arquitetura multiagente aderente ao OpenAI Agents SDK.

O fluxo usa handoffs explícitos, function tools, contexto compartilhado,
SQLiteSession e saída Pydantic. A matemática do risco e os protocolos
permanecem determinísticos e fora do LLM.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from time import perf_counter
import uuid

from agents import Agent, Runner, RunContextWrapper, SQLiteSession, function_tool

from .audit import append_record, fingerprint
from .context import CardioContext
from .model_service import predict
from .protocol_service import select_protocols
from .schemas import AuditRecord, FinalResponse, PatientData


DISCLAIMER = (
    "Protótipo acadêmico com dados e protocolos sintéticos, sem validação clínica. "
    "Não utilizar para diagnóstico, triagem, prescrição ou decisão médica real."
)


def build_agents(model: str):
    @function_tool
    def analisar_caso(
        wrapper: RunContextWrapper[CardioContext],
        idade_media: float,
        carga_sistema: float,
        tempo_espera: float,
        fc_media: float,
        spo2_media: float,
        pa_sistolica: float,
        temperatura: float,
        densidade_eventos: int,
        eventos_24h: int,
        disponibilidade_recursos: float,
    ) -> dict:
        """Valida os dez campos e executa o artefato de Machine Learning."""
        patient = PatientData(
            idade_media=idade_media,
            carga_sistema=carga_sistema,
            tempo_espera=tempo_espera,
            fc_media=fc_media,
            spo2_media=spo2_media,
            pa_sistolica=pa_sistolica,
            temperatura=temperatura,
            densidade_eventos=densidade_eventos,
            eventos_24h=eventos_24h,
            disponibilidade_recursos=disponibilidade_recursos,
        )
        wrapper.context.patient = patient
        wrapper.context.risk = predict(patient, wrapper.context.project_root / "artifacts")
        wrapper.context.stages.extend(["entrada_validada", "risco_calculado"])
        return wrapper.context.risk.model_dump()

    @function_tool
    def consultar_protocolos(wrapper: RunContextWrapper[CardioContext]) -> list[dict]:
        """Aplica somente as regras objetivas da base sintética de protocolos."""
        patient = wrapper.context.require_patient()
        risk = wrapper.context.require_risk()
        wrapper.context.protocols = select_protocols(
            patient,
            risk,
            wrapper.context.project_root / "data" / "protocolos.json",
        )
        wrapper.context.stages.append("protocolos_consultados")
        return [item.model_dump() for item in wrapper.context.protocols]

    @function_tool
    def obter_evidencias(wrapper: RunContextWrapper[CardioContext]) -> dict:
        """Entrega ao último agente os valores imutáveis calculados pelo pipeline."""
        risk = wrapper.context.require_risk()
        if "protocolos_consultados" not in wrapper.context.stages:
            raise RuntimeError("Pipeline incompleto: protocolos ainda não consultados.")
        wrapper.context.stages.append("evidencias_consolidadas")
        return {
            "execution_id": wrapper.context.execution_id,
            "risk": risk.model_dump(),
            "protocols": [item.model_dump() for item in wrapper.context.protocols],
            "stages": wrapper.context.stages,
            "disclaimer": DISCLAIMER,
        }

    planner = Agent[CardioContext](
        name="PlanejadorResposta",
        model=model,
        instructions=(
            "Chame obter_evidencias uma vez. Produza FinalResponse sem alterar números, "
            "faixa ou protocolos. evidence deve citar o modelo, a faixa e o total de regras. "
            "Mantenha human_review_required=true e reproduza o disclaimer recebido."
        ),
        tools=[obter_evidencias],
        output_type=FinalResponse,
    )
    specialist = Agent[CardioContext](
        name="EspecialistaProtocolos",
        model=model,
        instructions=(
            "Chame consultar_protocolos exatamente uma vez. Não invente ações. "
            "Depois transfira para PlanejadorResposta."
        ),
        tools=[consultar_protocolos],
        handoffs=[planner],
    )
    analyst = Agent[CardioContext](
        name="AnalistaRisco",
        model=model,
        instructions=(
            "Copie os dez campos do JSON sem modificar e chame analisar_caso uma vez. "
            "Não calcule probabilidade manualmente. Depois transfira para EspecialistaProtocolos."
        ),
        tools=[analisar_caso],
        handoffs=[specialist],
    )
    orchestrator = Agent[CardioContext](
        name="OrquestradorCardioIA",
        model=model,
        instructions=(
            "Você coordena o CardioIA. Para qualquer caso JSON válido, transfira imediatamente "
            "para AnalistaRisco. Não produza recomendação própria."
        ),
        handoffs=[analyst],
    )
    return orchestrator


async def run_agents(
    patient: PatientData,
    project_root: Path,
    session_id: str | None = None,
    audit_path: Path | None = None,
) -> FinalResponse:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY ausente. Use --mode local ou configure .env.")

    started = perf_counter()
    execution_id = session_id or f"agents-{uuid.uuid4().hex[:12]}"
    model = os.getenv("CARDIOIA_AGENT_MODEL", "gpt-4.1-mini")
    context = CardioContext(execution_id=execution_id, project_root=project_root)
    agent = build_agents(model)

    db_path = Path(os.getenv("CARDIOIA_SESSION_DB", str(project_root / ".runtime" / "cardioia_sessions.db")))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    session = SQLiteSession(execution_id, str(db_path))
    prompt = "Execute o pipeline completo usando somente este JSON:\n" + patient.model_dump_json(indent=2)
    result = await Runner.run(agent, input=prompt, context=context, session=session)
    output = result.final_output
    response = output if isinstance(output, FinalResponse) else FinalResponse.model_validate(output)

    record = AuditRecord(
        execution_id=execution_id,
        timestamp_utc=datetime.now(timezone.utc),
        mode="agents",
        input_fingerprint=fingerprint(patient),
        risk=context.require_risk(),
        protocol_ids=[item.protocol_id for item in context.protocols],
        output_validated=True,
        duration_ms=int((perf_counter() - started) * 1000),
    )
    append_record(audit_path or project_root / ".runtime" / "decisoes_cardioia.jsonl", record)
    return response
