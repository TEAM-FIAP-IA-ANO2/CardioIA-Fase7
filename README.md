# CardioIA 2.0 — solução integrada IoT + IA + Web + Mobile

Fluxo completo: **Sensor ESP32 no Wokwi → MicroPython → FastAPI/Python → modelo preditivo + agentes/LLM → classificação e recomendação → React Web/Vercel + React Native/Expo**.

> **Uso exclusivamente acadêmico.** Dados, rótulos, limites e protocolos são sintéticos, sem validação clínica. Não usar para diagnóstico, triagem, prescrição ou decisão médica real.

## Entrega final

- Firmware MicroPython com DHT22, quatro potenciômetros, LEDs, Wi-Fi e telemetria HTTP.
- FastAPI com validação Pydantic, OpenAPI, CORS, chave de dispositivo e persistência SQLite.
- Random Forest versionado em Joblib; modo local reproduzível e modo multiagente opcional.
- Quatro agentes com handoffs, function tools, contexto compartilhado, SQLiteSession e saída estruturada.
- Motor determinístico com dez protocolos; LLM não altera probabilidade, faixa ou ações.
- React + Vite + TypeScript responsivo, configurado para Vercel.
- React Native + Expo Router + TypeScript, preparado para EAS.
- Docker/Compose, Render blueprint, CI, testes e documentação de demonstração/avaliação.

## Arquitetura

```text
ESP32/Wokwi ──HTTPS JSON──> FastAPI ──Pydantic──> modelo .joblib
                                                    │
                                      classificação BAIXO/MODERADO/ALTO
                                                    │
                          protocolos JSON <── tools/agentes opcionais
                                                    │
                              SQLite + auditoria JSONL + OpenAPI
                                                    │
                                React Web             Expo Mobile
```

Detalhes e diagrama Mermaid: `docs/ARQUITETURA_E2E.md`.

## Estrutura

```text
├── firmware/wokwi/       # ESP32, MicroPython, circuito e instruções
├── cardioia/             # domínio, ML, agentes, FastAPI e SQLite
├── artifacts/            # modelo e ordem das colunas
├── data/                 # protocolos determinísticos
├── backend/              # Dockerfile e ambiente da API
├── web/                  # React/Vite/TypeScript + Vercel
├── mobile/               # React Native/Expo Router + EAS
├── tests/                # modelo, contratos, protocolos, API e storage
├── docs/                 # arquitetura, API, avaliação, demo e troubleshooting
├── docker-compose.yml
└── render.yaml
```

## 1. Backend

Requer Python 3.11–3.13.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp backend/.env.example backend/.env
uvicorn cardioia.api:app --reload --port 8000
```

Abra `http://localhost:8000/docs` e `http://localhost:8000/health`.

### Docker

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

### CLI sem API/LLM

```bash
python -m cardioia.cli --case examples/caso_alto.json --mode local
```

### Modo multiagente

Configure `OPENAI_API_KEY` e execute `--mode agents` na CLI ou `?mode=agents` na API. O modo `local` é o padrão para permitir avaliação sem custo/chave externa.

## 2. Wokwi/MicroPython

1. Abra `firmware/wokwi` no Wokwi.
2. Copie `config.example.py` para `config.py`.
3. Configure URL pública HTTPS da API e a mesma chave de `CARDIOIA_DEVICE_API_KEY`.
4. Inicie a simulação e mova os potenciômetros.

Para execução local via extensão Wokwi for VS Code, use `http://host.wokwi.internal:8000/api/v1/readings`. O simulador web precisa de um backend público HTTPS.

## 3. React Web / Vercel

```bash
cd web
cp .env.example .env
npm install
npm run dev
npm run build
```

Na Vercel, Root Directory = `web` e variável `VITE_API_URL=https://SEU-BACKEND`. Adicione a origem final à variável `CARDIOIA_CORS_ORIGINS` do backend.

## 4. React Native / Expo

```bash
cd mobile
cp .env.example .env
npm install
npx expo start
npm run typecheck
```

Em dispositivo físico, use IP LAN ou backend HTTPS em `EXPO_PUBLIC_API_URL`; `localhost` aponta para o próprio celular. Para build, configure o projeto EAS e execute `eas build --profile preview`.

## 5. Testes e validação

```bash
pytest -q
cd web && npm ci && npm run build
cd ../mobile && npm ci && npm run typecheck
```

Smoke test com API ativa: `python scripts/smoke_e2e.py`.

## Modelo e decisão

O experimento original usa 5.000 amostras sintéticas, split 80/20 estratificado e `random_state=42`. Foram comparadas Regressão Logística e Random Forest. O artefato selecionado foi Random Forest, com matriz `[[734,0],[1,265]]` no conjunto sintético de teste. O resultado elevado decorre do alvo baseado nos próprios atributos e **não demonstra eficácia clínica**.

A probabilidade gera faixas acadêmicas: `<0,30 = BAIXO`, `<0,70 = MODERADO`, caso contrário `ALTO`. Recomendações vêm apenas das regras de `data/protocolos.json`.

## Segurança, ética e limites

- Nenhuma chave real é versionada; `.env` e `firmware/wokwi/config.py` ficam fora do Git.
- Payloads têm validação estrita; o sensor pode exigir `X-Device-Key`.
- CORS é explícito; container usa usuário não-root.
- Auditoria grava fingerprint SHA-256, não uma cópia adicional dos dados na trilha JSONL.
- Revisão humana é sempre obrigatória.
- Uso real exigiria dados autorizados, consentimento, criptografia/identidade robusta, validação externa, calibração, avaliação de vieses, drift, segurança e governança clínica.

## Evidências para avaliação

Consulte `docs/MATRIZ_CRITERIOS_FINAL.md` e `docs/GUIA_DEMONSTRACAO.md`. A API expõe o contrato em `/openapi.json`.

## Equipe

- Felipe Almeida — RM 562434 — `@Febdev27`
- Vinícius Burchert Vilas Boas — RM 565395 — `@Vburchert`
- Renan Wesler Nunes — RM 562839 — `@W-Nunes`

Projeto acadêmico FIAP.
