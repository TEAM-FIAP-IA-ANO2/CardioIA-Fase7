"""Smoke test HTTP: requer a API já em execução."""
import json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
payload=json.loads((root/'examples/caso_alto.json').read_text())
payload.update(device_id='smoke-e2e',sequence=1,firmware_version='smoke')
req=urllib.request.Request('http://localhost:8000/api/v1/readings',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(req,timeout=10) as response: print(response.read().decode())
