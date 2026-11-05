# Roteiro de demonstração (5–7 minutos)

1. **Problema e ética (30 s):** risco sintético e apoio educacional; não é ferramenta clínica.
2. **Wokwi (60 s):** mostrar ESP32, DHT22 e potenciômetros; alterar FC/SpO2; iniciar simulação.
3. **API (45 s):** abrir `/docs`, `/health` e confirmar POST 201 em `/api/v1/readings`.
4. **ML (45 s):** explicar dez atributos, Random Forest, artefatos e limites 0,30/0,70.
5. **Agentes (60 s):** Orquestrador → Analista → Protocolos → Planejador; tools imutáveis, Pydantic e sessão.
6. **Web (60 s):** dashboard, telemetria, gráfico e simulação manual.
7. **Mobile (45 s):** atualização por pull-to-refresh e visão do risco atual.
8. **Qualidade (30 s):** testes, CI, Docker, Vercel/Expo e auditoria.
9. **Limitações (30 s):** dados sintéticos, métricas otimistas, necessidade de dados autorizados e validação externa.

## Checklist antes de gravar
- `pytest -q` verde; `npm run build` no web; `npm run typecheck` no mobile.
- backend público com HTTPS e `/health` ok.
- CORS contém o domínio da Vercel.
- `config.py` do Wokwi aponta para o backend e não será versionado.
- app web e Expo usam a mesma API.
