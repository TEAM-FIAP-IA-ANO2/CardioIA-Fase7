from datetime import datetime,timezone
from cardioia.schemas import SensorReading
from cardioia.local_pipeline import run_local
from cardioia.storage import ReadingRepository
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_storage_roundtrip(tmp_path):
    reading=SensorReading(device_id='device-1',captured_at=datetime.now(timezone.utc),idade_media=58,carga_sistema=40,tempo_espera=20,fc_media=72,spo2_media=98,pa_sistolica=120,temperatura=36.5,densidade_eventos=1,eventos_24h=0,disponibilidade_recursos=80)
    analysis=run_local(reading.patient_data(),ROOT,audit_path=tmp_path/'audit.jsonl')
    repo=ReadingRepository(tmp_path/'db.sqlite');rid=repo.save(reading,analysis)
    latest=repo.latest_analysis();assert latest and latest[0]==rid and latest[1].device_id=='device-1'
