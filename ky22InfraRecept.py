import time
import network
from machine import Pin
from umqtt.simple import MQTTClient
from ir_receiver import IRReceiver

WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

MQTT_CLIENT_ID = "esp32_ky022"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

IR_PIN = 14  # Pin donde está conectado el receptor IR (ajusta según tu conexión)

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

def ir_callback(ir_code):
    client.publish(MQTT_TOPIC, f"Código IR recibido: {ir_code}")

conectar_wifi()
client = conectar_mqtt()

ir_receiver = IRReceiver(IR_PIN)
ir_receiver.callback(ir_callback)

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        ir_receiver.listen()  # Escucha las señales IR entrantes

        time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
