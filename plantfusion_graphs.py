
import pandas as pd
import matplotlib.pyplot as plt

file = "plantfusion_mqtt_data.csv"
df = pd.read_csv(file)

print("Total logged readings:", len(df))
print(df.tail())

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Graph 1: Air and soil temperature
df.plot(
    x="timestamp",
    y=["air_temp_c", "soil_temp_c"],
    marker="o",
    title="PlantFusion - Temperature"
)
plt.ylabel("Temperature (°C)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

# Graph 2: Soil moisture and light
df.plot(
    x="timestamp",
    y=["soil_moisture_pct", "light_pct"],
    marker="o",
    title="PlantFusion - Moisture and Light"
)
plt.ylabel("Percentage (%)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

# Graph 3: Virtual pH and EC
df.plot(
    x="timestamp",
    y=["virtual_ph", "virtual_ec"],
    marker="o",
    title="PlantFusion - Virtual pH and EC"
)
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
