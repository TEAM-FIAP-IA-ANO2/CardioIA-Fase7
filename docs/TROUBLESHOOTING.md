# Troubleshooting
- **Wokwi não conecta:** use `Wokwi-GUEST`; para API local use Wokwi for VS Code e `host.wokwi.internal`, ou publique o backend HTTPS.
- **401:** `DEVICE_API_KEY` do firmware deve ser idêntica a `CARDIOIA_DEVICE_API_KEY`.
- **422:** confira os limites do schema e se todos os dez atributos foram enviados.
- **CORS no navegador:** inclua a origem exata da Vercel em `CARDIOIA_CORS_ORIGINS` e reinicie a API.
- **Expo no celular:** `localhost` é o celular; use IP LAN ou backend público HTTPS em `EXPO_PUBLIC_API_URL`.
- **Modo agents falha:** configure `OPENAI_API_KEY`; mantenha `local` como fallback reprodutível.
- **Modelo ausente:** restaure `artifacts/*.joblib` ou execute `python scripts/train_model.py`.
