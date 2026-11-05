"""Contexto tipado compartilhado entre os agentes."""
from dataclasses import dataclass, field
from pathlib import Path
from .schemas import PatientData, ProtocolRecommendation, RiskResult

@dataclass
class CardioContext:
    execution_id: str
    project_root: Path
    patient: PatientData | None = None
    risk: RiskResult | None = None
    protocols: list[ProtocolRecommendation] = field(default_factory=list)
    stages: list[str] = field(default_factory=list)

    def require_patient(self) -> PatientData:
        if self.patient is None:
            raise RuntimeError("Entrada ainda não validada.")
        return self.patient

    def require_risk(self) -> RiskResult:
        if self.risk is None:
            raise RuntimeError("Risco ainda não calculado.")
        return self.risk
