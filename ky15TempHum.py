from machine import Pin
import dht
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines
dht_pin = Pin(4)  # GPIO4 para el sensor DHT11 (KY-015)
sensor_dht = dht.DHT11(dht_pin)

# Configuración WiFi
WIFI_SSID = "DESKTOP-BVQOQ56 7592"
WIFI_PASSWORD = "Popeye08"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_dht11"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "postgres/sensors"  # Publicará solo un número (temperatura o humedad)

# Variables de control
errores_conexion = 0

def conectar_wifi():
    """Conecta el ESP32 a la red WiFi."""
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    
    print("\n[INFO] WiFi Conectada!")
    print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")

def conectar_mqtt():
    """Conecta a MQTT y maneja reconexiones."""
    global errores_conexion
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        errores_conexion = 0
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        errores_conexion += 1
        return None

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# Bucle principal
while True:
    try:
        # Verificar conexión WiFi
        if not network.WLAN(network.STA_IF).isconnected():
            print("[ERROR] WiFi desconectado, reconectando...")
            conectar_wifi()
            client = conectar_mqtt()

        # Verificar conexión MQTT
        if client is None:
            print("[ERROR] MQTT desconectado, reconectando...")
            client = conectar_mqtt()
            time.sleep(5)
            continue

        # Leer datos del sensor DHT11
        try:
            sensor_dht.measure()
            temperatura = sensor_dht.temperature()  # Temperatura en °C

            # Publicar solo la temperatura en MQTT
            mensaje = str(temperatura)  # Enviar solo la temperatura como string

            # Publicar en MQTT
            client.publish(MQTT_TOPIC_SENSOR, mensaje)
            print(f"[INFO] Publicado en {MQTT_TOPIC_SENSOR}: {mensaje}")

        except Exception as e:
            print(f"[ERROR] Error al leer DHT11: {e}")

        # Si hay demasiados errores, reiniciar conexiones
        if errores_conexion >= 10:
            print("[ERROR] Demasiados errores, reiniciando conexiones...")
            conectar_wifi()
            client = conectar_mqtt()
            errores_conexion = 0

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(5)  # Esperar 5 segundos antes de la siguiente lectura
