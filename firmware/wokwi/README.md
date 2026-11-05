# ESP32/Wokwi
1. Importe esta pasta no Wokwi como projeto MicroPython.
2. Copie `config.example.py` para `config.py` e configure a URL pública HTTPS da API e a mesma `CARDIOIA_DEVICE_API_KEY` do backend.
3. Inicie a simulação e mova os potenciômetros. DHT22 = temperatura; potenciômetros = FC, SpO2, pressão e carga.
4. Em execução local com Wokwi for VS Code, `host.wokwi.internal:8000` alcança o computador host.

O firmware aplica timeout operacional pelo laço, reconecta o Wi-Fi, fecha respostas HTTP e não contém segredo real.
