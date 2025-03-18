import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky011"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

LED_ROJO = Pin(18, Pin.OUT)
LED_VERDE = Pin(19, Pin.OUT)

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

        LED_ROJO.value(1)
        LED_VERDE.value(0)
        client.publish(MQTT_TOPIC, "LED Rojo encendido")
        time.sleep(5)

        LED_ROJO.value(0)
        LED_VERDE.value(1)
        client.publish(MQTT_TOPIC, "LED Verde encendido")
        time.sleep(5)

    except Exception as e:
        time.sleep(2)
