import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky016"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

RED_PIN = 25
GREEN_PIN = 26
BLUE_PIN = 27

red = Pin(RED_PIN, Pin.OUT)
green = Pin(GREEN_PIN, Pin.OUT)
blue = Pin(BLUE_PIN, Pin.OUT)

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

def cambiar_color(r, g, b):
    red.value(r)
    green.value(g)
    blue.value(b)
    mensaje = f"Color cambiado a: R{r} G{g} B{b}"
    client.publish(MQTT_TOPIC, mensaje)

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        cambiar_color(1, 0, 0)
        time.sleep(2)
        cambiar_color(0, 1, 0)
        time.sleep(2)
        cambiar_color(0, 0, 1)
        time.sleep(2)

    except Exception as e:
        time.sleep(2)
