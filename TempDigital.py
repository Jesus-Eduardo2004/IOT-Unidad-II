import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky028"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

TEMP_SENSOR_PIN = 34
temp_sensor = ADC(Pin(TEMP_SENSOR_PIN))
temp_sensor.atten(ADC.ATTN_11DB)

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

        temperatura = temp_sensor.read()
        mensaje = f"Temperatura: {temperatura}"
        client.publish(MQTT_TOPIC, mensaje)

        time.sleep(2)

    except Exception as e:
        time.sleep(2)
