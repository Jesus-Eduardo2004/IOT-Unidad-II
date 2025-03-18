import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_mq9"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors/mq9"

# Configuración del MQ-9 (Detector de Gases)
SENSOR_ANALOG_PIN = 36  # Entrada analógica (A0)
sensor = ADC(Pin(SENSOR_ANALOG_PIN))
sensor.atten(ADC.ATTN_11DB)  # Configura el rango de 0 a ~3.3V

# Variables de control
ultimo_envio = 0
INTERVALO_ENVIO = 5000  # Enviar datos cada 5 segundos

# Conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nWiFi Conectada!")

# Conectar a MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print("Conectado a MQTT")
        return client
    except:
        print("Error conectando a MQTT")
        return None

# Función para obtener tiempo en milisegundos
def millis():
    return time.ticks_ms()

# Inicialización
print("Iniciando sensor MQ-9 (Detección de CO, GLP y Metano)")
conectar_wifi()
client = conectar_mqtt()

print("Sistema listo! Midiendo calidad del aire...")

# Bucle principal
while True:
    try:
        # Verificar conexión WiFi y MQTT
        if not network.WLAN(network.STA_IF).isconnected() or client is None:
            print("Reconectando...")
            conectar_wifi()
            client = conectar_mqtt()
            time.sleep(2)
            continue

        # Leer valor analógico del MQ-9
        valor_mq9 = sensor.read()
        porcentaje = (valor_mq9 / 4095) * 100  # Convertir a porcentaje (0-100%)

        # Obtener tiempo actual
        ahora = millis()

        # Enviar datos cada INTERVALO_ENVIO ms
        if ahora - ultimo_envio > INTERVALO_ENVIO:
            mensaje = f"CO/GLP/CH4: {porcentaje:.2f}%"
            client.publish(MQTT_TOPIC, mensaje)
            print(f"Enviado: {mensaje}")
            ultimo_envio = ahora

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)

    time.sleep(0.1)  # Pequeña pausa
