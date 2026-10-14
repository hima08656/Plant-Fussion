
import json
import time
import queue
from datetime import datetime

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

# -----------------------------
# PlantFusion MQTT settings
# -----------------------------
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "plantfusion/demo/sensors"

st.set_page_config(
    page_title="PlantFusion Live Dashboard",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 PlantFusion — Live Sensor Dashboard")
st.caption("ESP32 + MQTT | Live simulated sensor readings")

# Queue shares incoming MQTT messages with the Streamlit page.
@st.cache_resource
def start_mqtt():
    message_queue = queue.Queue()
    connection_status = {"connected": False}

    def on_connect(client, userdata, flags, reason_code, properties):
        if str(reason_code) == "Success" or str(reason_code) == "0":
            connection_status["connected"] = True
            client.subscribe(MQTT_TOPIC)
        else:
            connection_status["connected"] = False

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        connection_status["connected"] = False

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            data["received_at"] = datetime.now().strftime("%H:%M:%S")
            message_queue.put(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="plantfusion_dashboard_client"
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
    except Exception as error:
        connection_status["error"] = str(error)

    return message_queue, connection_status, client


message_queue, connection_status, mqtt_client = start_mqtt()

if connection_status["connected"]:
    st.success(f"MQTT connected — topic: {MQTT_TOPIC}")
else:
    st.warning(
        "MQTT connection pending. Check that your Wokwi ESP32 simulation "
        "is running and publishing to the same topic."
    )
    if "error" in connection_status:
        st.caption(f"Connection detail: {connection_status['error']}")

# Keep a recent history of readings for the charts.
if "sensor_history" not in st.session_state:
    st.session_state.sensor_history = []

while not message_queue.empty():
    reading = message_queue.get()
    reading.setdefault("received_at", datetime.now().strftime("%H:%M:%S"))
    st.session_state.sensor_history.append(reading)

# Keep the latest 100 readings in the dashboard.
st.session_state.sensor_history = st.session_state.sensor_history[-100:]
history = st.session_state.sensor_history

if history:
    df = pd.DataFrame(history)

    # Numeric conversion helps graphs handle incoming JSON values.
    sensor_columns = [
        "air_temp_c",
        "air_humidity_pct",
        "soil_moisture_pct",
        "light_pct",
        "virtual_ph",
        "virtual_ec",
        "soil_temp_c",
    ]

    for column in sensor_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    latest = df.iloc[-1]

    st.subheader("📡 Latest Sensor Readings")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Air Temperature", f"{latest.get('air_temp_c', float('nan')):.1f} °C")
    c2.metric("Air Humidity", f"{latest.get('air_humidity_pct', float('nan')):.1f} %")
    c3.metric("Soil Moisture", f"{latest.get('soil_moisture_pct', float('nan')):.1f} %")
    c4.metric("Light Level", f"{latest.get('light_pct', float('nan')):.1f} %")

    c5, c6, c7 = st.columns(3)
    c5.metric("Virtual pH", f"{latest.get('virtual_ph', float('nan')):.2f}")
    c6.metric("Virtual EC", f"{latest.get('virtual_ec', float('nan')):.2f}")
    c7.metric("Soil Temperature", f"{latest.get('soil_temp_c', float('nan')):.1f} °C")

    st.subheader("📈 Live Sensor Graphs")

    if "received_at" in df.columns:
        chart_df = df.set_index("received_at")

        left, right = st.columns(2)

        with left:
            st.markdown("**Temperature**")
            temp_columns = [
                col for col in ["air_temp_c", "soil_temp_c"]
                if col in chart_df.columns
            ]
            if temp_columns:
                st.line_chart(chart_df[temp_columns])

        with right:
            st.markdown("**Soil Moisture and Light**")
            moisture_columns = [
                col for col in ["soil_moisture_pct", "light_pct"]
                if col in chart_df.columns
            ]
            if moisture_columns:
                st.line_chart(chart_df[moisture_columns])

        left2, right2 = st.columns(2)

        with left2:
            st.markdown("**Virtual pH**")
            if "virtual_ph" in chart_df.columns:
                st.line_chart(chart_df[["virtual_ph"]])

        with right2:
            st.markdown("**Virtual EC**")
            if "virtual_ec" in chart_df.columns:
                st.line_chart(chart_df[["virtual_ec"]])

    with st.expander("View recent raw sensor data"):
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.info(
        "Waiting for the first MQTT message. Start your Wokwi ESP32 simulation "
        "and confirm that it publishes to plantfusion/demo/sensors."
    )

st.caption("Dashboard refreshes approximately every 2 seconds.")

# Refresh the page so newly received readings appear automatically.
time.sleep(2)
st.rerun()
