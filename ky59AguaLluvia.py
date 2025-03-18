import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky059"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

SENSOR_PIN = 34  # Pin donde está conectado el sensor de agua (ajusta según tu conexión)

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

def leer_nivel_agua():
    sensor = ADC(Pin(SENSOR_PIN))
    sensor.atten(ADC.ATTN_0DB)  # Rango de 0 a 3.3V
    sensor.width(ADC.WIDTH_12BIT)  # Resolución de 12 bits
    lectura = sensor.read()  # Valor analógico entre 0 y 4095
    # Convertir la lectura a un porcentaje de inmersión (suponiendo que el valor 0 es completamente mojado)
    porcentaje = (lectura / 4095) * 100
    return porcentaje

conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        porcentaje_agua = leer_nivel_agua()  # Lee el nivel de agua del sensor
        client.publish(MQTT_TOPIC, f"Nivel de agua: {porcentaje_agua}%")
        print(f"Nivel de agua: {porcentaje_agua}%")
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
