import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky031"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "gds0653/ky-031"

# Configuración del sensor KY-031 (Sensor de Impacto/Golpe)
IMPACT_SENSOR_PIN = 23  # Pin digital para el sensor de impacto
impact_sensor = Pin(IMPACT_SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Pull-up para estabilidad

# LED para indicación visual
led_onboard = Pin(2, Pin.OUT)

# Variables para control de rebotes y estado
ultimo_cambio = 0
DEBOUNCE_TIME = 200  # Tiempo anti-rebote en milisegundos
ultimo_estado = None  # Para seguimiento del estado actual
ultimo_envio = 0  # Tiempo del último envío
INTERVALO_REPOSO = 5000  # Enviar estado de reposo cada 5 segundos

# Conectar a WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n[INFO] WiFi Conectada!")
    print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")

# Conectar a MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# Función para obtener tiempo en milisegundos
def millis():
    return time.ticks_ms()

# Función de interrupción para detectar impactos
def detectar_impacto(pin):
    global ultimo_cambio, client, ultimo_estado
    ahora = millis()
    # Anti-rebote para evitar detecciones falsas
    if ahora - ultimo_cambio > DEBOUNCE_TIME:
        print("¡IMPACTO DETECTADO! Valor: 1")
        led_onboard.value(1)  # Encender LED
        
        # Publicar en MQTT
        if client:
            client.publish(MQTT_TOPIC_SENSOR, "1")
            ultimo_estado = "1"
        
        ultimo_cambio = ahora

# Inicialización
print("[INFO] Iniciando sensor KY-031 (Detección de Impacto)")
print("[INFO] Golpee o mueva el sensor para detectar impactos")
conectar_wifi()
client = conectar_mqtt()

# Configurar interrupción - Detecta el flanco de bajada (cuando el sensor detecta impacto)
impact_sensor.irq(trigger=Pin.IRQ_FALLING, handler=detectar_impacto)

# Enviar estado inicial de reposo
if client:
    client.publish(MQTT_TOPIC_SENSOR, "0")
    ultimo_estado = "0"
    print("Estado inicial: REPOSO (0)")

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
            time.sleep(2)
            continue
        
        # Leer estado actual del sensor
        impacto_actual = not impact_sensor.value()  # Invertir si es necesario
        
        # Obtener tiempo actual
        ahora = millis()
        
        # Si hace más de DEBOUNCE_TIME desde el último impacto, y el LED está encendido,
        # apagamos el LED y enviamos el estado de reposo
        if (not impacto_actual) and (ahora - ultimo_cambio > DEBOUNCE_TIME) and led_onboard.value():
            led_onboard.value(0)  # Apagar LED
            if client and ultimo_estado != "0":
                client.publish(MQTT_TOPIC_SENSOR, "0")
                ultimo_estado = "0"
                print("Estado: REPOSO (0)")
        
        # Enviar periódicamente el estado de reposo para asegurar sincronización
        if (not impacto_actual) and (ahora - ultimo_envio > INTERVALO_REPOSO):
            if client:
                client.publish(MQTT_TOPIC_SENSOR, "0")
                ultimo_envio = ahora
                if led_onboard.value():
                    led_onboard.value(0)  # Asegurar que el LED esté apagado
                print("Heartbeat: REPOSO (0)")
                
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(2)
        
    time.sleep(0.05)  # Pequeña pausa para estabilidad
