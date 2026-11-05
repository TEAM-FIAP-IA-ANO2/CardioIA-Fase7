# API CardioIA

Base local: `http://localhost:8000`. Documentação interativa: `/docs`; OpenAPI: `/openapi.json`.

| Método | Rota | Função |
|---|---|---|
| GET | `/health` | saúde, versão, carga do modelo e banco |
| POST | `/api/v1/analyze?mode=local` | classifica um `PatientData` sem persistir telemetria |
| POST | `/api/v1/readings?mode=local` | recebe `SensorReading`, analisa e persiste |
| GET | `/api/v1/readings?limit=50&device_id=...` | histórico paginado por limite |
| GET | `/api/v1/readings/latest?device_id=...` | última análise |

Se `CARDIOIA_DEVICE_API_KEY` estiver definido, o sensor deve enviar `X-Device-Key`. O modo `agents` requer `OPENAI_API_KEY`; para demonstração reproduzível e testes, use `local`.

Exemplo:
```bash
curl -X POST http://localhost:8000/api/v1/readings \
 -H 'Content-Type: application/json' -H 'X-Device-Key: sua-chave' \
 --data-binary @examples/leitura_sensor.json
```
