
import pandas as pd
from pathlib import Path

file_path = Path("plantfusion_new_data.csv")

if not file_path.exists():
    print("CSV file not found!")
    raise SystemExit

df = pd.read_csv(file_path)

print("\n===== PLANTFUSION DATA QUALITY REPORT =====")
print("Total readings:", len(df))
print("Total columns:", len(df.columns))

sensor_columns = [
    "air_temp_c",
    "air_humidity_pct",
    "soil_moisture_pct",
    "light_pct",
    "virtual_ph",
    "virtual_ec",
    "soil_temp_c",
]

print("\n--- Missing values ---")
print(df[sensor_columns].isnull().sum())

print("\n--- Unique values ---")
print(df[sensor_columns].nunique())

print("\n--- Sensor statistics ---")
print(df[sensor_columns].describe().round(2).to_string())

print("\n--- Duplicate rows ---")
print("Exact duplicate rows:", df.duplicated().sum())

print("\n--- Values outside simulation ranges ---")
checks = {
    "soil_moisture_pct": (0, 100),
    "light_pct": (0, 100),
    "virtual_ph": (0, 14),
    "virtual_ec": (0, 4),
    "air_humidity_pct": (0, 100),
}

for column, (low, high) in checks.items():
    invalid = ((df[column] < low) | (df[column] > high)).sum()
    print(f"{column}: {invalid} out-of-range readings")

print("\nReport completed.")
