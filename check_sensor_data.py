
import pandas as pd
from pathlib import Path

files = [
    Path("PlantFusion_Data.xlsx"),
    Path("plantfusion_mqtt_data.csv"),
]

sensor_columns = [
    "air_temp_c",
    "air_humidity_pct",
    "soil_moisture_pct",
    "light_pct",
    "virtual_ph",
    "virtual_ec",
    "soil_temp_c",
]

for file in files:
    if not file.exists():
        print(f"\nFile not found: {file}")
        continue

    if file.suffix == ".xlsx":
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    print("\n" + "=" * 55)
    print("FILE:", file.name)
    print("Total rows:", len(df))

    missing_columns = [
        col for col in sensor_columns
        if col not in df.columns
    ]

    if missing_columns:
        print("Missing columns:", missing_columns)
        continue

    for col in sensor_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print("\nMissing values:")
    print(df[sensor_columns].isna().sum())

    print("\nUnique values:")
    print(df[sensor_columns].nunique())

    print("\nMinimum values:")
    print(df[sensor_columns].min())

    print("\nMaximum values:")
    print(df[sensor_columns].max())

    print("\nDuplicate rows:", df.duplicated().sum())

    print("\nFirst 5 readings:")
    print(df.head().to_string(index=False))

print("\nData inspection complete.")
