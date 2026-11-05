from datetime import datetime,timezone
import pytest
from pydantic import ValidationError
from cardioia.schemas import SensorReading

def base():return dict(device_id='esp32-01',captured_at=datetime.now(timezone.utc),idade_media=58,carga_sistema=40,tempo_espera=20,fc_media=72,spo2_media=98,pa_sistolica=120,temperatura=36.5,densidade_eventos=1,eventos_24h=0,disponibilidade_recursos=80)
def test_sensor_to_patient():
    r=SensorReading(**base());assert r.patient_data().fc_media==72 and 'device_id' not in r.patient_data().model_dump()
def test_device_id_is_restricted():
    x=base();x['device_id']='id inválido';
    with pytest.raises(ValidationError):SensorReading(**x)
