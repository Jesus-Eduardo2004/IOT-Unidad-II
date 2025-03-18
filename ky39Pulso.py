import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky039"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

SENSOR_PIN = 34  # Pin donde está conectado el sensor de pulso (ajusta según tu conexión)

def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        time.sleep(0.5)

def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        return client
    except:
        return None

def contar_pulsos(pin):
    count = 0
    while pin.value() == 1:
        count += 1
        time.sleep_ms(1)  # Pequeña pausa para estabilizar la lectura
    return count

def medir_pulso():
    sensor = Pin(SENSOR_PIN, Pin.IN)
    pulsos = 0
    tiempo_inicial = time.time()
    while time.time() - tiempo_inicial < 10:  # Medir durante 10 segundos
        if sensor.value() == 1:
            pulsos += 1
        time.sleep_ms(5)

    frecuencia_cardíaca = pulsos * 6  # Frecuencia cardíaca por minuto (pulsos por 6)
    return frecuencia_cardíaca

conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        frecuencia = medir_pulso()  # Mide la frecuencia cardíaca
        client.publish(MQTT_TOPIC, f"Frecuencia cardíaca: {frecuencia} BPM")
        print(f"Frecuencia cardíaca: {frecuencia} BPM")
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
