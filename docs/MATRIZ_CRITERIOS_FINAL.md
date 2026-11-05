# Matriz final de critérios e evidências

| Critério | Implementação | Evidência/verificação |
|---|---|---|
| Sensor/simulação | ESP32, DHT22, 4 ADCs, LEDs, Wi-Fi e POST JSON | `firmware/wokwi/`; simulação Wokwi |
| MicroPython | leitura, escala, reconexão, fechamento HTTP e configuração externa | `firmware/wokwi/main.py` |
| Backend Python | FastAPI, OpenAPI, CORS, autenticação de dispositivo e validação | `cardioia/api.py`; `/docs`; testes API |
| Persistência | SQLite transacional e índice dispositivo/tempo | `cardioia/storage.py`; testes de roundtrip |
| Modelo preditivo | pipeline Joblib, 10 atributos, probabilidade, classificação | `artifacts/`; `model_service.py`; testes |
| Comparação de modelos | Regressão Logística x Random Forest, métricas e matriz | relatório e métricas da entrega Fase 6 |
| Agentes/LLM | quatro agentes, tools, handoffs, contexto, sessão e output Pydantic | `agents_pipeline.py`; teste de contrato |
| Recomendação | dez regras JSON determinísticas, sem `eval` | `data/protocolos.json`; testes de limites |
| Rastreabilidade | fingerprint SHA-256, execução, duração, modelo e regras | `audit.py`; `.runtime/decisoes_cardioia.jsonl` |
| React Web | dashboard responsivo, formulário, histórico e estados de erro | `web/`; `npm run build` |
| Vercel | SPA rewrite, headers e variável `VITE_API_URL` | `web/vercel.json`; `web/.env.example` |
| React Native/Expo | risco atual, métricas, histórico e refresh | `mobile/`; `npm run typecheck` |
| Segurança/ética | segredos externos, CORS, chave do sensor, não-root, disclaimers | env examples, Dockerfile, documentação |
| DevOps | Docker Compose, Render, CI backend/web/mobile | arquivos de implantação e workflow |
| Testes | schema, modelo, protocolos, pipeline, API, storage | `pytest -q` |
| Documentação | README, arquitetura, API, roteiro e troubleshooting | `README.md`; `docs/` |
