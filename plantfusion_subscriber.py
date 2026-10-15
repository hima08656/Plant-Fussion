
import json
import csv
import os
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "plantfusion/demo/sensors"
CSV_FILE = "plantfusion_mqtt_data.csv"

FIELDS = [
    "timestamp",
    "air_temp_c",
    "air_humidity_pct",
    "soil_moisture_pct",
    "light_pct",
    "virtual_ph",
    "virtual_ec",
    "soil_temp_c",
]

def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT connection result:", reason_code)
    if reason_code == 0:
        client.subscribe(TOPIC)
        print("Subscribed to:", TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        data["timestamp"] = datetime.now().isoformat(
            timespec="seconds"
        )

        new_file = (
            not os.path.exists(CSV_FILE)
            or os.path.getsize(CSV_FILE) == 0
        )

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)

            if new_file:
                writer.writeheader()

            writer.writerow({
                key: data.get(key, "")
                for key in FIELDS
            })

        print("Received:", data)
        print("Saved to:", CSV_FILE)

    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        print("Error:", e)

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="plantfusion-python-reader"
)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(BROKER, PORT, 60)
client.loop_forever()
