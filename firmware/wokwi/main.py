"""Firmware MicroPython para ESP32 no Wokwi.
DHT22 mede temperatura; quatro potenciômetros simulam FC, SpO2, pressão e carga.
Demais atributos variam de forma controlada para demonstrar o pipeline.
"""
import gc
import json
import time
import network
import urequests
from machine import ADC, Pin
import dht
try:
    from config import API_URL, DEVICE_API_KEY, DEVICE_ID, SEND_INTERVAL_MS
except ImportError:
    from config_example import API_URL, DEVICE_API_KEY, DEVICE_ID, SEND_INTERVAL_MS

sensor_temp = dht.DHT22(Pin(15))
fc_adc = ADC(Pin(34)); spo2_adc = ADC(Pin(35)); pa_adc = ADC(Pin(32)); carga_adc = ADC(Pin(33))
led_ok = Pin(2, Pin.OUT); led_alerta = Pin(4, Pin.OUT)
sequence = 0

def scale(raw, low, high):
    return round(low + (raw / 4095) * (high - low), 1)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF); wlan.active(True)
    if not wlan.isconnected():
        wlan.connect("Wokwi-GUEST", "")
        deadline = time.ticks_add(time.ticks_ms(), 15000)
        while not wlan.isconnected() and time.ticks_diff(deadline, time.ticks_ms()) > 0:
            time.sleep_ms(250)
    if not wlan.isconnected(): raise RuntimeError("Wi-Fi indisponível")
    return wlan

def read_payload():
    global sequence
    sensor_temp.measure(); sequence += 1
    fc = scale(fc_adc.read(), 45, 155)
    spo2 = scale(spo2_adc.read(), 82, 100)
    pa = scale(pa_adc.read(), 75, 185)
    carga = scale(carga_adc.read(), 10, 100)
    return {
        "device_id": DEVICE_ID, "firmware_version": "wokwi-1.0.0", "sequence": sequence,
        "idade_media": 58, "carga_sistema": carga,
        "tempo_espera": round(10 + carga * 1.2, 1), "fc_media": fc,
        "spo2_media": spo2, "pa_sistolica": pa, "temperatura": sensor_temp.temperature(),
        "densidade_eventos": int(max(0, (fc - 70) / 10)),
        "eventos_24h": int(max(0, (100 - spo2) / 2)),
        "disponibilidade_recursos": round(max(0, 100 - carga), 1)
    }

def send(payload):
    headers = {"Content-Type": "application/json", "X-Device-Key": DEVICE_API_KEY}
    response = urequests.post(API_URL, data=json.dumps(payload), headers=headers)
    try:
        body = response.json()
        band = body.get("analysis", {}).get("risk_band", "ALTO")
        led_ok.value(band == "BAIXO"); led_alerta.value(band != "BAIXO")
        print("HTTP", response.status_code, "risco", band, "seq", payload["sequence"])
    finally:
        response.close(); gc.collect()

wifi_connect()
while True:
    try:
        send(read_payload())
    except Exception as exc:
        led_ok.value(0); led_alerta.value(1); print("erro:", exc)
        try: wifi_connect()
        except Exception: pass
    time.sleep_ms(SEND_INTERVAL_MS)
