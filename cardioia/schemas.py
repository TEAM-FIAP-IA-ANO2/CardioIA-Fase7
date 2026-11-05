"""Contratos de entrada, saída, telemetria e auditoria do CardioIA."""
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RiskBand = Literal["BAIXO", "MODERADO", "ALTO"]

class PatientData(BaseModel):
    """Entrada sintética validada do experimento."""
    model_config = ConfigDict(extra="forbid")
    idade_media: float = Field(ge=18, le=120)
    carga_sistema: float = Field(ge=0, le=100)
    tempo_espera: float = Field(ge=0, le=1440)
    fc_media: float = Field(ge=20, le=250)
    spo2_media: float = Field(ge=0, le=100)
    pa_sistolica: float = Field(ge=30, le=300)
    temperatura: float = Field(ge=0, le=50)
    densidade_eventos: int = Field(ge=0, le=10000)
    eventos_24h: int = Field(ge=0, le=10000)
    disponibilidade_recursos: float = Field(ge=0, le=100)

class SensorReading(PatientData):
    """Payload transmitido pelo ESP32/Wokwi."""
    device_id: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9._-]+$")
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    firmware_version: str = Field(default="wokwi-1.0.0", max_length=32)
    sequence: int = Field(default=0, ge=0)

    @field_validator("captured_at")
    @classmethod
    def timezone_required(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("captured_at deve conter fuso horário")
        return value

    def patient_data(self) -> PatientData:
        keys = PatientData.model_fields.keys()
        return PatientData(**{key: getattr(self, key) for key in keys})

class RiskResult(BaseModel):
    probability: float = Field(ge=0, le=1)
    predicted_class: Literal[0, 1]
    risk_band: RiskBand
    model_name: str
    model_version: str

    @model_validator(mode="after")
    def validate_class_threshold(self):
        if self.predicted_class != int(self.probability >= 0.5):
            raise ValueError("predicted_class diverge do limiar binário 0,50")
        return self

class ProtocolRecommendation(BaseModel):
    protocol_id: str
    action: str
    reason: str
    severity: Literal["informativa", "atencao", "critica"]

class FinalResponse(BaseModel):
    execution_id: str
    probability: float = Field(ge=0, le=1)
    predicted_class: Literal[0, 1]
    risk_band: RiskBand
    protocols: list[ProtocolRecommendation]
    evidence: list[str] = Field(min_length=1)
    rationale: str = Field(min_length=30, max_length=1600)
    human_review_required: bool = True
    disclaimer: str = Field(min_length=30)

    @field_validator("protocols")
    @classmethod
    def remove_duplicates(cls, value):
        seen: set[str] = set()
        return [item for item in value if not (item.protocol_id in seen or seen.add(item.protocol_id))]

class AuditRecord(BaseModel):
    execution_id: str
    timestamp_utc: datetime
    mode: Literal["local", "agents"]
    input_fingerprint: str
    risk: RiskResult
    protocol_ids: list[str]
    output_validated: bool
    duration_ms: int = Field(ge=0)

class ReadingAnalysis(BaseModel):
    reading_id: int
    device_id: str
    captured_at: datetime
    analysis: FinalResponse

class ReadingHistoryItem(BaseModel):
    reading_id: int
    device_id: str
    captured_at: datetime
    received_at: datetime
    probability: float
    risk_band: RiskBand
    payload: PatientData

class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "cardioia-api"
    version: str
    model_loaded: bool
    database: str
