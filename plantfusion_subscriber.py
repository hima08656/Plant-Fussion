
import json
import csv
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

# ==========================================
# PlantFusion MQTT Configuration
# ==========================================

BROKER = "test.mosquitto.org"
PORT = 1883

# Must match the topic in Wokwi sketch.ino
TOPIC = "plantfusion/hima08656/sensors"

# Save new readings in a separate CSV file
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "plantfusion_new_data.csv"

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


# ==========================================
# When MQTT connects
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT connection result:", reason_code)

    if reason_code == 0:
        client.subscribe(TOPIC)
        print("Subscribed to:", TOPIC)
        print("Saving new readings to:", CSV_FILE)
        print("Waiting for PlantFusion sensor data...")


# ==========================================
# When a sensor message arrives
# ==========================================

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))

        # Create a row with the expected CSV columns
        row = {
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        for field in FIELDS[1:]:
            row[field] = data.get(field)

        # Check whether the CSV needs a header
        file_is_new = (
            not CSV_FILE.exists()
            or CSV_FILE.stat().st_size == 0
        )

        # Append the new reading
        with open(
            CSV_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=FIELDS
            )

            if file_is_new:
                writer.writeheader()

            writer.writerow(row)

        print("\nNew PlantFusion reading received!")
        print("Timestamp:", row["timestamp"])

        for field in FIELDS[1:]:
            print(f"{field}: {row[field]}")

        print("Saved to:", CSV_FILE)

    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        print("Invalid MQTT message:", error)

    except (OSError, csv.Error) as error:
        print("CSV save error:", error)


# ==========================================
# Create MQTT client
# ==========================================

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="plantfusion-hima08656-subscriber"
)

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# Start subscriber
# ==========================================

print("Connecting to MQTT broker:", BROKER)
print("Listening on topic:", TOPIC)

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\nSubscriber stopped by user.")

except OSError as error:
    print("MQTT connection error:", error)

finally:
    client.disconnect()
    print("Subscriber closed.")
