from fastapi.testclient import TestClient
import cardioia.api as api_module
from cardioia.storage import ReadingRepository

def payload():
    return {"device_id":"esp32-test","firmware_version":"test","sequence":1,"idade_media":58,"carga_sistema":92,"tempo_espera":110,"fc_media":130,"spo2_media":86,"pa_sistolica":145,"temperatura":38.4,"densidade_eventos":8,"eventos_24h":7,"disponibilidade_recursos":20}

def test_health():
    with TestClient(api_module.app) as client:
        r=client.get('/health')
    assert r.status_code==200 and r.json()['status']=='ok'

def test_iot_ingestion_and_history(tmp_path, monkeypatch):
    monkeypatch.setattr(api_module,'repository',ReadingRepository(tmp_path/'db.sqlite'))
    with TestClient(api_module.app) as client:
        r=client.post('/api/v1/readings',json=payload())
        assert r.status_code==201
        body=r.json(); assert body['device_id']=='esp32-test'; assert body['analysis']['risk_band'] in {'BAIXO','MODERADO','ALTO'}
        h=client.get('/api/v1/readings?limit=10').json()
    assert len(h)==1 and h[0]['reading_id']==body['reading_id']

def test_rejects_invalid_sensor_payload():
    p=payload();p['spo2_media']=120
    with TestClient(api_module.app) as client:r=client.post('/api/v1/readings',json=p)
    assert r.status_code==422
