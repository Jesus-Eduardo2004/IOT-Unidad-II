import time
import network
from machine import Pin
from umqtt.simple import MQTTClient
import math

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_hcsr04"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

TRIGGER_PIN = 5  # Pin del Trigger del sensor ultrasónico (ajusta según tu conexión)
ECHO_PIN = 18    # Pin del Echo del sensor ultrasónico (ajusta según tu conexión)

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

def medir_distancia():
    trigger = Pin(TRIGGER_PIN, Pin.OUT)
    echo = Pin(ECHO_PIN, Pin.IN)
    
    # Enviar pulso de disparo
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    # Medir el tiempo que tarda el eco en regresar
    while echo.value() == 0:
        pulse_start = time.ticks_us()

    while echo.value() == 1:
        pulse_end = time.ticks_us()

    # Calcular la distancia en centímetros
    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    distancia = (pulse_duration / 2) / 29.1  # 29.1 es la velocidad del sonido en cm/us
    return distancia

conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        distancia = medir_distancia()  # Mide la distancia
        client.publish(MQTT_TOPIC, f"Distancia: {distancia} cm")
        print(f"Distancia: {distancia} cm")
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
