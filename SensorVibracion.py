import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky002"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

VIBRATION_SENSOR_PIN = 5
vibration_sensor = Pin(VIBRATION_SENSOR_PIN, Pin.IN)

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

conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        if vibration_sensor.value() == 1:
            mensaje = "Vibración detectada"
            client.publish(MQTT_TOPIC, mensaje)

        time.sleep(0.1)

    except Exception as e:
        time.sleep(2)
