"""API HTTP que integra ESP32/Wokwi, modelo, agentes e clientes web/mobile."""
from contextlib import asynccontextmanager
import os
import secrets
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from . import __version__
from .local_pipeline import run_local
from .model_service import load_model
from .schemas import FinalResponse, HealthResponse, PatientData, ReadingAnalysis, ReadingHistoryItem, SensorReading
from .settings import Settings
from .storage import ReadingRepository

settings = Settings.from_env()
repository = ReadingRepository(settings.database_path)

@asynccontextmanager
async def lifespan(_: FastAPI):
    load_model(str(settings.project_root / "artifacts" / "modelo_risco_cardiaco.joblib"))
    yield

app = FastAPI(title="CardioIA API", version=__version__, description="API acadêmica de telemetria e risco sintético.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Device-Key"])

def verify_device_key(x_device_key: str | None = Header(default=None)) -> None:
    if settings.device_api_key and (not x_device_key or not secrets.compare_digest(x_device_key, settings.device_api_key)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chave do dispositivo inválida")

async def analyze(patient: PatientData, mode: str) -> FinalResponse:
    if mode == "local":
        return run_local(patient, settings.project_root)
    if mode == "agents":
        from .agents_pipeline import run_agents
        return await run_agents(patient, settings.project_root)
    raise HTTPException(status_code=422, detail="mode deve ser local ou agents")

@app.get("/health", response_model=HealthResponse, tags=["operacao"])
def health() -> HealthResponse:
    return HealthResponse(version=__version__, model_loaded=True, database=str(settings.database_path))

@app.post("/api/v1/analyze", response_model=FinalResponse, tags=["analise"])
async def analyze_case(patient: PatientData, mode: str = Query(default=settings.default_mode, pattern="^(local|agents)$")) -> FinalResponse:
    return await analyze(patient, mode)

@app.post("/api/v1/readings", response_model=ReadingAnalysis, status_code=201, tags=["iot"], dependencies=[Depends(verify_device_key)])
async def ingest_reading(reading: SensorReading, mode: str = Query(default=settings.default_mode, pattern="^(local|agents)$")) -> ReadingAnalysis:
    result = await analyze(reading.patient_data(), mode)
    reading_id = repository.save(reading, result)
    return ReadingAnalysis(reading_id=reading_id, device_id=reading.device_id, captured_at=reading.captured_at, analysis=result)

@app.get("/api/v1/readings", response_model=list[ReadingHistoryItem], tags=["iot"])
def history(limit: int = Query(default=50, ge=1, le=500), device_id: str | None = None) -> list[ReadingHistoryItem]:
    return repository.history(limit, device_id)

@app.get("/api/v1/readings/latest", response_model=ReadingAnalysis, tags=["iot"])
def latest(device_id: str | None = None) -> ReadingAnalysis:
    item = repository.latest_analysis(device_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Nenhuma leitura disponível")
    reading_id, reading, result = item
    return ReadingAnalysis(reading_id=reading_id, device_id=reading.device_id, captured_at=reading.captured_at, analysis=result)
